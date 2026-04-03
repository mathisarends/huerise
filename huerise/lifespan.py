from contextlib import asynccontextmanager

from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from huerise.infrastructure.credentials import DatabaseSettings
from huerise.infrastructure.di import AlarmProvider, DatabaseProvider


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = DatabaseSettings()
    container = make_async_container(
        DatabaseProvider(database_url=settings.async_url),
        AlarmProvider(),
    )
    setup_dishka(container, app=app)
    yield
    await container.close()
