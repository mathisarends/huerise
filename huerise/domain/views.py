from dataclasses import dataclass
from enum import IntEnum, StrEnum


class Weekday(IntEnum):
    MON = 0
    TUE = 1
    WED = 2
    THU = 3
    FRI = 4
    SAT = 5
    SUN = 6


class AlarmStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    CANCELLED = "cancelled"


class AlarmType(StrEnum):
    ONE_TIME = "one_time"
    RECURRING = "recurring"


@dataclass(frozen=True)
class Schedule:
    hour: int
    minute: int
    recurrence: frozenset[Weekday] | None = None

    def __post_init__(self) -> None:
        if not (0 <= self.hour <= 23):
            raise ValueError("Hour must be 0-23")
        if not (0 <= self.minute <= 59):
            raise ValueError("Minute must be 0-59")

    def is_recurring(self) -> bool:
        return self.recurrence is not None
