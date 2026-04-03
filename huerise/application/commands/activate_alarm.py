import uuid
from dataclasses import dataclass

from huerise.domain import Alarm, AlarmNotFound, AlarmRepository


@dataclass(frozen=True)
class ActivateAlarmCommand:
    alarm_id: uuid.UUID


class ActivateAlarmCommandHandler:
    def __init__(self, alarm_repository: AlarmRepository) -> None:
        self._alarm_repository = alarm_repository

    async def execute(self, command: ActivateAlarmCommand) -> Alarm:
        alarm = await self._alarm_repository.get(command.alarm_id)
        if alarm is None:
            raise AlarmNotFound(command.alarm_id)
        alarm.activate()
        await self._alarm_repository.save(alarm)
        return alarm
