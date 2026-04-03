try:
    from dishka.integrations.fastapi import setup_dishka
    from fastapi import FastAPI
except ImportError as e:
    raise ImportError(
        "API support requires 'fastapi' and 'uvicorn'. "
        "Install with: pip install huerise[api]"
    ) from e

from dishka import make_async_container

from huerise.infrastructure import DatabaseSettings
from huerise.infrastructure.di import AlarmProvider, DatabaseProvider, SchedulerProvider
from huerise.lifespan import lifespan
from huerise.presentation import router
from huerise.presentation.api.exception_mappings import register_exception_handlers

_settings = DatabaseSettings()
_container = make_async_container(
    DatabaseProvider(database_url=_settings.async_url),
    AlarmProvider(),
    SchedulerProvider(),
)

app = FastAPI(
    title="Huerise Alarm API",
    version="1.0.0",
    description="API for managing sunrise alarms with Philips Hue",
    lifespan=lifespan,
)

setup_dishka(_container, app=app)
app.include_router(router)
register_exception_handlers(app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("huerise.main:app", host="127.0.0.1", port=8000, reload=True)
