import logging
from dataclasses import dataclass

from huerise.domain import (
    Alarm,
    AlarmRepository,
    IntroConfig,
    RingtoneConfig,
    SunriseConfig,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CreateOneTimeAlarmCommand:
    label: str
    hour: int
    minute: int
    room_name: str
    intro_audio_file: str = "wake-up-bowls.mp3"
    ringtone_audio_file: str = "get-up-aurora.mp3"
    ringtone_volume: int = 80
    sunrise_duration_minutes: int = 7


class CreateOneTimeAlarmCommandHandler:
    def __init__(self, alarm_repository: AlarmRepository) -> None:
        self._alarm_repository = alarm_repository

    async def execute(self, command: CreateOneTimeAlarmCommand) -> Alarm:
        logger.info(
            "Creating one-time alarm '%s' at %02d:%02d",
            command.label,
            command.hour,
            command.minute,
        )
        alarm = Alarm.create_one_time(
            label=command.label,
            hour=command.hour,
            minute=command.minute,
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
        return await self._alarm_repository.save(alarm)
