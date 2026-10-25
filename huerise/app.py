from fastapi import FastAPI
from fastapi_canon import Composition, ErrorOptions, Feature

from huerise import __version__
from huerise.composition import FEATURES
from huerise.platform.api.openapi import include_request_validation
from huerise.platform.feature import platform_feature


def create_app(*extra_features: Feature) -> FastAPI:
    app = FastAPI(
        title="Huerise Daylight Alarm API",
        version=__version__,
        description="Run one YAML-configured Philips Hue daylight alarm.",
    )
    composition = Composition(
        platform_feature,
        *FEATURES,
        *extra_features,
        errors=ErrorOptions(type_base="urn:huerise:problem"),
    )
    composition.apply(app)
    composition.validate(app)
    include_request_validation(app.openapi())
    return app


app = create_app()
