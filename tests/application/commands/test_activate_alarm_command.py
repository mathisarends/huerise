import uuid
from unittest.mock import AsyncMock

import pytest

from huerise.application.commands import (
    ActivateAlarmCommand,
    ActivateAlarmCommandHandler,
)
from huerise.domain import AlarmNotFoundError, AlarmStatus
from tests.application.conftest import make_alarm, make_repo


class TestActivateAlarmCommandHandler:
    async def test_returns_the_alarm(self) -> None:
        alarm = make_alarm(status=AlarmStatus.INACTIVE)
        repo = make_repo(get_return=alarm)
        repo.save = AsyncMock(return_value=alarm)
        handler = ActivateAlarmCommandHandler(repo)

        result = await handler.execute(ActivateAlarmCommand(alarm_id=alarm.id))

        assert result is alarm

    async def test_sets_status_to_scheduled(self) -> None:
        alarm = make_alarm(status=AlarmStatus.INACTIVE)
        handler = ActivateAlarmCommandHandler(make_repo(get_return=alarm))

        await handler.execute(ActivateAlarmCommand(alarm_id=alarm.id))

        assert alarm.status == AlarmStatus.SCHEDULED

    async def test_saves_alarm_after_activation(self) -> None:
        alarm = make_alarm(status=AlarmStatus.INACTIVE)
        repo = make_repo(get_return=alarm)
        handler = ActivateAlarmCommandHandler(repo)

        await handler.execute(ActivateAlarmCommand(alarm_id=alarm.id))

        repo.save.assert_awaited_once_with(alarm)

    async def test_raises_when_alarm_not_found(self) -> None:
        repo = make_repo(get_return=None)
        handler = ActivateAlarmCommandHandler(repo)

        with pytest.raises(AlarmNotFoundError):
            await handler.execute(ActivateAlarmCommand(alarm_id=uuid.uuid4()))
