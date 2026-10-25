from fastapi_canon import Feature

from huerise.features.health.infrastructure.provider import HealthProvider
from huerise.features.health.presentation.routers import doctor_router, probe_router

feature = Feature(
    name="health",
    routers=[doctor_router, probe_router],
    providers=[HealthProvider],
)
