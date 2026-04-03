import logging
from dataclasses import dataclass
from uuid import UUID

from huerise.domain import AlarmRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeleteSeriesCommand:
    series_id: UUID


class DeleteSeriesCommandHandler:
    def __init__(self, alarm_repository: AlarmRepository) -> None:
        self._alarm_repository = alarm_repository

    async def execute(self, command: DeleteSeriesCommand) -> None:
        logger.info("Deleting alarm series %s", command.series_id)
        alarms = await self._alarm_repository.get_all()
        series_alarms = [a for a in alarms if a.series_id == command.series_id]
        for alarm in series_alarms:
            await self._alarm_repository.delete(alarm.id)
