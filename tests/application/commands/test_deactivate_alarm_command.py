import uuid

import pytest

from huerise.application.commands import (
    DeactivateAlarmCommand,
    DeactivateAlarmCommandHandler,
)
from huerise.domain import AlarmNotFoundError, AlarmStatus
from tests.application.conftest import make_alarm, make_repo


class TestDeactivateAlarmCommandHandler:
    async def test_returns_the_alarm(self) -> None:
        alarm = make_alarm(status=AlarmStatus.SCHEDULED)
        handler = DeactivateAlarmCommandHandler(make_repo(get_return=alarm))

        result = await handler.execute(DeactivateAlarmCommand(alarm_id=alarm.id))

        assert result is alarm

    async def test_sets_status_to_inactive(self) -> None:
        alarm = make_alarm(status=AlarmStatus.SCHEDULED)
        handler = DeactivateAlarmCommandHandler(make_repo(get_return=alarm))

        await handler.execute(DeactivateAlarmCommand(alarm_id=alarm.id))

        assert alarm.status == AlarmStatus.INACTIVE

    async def test_saves_alarm_after_deactivation(self) -> None:
        alarm = make_alarm(status=AlarmStatus.SCHEDULED)
        repo = make_repo(get_return=alarm)
        handler = DeactivateAlarmCommandHandler(repo)

        await handler.execute(DeactivateAlarmCommand(alarm_id=alarm.id))

        repo.save.assert_awaited_once_with(alarm)

    async def test_raises_when_alarm_not_found(self) -> None:
        repo = make_repo(get_return=None)
        handler = DeactivateAlarmCommandHandler(repo)

        with pytest.raises(AlarmNotFoundError):
            await handler.execute(DeactivateAlarmCommand(alarm_id=uuid.uuid4()))
