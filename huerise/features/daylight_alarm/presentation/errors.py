from fastapi_canon import Error, ErrorRegistry

from huerise.features.daylight_alarm.application import (
    AlarmAlreadyRunningError,
    SceneDoesNotBelongToRoomError,
)
from huerise.features.lighting.presentation.errors import (
    HUE_UNAVAILABLE,
    SCENE_NOT_FOUND,
    lighting_errors,
)
from huerise.platform.api.errors import CONFIGURATION_INVALID

ALARM_ALREADY_RUNNING = Error(
    AlarmAlreadyRunningError,
    status=409,
    code="alarm_already_running",
    title="Alarm already running",
    detail=str,
    description="A daylight alarm is already running.",
)
SCENE_ROOM_MISMATCH = Error(
    SceneDoesNotBelongToRoomError,
    status=422,
    code="scene_room_mismatch",
    title="Scene does not belong to room",
    detail=str,
    description="The selected scene does not belong to the selected room.",
)

alarm_errors = ErrorRegistry.merge(
    lighting_errors,
    ErrorRegistry(
        name="daylight_alarm", errors=[ALARM_ALREADY_RUNNING, SCENE_ROOM_MISMATCH]
    ),
    name="daylight_alarm",
)

start_alarm_errors = [
    ALARM_ALREADY_RUNNING,
    SCENE_NOT_FOUND,
    CONFIGURATION_INVALID,
    HUE_UNAVAILABLE,
]
configuration_errors = [
    SCENE_ROOM_MISMATCH,
    SCENE_NOT_FOUND,
    CONFIGURATION_INVALID,
    HUE_UNAVAILABLE,
]
