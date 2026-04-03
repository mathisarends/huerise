from huerise.application.commands import (
    CreateRecurringAlarmCommand,
    CreateRecurringAlarmCommandHandler,
)
from huerise.domain import AlarmStatus, AlarmType, Weekday
from tests.application.conftest import make_repo


class TestCreateRecurringAlarmCommandHandler:
    async def test_returns_created_alarm(self) -> None:
        repo = make_repo()
        handler = CreateRecurringAlarmCommandHandler(repo)
        command = CreateRecurringAlarmCommand(
            label="Weekday",
            hour=7,
            minute=0,
            days=frozenset({Weekday.MON, Weekday.FRI}),
            room_name="Bedroom",
        )

        result = await handler.execute(command)

        assert result is not None
        assert result.label == "Weekday"

    async def test_alarm_type_is_recurring(self) -> None:
        repo = make_repo()
        handler = CreateRecurringAlarmCommandHandler(repo)
        command = CreateRecurringAlarmCommand(
            label="Weekday",
            hour=7,
            minute=0,
            days=frozenset({Weekday.MON}),
            room_name="Bedroom",
        )

        result = await handler.execute(command)

        assert result.alarm_type == AlarmType.RECURRING

    async def test_alarm_has_correct_days(self) -> None:
        repo = make_repo()
        handler = CreateRecurringAlarmCommandHandler(repo)
        command = CreateRecurringAlarmCommand(
            label="Weekday",
            hour=7,
            minute=0,
            days=frozenset({Weekday.MON, Weekday.WED, Weekday.FRI}),
            room_name="Bedroom",
        )

        result = await handler.execute(command)

        assert result.schedule.recurrence == frozenset(
            {Weekday.MON, Weekday.WED, Weekday.FRI}
        )

    async def test_alarm_has_series_id_assigned(self) -> None:
        repo = make_repo()
        handler = CreateRecurringAlarmCommandHandler(repo)
        command = CreateRecurringAlarmCommand(
            label="Weekday",
            hour=7,
            minute=0,
            days=frozenset({Weekday.MON}),
            room_name="Bedroom",
        )

        result = await handler.execute(command)

        assert result.series_id is not None

    async def test_alarm_is_scheduled_on_creation(self) -> None:
        repo = make_repo()
        handler = CreateRecurringAlarmCommandHandler(repo)
        command = CreateRecurringAlarmCommand(
            label="Weekday",
            hour=7,
            minute=0,
            days=frozenset({Weekday.MON}),
            room_name="Bedroom",
        )

        result = await handler.execute(command)

        assert result.status == AlarmStatus.SCHEDULED

    async def test_saves_alarm_to_repository(self) -> None:
        repo = make_repo()
        handler = CreateRecurringAlarmCommandHandler(repo)
        command = CreateRecurringAlarmCommand(
            label="Weekday",
            hour=7,
            minute=0,
            days=frozenset({Weekday.MON}),
            room_name="Bedroom",
        )

        result = await handler.execute(command)

        repo.save.assert_awaited_once_with(result)
