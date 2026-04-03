import logging
from dataclasses import dataclass
from uuid import UUID

from huerise.domain import Alarm, AlarmNotFoundError, AlarmRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ActivateAlarmCommand:
    alarm_id: UUID


class ActivateAlarmCommandHandler:
    def __init__(self, alarm_repository: AlarmRepository) -> None:
        self._alarm_repository = alarm_repository

    async def execute(self, command: ActivateAlarmCommand) -> Alarm:
        logger.info("Activating alarm %s", command.alarm_id)
        alarm = await self._alarm_repository.get(command.alarm_id)
        if alarm is None:
            raise AlarmNotFoundError(command.alarm_id)

        alarm.activate()
        return await self._alarm_repository.save(alarm)
