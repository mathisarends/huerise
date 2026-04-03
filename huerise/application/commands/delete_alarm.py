import uuid
from dataclasses import dataclass

from huerise.domain import AlarmNotFound, AlarmRepository


@dataclass(frozen=True)
class DeleteAlarmCommand:
    alarm_id: uuid.UUID


class DeleteAlarmCommandHandler:
    def __init__(self, alarm_repository: AlarmRepository) -> None:
        self._alarm_repository = alarm_repository

    async def execute(self, command: DeleteAlarmCommand) -> None:
        alarm = await self._alarm_repository.get(command.alarm_id)
        if alarm is None:
            raise AlarmNotFound(command.alarm_id)
        await self._alarm_repository.delete(command.alarm_id)
