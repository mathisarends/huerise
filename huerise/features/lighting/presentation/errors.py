from fastapi_canon import Error, ErrorRegistry

from huerise.features.lighting.domain import (
    BridgeNotFoundError,
    BridgeNotSelectedError,
    HueUnavailableError,
    LinkButtonTimeoutError,
    OnboardingReadOnlyError,
    SceneNotFoundError,
)
from huerise.platform.api.errors import CONFIGURATION_INVALID, api_errors

SCENE_NOT_FOUND = Error(
    SceneNotFoundError,
    status=404,
    code="scene_not_found",
    title="Scene not found",
    detail=str,
    description="The selected Hue scene does not exist.",
)
HUE_UNAVAILABLE = Error(
    HueUnavailableError,
    status=503,
    code="hue_unavailable",
    title="Hue Bridge unavailable",
    detail=str,
    description="The Hue Bridge is not configured, reachable, or authenticated.",
)
BRIDGE_NOT_FOUND = Error(
    BridgeNotFoundError,
    status=404,
    code="bridge_not_found",
    title="Bridge not found",
    detail=str,
    description="The selected Hue Bridge was not discovered.",
)
BRIDGE_NOT_SELECTED = Error(
    BridgeNotSelectedError,
    status=409,
    code="bridge_not_selected",
    title="Bridge not selected",
    detail=str,
    description="A Hue Bridge must be selected before registration.",
)
LINK_BUTTON_TIMEOUT = Error(
    LinkButtonTimeoutError,
    status=409,
    code="link_button_timeout",
    title="Link button timeout",
    detail=str,
    description="The Hue Bridge link button was not pressed in time.",
)
ONBOARDING_READ_ONLY = Error(
    OnboardingReadOnlyError,
    status=409,
    code="onboarding_read_only",
    title="Onboarding is read-only",
    detail=str,
    description="Environment overrides make Hue onboarding read-only.",
)

lighting_errors = ErrorRegistry.merge(
    api_errors,
    ErrorRegistry(
        name="lighting",
        errors=[
            SCENE_NOT_FOUND,
            HUE_UNAVAILABLE,
            BRIDGE_NOT_FOUND,
            BRIDGE_NOT_SELECTED,
            LINK_BUTTON_TIMEOUT,
            ONBOARDING_READ_ONLY,
        ],
    ),
    name="lighting",
)

doctor_errors = [SCENE_NOT_FOUND, CONFIGURATION_INVALID, HUE_UNAVAILABLE]
scene_errors = [CONFIGURATION_INVALID, HUE_UNAVAILABLE]
discover_bridges_errors = [CONFIGURATION_INVALID, HUE_UNAVAILABLE]
bridge_status_errors = [CONFIGURATION_INVALID]
select_bridge_errors = [
    BRIDGE_NOT_FOUND,
    ONBOARDING_READ_ONLY,
    *discover_bridges_errors,
]
register_bridge_errors = [
    BRIDGE_NOT_SELECTED,
    LINK_BUTTON_TIMEOUT,
    ONBOARDING_READ_ONLY,
    CONFIGURATION_INVALID,
    HUE_UNAVAILABLE,
]
