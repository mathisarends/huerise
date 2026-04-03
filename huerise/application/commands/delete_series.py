import uuid
from dataclasses import dataclass

from huerise.domain import AlarmRepository


@dataclass(frozen=True)
class DeleteSeriesCommand:
    series_id: uuid.UUID


class DeleteSeriesCommandHandler:
    def __init__(self, alarm_repository: AlarmRepository) -> None:
        self._alarm_repository = alarm_repository

    async def execute(self, command: DeleteSeriesCommand) -> None:
        alarms = await self._alarm_repository.get_all()
        series_alarms = [a for a in alarms if a.series_id == command.series_id]
        for alarm in series_alarms:
            await self._alarm_repository.delete(alarm.id)
