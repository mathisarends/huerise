from fastapi import Depends, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi_canon import CanonRouter, Composition, Feature

from huerise import __version__
from huerise.composition import FEATURES
from huerise.platform.api.authentication import require_api_key
from huerise.platform.api.errors import request_validation_error
from huerise.platform.feature import platform_feature


def create_app(*extra_features: Feature) -> FastAPI:
    app = FastAPI(
        title="Huerise Daylight Alarm API",
        version=__version__,
        description="Run one YAML-configured Philips Hue daylight alarm.",
        exception_handlers={RequestValidationError: request_validation_error},
    )
    composition = Composition(
        platform_feature,
        *FEATURES,
        *extra_features,
        router_factory=lambda: CanonRouter(dependencies=[Depends(require_api_key)]),
    )
    composition.apply(app)
    composition.validate(app)
    return app


app = create_app()
