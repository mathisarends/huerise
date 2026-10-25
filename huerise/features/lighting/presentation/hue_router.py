from dishka.integrations.fastapi import DishkaRoute, FromDishka

from huerise.features.lighting.application import HueOnboarding, SceneService
from huerise.features.lighting.presentation.errors import (
    bridge_status_errors,
    discover_bridges_errors,
    register_bridge_errors,
    scene_errors,
    select_bridge_errors,
)
from huerise.features.lighting.presentation.mappers import (
    to_bridges_response,
    to_onboarding_status_response,
    to_rooms_response,
)
from huerise.features.lighting.presentation.schemas import (
    BridgeResponse,
    BridgeSelectionRequest,
    OnboardingStatusResponse,
    RoomResponse,
)
from huerise.platform.api.errors import ExceptionRouter

hue_router = ExceptionRouter(
    prefix="/hue",
    tags=["hue"],
    route_class=DishkaRoute,
)


@hue_router.get(
    "/bridges",
    response_model=list[BridgeResponse],
    operation_id="listHueBridges",
    errors=discover_bridges_errors,
)
async def discover_bridges(
    onboarding: FromDishka[HueOnboarding],
) -> list[BridgeResponse]:
    bridges = await onboarding.discover()
    return to_bridges_response(bridges)


@hue_router.get(
    "/bridge",
    response_model=OnboardingStatusResponse,
    operation_id="getHueBridge",
    errors=bridge_status_errors,
)
async def bridge_status(
    onboarding: FromDishka[HueOnboarding],
) -> OnboardingStatusResponse:
    status = onboarding.status()
    return to_onboarding_status_response(status)


@hue_router.put(
    "/bridge",
    response_model=OnboardingStatusResponse,
    operation_id="selectHueBridge",
    errors=select_bridge_errors,
)
async def select_bridge(
    body: BridgeSelectionRequest,
    onboarding: FromDishka[HueOnboarding],
) -> OnboardingStatusResponse:
    status = await onboarding.select(body.bridge_id)
    return to_onboarding_status_response(status)


@hue_router.post(
    "/bridge/register",
    response_model=OnboardingStatusResponse,
    operation_id="registerHueBridge",
    errors=register_bridge_errors,
)
async def register_bridge(
    onboarding: FromDishka[HueOnboarding],
) -> OnboardingStatusResponse:
    status = await onboarding.register()
    return to_onboarding_status_response(status)


@hue_router.get(
    "/rooms",
    response_model=list[RoomResponse],
    operation_id="listRooms",
    errors=scene_errors,
)
async def rooms(
    scenes: FromDishka[SceneService],
) -> list[RoomResponse]:
    rooms = await scenes.list_rooms()
    return to_rooms_response(rooms)
