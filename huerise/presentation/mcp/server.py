import importlib.util

if importlib.util.find_spec("fastmcp") is None:
    raise ImportError(
        "MCP support requires 'fastmcp'. Install with: pip install huerise[mcp]"
    )

from fastmcp import FastMCP

from contextlib import asynccontextmanager

from dishka import make_async_container

from huerise.infrastructure import DatabaseSettings
from huerise.infrastructure.di import AlarmProvider, DatabaseProvider, SchedulerProvider


@asynccontextmanager
async def lifespan(server: FastMCP):
    settings = DatabaseSettings()
    container = make_async_container(
        DatabaseProvider(database_url=settings.async_url),
        AlarmProvider(),
        SchedulerProvider(),
    )
    try:
        yield {"container": container}
    finally:
        await container.close()


mcp = FastMCP("Huerise Alarm System", lifespan=lifespan)

# Register tools by importing the tool modules (side-effect: decorators fire)
import huerise.presentation.mcp.alarm_tools  # noqa: E402, F401
import huerise.presentation.mcp.audio_tools  # noqa: E402, F401
