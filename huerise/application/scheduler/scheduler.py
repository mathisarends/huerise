import asyncio
import logging
from datetime import datetime, timezone

from huerise.application.scheduler.runner import AlarmRunner
from huerise.domain.repository import AlarmRepository
from huerise.domain.views import Schedule, Weekday

logger = logging.getLogger(__name__)


class AlarmScheduler:
    def __init__(self, repo: AlarmRepository, runner: AlarmRunner) -> None:
        self._repo = repo
        self._runner = runner

    async def run(self) -> None:
        while True:
            await self._tick()
            await asyncio.sleep(30)

    async def _tick(self) -> None:
        now = datetime.now(timezone.utc)
        try:
            alarms = await self._repo.get_scheduled()
        except Exception:
            logger.exception("Error fetching scheduled alarms")
            return

        for alarm in alarms:
            if self._should_trigger(alarm.schedule, now):
                asyncio.create_task(self._runner.run(alarm))

    @staticmethod
    def _should_trigger(schedule: Schedule, now: datetime) -> bool:
        if schedule.hour != now.hour or schedule.minute != now.minute:
            return False
        if schedule.recurrence is None:
            return True
        return Weekday(now.weekday()) in schedule.recurrence
