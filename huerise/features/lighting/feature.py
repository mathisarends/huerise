from fastapi_canon import Feature

from huerise.features.lighting.infrastructure.provider import LightingProvider
from huerise.features.lighting.presentation.hue_router import hue_router

feature = Feature(
    name="lighting",
    routers=[hue_router],
    providers=[LightingProvider],
)
