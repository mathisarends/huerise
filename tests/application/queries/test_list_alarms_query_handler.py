from huerise.application.queries import ListAlarmsQuery, ListAlarmsQueryHandler
from huerise.domain import AlarmStatus
from tests.application.conftest import make_alarm, make_repo


class TestListAlarmsQueryHandler:
    async def test_returns_all_alarms_from_repository(self) -> None:
        alarm_a = make_alarm(status=AlarmStatus.SCHEDULED)
        alarm_b = make_alarm(status=AlarmStatus.INACTIVE)
        repo = make_repo(get_all_return=[alarm_a, alarm_b])
        handler = ListAlarmsQueryHandler(repo)

        result = await handler.execute(ListAlarmsQuery())

        assert list(result) == [alarm_a, alarm_b]

    async def test_returns_empty_sequence_when_no_alarms(self) -> None:
        repo = make_repo(get_all_return=[])
        handler = ListAlarmsQueryHandler(repo)

        result = await handler.execute(ListAlarmsQuery())

        assert len(result) == 0

    async def test_delegates_to_repository_get_all(self) -> None:
        repo = make_repo()
        handler = ListAlarmsQueryHandler(repo)

        await handler.execute(ListAlarmsQuery())

        repo.get_all.assert_awaited_once()
