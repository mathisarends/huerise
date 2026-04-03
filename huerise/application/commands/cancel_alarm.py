import uuid
from dataclasses import dataclass

from huerise.domain import Alarm, AlarmNotFoundError, AlarmRepository


@dataclass(frozen=True)
class CancelAlarmCommand:
    alarm_id: uuid.UUID


class CancelAlarmCommandHandler:
    def __init__(self, alarm_repository: AlarmRepository) -> None:
        self._alarm_repository = alarm_repository

    async def execute(self, command: CancelAlarmCommand) -> Alarm:
        alarm = await self._alarm_repository.get(command.alarm_id)
        if alarm is None:
            raise AlarmNotFoundError(command.alarm_id)
        alarm.cancel()
        await self._alarm_repository.save(alarm)
        return alarm
