import asyncio
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from math import isclose
from typing import Any, Literal
from uuid import UUID

from hueify import ConnectionStatus, Hueify
from hueify.models import (
    EntertainmentConfigurationEvent,
    HueEvent,
    HueModel,
    Scene,
    SceneEvent,
    SceneStatusValue,
)

from huerise.features.lighting.domain import HueUnavailableError, LightingOverrideError

_STATE_PATHS = {
    "on": ("on", "on"),
    "brightness": ("dimming", "brightness"),
    "xy": ("color", "xy"),
    "mirek": ("color_temperature", "mirek"),
    "gradient": ("gradient", "points"),
    "effect": ("effects", "status"),
}
_ECHO_SECONDS = 5.0
_ACTIVE_SCENES = {
    SceneStatusValue.ACTIVE,
    SceneStatusValue.STATIC,
    SceneStatusValue.DYNAMIC_PALETTE,
}


@dataclass(frozen=True, slots=True)
class _ExpectedChange:
    value: Any
    expires: float


class RoomControlMonitor:
    def __init__(
        self,
        client: Hueify,
        *,
        clock: Callable[[], float] = time.monotonic,
        connection_timeout: float = 5.0,
    ) -> None:
        self._client = client
        self._clock = clock
        self._connection_timeout = connection_timeout
        self._states: dict[UUID, dict[str, Any]] = {}
        self._expected: dict[tuple[UUID, str], deque[_ExpectedChange]] = {}
        self._targets: dict[tuple[UUID, str], Any] = {}
        self._room_lights: dict[UUID, set[UUID]] = {}
        self._groups: dict[UUID, UUID] = {}
        self._scenes: dict[UUID, Scene] = {}
        self._areas: set[UUID] = set()
        self._scene_id: UUID | None = None
        self._changed = asyncio.Event()
        self._ready = asyncio.Event()
        self._signals: asyncio.Queue[Literal["override", "disconnected"]] = (
            asyncio.Queue()
        )
        self._failure: Exception | None = None
        self._connected = False
        self._ever_connected = False
        self._buffer: list[HueEvent] | None = None

    async def start(self, room_id: UUID) -> None:
        lights = await self._client.rooms.lights(room_id)
        group = await self._client.rooms.grouped_light(room_id)
        scenes = await self._client.rooms.scenes(room_id)
        self._room_lights[room_id] = {light.id for light in lights}
        self._groups[room_id] = group.id
        self._states.update({light.id: _state(light) for light in lights})
        self._states[group.id] = _state(group)
        self._scenes.update({scene.id: scene for scene in scenes})
        for area in (await self._client.entertainment.list()).data:
            members = {service.rid for service in area.light_services}
            members.update(
                member.service.rid
                for channel in area.channels
                for member in channel.members
            )
            if members & self._room_lights[room_id]:
                if area.is_streaming:
                    raise HueUnavailableError(
                        "Alarm lights are controlled by an entertainment stream"
                    )
                self._areas.add(area.id)
        self._client.on("*", self._on_event)
        self._client.on_connection_change(self._on_connection)
        await self._client.start_stream(timeout=self._connection_timeout)
        await self.wait_ready()
        await self._resync(initial=True)
        self.ensure_control()

    async def wait_ready(self) -> None:
        try:
            async with asyncio.timeout(self._connection_timeout):
                await self._ready.wait()
        except TimeoutError as error:
            raise HueUnavailableError("Lost the Hue Bridge event stream") from error
        self.ensure_control()

    def ensure_control(self) -> None:
        if self._failure is not None:
            raise self._failure
        if self._changed.is_set():
            raise LightingOverrideError("Another control changed the alarm lights")

    async def wait_for_override(self) -> None:
        while not self._changed.is_set():
            if await self._signals.get() == "disconnected":
                await self.wait_ready()
        self.ensure_control()

    def expect_scene(self, scene_id: UUID, brightness: float) -> bool:
        self.ensure_control()
        if scene_id not in self._scenes:
            return False
        scene = self._scenes[scene_id]
        self._scene_id = scene_id
        self._buffer = []
        for action in scene.actions:
            values = _state(action.action)
            if values.get("on", True):
                values["brightness"] = brightness
            self._expect(action.target.rid, values)
        self._expect(
            self._groups[scene.group.rid],
            {
                "brightness": brightness,
                "on": any(action.action.is_on for action in scene.actions),
            },
        )
        return True

    async def finish_scene(self, scene_id: UUID) -> None:
        scene = self._scenes[scene_id]
        # The bridge may clip scene colors to a lamp's gamut or derive xy from mirek.
        for light in await self._client.rooms.lights(scene.group.rid):
            values = _state(light)
            self._expect(
                light.id,
                {
                    key: values[key]
                    for key in ("xy", "mirek", "gradient")
                    if key in values
                },
            )
        buffered, self._buffer = self._buffer or [], None
        for event in buffered:
            self._observe(event)
        self.ensure_control()

    def expect_brightness(self, room_id: UUID, brightness: float) -> None:
        self.ensure_control()
        for resource_id in {*self._room_lights[room_id], self._groups[room_id]}:
            self._expect(resource_id, {"brightness": brightness, "on": True})

    def close(self) -> None:
        self._connected = False
        self._client.off("*", self._on_event)
        self._client.off_connection_change(self._on_connection)

    def _expect(self, resource_id: UUID, values: dict[str, Any]) -> None:
        for name, value in values.items():
            self._targets[resource_id, name] = value
            expected = self._expected.setdefault((resource_id, name), deque(maxlen=16))
            expected.append(_ExpectedChange(value, self._clock() + _ECHO_SECONDS))

    async def _on_connection(self, status: ConnectionStatus) -> None:
        if status.connected:
            if self._ever_connected:
                try:
                    await self._resync()
                except Exception as error:
                    self._failure = HueUnavailableError(
                        "Could not verify alarm lights after reconnecting"
                    )
                    self._failure.__cause__ = error
                    self._override()
            self._ever_connected = True
            self._connected = True
            self._ready.set()
        elif self._connected:
            self._connected = False
            self._ready.clear()
            self._signals.put_nowait("disconnected")

    async def _resync(self, *, initial: bool = False) -> None:
        for room_id in self._room_lights:
            resources = [
                *await self._client.rooms.lights(room_id),
                await self._client.rooms.grouped_light(room_id),
            ]
            for resource in resources:
                self._observe(
                    HueEvent.model_validate(resource.model_dump()), resync=True
                )
            for scene in await self._client.rooms.scenes(room_id):
                previous = self._scenes.get(scene.id)
                if initial and previous is not None and previous.status == scene.status:
                    continue
                self._scenes.setdefault(scene.id, scene)
                await self._on_event(SceneEvent(id=scene.id, status=scene.status))
        for area in (await self._client.entertainment.list()).data:
            if area.id in self._areas and area.is_streaming:
                self._override()

    def _override(self) -> None:
        if not self._changed.is_set():
            self._changed.set()
            self._signals.put_nowait("override")

    async def _on_event(self, event: HueEvent) -> None:
        if isinstance(event, SceneEvent):
            if (
                event.id in self._scenes
                and event.id != self._scene_id
                and event.status is not None
                and event.status.active in _ACTIVE_SCENES
            ):
                self._override()
            return
        if isinstance(event, EntertainmentConfigurationEvent):
            if event.id in self._areas and event.is_streaming:
                self._override()
            return
        if event.id not in self._states:
            return
        if self._buffer is not None:
            self._buffer.append(event)
        else:
            self._observe(event)

    def _observe(self, event: HueEvent, *, resync: bool = False) -> None:
        raw = event.model_dump(exclude_none=True)
        if raw.get("dimming_delta") or raw.get("mode") == "streaming":
            self._override()
            return
        state = self._states[event.id]
        for name, value in _state(event).items():
            key = (event.id, name)
            if resync and key in self._targets:
                if not _matches(name, self._targets[key], value):
                    self._override()
                    return
                state[name] = value
                self._expected.pop(key, None)
                continue
            if name in state and _matches(name, state[name], value):
                continue
            expected = self._expected.get((event.id, name), deque())
            while expected and expected[0].expires < self._clock():
                expected.popleft()
            match = next(
                (
                    index
                    for index, change in enumerate(expected)
                    if _matches(name, change.value, value)
                ),
                None,
            )
            if match is None:
                self._override()
                return
            for _ in range(match + 1):
                expected.popleft()
            state[name] = value


def _state(resource: HueModel) -> dict[str, Any]:
    raw = resource.model_dump(exclude_none=True, exclude_unset=True)
    values = {
        name: raw[parent][child]
        for name, (parent, child) in _STATE_PATHS.items()
        if isinstance(raw.get(parent), dict) and raw[parent].get(child) is not None
    }
    effect = raw.get("effects", {})
    if "effect" in effect:
        values["effect"] = effect["effect"]
    if raw.get("color_temperature", {}).get("mirek_valid") is False:
        values.pop("mirek", None)
    if "gradient" in values:
        values["gradient"] = [point["color"]["xy"] for point in values["gradient"]]
    return values


def _matches(name: str, expected: Any, actual: Any) -> bool:
    if name == "brightness":
        # Hue brightness reports are quantized to approximately 100 / 254 percent.
        return isclose(expected, actual, abs_tol=0.5)
    if name == "xy":
        return all(
            isclose(expected[key], actual[key], abs_tol=0.002) for key in ("x", "y")
        )
    if name == "gradient":
        return len(expected) == len(actual) and all(
            _matches("xy", left, right)
            for left, right in zip(expected, actual, strict=True)
        )
    return expected == actual
