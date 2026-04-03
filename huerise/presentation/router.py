from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from huerise.application.commands import (
    ActivateAlarmCommand,
    ActivateAlarmCommandHandler,
    CancelAlarmCommand,
    CancelAlarmCommandHandler,
    CreateOneTimeAlarmCommand,
    CreateOneTimeAlarmCommandHandler,
    CreateRecurringAlarmCommand,
    CreateRecurringAlarmCommandHandler,
    DeactivateAlarmCommand,
    DeactivateAlarmCommandHandler,
    DeleteAlarmCommand,
    DeleteAlarmCommandHandler,
    DeleteSeriesCommand,
    DeleteSeriesCommandHandler,
)
from huerise.application.queries import ListAlarmsQuery, ListAlarmsQueryHandler
from huerise.presentation.mapper import to_alarm_out
from huerise.presentation.schemas import (
    AlarmOut,
    CreateOneTimeAlarmBody,
    CreateRecurringAlarmBody,
)

router = APIRouter(prefix="/alarms", tags=["Alarms"], route_class=DishkaRoute)


@router.get("", response_model=list[AlarmOut], operation_id="listAlarms")
async def list_alarms(
    handler: FromDishka[ListAlarmsQueryHandler],
) -> list[AlarmOut]:
    alarms = await handler.execute(ListAlarmsQuery())
    return [to_alarm_out(a) for a in alarms]


@router.post(
    "/one-time",
    response_model=AlarmOut,
    status_code=201,
    operation_id="createOneTimeAlarm",
)
async def create_one_time_alarm(
    body: CreateOneTimeAlarmBody,
    handler: FromDishka[CreateOneTimeAlarmCommandHandler],
) -> AlarmOut:
    alarm = await handler.execute(
        CreateOneTimeAlarmCommand(
            label=body.label,
            hour=body.hour,
            minute=body.minute,
            room_name=body.room_name,
            intro_audio_file=body.intro_audio_file,
            ringtone_audio_file=body.ringtone_audio_file,
            ringtone_volume=body.ringtone_volume,
            sunrise_duration_minutes=body.sunrise_duration_minutes,
        )
    )
    return to_alarm_out(alarm)


@router.post(
    "/recurring",
    response_model=AlarmOut,
    status_code=201,
    operation_id="createRecurringAlarm",
)
async def create_recurring_alarm(
    body: CreateRecurringAlarmBody,
    handler: FromDishka[CreateRecurringAlarmCommandHandler],
) -> AlarmOut:
    alarm = await handler.execute(
        CreateRecurringAlarmCommand(
            label=body.label,
            hour=body.hour,
            minute=body.minute,
            days=frozenset(body.days),
            room_name=body.room_name,
            intro_audio_file=body.intro_audio_file,
            ringtone_audio_file=body.ringtone_audio_file,
            ringtone_volume=body.ringtone_volume,
            sunrise_duration_minutes=body.sunrise_duration_minutes,
        )
    )
    return to_alarm_out(alarm)


@router.post(
    "/{alarm_id}/activate", response_model=AlarmOut, operation_id="activateAlarm"
)
async def activate_alarm(
    alarm_id: UUID,
    handler: FromDishka[ActivateAlarmCommandHandler],
) -> AlarmOut:
    alarm = await handler.execute(ActivateAlarmCommand(alarm_id=alarm_id))
    return to_alarm_out(alarm)


@router.post(
    "/{alarm_id}/deactivate", response_model=AlarmOut, operation_id="deactivateAlarm"
)
async def deactivate_alarm(
    alarm_id: UUID,
    handler: FromDishka[DeactivateAlarmCommandHandler],
) -> AlarmOut:
    alarm = await handler.execute(DeactivateAlarmCommand(alarm_id=alarm_id))
    return to_alarm_out(alarm)


@router.post("/{alarm_id}/cancel", response_model=AlarmOut, operation_id="cancelAlarm")
async def cancel_alarm(
    alarm_id: UUID,
    handler: FromDishka[CancelAlarmCommandHandler],
) -> AlarmOut:
    alarm = await handler.execute(CancelAlarmCommand(alarm_id=alarm_id))
    return to_alarm_out(alarm)


@router.delete(
    "/series/{series_id}",
    status_code=204,
    response_model=None,
    operation_id="deleteSeries",
)
async def delete_series(
    series_id: UUID,
    handler: FromDishka[DeleteSeriesCommandHandler],
) -> None:
    await handler.execute(DeleteSeriesCommand(series_id=series_id))


@router.delete(
    "/{alarm_id}", status_code=204, response_model=None, operation_id="deleteAlarm"
)
async def delete_alarm(
    alarm_id: UUID,
    handler: FromDishka[DeleteAlarmCommandHandler],
) -> None:
    await handler.execute(DeleteAlarmCommand(alarm_id=alarm_id))
