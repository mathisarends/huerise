from uuid import UUID

from fastapi import APIRouter

from huerise.presentation.schemas import (
    AlarmOut,
    CreateOneTimeAlarmBody,
    CreateRecurringAlarmBody,
)

router = APIRouter(prefix="/alarms", tags=["Alarms"])


@router.get("", response_model=list[AlarmOut])
def list_alarms():
    raise NotImplementedError


@router.post("/one-time", response_model=AlarmOut, status_code=201)
def create_one_time_alarm(body: CreateOneTimeAlarmBody):
    raise NotImplementedError


@router.post("/recurring", response_model=AlarmOut, status_code=201)
def create_recurring_alarm(body: CreateRecurringAlarmBody):
    raise NotImplementedError


@router.post("/{alarm_id}/activate", response_model=AlarmOut)
def activate_alarm(alarm_id: UUID):
    raise NotImplementedError


@router.post("/{alarm_id}/deactivate", response_model=AlarmOut)
def deactivate_alarm(alarm_id: UUID):
    raise NotImplementedError


@router.post("/{alarm_id}/cancel", response_model=AlarmOut)
def cancel_alarm(alarm_id: UUID):
    raise NotImplementedError


@router.delete("/{alarm_id}", status_code=204)
def delete_alarm(alarm_id: UUID):
    raise NotImplementedError
