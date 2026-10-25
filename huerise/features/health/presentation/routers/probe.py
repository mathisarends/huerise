from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi_canon import CanonRouter

from huerise.features.health.application import Readiness
from huerise.features.health.presentation.errors import NOT_READY, health_errors
from huerise.features.health.presentation.schemas import HealthResponse

probe_router = CanonRouter(
    tags=["health"],
    route_class=DishkaRoute,
    error_registry=health_errors,
)


@probe_router.get(
    "/health",
    status_code=200,
    response_model=HealthResponse,
    operation_id="getHealth",
)
async def health() -> HealthResponse:
    return HealthResponse()


@probe_router.get(
    "/readiness",
    status_code=200,
    response_model=HealthResponse,
    operation_id="getReadiness",
    raises=[NOT_READY],
)
async def readiness(readiness: FromDishka[Readiness]) -> HealthResponse:
    await readiness.check()
    return HealthResponse()
