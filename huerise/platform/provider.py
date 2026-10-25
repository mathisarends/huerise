from dishka import Provider, Scope, provide

from huerise.platform.configuration import YamlConfiguration
from huerise.platform.settings import AppSettings, HueEnvironment


class PlatformProvider(Provider):
    scope = Scope.APP

    @provide
    def app_settings(self) -> AppSettings:
        return AppSettings()

    @provide
    def hue_environment(self) -> HueEnvironment:
        return HueEnvironment()

    @provide
    def configuration(self, settings: AppSettings) -> YamlConfiguration:
        return YamlConfiguration(settings.config_path)
