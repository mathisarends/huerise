import logging
from dataclasses import dataclass

from huerise.domain import Alarm, AlarmRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CreateOneTimeAlarmCommand:
    label: str
    hour: int
    minute: int
    room_name: str
    intro_audio_file: str = "wake-up-bowls.mp3"
    ringtone_audio_file: str = "get-up-aurora.mp3"


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
            room_name=command.room_name,
            intro_audio_file=command.intro_audio_file,
            ringtone_audio_file=command.ringtone_audio_file,
        )
        return await self._alarm_repository.save(alarm)
