from unittest.mock import AsyncMock, MagicMock, patch


from huerise.application.ports import AudioPlayer, Lights
from huerise.application.scheduler.runner import AlarmRunner
from huerise.domain import AlarmStatus
from tests.application.conftest import make_alarm, make_repo


def make_lights() -> Lights:
    lights = MagicMock(spec=Lights)
    lights.activate_scene = AsyncMock()
    lights.set_brightness = AsyncMock()
    return lights


def make_audio() -> AudioPlayer:
    audio = MagicMock(spec=AudioPlayer)
    audio.play = AsyncMock()
    audio.stop = AsyncMock()
    audio.set_volume = AsyncMock()
    return audio


class TestAlarmRunnerStateTransitions:
    async def test_alarm_reaches_completed_status(self) -> None:
        alarm = make_alarm(status=AlarmStatus.SCHEDULED)
        repo = make_repo()
        runner = AlarmRunner(lights=make_lights(), audio=make_audio(), repo=repo)
        runner._run_sunrise = AsyncMock()  # type: ignore[method-assign]
        runner._run_ringtone = AsyncMock()  # type: ignore[method-assign]

        await runner.run(alarm)

        assert alarm.status == AlarmStatus.COMPLETED

    async def test_repo_save_called_after_each_transition(self) -> None:
        alarm = make_alarm(status=AlarmStatus.SCHEDULED)
        repo = make_repo()
        runner = AlarmRunner(lights=make_lights(), audio=make_audio(), repo=repo)
        runner._run_sunrise = AsyncMock()  # type: ignore[method-assign]
        runner._run_ringtone = AsyncMock()  # type: ignore[method-assign]

        await runner.run(alarm)

        assert repo.save.await_count == 3

    async def test_run_sunrise_is_called(self) -> None:
        alarm = make_alarm(status=AlarmStatus.SCHEDULED)
        repo = make_repo()
        runner = AlarmRunner(lights=make_lights(), audio=make_audio(), repo=repo)
        runner._run_sunrise = AsyncMock()  # type: ignore[method-assign]
        runner._run_ringtone = AsyncMock()  # type: ignore[method-assign]

        await runner.run(alarm)

        runner._run_sunrise.assert_awaited_once_with(alarm)

    async def test_run_ringtone_is_called(self) -> None:
        alarm = make_alarm(status=AlarmStatus.SCHEDULED)
        repo = make_repo()
        runner = AlarmRunner(lights=make_lights(), audio=make_audio(), repo=repo)
        runner._run_sunrise = AsyncMock()  # type: ignore[method-assign]
        runner._run_ringtone = AsyncMock()  # type: ignore[method-assign]

        await runner.run(alarm)

        runner._run_ringtone.assert_awaited_once_with(alarm)


class TestAlarmRunnerRunSunrise:
    async def test_activates_light_scene(self) -> None:
        alarm = make_alarm(status=AlarmStatus.SCHEDULED)
        lights = make_lights()
        runner = AlarmRunner(lights=lights, audio=make_audio(), repo=make_repo())

        with patch("huerise.application.scheduler.runner.asyncio.create_task"):
            await runner._run_sunrise(alarm)

        lights.activate_scene.assert_awaited_once_with(
            alarm.sunrise_config.room_name,
            alarm.sunrise_config.scene_name,
        )

    async def test_sets_brightness_for_each_step(self) -> None:
        alarm = make_alarm(status=AlarmStatus.SCHEDULED)
        lights = make_lights()
        runner = AlarmRunner(lights=lights, audio=make_audio(), repo=make_repo())

        with patch("huerise.application.scheduler.runner.asyncio.create_task"):
            await runner._run_sunrise(alarm)

        # make_alarm uses steps=1
        assert lights.set_brightness.await_count == alarm.sunrise_config.steps


class TestAlarmRunnerRunRingtone:
    async def test_stops_audio_before_playing(self) -> None:
        alarm = make_alarm(status=AlarmStatus.SCHEDULED)
        audio = make_audio()
        runner = AlarmRunner(lights=make_lights(), audio=audio, repo=make_repo())

        await runner._run_ringtone(alarm)

        audio.stop.assert_awaited_once()

    async def test_plays_ringtone_with_correct_file_and_volume(self) -> None:
        alarm = make_alarm(status=AlarmStatus.SCHEDULED)
        audio = make_audio()
        runner = AlarmRunner(lights=make_lights(), audio=audio, repo=make_repo())

        await runner._run_ringtone(alarm)

        audio.play.assert_awaited_once_with(
            alarm.ringtone_config.audio_file,
            alarm.ringtone_config.volume,
        )
