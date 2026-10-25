import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import cast
from uuid import UUID

import pytest
from hueify import Hueify
from hueify.models import (
    ColorTemperatureState,
    EffectsState,
    EntertainmentChannel,
    EntertainmentConfiguration,
    EntertainmentConfigurationEvent,
    GradientState,
    GroupedLight,
    HueEvent,
    Light,
    LightEvent,
    Scene,
    SceneEvent,
    SceneStatus,
)
from hueify.sse.bus import EventBus
from hueify.sse.connection import ConnectionHandler, StreamConnection

from huerise.features.lighting.domain import HueUnavailableError, LightingOverrideError
from huerise.features.lighting.infrastructure.control import RoomControlMonitor
from huerise.features.lighting.infrastructure.hue import HueifyClient

ROOM = UUID(int=1)
LIGHT = UUID(int=2)
GROUP = UUID(int=3)
SCENE = UUID(int=4)
OTHER_SCENE = UUID(int=5)
AREA = UUID(int=6)
UNRELATED = UUID(int=7)


def scene(scene_id: UUID, room_id: UUID = ROOM) -> Scene:
    return Scene.model_validate(
        {
            "id": scene_id,
            "metadata": {"name": "Sunrise"},
            "group": {"rid": room_id, "rtype": "room"},
            "actions": [
                {
                    "target": {"rid": LIGHT, "rtype": "light"},
                    "action": {
                        "on": {"on": True},
                        "dimming": {"brightness": 80},
                        "color": {"xy": {"x": 0.6, "y": 0.3}},
                    },
                }
            ],
        }
    )


@dataclass
class Bridge:
    light: Light = field(
        default_factory=lambda: Light.model_validate(
            {
                "id": LIGHT,
                "metadata": {"name": "Bed"},
                "owner": {"rid": UUID(int=8), "rtype": "device"},
                "on": {"on": False},
                "dimming": {"brightness": 10},
                "color": {"xy": {"x": 0.2, "y": 0.3}},
            }
        )
    )
    group: GroupedLight = field(
        default_factory=lambda: GroupedLight.model_validate(
            {"id": GROUP, "on": {"on": False}, "dimming": {"brightness": 10}}
        )
    )
    scenes_data: list[Scene] = field(
        default_factory=lambda: [scene(SCENE), scene(OTHER_SCENE)]
    )
    areas: list[EntertainmentConfiguration] = field(
        default_factory=lambda: [
            EntertainmentConfiguration.model_validate(
                {
                    "id": AREA,
                    "metadata": {"name": "TV"},
                    "status": "inactive",
                    "light_services": [{"rid": LIGHT, "rtype": "light"}],
                }
            )
        ]
    )
    bus: EventBus = field(default_factory=EventBus)
    connection: StreamConnection = field(default_factory=StreamConnection)
    commands: list[tuple[str, UUID, float]] = field(default_factory=list)
    start_timeouts: list[float | None] = field(default_factory=list)
    echo: bool = True
    start_error: Exception | None = None
    read_error: Exception | None = None
    clipped_color: dict[str, float] | None = None
    closed: bool = False

    @property
    def rooms(self) -> SimpleNamespace:
        return SimpleNamespace(
            lights=self.lights,
            grouped_light=self.grouped_light,
            scenes=self.scenes_for_room,
            set_brightness=self.set_brightness,
        )

    @property
    def scenes(self) -> SimpleNamespace:
        return SimpleNamespace(activate=self.activate)

    @property
    def entertainment(self) -> SimpleNamespace:
        return SimpleNamespace(list=self.entertainment_areas)

    async def lights(self, room_id: UUID) -> list[Light]:
        assert room_id == ROOM
        if self.read_error is not None:
            raise self.read_error
        return [self.light]

    async def grouped_light(self, room_id: UUID) -> GroupedLight:
        assert room_id == ROOM
        return self.group

    async def scenes_for_room(self, room_id: UUID) -> list[Scene]:
        return [item for item in self.scenes_data if item.group.rid == room_id]

    async def entertainment_areas(self) -> SimpleNamespace:
        return SimpleNamespace(data=self.areas)

    def on(
        self, resource_type: str, handler: Callable[[HueEvent], Awaitable[None]]
    ) -> None:
        assert resource_type == "*"
        self.bus.on("*", handler)

    def off(
        self, resource_type: str, handler: Callable[[HueEvent], Awaitable[None]]
    ) -> None:
        assert resource_type == "*"
        self.bus.off("*", handler)

    def on_connection_change(self, handler: ConnectionHandler) -> None:
        self.connection.on_change(handler)

    def off_connection_change(self, handler: ConnectionHandler) -> None:
        self.connection.off_change(handler)

    async def start_stream(self, timeout: float | None = None) -> None:
        self.start_timeouts.append(timeout)
        if self.start_error is not None:
            raise self.start_error
        await self.connection.opened()

    async def close(self) -> None:
        self.closed = True
        await self.connection.closed()

    async def emit(self, event: HueEvent) -> None:
        await self.bus.dispatch(event)

    async def activate(self, scene_id: UUID, *, brightness: float) -> None:
        assert self.connection.connected
        self.commands.append(("activate", scene_id, brightness))
        chosen = next(item for item in self.scenes_data if item.id == scene_id)
        if chosen.group.rid != ROOM:
            return
        for item in self.scenes_data:
            item.status = SceneStatus(
                active="static" if item.id == scene_id else "inactive"
            )
        update = chosen.actions[0].action.model_dump(exclude_none=True)
        update["dimming"] = {"brightness": brightness}
        if self.clipped_color is not None:
            update["color"] = {"xy": self.clipped_color}
        self.light = Light.model_validate(self.light.model_dump() | update)
        self.group = GroupedLight.model_validate(
            self.group.model_dump()
            | {"on": {"on": True}, "dimming": {"brightness": brightness}}
        )
        if self.echo:
            await self.emit(SceneEvent(id=scene_id, status=chosen.status))
            await self.emit(LightEvent.model_validate({"id": LIGHT} | update))
            await self.emit(HueEvent.model_validate(self.group.model_dump()))

    async def set_brightness(self, room_id: UUID, brightness: float) -> None:
        assert room_id == ROOM
        self.commands.append(("brightness", room_id, brightness))
        update = {"on": {"on": True}, "dimming": {"brightness": brightness}}
        self.light = Light.model_validate(self.light.model_dump() | update)
        self.group = GroupedLight.model_validate(self.group.model_dump() | update)
        if self.echo:
            await self.emit(LightEvent.model_validate({"id": LIGHT} | update))
            await self.emit(HueEvent.model_validate(self.group.model_dump()))


@pytest.fixture
def bridge() -> Bridge:
    return Bridge()


async def monitored(bridge: Bridge) -> HueifyClient:
    client = HueifyClient(cast(Hueify, bridge))
    await client.watch_room(ROOM)
    await client.activate_scene(SCENE, brightness=1)
    return client


async def test_connects_before_commands_and_ignores_own_state_updates(
    bridge: Bridge,
) -> None:
    client = await monitored(bridge)
    await client.set_brightness(ROOM, 20)
    await client.set_brightness(ROOM, 30)
    await bridge.emit(SceneEvent(id=SCENE, status=SceneStatus(active="inactive")))
    await client.set_brightness(ROOM, 40)
    await client.close()

    assert bridge.start_timeouts == [5]
    assert bridge.closed
    assert not bridge.bus._handlers["*"]
    assert not bridge.connection._handlers
    assert len(bridge.commands) == 4


@pytest.mark.parametrize(
    "event",
    [
        LightEvent(id=LIGHT, on={"on": False}),
        LightEvent(id=LIGHT, dimming={"brightness": 80}),
        LightEvent(id=LIGHT, color={"xy": {"x": 0.1, "y": 0.8}}),
        LightEvent(id=LIGHT, color_temperature={"mirek": 300}),
        LightEvent(id=LIGHT, effects={"status": "candle"}),
        LightEvent(
            id=LIGHT, gradient={"points": [{"color": {"xy": {"x": 0.2, "y": 0.7}}}]}
        ),
        LightEvent(id=LIGHT, dimming_delta={"action": "down", "brightness_delta": 10}),
        LightEvent(id=LIGHT, mode="streaming"),
        HueEvent(id=GROUP, type="grouped_light", on={"on": False}),
        HueEvent(id=GROUP, type="grouped_light", dimming={"brightness": 80}),
        SceneEvent(id=OTHER_SCENE, status=SceneStatus(active="static")),
        EntertainmentConfigurationEvent(id=AREA, status="active"),
    ],
)
async def test_external_control_blocks_all_further_commands(
    bridge: Bridge, event: HueEvent
) -> None:
    client = await monitored(bridge)
    await bridge.emit(event)

    with pytest.raises(LightingOverrideError):
        await client.wait_for_override()
    with pytest.raises(LightingOverrideError):
        await client.set_brightness(ROOM, 50)

    assert bridge.commands == [("activate", SCENE, 1)]
    await client.close()


@pytest.mark.parametrize(
    "event",
    [
        LightEvent(id=UNRELATED, on={"on": False}),
        HueEvent(id=UNRELATED, type="grouped_light", dimming={"brightness": 80}),
        SceneEvent(id=UNRELATED, status=SceneStatus(active="static")),
        EntertainmentConfigurationEvent(id=UNRELATED, status="active"),
        EntertainmentConfigurationEvent(id=AREA, status="inactive"),
        LightEvent(id=LIGHT, metadata={"name": "Renamed"}),
        LightEvent(id=LIGHT, gradient={"points_capable": 5}),
        LightEvent(id=LIGHT, color_temperature={"mirek": 400, "mirek_valid": False}),
        LightEvent(id=LIGHT, on={"on": True}),
    ],
)
async def test_unrelated_or_unchanged_events_do_not_stop_the_alarm(
    bridge: Bridge, event: HueEvent
) -> None:
    client = await monitored(bridge)
    await bridge.emit(event)
    await client.set_brightness(ROOM, 20)
    await client.close()


async def test_scene_color_clipping_does_not_look_like_manual_control(
    bridge: Bridge,
) -> None:
    bridge.clipped_color = {"x": 0.4, "y": 0.4}
    client = await monitored(bridge)
    await client.set_brightness(ROOM, 20)
    await client.close()


async def test_late_and_quantized_echoes_are_accepted_once(bridge: Bridge) -> None:
    client = await monitored(bridge)
    bridge.echo = False
    await client.set_brightness(ROOM, 10)
    await client.set_brightness(ROOM, 20)
    await bridge.emit(LightEvent(id=LIGHT, dimming={"brightness": 10.19}))
    await bridge.emit(LightEvent(id=LIGHT, dimming={"brightness": 20.08}))
    await bridge.emit(LightEvent(id=LIGHT, dimming={"brightness": 10}))

    with pytest.raises(LightingOverrideError):
        await client.set_brightness(ROOM, 30)
    await client.close()


async def test_expired_echo_is_treated_as_a_new_external_change(bridge: Bridge) -> None:
    now = 0.0
    monitor = RoomControlMonitor(cast(Hueify, bridge), clock=lambda: now)
    await monitor.start(ROOM)
    monitor.expect_brightness(ROOM, 30)
    now = 6.0
    await bridge.emit(LightEvent(id=LIGHT, dimming={"brightness": 30}))

    with pytest.raises(LightingOverrideError):
        monitor.ensure_control()
    monitor.close()


async def test_reconnect_verifies_state_before_allowing_more_commands(
    bridge: Bridge,
) -> None:
    client = await monitored(bridge)
    await client.set_brightness(ROOM, 20)
    await bridge.connection.closed()
    pending = asyncio.create_task(client.set_brightness(ROOM, 30))
    await asyncio.sleep(0)
    assert bridge.commands[-1] == ("brightness", ROOM, 20)
    await bridge.connection.opened()
    await pending
    await client.close()

    assert bridge.commands[-1] == ("brightness", ROOM, 30)


async def test_changes_during_reconnect_prevent_later_commands(bridge: Bridge) -> None:
    client = await monitored(bridge)
    await bridge.connection.closed()
    bridge.light = bridge.light.model_copy(
        update={"on": bridge.light.on.model_copy(update={"on": False})}
    )
    await bridge.connection.opened()

    with pytest.raises(LightingOverrideError):
        await client.wait_for_override()
    assert len(bridge.commands) == 1
    await client.close()


async def test_failed_reconnect_read_stops_observation(bridge: Bridge) -> None:
    client = await monitored(bridge)
    await bridge.connection.closed()
    bridge.read_error = OSError("offline")
    await bridge.connection.opened()

    with pytest.raises(HueUnavailableError, match="verify alarm lights"):
        await client.wait_for_override()
    await client.close()


async def test_disconnected_stream_has_a_bounded_wait(bridge: Bridge) -> None:
    monitor = RoomControlMonitor(cast(Hueify, bridge), connection_timeout=0.01)
    await monitor.start(ROOM)
    await bridge.connection.closed()

    with pytest.raises(HueUnavailableError, match="event stream"):
        await monitor.wait_for_override()
    monitor.close()


async def test_existing_entertainment_control_is_not_taken_over(bridge: Bridge) -> None:
    bridge.areas[0].status = "active"
    client = HueifyClient(cast(Hueify, bridge))

    with pytest.raises(HueUnavailableError, match="entertainment stream"):
        await client.watch_room(ROOM)
    assert bridge.commands == []
    await client.close()


async def test_other_after_alarm_room_can_be_activated(bridge: Bridge) -> None:
    foreign = scene(UNRELATED, UNRELATED)
    bridge.scenes_data.append(foreign)
    client = await monitored(bridge)
    await client.activate_scene(UNRELATED, brightness=40)
    await client.close()

    assert bridge.commands[-1] == ("activate", UNRELATED, 40)


async def test_stream_start_failure_does_not_send_a_light_command(
    bridge: Bridge,
) -> None:
    bridge.start_error = TimeoutError("not connected")
    client = HueifyClient(cast(Hueify, bridge))

    with pytest.raises(TimeoutError):
        await client.watch_room(ROOM)
    assert bridge.commands == []
    await client.close()


async def test_entertainment_channels_identify_the_affected_lights(
    bridge: Bridge,
) -> None:
    bridge.areas[0].light_services = []
    bridge.areas[0].channels = [
        EntertainmentChannel.model_validate(
            {
                "channel_id": 0,
                "position": {"x": 0, "y": 0, "z": 0},
                "members": [{"service": {"rid": LIGHT, "rtype": "light"}, "index": 0}],
            }
        )
    ]
    client = await monitored(bridge)
    await bridge.emit(EntertainmentConfigurationEvent(id=AREA, status="active"))

    with pytest.raises(LightingOverrideError):
        await client.wait_for_override()
    await client.close()


async def test_scene_gradients_and_metadata_are_correlated(bridge: Bridge) -> None:
    bridge.scenes_data[0].actions[0].action.gradient = GradientState.model_validate(
        {
            "points": [{"color": {"xy": {"x": 0.4, "y": 0.4}}}],
        }
    )
    client = await monitored(bridge)
    await bridge.emit(
        LightEvent(
            id=LIGHT,
            gradient={
                "points": [
                    {"color": {"xy": {"x": 0.4001, "y": 0.3999}, "gamut_type": "C"}}
                ],
            },
        )
    )
    await client.set_brightness(ROOM, 20)
    await bridge.emit(LightEvent(id=LIGHT, gradient={"points": []}))

    with pytest.raises(LightingOverrideError):
        await client.set_brightness(ROOM, 30)
    await client.close()


async def test_scene_effect_acknowledgements_are_ignored(bridge: Bridge) -> None:
    bridge.scenes_data[0].actions[0].action.effects = EffectsState(effect="candle")
    client = await monitored(bridge)
    await bridge.emit(LightEvent(id=LIGHT, effects={"status": "candle"}))
    await client.set_brightness(ROOM, 20)
    await bridge.emit(LightEvent(id=LIGHT, effects={"status": "no_effect"}))

    with pytest.raises(LightingOverrideError):
        await client.wait_for_override()
    await client.close()


async def test_scene_temperature_is_an_own_command(bridge: Bridge) -> None:
    action = bridge.scenes_data[0].actions[0].action
    action.color = None
    action.color_temperature = ColorTemperatureState(mirek=300)
    bridge.clipped_color = {"x": 0.4, "y": 0.4}
    client = await monitored(bridge)
    await client.set_brightness(ROOM, 20)
    await client.close()


async def test_entertainment_in_another_room_is_ignored(bridge: Bridge) -> None:
    bridge.areas[0].light_services[0].rid = UNRELATED
    bridge.areas[0].status = "active"
    client = await monitored(bridge)
    await bridge.emit(EntertainmentConfigurationEvent(id=AREA, status="active"))
    await client.set_brightness(ROOM, 20)
    await client.close()


async def test_a_scene_switch_during_reconnect_is_detected(bridge: Bridge) -> None:
    client = await monitored(bridge)
    await bridge.connection.closed()
    bridge.scenes_data[1].status = SceneStatus(active="static")
    await bridge.connection.opened()

    with pytest.raises(LightingOverrideError):
        await client.wait_for_override()
    await client.close()


async def test_entertainment_takeover_during_reconnect_is_detected(
    bridge: Bridge,
) -> None:
    client = await monitored(bridge)
    await bridge.connection.closed()
    bridge.areas[0].status = "active"
    await bridge.connection.opened()

    with pytest.raises(LightingOverrideError):
        await client.wait_for_override()
    await client.close()
