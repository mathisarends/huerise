from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from huerise.domain.views import AlarmStatus, AlarmType, Weekday


class CreateOneTimeAlarmBody(BaseModel):
    label: str
    hour: int = Field(ge=0, le=23)
    minute: int = Field(ge=0, le=59)


class CreateRecurringAlarmBody(BaseModel):
    label: str
    hour: int = Field(ge=0, le=23)
    minute: int = Field(ge=0, le=59)
    days: list[Weekday] = Field(min_length=1)


class ScheduleOut(BaseModel):
    hour: int
    minute: int
    recurrence: list[Weekday] | None = None


class AlarmOut(BaseModel):
    id: UUID
    label: str
    schedule: ScheduleOut
    status: AlarmStatus
    alarm_type: AlarmType
    series_id: UUID | None = None
    created_at: datetime
