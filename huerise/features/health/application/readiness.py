import asyncio

from huerise.features.health.application.doctor import Doctor
from huerise.features.lighting.domain import HueUnavailableError, SceneNotFoundError
from huerise.platform.configuration import ConfigurationError


class ServiceNotReadyError(Exception):
    pass


class Readiness:
    def __init__(self, doctor: Doctor, *, timeout_seconds: float = 5.0) -> None:
        self._doctor = doctor
        self._timeout_seconds = timeout_seconds

    async def check(self) -> None:
        try:
            async with asyncio.timeout(self._timeout_seconds):
                await self._doctor.check()
        except (
            ConfigurationError,
            HueUnavailableError,
            SceneNotFoundError,
            TimeoutError,
        ) as error:
            raise ServiceNotReadyError from error
