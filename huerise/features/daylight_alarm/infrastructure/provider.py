from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide

from huerise.features.daylight_alarm.application import (
    DaylightAlarm,
    DaylightAlarmConfiguration,
)
from huerise.features.lighting.application import HueClientFactory, SceneService
from huerise.features.lighting.infrastructure import HueCredentialsProvider
from huerise.platform.configuration import YamlConfiguration


class DaylightAlarmProvider(Provider):
    scope = Scope.APP

    @provide
    async def daylight_alarm(
        self,
        configuration: YamlConfiguration,
        credentials: HueCredentialsProvider,
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
        configuration: YamlConfiguration,
        scenes: SceneService,
    ) -> DaylightAlarmConfiguration:
        return DaylightAlarmConfiguration(configuration, scenes)
