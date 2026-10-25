from fastapi_canon import Feature

from huerise.features.health.infrastructure.provider import HealthProvider
from huerise.features.health.presentation.doctor_router import doctor_router

feature = Feature(
    name="health",
    routers=[doctor_router],
    providers=[HealthProvider],
)
