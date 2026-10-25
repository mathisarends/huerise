from dishka import Provider, Scope, provide

from huerise.features.health.application import Doctor
from huerise.features.lighting.domain import HueClientFactory, HueCredentialsSource
from huerise.platform.configuration import ConfigurationSource


class HealthProvider(Provider):
    scope = Scope.APP

    @provide
    def doctor(
        self,
        configuration: ConfigurationSource,
        credentials: HueCredentialsSource,
        clients: HueClientFactory,
    ) -> Doctor:
        return Doctor(configuration, credentials, clients)
