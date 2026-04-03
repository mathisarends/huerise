from fastapi import FastAPI

from huerise.presentation.api.exception_mappings import register_exception_handlers
from huerise.presentation.api.lifespan import lifespan
from huerise.presentation.api.router import alarms_router, series_router

app = FastAPI(
    title="Huerise Alarm API",
    version="1.0.0",
    description="API for managing sunrise alarms with Philips Hue",
    lifespan=lifespan,
)

app.include_router(alarms_router)
app.include_router(series_router)

register_exception_handlers(app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "huerise.presentation.api.main:app", host="127.0.0.1", port=8000, reload=True
    )
