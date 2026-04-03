from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from huerise.domain.exceptions import (
    AlarmAlreadyCancelled,
    AlarmAlreadyInStatus,
    AlarmNotFound,
)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AlarmNotFound)
    async def alarm_not_found_handler(
        request: Request, exc: AlarmNotFound
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(AlarmAlreadyCancelled)
    async def alarm_already_cancelled_handler(
        request: Request, exc: AlarmAlreadyCancelled
    ) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(AlarmAlreadyInStatus)
    async def alarm_already_in_status_handler(
        request: Request, exc: AlarmAlreadyInStatus
    ) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})
