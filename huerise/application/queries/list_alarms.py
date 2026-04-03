from dataclasses import dataclass
from collections.abc import Sequence

from huerise.domain import Alarm, AlarmRepository


@dataclass(frozen=True)
class ListAlarmsQuery:
    pass


class ListAlarmsQueryHandler:
    def __init__(self, alarm_repository: AlarmRepository) -> None:
        self._alarm_repository = alarm_repository

    async def execute(self, query: ListAlarmsQuery) -> Sequence[Alarm]:
        return await self._alarm_repository.get_all()
