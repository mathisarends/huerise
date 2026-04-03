import uuid
from unittest.mock import AsyncMock

import pytest

from huerise.application.commands import SnoozeAlarmCommand, SnoozeAlarmCommandHandler
from huerise.application.ports import AudioPlayer
from huerise.domain import AlarmNotFoundError, AlarmNotRunningError, AlarmStatus
from tests.application.conftest import make_alarm, make_repo


def make_audio() -> AudioPlayer:
    audio = AsyncMock(spec=AudioPlayer)
    return audio


class TestSnoozeAlarmCommandHandler:
    async def test_returns_the_alarm(self) -> None:
        alarm = make_alarm(status=AlarmStatus.RINGING)
        handler = SnoozeAlarmCommandHandler(make_repo(get_return=alarm), make_audio())

        result = await handler.execute(SnoozeAlarmCommand(alarm_id=alarm.id))

        assert result is alarm

    async def test_sets_status_to_scheduled(self) -> None:
        alarm = make_alarm(status=AlarmStatus.RINGING)
        handler = SnoozeAlarmCommandHandler(make_repo(get_return=alarm), make_audio())

        await handler.execute(SnoozeAlarmCommand(alarm_id=alarm.id))

        assert alarm.status == AlarmStatus.SCHEDULED

    async def test_stops_audio(self) -> None:
        alarm = make_alarm(status=AlarmStatus.RINGING)
        audio = make_audio()
        handler = SnoozeAlarmCommandHandler(make_repo(get_return=alarm), audio)

        await handler.execute(SnoozeAlarmCommand(alarm_id=alarm.id))

        audio.stop.assert_awaited_once()

    async def test_saves_alarm_after_snooze(self) -> None:
        alarm = make_alarm(status=AlarmStatus.RINGING)
        repo = make_repo(get_return=alarm)
        handler = SnoozeAlarmCommandHandler(repo, make_audio())

        await handler.execute(SnoozeAlarmCommand(alarm_id=alarm.id))

        repo.save.assert_awaited_once_with(alarm)

    async def test_raises_when_alarm_not_found(self) -> None:
        handler = SnoozeAlarmCommandHandler(make_repo(get_return=None), make_audio())

        with pytest.raises(AlarmNotFoundError):
            await handler.execute(SnoozeAlarmCommand(alarm_id=uuid.uuid4()))

    async def test_raises_when_alarm_not_running(self) -> None:
        alarm = make_alarm(status=AlarmStatus.SCHEDULED)
        handler = SnoozeAlarmCommandHandler(make_repo(get_return=alarm), make_audio())

        with pytest.raises(AlarmNotRunningError):
            await handler.execute(SnoozeAlarmCommand(alarm_id=alarm.id))

    async def test_snoozes_with_custom_minutes(self) -> None:
        alarm = make_alarm(status=AlarmStatus.INTRO)
        handler = SnoozeAlarmCommandHandler(make_repo(get_return=alarm), make_audio())

        await handler.execute(SnoozeAlarmCommand(alarm_id=alarm.id, minutes=5))

        assert alarm.status == AlarmStatus.SCHEDULED
