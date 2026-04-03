import uuid

import pytest

from huerise.application.commands import DeleteAlarmCommand, DeleteAlarmCommandHandler
from huerise.domain import AlarmNotFoundError, AlarmStatus
from tests.application.conftest import make_alarm, make_repo


class TestDeleteAlarmCommandHandler:
    async def test_deletes_existing_alarm(self) -> None:
        alarm = make_alarm(status=AlarmStatus.SCHEDULED)
        repo = make_repo(get_return=alarm)
        handler = DeleteAlarmCommandHandler(repo)

        await handler.execute(DeleteAlarmCommand(alarm_id=alarm.id))

        repo.delete.assert_awaited_once_with(alarm.id)

    async def test_returns_none(self) -> None:
        alarm = make_alarm(status=AlarmStatus.SCHEDULED)
        repo = make_repo(get_return=alarm)
        handler = DeleteAlarmCommandHandler(repo)

        result = await handler.execute(DeleteAlarmCommand(alarm_id=alarm.id))

        assert result is None

    async def test_raises_when_alarm_not_found(self) -> None:
        repo = make_repo(get_return=None)
        handler = DeleteAlarmCommandHandler(repo)

        with pytest.raises(AlarmNotFoundError):
            await handler.execute(DeleteAlarmCommand(alarm_id=uuid.uuid4()))

    async def test_does_not_delete_when_not_found(self) -> None:
        repo = make_repo(get_return=None)
        handler = DeleteAlarmCommandHandler(repo)

        with pytest.raises(AlarmNotFoundError):
            await handler.execute(DeleteAlarmCommand(alarm_id=uuid.uuid4()))

        repo.delete.assert_not_awaited()
