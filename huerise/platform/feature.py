import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_canon import Feature

from huerise.platform.provider import PlatformProvider
from huerise.platform.settings import AppSettings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = await app.state.dishka_container.get(AppSettings)
    logging.basicConfig(
        level=settings.log_level.value,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    yield


platform_feature = Feature(
    name="platform",
    providers=[PlatformProvider],
    lifespan=lifespan,
)
