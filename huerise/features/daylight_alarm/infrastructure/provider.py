from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide

from huerise.features.daylight_alarm.application import (
    DaylightAlarm,
    DaylightAlarmConfiguration,
)
from huerise.features.lighting.application import SceneService
from huerise.features.lighting.domain import HueClientFactory, HueCredentialsSource
from huerise.platform.configuration import ConfigurationSource, ConfigurationStore


class DaylightAlarmProvider(Provider):
    scope = Scope.APP

    @provide
    async def daylight_alarm(
        self,
        configuration: ConfigurationSource,
        credentials: HueCredentialsSource,
        clients: HueClientFactory,
    ) -> AsyncIterator[DaylightAlarm]:
        alarm = DaylightAlarm(configuration, credentials, clients)
        try:
            yield alarm
        finally:
            await alarm.stop()

    @provide
    def configuration(
        self,
        configuration: ConfigurationStore,
        scenes: SceneService,
    ) -> DaylightAlarmConfiguration:
        return DaylightAlarmConfiguration(configuration, scenes)
