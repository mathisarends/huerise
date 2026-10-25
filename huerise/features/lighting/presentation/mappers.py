from collections.abc import Sequence

from huerise.features.lighting.application import DoctorReport
from huerise.features.lighting.domain import DiscoveredBridge, OnboardingStatus, Room
from huerise.features.lighting.presentation.schemas import (
    BridgeResponse,
    DoctorCheckResponse,
    DoctorResponse,
    OnboardingStatusResponse,
    RoomResponse,
    SceneResponse,
)


def to_doctor_response(report: DoctorReport) -> DoctorResponse:
    return DoctorResponse(
        status=report.status,
        checks=[
            DoctorCheckResponse(name=check.name, status=check.status)
            for check in report.checks
        ],
    )


def to_room_response(room: Room) -> RoomResponse:
    return RoomResponse(
        id=room.id,
        name=room.name,
        scenes=[
            SceneResponse(id=scene.id, name=scene.name, brightness=scene.brightness)
            for scene in room.scenes
        ],
    )


def to_bridge_response(bridge: DiscoveredBridge) -> BridgeResponse:
    return BridgeResponse(
        id=bridge.id,
        ip_address=bridge.ip_address,
        selected=bridge.selected,
    )


def to_bridges_response(bridges: Sequence[DiscoveredBridge]) -> list[BridgeResponse]:
    return [to_bridge_response(bridge) for bridge in bridges]


def to_rooms_response(rooms: Sequence[Room]) -> list[RoomResponse]:
    return [to_room_response(room) for room in rooms]


def to_onboarding_status_response(
    onboarding: OnboardingStatus,
) -> OnboardingStatusResponse:
    return OnboardingStatusResponse(
        state=onboarding.state,
        bridge_id=onboarding.bridge_id,
        ip_address=onboarding.ip_address,
        read_only=onboarding.read_only,
    )
