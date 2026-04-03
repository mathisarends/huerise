import uuid

from huerise.domain.alarm import Alarm
from huerise.domain.views import (
    AlarmStatus,
    AlarmType,
    IntroConfig,
    RingtoneConfig,
    Schedule,
    SunriseConfig,
    Weekday,
)


def create_one_time(
    label: str,
    hour: int,
    minute: int,
    intro_config: IntroConfig,
    sunrise_config: SunriseConfig,
    ringtone_config: RingtoneConfig,
) -> Alarm:
    return Alarm(
        label=label,
        schedule=Schedule(hour=hour, minute=minute),
        status=AlarmStatus.SCHEDULED,
        alarm_type=AlarmType.ONE_TIME,
        series_id=None,
        intro_config=intro_config,
        sunrise_config=sunrise_config,
        ringtone_config=ringtone_config,
    )


def create_recurring(
    label: str,
    hour: int,
    minute: int,
    days: set[Weekday],
    series_id: uuid.UUID,
    intro_config: IntroConfig,
    sunrise_config: SunriseConfig,
    ringtone_config: RingtoneConfig,
) -> Alarm:
    return Alarm(
        label=label,
        schedule=Schedule(hour=hour, minute=minute, recurrence=frozenset(days)),
        status=AlarmStatus.SCHEDULED,
        alarm_type=AlarmType.RECURRING,
        series_id=series_id,
        intro_config=intro_config,
        sunrise_config=sunrise_config,
        ringtone_config=ringtone_config,
    )
