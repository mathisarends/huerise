from huerise.application.commands import (
    CreateOneTimeAlarmCommand,
    CreateOneTimeAlarmCommandHandler,
)
from huerise.domain import AlarmStatus, AlarmType
from tests.application.conftest import make_repo


class TestCreateOneTimeAlarmCommandHandler:
    async def test_returns_created_alarm(self) -> None:
        repo = make_repo()
        handler = CreateOneTimeAlarmCommandHandler(repo)
        command = CreateOneTimeAlarmCommand(
            label="Sun", hour=7, minute=30, room_name="Bedroom"
        )

        result = await handler.execute(command)

        assert result is not None
        assert result.label == "Sun"

    async def test_alarm_has_correct_schedule(self) -> None:
        repo = make_repo()
        handler = CreateOneTimeAlarmCommandHandler(repo)
        command = CreateOneTimeAlarmCommand(
            label="Sun", hour=6, minute=45, room_name="Bedroom"
        )

        result = await handler.execute(command)

        assert result.schedule.hour == 6
        assert result.schedule.minute == 45

    async def test_alarm_type_is_one_time(self) -> None:
        repo = make_repo()
        handler = CreateOneTimeAlarmCommandHandler(repo)
        command = CreateOneTimeAlarmCommand(
            label="Sun", hour=7, minute=0, room_name="Bedroom"
        )

        result = await handler.execute(command)

        assert result.alarm_type == AlarmType.ONE_TIME

    async def test_alarm_is_scheduled_on_creation(self) -> None:
        repo = make_repo()
        handler = CreateOneTimeAlarmCommandHandler(repo)
        command = CreateOneTimeAlarmCommand(
            label="Sun", hour=7, minute=0, room_name="Bedroom"
        )

        result = await handler.execute(command)

        assert result.status == AlarmStatus.SCHEDULED

    async def test_saves_alarm_to_repository(self) -> None:
        repo = make_repo()
        handler = CreateOneTimeAlarmCommandHandler(repo)
        command = CreateOneTimeAlarmCommand(
            label="Sun", hour=7, minute=0, room_name="Bedroom"
        )

        result = await handler.execute(command)

        repo.save.assert_awaited_once_with(result)

    async def test_uses_default_audio_files(self) -> None:
        repo = make_repo()
        handler = CreateOneTimeAlarmCommandHandler(repo)
        command = CreateOneTimeAlarmCommand(
            label="Sun", hour=7, minute=0, room_name="Bedroom"
        )

        result = await handler.execute(command)

        assert result.intro_config.audio_file == "wake-up-bowls.mp3"
        assert result.ringtone_config.audio_file == "get-up-aurora.mp3"

    async def test_uses_custom_audio_files_when_provided(self) -> None:
        repo = make_repo()
        handler = CreateOneTimeAlarmCommandHandler(repo)
        command = CreateOneTimeAlarmCommand(
            label="Sun",
            hour=7,
            minute=0,
            room_name="Bedroom",
            intro_audio_file="custom-intro.mp3",
            ringtone_audio_file="custom-ringtone.mp3",
        )

        result = await handler.execute(command)

        assert result.intro_config.audio_file == "custom-intro.mp3"
        assert result.ringtone_config.audio_file == "custom-ringtone.mp3"
