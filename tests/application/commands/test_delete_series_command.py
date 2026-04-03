import uuid

from huerise.application.commands import DeleteSeriesCommand, DeleteSeriesCommandHandler
from huerise.domain import AlarmStatus
from tests.application.conftest import make_alarm, make_repo


class TestDeleteSeriesCommandHandler:
    async def test_deletes_all_alarms_in_series(self) -> None:
        series_id = uuid.uuid4()
        alarm_a = make_alarm(status=AlarmStatus.SCHEDULED, series_id=series_id)
        alarm_b = make_alarm(status=AlarmStatus.SCHEDULED, series_id=series_id)
        repo = make_repo(get_all_return=[alarm_a, alarm_b])
        handler = DeleteSeriesCommandHandler(repo)

        await handler.execute(DeleteSeriesCommand(series_id=series_id))

        assert repo.delete.await_count == 2
        repo.delete.assert_any_await(alarm_a.id)
        repo.delete.assert_any_await(alarm_b.id)

    async def test_does_not_delete_alarms_from_other_series(self) -> None:
        series_id = uuid.uuid4()
        other_series_id = uuid.uuid4()
        alarm_in_series = make_alarm(status=AlarmStatus.SCHEDULED, series_id=series_id)
        alarm_other = make_alarm(
            status=AlarmStatus.SCHEDULED, series_id=other_series_id
        )
        repo = make_repo(get_all_return=[alarm_in_series, alarm_other])
        handler = DeleteSeriesCommandHandler(repo)

        await handler.execute(DeleteSeriesCommand(series_id=series_id))

        repo.delete.assert_awaited_once_with(alarm_in_series.id)

    async def test_does_nothing_when_series_has_no_alarms(self) -> None:
        series_id = uuid.uuid4()
        repo = make_repo(get_all_return=[])
        handler = DeleteSeriesCommandHandler(repo)

        await handler.execute(DeleteSeriesCommand(series_id=series_id))

        repo.delete.assert_not_awaited()
