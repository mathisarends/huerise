from dishka import Provider, Scope, provide

from huerise.features.lighting.application import HueOnboarding, SceneService
from huerise.features.lighting.domain import (
    HueClientFactory,
    HueCredentialsSource,
    OnboardingGateway,
)
from huerise.features.lighting.infrastructure.hue import (
    HueCredentialsProvider,
    HueifyClientFactory,
    HueifyOnboarding,
)
from huerise.platform.configuration import ConfigurationStore
from huerise.platform.settings import HueEnvironment


class LightingProvider(Provider):
    scope = Scope.APP

    @provide
    def client_factory(self) -> HueClientFactory:
        return HueifyClientFactory()

    @provide
    def credentials(
        self,
        configuration: ConfigurationStore,
        environment: HueEnvironment,
    ) -> HueCredentialsSource:
        return HueCredentialsProvider(configuration, environment)

    @provide
    def onboarding_gateway(self) -> OnboardingGateway:
        return HueifyOnboarding()

    @provide
    def onboarding(
        self,
        configuration: ConfigurationStore,
        environment: HueEnvironment,
        gateway: OnboardingGateway,
    ) -> HueOnboarding:
        return HueOnboarding(configuration, environment, gateway)

    @provide
    def scenes(
        self,
        credentials: HueCredentialsSource,
        clients: HueClientFactory,
    ) -> SceneService:
        return SceneService(credentials, clients)
