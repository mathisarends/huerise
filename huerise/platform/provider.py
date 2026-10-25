from dishka import Provider, Scope, alias, provide

from huerise.platform.configuration import ConfigurationSource, ConfigurationStore
from huerise.platform.configuration.yaml import YamlConfiguration
from huerise.platform.settings import AppSettings, HueEnvironment


class PlatformProvider(Provider):
    scope = Scope.APP
    configuration_store = alias(YamlConfiguration, provides=ConfigurationStore)
    configuration_source = alias(ConfigurationStore, provides=ConfigurationSource)

    @provide
    def app_settings(self) -> AppSettings:
        return AppSettings()

    @provide
    def hue_environment(self) -> HueEnvironment:
        return HueEnvironment()

    @provide
    def configuration(self, settings: AppSettings) -> YamlConfiguration:
        return YamlConfiguration(settings.config_path)
