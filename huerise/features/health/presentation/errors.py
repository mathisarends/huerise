from fastapi_canon import ErrorRegistry

from huerise.features.lighting.presentation.errors import (
    HUE_UNAVAILABLE,
    SCENE_NOT_FOUND,
)
from huerise.platform.api.errors import CONFIGURATION_INVALID, api_errors

health_errors = ErrorRegistry.merge(
    api_errors,
    ErrorRegistry(name="health", errors=[SCENE_NOT_FOUND, HUE_UNAVAILABLE]),
    name="health",
)

doctor_errors = [SCENE_NOT_FOUND, CONFIGURATION_INVALID, HUE_UNAVAILABLE]
