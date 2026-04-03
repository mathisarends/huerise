import logging
from dataclasses import dataclass

from huerise.application.ports import AudioPlayer

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SetVolumeCommand:
    volume: int


class SetVolumeCommandHandler:
    def __init__(self, audio: AudioPlayer) -> None:
        self._audio = audio

    async def execute(self, command: SetVolumeCommand) -> None:
        logger.info("Setting volume to %d", command.volume)
        await self._audio.set_volume(command.volume)
