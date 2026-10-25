from fastapi_canon import Feature

from huerise.features.daylight_alarm.infrastructure.provider import (
    DaylightAlarmProvider,
)
from huerise.features.daylight_alarm.presentation import router

feature = Feature(
    name="daylight_alarm",
    routers=[router],
    providers=[DaylightAlarmProvider],
)
