import logging
from dataclasses import dataclass
from uuid import UUID

from huerise.domain import AlarmNotFoundError, AlarmRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeleteAlarmCommand:
    alarm_id: UUID


class DeleteAlarmCommandHandler:
    def __init__(self, alarm_repository: AlarmRepository) -> None:
        self._alarm_repository = alarm_repository

    async def execute(self, command: DeleteAlarmCommand) -> None:
        logger.info("Deleting alarm %s", command.alarm_id)
        alarm = await self._alarm_repository.get(command.alarm_id)
        if alarm is None:
            raise AlarmNotFoundError(command.alarm_id)
        await self._alarm_repository.delete(command.alarm_id)
