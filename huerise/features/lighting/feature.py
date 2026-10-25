from fastapi_canon import Feature

from huerise.features.lighting.infrastructure.provider import LightingProvider
from huerise.features.lighting.presentation import doctor_router, hue_router

feature = Feature(
    name="lighting",
    routers=[doctor_router, hue_router],
    providers=[LightingProvider],
)
