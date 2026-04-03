from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from huerise.application.scheduler.runner import AlarmRunner
from huerise.application.scheduler.scheduler import AlarmScheduler
from huerise.domain import AlarmStatus
from huerise.domain.views import Schedule, Weekday
from tests.application.conftest import make_alarm, make_repo

# April 6, 2026 is a Monday (weekday() == 0)
_MONDAY_7_00 = datetime(2026, 4, 6, 7, 0, tzinfo=timezone.utc)
_MONDAY_8_30 = datetime(2026, 4, 6, 8, 30, tzinfo=timezone.utc)


def make_runner() -> AlarmRunner:
    return MagicMock(spec=AlarmRunner)


class TestAlarmSchedulerShouldTrigger:
    def test_returns_true_when_hour_and_minute_match_no_recurrence(self) -> None:
        schedule = Schedule(hour=7, minute=0)
        assert AlarmScheduler._should_trigger(schedule, _MONDAY_7_00) is True

    def test_returns_false_when_hour_does_not_match(self) -> None:
        schedule = Schedule(hour=8, minute=0)
        assert AlarmScheduler._should_trigger(schedule, _MONDAY_7_00) is False

    def test_returns_false_when_minute_does_not_match(self) -> None:
        schedule = Schedule(hour=7, minute=15)
        assert AlarmScheduler._should_trigger(schedule, _MONDAY_7_00) is False

    def test_returns_true_when_weekday_in_recurrence(self) -> None:
        schedule = Schedule(hour=7, minute=0, recurrence=frozenset({Weekday.MON}))
        assert AlarmScheduler._should_trigger(schedule, _MONDAY_7_00) is True

    def test_returns_false_when_weekday_not_in_recurrence(self) -> None:
        schedule = Schedule(hour=7, minute=0, recurrence=frozenset({Weekday.TUE}))
        assert AlarmScheduler._should_trigger(schedule, _MONDAY_7_00) is False

    def test_returns_true_when_one_of_multiple_days_matches(self) -> None:
        schedule = Schedule(
            hour=7,
            minute=0,
            recurrence=frozenset({Weekday.MON, Weekday.WED, Weekday.FRI}),
        )
        assert AlarmScheduler._should_trigger(schedule, _MONDAY_7_00) is True


class TestAlarmSchedulerTick:
    async def test_triggers_alarm_due_at_current_time(self) -> None:
        alarm = make_alarm(status=AlarmStatus.SCHEDULED, hour=7, minute=0)
        repo = make_repo(get_scheduled_return=[alarm])
        runner = make_runner()
        runner.run = AsyncMock()
        scheduler = AlarmScheduler(repo=repo, runner=runner)

        with patch("huerise.application.scheduler.scheduler.datetime") as mock_dt:
            mock_dt.now.return_value = _MONDAY_7_00
            with patch(
                "huerise.application.scheduler.scheduler.asyncio.create_task"
            ) as mock_task:
                await scheduler._tick()

        mock_task.assert_called_once()

    async def test_does_not_trigger_alarm_at_wrong_time(self) -> None:
        alarm = make_alarm(status=AlarmStatus.SCHEDULED, hour=8, minute=30)
        repo = make_repo(get_scheduled_return=[alarm])
        runner = make_runner()
        scheduler = AlarmScheduler(repo=repo, runner=runner)

        with patch("huerise.application.scheduler.scheduler.datetime") as mock_dt:
            mock_dt.now.return_value = _MONDAY_7_00
            with patch(
                "huerise.application.scheduler.scheduler.asyncio.create_task"
            ) as mock_task:
                await scheduler._tick()

        mock_task.assert_not_called()

    async def test_skips_tick_when_repository_raises(self) -> None:
        repo = make_repo()
        repo.get_scheduled = AsyncMock(side_effect=RuntimeError("db error"))
        runner = make_runner()
        scheduler = AlarmScheduler(repo=repo, runner=runner)

        with patch("huerise.application.scheduler.scheduler.datetime") as mock_dt:
            mock_dt.now.return_value = _MONDAY_7_00
            with patch(
                "huerise.application.scheduler.scheduler.asyncio.create_task"
            ) as mock_task:
                await scheduler._tick()

        mock_task.assert_not_called()

    async def test_triggers_only_alarms_matching_current_time(self) -> None:
        alarm_due = make_alarm(status=AlarmStatus.SCHEDULED, hour=7, minute=0)
        alarm_not_due = make_alarm(status=AlarmStatus.SCHEDULED, hour=8, minute=30)
        repo = make_repo(get_scheduled_return=[alarm_due, alarm_not_due])
        runner = make_runner()
        runner.run = AsyncMock()
        scheduler = AlarmScheduler(repo=repo, runner=runner)

        with patch("huerise.application.scheduler.scheduler.datetime") as mock_dt:
            mock_dt.now.return_value = _MONDAY_7_00
            with patch(
                "huerise.application.scheduler.scheduler.asyncio.create_task"
            ) as mock_task:
                await scheduler._tick()

        assert mock_task.call_count == 1
