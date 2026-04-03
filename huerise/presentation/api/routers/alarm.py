# router.py
from uuid import UUID
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException
from huerise.application.alarm_service import AlarmService
from huerise.presentation.api.schemas import (
    AlarmOut,
    CreateOneTimeAlarmBody,
    CreateRecurringAlarmBody,
)

alarms_router = APIRouter(
    prefix="/alarms",
    tags=["Alarms"],
    route_class=DishkaRoute,
)


@alarms_router.get(
    "",
    response_model=list[AlarmOut],
    summary="List all alarms",
    operation_id="listAlarms",
)
async def list_alarms(service: FromDishka[AlarmService]) -> list[AlarmOut]:
    return await service.list_all()


@alarms_router.post(
    "/one-time",
    response_model=AlarmOut,
    status_code=201,
    summary="Create a one-time alarm",
    operation_id="createOneTimeAlarm",
)
async def create_one_time_alarm(
    body: CreateOneTimeAlarmBody,
    service: FromDishka[AlarmService],
) -> AlarmOut:
    return await service.create_one_time(body)


@alarms_router.post(
    "/recurring",
    response_model=AlarmOut,
    status_code=201,
    summary="Create a recurring alarm",
    operation_id="createRecurringAlarm",
)
async def create_recurring_alarm(
    body: CreateRecurringAlarmBody,
    service: FromDishka[AlarmService],
) -> AlarmOut:
    return await service.create_recurring(body)


@alarms_router.post(
    "/{alarm_id}/activate",
    response_model=AlarmOut,
    summary="Activate an inactive alarm",
    operation_id="activateAlarm",
)
async def activate_alarm(
    alarm_id: UUID,
    service: FromDishka[AlarmService],
) -> AlarmOut:
    try:
        return await service.activate(alarm_id)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@alarms_router.post(
    "/{alarm_id}/deactivate",
    response_model=AlarmOut,
    summary="Deactivate a scheduled alarm",
    operation_id="deactivateAlarm",
)
async def deactivate_alarm(
    alarm_id: UUID,
    service: FromDishka[AlarmService],
) -> AlarmOut:
    try:
        return await service.deactivate(alarm_id)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@alarms_router.post(
    "/{alarm_id}/cancel",
    response_model=AlarmOut,
    summary="Cancel the next trigger of an alarm",
    operation_id="cancelAlarm",
)
async def cancel_alarm(
    alarm_id: UUID,
    service: FromDishka[AlarmService],
) -> AlarmOut:
    try:
        return await service.cancel(alarm_id)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@alarms_router.delete(
    "/{alarm_id}",
    status_code=204,
    summary="Permanently delete an alarm",
    operation_id="deleteAlarm",
)
async def delete_alarm(
    alarm_id: UUID,
    service: FromDishka[AlarmService],
) -> None:
    await service.delete(alarm_id)


@alarms_router.delete(
    "/series/{series_id}",
    status_code=204,
    summary="Delete all alarms in a series",
    operation_id="deleteSeries",
)
async def delete_series(
    series_id: UUID,
    service: FromDishka[AlarmService],
) -> None:
    await service.delete_series(series_id)
