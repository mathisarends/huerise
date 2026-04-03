import uuid
from datetime import datetime, timezone
from typing import Self

from huerise.domain.exceptions import AlarmAlreadyCancelled, AlarmAlreadyInStatus
from huerise.domain.views import AlarmStatus, AlarmType, Schedule, Weekday


class Alarm:
    def __init__(
        self,
        id: uuid.UUID,
        label: str,
        schedule: Schedule,
        status: AlarmStatus,
        alarm_type: AlarmType,
        series_id: uuid.UUID | None,
        created_at: datetime,
    ) -> None:
        self.id = id
        self.label = label
        self.schedule = schedule
        self.status = status
        self.alarm_type = alarm_type
        self.series_id = series_id
        self.created_at = created_at

    @classmethod
    def create_one_time(cls, label: str, hour: int, minute: int) -> Self:
        alarm = cls(
            id=uuid.uuid4(),
            label=label,
            schedule=Schedule(hour=hour, minute=minute),
            status=AlarmStatus.ACTIVE,
            alarm_type=AlarmType.ONE_TIME,
            series_id=None,
            created_at=datetime.now(timezone.utc),
        )
        return alarm

    @classmethod
    def create_recurring(
        cls,
        label: str,
        hour: int,
        minute: int,
        days: set[Weekday],
        series_id: uuid.UUID,
    ) -> Self:
        alarm = cls(
            id=uuid.uuid4(),
            label=label,
            schedule=Schedule(hour=hour, minute=minute, recurrence=frozenset(days)),
            status=AlarmStatus.ACTIVE,
            alarm_type=AlarmType.RECURRING,
            series_id=series_id,
            created_at=datetime.now(timezone.utc),
        )
        return alarm

    def deactivate(self) -> None:
        self._guard_not_cancelled()
        if self.status == AlarmStatus.INACTIVE:
            raise AlarmAlreadyInStatus(self.id, AlarmStatus.INACTIVE)
        self.status = AlarmStatus.INACTIVE

    def activate(self) -> None:
        self._guard_not_cancelled()
        if self.status == AlarmStatus.ACTIVE:
            raise AlarmAlreadyInStatus(self.id, AlarmStatus.ACTIVE)
        self.status = AlarmStatus.ACTIVE

    def cancel(self) -> None:
        """Nächste Auslösung skippen – bei one_time endgültig."""
        self._guard_not_cancelled()
        self.status = AlarmStatus.CANCELLED

    def _guard_not_cancelled(self) -> None:
        if self.status == AlarmStatus.CANCELLED:
            raise AlarmAlreadyCancelled(self.id)
