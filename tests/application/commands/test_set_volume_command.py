from unittest.mock import AsyncMock

from huerise.application.commands import SetVolumeCommand, SetVolumeCommandHandler
from huerise.application.ports import AudioPlayer


def make_audio() -> AudioPlayer:
    return AsyncMock(spec=AudioPlayer)


class TestSetVolumeCommandHandler:
    async def test_calls_set_volume_with_given_volume(self) -> None:
        audio = make_audio()
        handler = SetVolumeCommandHandler(audio=audio)

        await handler.execute(SetVolumeCommand(volume=75))

        audio.set_volume.assert_awaited_once_with(75)

    async def test_calls_set_volume_with_zero(self) -> None:
        audio = make_audio()
        handler = SetVolumeCommandHandler(audio=audio)

        await handler.execute(SetVolumeCommand(volume=0))

        audio.set_volume.assert_awaited_once_with(0)

    async def test_calls_set_volume_with_max(self) -> None:
        audio = make_audio()
        handler = SetVolumeCommandHandler(audio=audio)

        await handler.execute(SetVolumeCommand(volume=100))

        audio.set_volume.assert_awaited_once_with(100)
