import uuid
from dataclasses import dataclass

from huerise.domain import (
    Alarm,
    AlarmRepository,
    IntroConfig,
    RingtoneConfig,
    SunriseConfig,
    Weekday,
)


@dataclass(frozen=True)
class CreateRecurringAlarmCommand:
    label: str
    hour: int
    minute: int
    days: frozenset[Weekday]
    room_name: str
    intro_audio_file: str = "wake-up-bowls.mp3"
    ringtone_audio_file: str = "get-up-aurora.mp3"
    ringtone_volume: int = 80
    sunrise_duration_minutes: int = 7


class CreateRecurringAlarmCommandHandler:
    def __init__(self, alarm_repository: AlarmRepository) -> None:
        self._alarm_repository = alarm_repository

    async def execute(self, command: CreateRecurringAlarmCommand) -> Alarm:
        series_id = uuid.uuid4()
        alarm = Alarm.create_recurring(
            label=command.label,
            hour=command.hour,
            minute=command.minute,
            days=set(command.days),
            series_id=series_id,
            intro_config=IntroConfig(audio_file=command.intro_audio_file),
            sunrise_config=SunriseConfig(
                room_name=command.room_name,
                duration_minutes=command.sunrise_duration_minutes,
            ),
            ringtone_config=RingtoneConfig(
                audio_file=command.ringtone_audio_file,
                volume=command.ringtone_volume,
            ),
        )
        await self._alarm_repository.save(alarm)
        return alarm
