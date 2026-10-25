from fastapi_canon import Error, ErrorRegistry

from huerise.features.health.application import ServiceNotReadyError
from huerise.features.lighting.presentation.errors import (
    HUE_UNAVAILABLE,
    SCENE_NOT_FOUND,
)
from huerise.platform.api.errors import CONFIGURATION_INVALID, api_errors

NOT_READY = Error(
    ServiceNotReadyError,
    status=503,
    code="not_ready",
    title="Service not ready",
    detail="The application is not ready to run daylight alarms.",
    headers={"Retry-After": "5"},
    openapi_headers={
        "Retry-After": {
            "description": "Seconds until the readiness probe should be retried.",
            "schema": {"type": "integer", "minimum": 0},
        },
    },
)

health_errors = ErrorRegistry.merge(
    api_errors,
    ErrorRegistry(name="health", errors=[SCENE_NOT_FOUND, HUE_UNAVAILABLE, NOT_READY]),
    name="health",
)

doctor_errors = [SCENE_NOT_FOUND, CONFIGURATION_INVALID, HUE_UNAVAILABLE]
