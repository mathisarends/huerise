import logging
from dataclasses import dataclass
from uuid import UUID

from huerise.application.ports import AudioPlayer
from huerise.domain import Alarm, AlarmNotFoundError, AlarmRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SnoozeAlarmCommand:
    alarm_id: UUID
    minutes: int = 10


class SnoozeAlarmCommandHandler:
    def __init__(self, alarm_repository: AlarmRepository, audio: AudioPlayer) -> None:
        self._alarm_repository = alarm_repository
        self._audio = audio

    async def execute(self, command: SnoozeAlarmCommand) -> Alarm:
        logger.info(
            "Snoozing alarm %s for %d minutes", command.alarm_id, command.minutes
        )
        alarm = await self._alarm_repository.get(command.alarm_id)
        if alarm is None:
            raise AlarmNotFoundError(command.alarm_id)

        alarm.snooze(command.minutes)
        await self._audio.stop()
        return await self._alarm_repository.save(alarm)
