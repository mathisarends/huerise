from fastapi_canon import Feature

from huerise.features.daylight_alarm.feature import feature as daylight_alarm
from huerise.features.health.feature import feature as health
from huerise.features.lighting.feature import feature as lighting

FEATURES: tuple[Feature, ...] = (
    health,
    lighting,
    daylight_alarm,
)
