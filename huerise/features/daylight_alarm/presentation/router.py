from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import Depends, status
from fastapi_canon import CanonResponse, CanonRouter

from huerise.features.daylight_alarm.application import (
    DaylightAlarm,
    DaylightAlarmConfiguration,
)
from huerise.features.daylight_alarm.presentation.errors import (
    alarm_errors,
    configuration_errors,
    start_alarm_errors,
)
from huerise.features.daylight_alarm.presentation.mappers import (
    to_configuration_response,
)
from huerise.features.daylight_alarm.presentation.schemas import (
    AlarmStatusResponse,
    DaylightAlarmConfigurationRequest,
    DaylightAlarmConfigurationResponse,
    StartRequest,
)
from huerise.platform.api.authentication import require_api_key
from huerise.platform.api.errors import AUTHENTICATION_REQUIRED, CONFIGURATION_INVALID

router = CanonRouter(
    prefix="/daylight-alarm",
    tags=["daylight-alarm"],
    route_class=DishkaRoute,
    error_registry=alarm_errors,
    raises=[AUTHENTICATION_REQUIRED],
    dependencies=[Depends(require_api_key)],
)


@router.get(
    "/configuration",
    status_code=200,
    response_model=DaylightAlarmConfigurationResponse,
    operation_id="getDaylightAlarmConfiguration",
    raises=[CONFIGURATION_INVALID],
)
async def get_configuration(
    configuration: FromDishka[DaylightAlarmConfiguration],
) -> DaylightAlarmConfigurationResponse:
    alarm_configuration = configuration.get()
    return to_configuration_response(alarm_configuration)


@router.put(
    "/configuration",
    status_code=200,
    response_model=DaylightAlarmConfigurationResponse,
    operation_id="setDaylightAlarmConfiguration",
    raises=configuration_errors,
)
async def set_configuration(
    body: DaylightAlarmConfigurationRequest,
    configuration: FromDishka[DaylightAlarmConfiguration],
) -> DaylightAlarmConfigurationResponse:
    after_alarm = body.after_alarm
    alarm_configuration = await configuration.save(
        room_id=body.room_id,
        scene_id=body.scene_id,
        duration_seconds=body.duration_seconds,
        after_alarm_room_id=after_alarm.room_id if after_alarm is not None else None,
        after_alarm_scene_id=after_alarm.scene_id if after_alarm is not None else None,
        after_alarm_delay_seconds=(
            after_alarm.delay_seconds if after_alarm is not None else None
        ),
    )
    return to_configuration_response(alarm_configuration)


@router.post(
    "/start",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=AlarmStatusResponse,
    operation_id="startDaylightAlarm",
    raises=start_alarm_errors,
)
async def start(
    alarm: FromDishka[DaylightAlarm],
    body: StartRequest | None = None,
) -> AlarmStatusResponse:
    duration_seconds = await alarm.start(
        duration_seconds=body.duration_seconds if body is not None else None
    )
    return AlarmStatusResponse(duration_seconds=duration_seconds)


@router.post(
    "/stop",
    response=CanonResponse.empty(),
    response_model=None,
    operation_id="stopDaylightAlarm",
)
async def stop(alarm: FromDishka[DaylightAlarm]) -> None:
    await alarm.stop()
