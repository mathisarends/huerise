from fastapi_canon import Feature

from huerise.features.lighting.infrastructure.provider import LightingProvider
from huerise.features.lighting.presentation.doctor_router import doctor_router
from huerise.features.lighting.presentation.hue_router import hue_router

feature = Feature(
    name="lighting",
    routers=[doctor_router, hue_router],
    providers=[LightingProvider],
)
