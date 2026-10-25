from abc import ABC, abstractmethod

from huerise.platform.configuration.models import (
    DaylightAlarmConfig,
    HueConfig,
    HueriseConfig,
)


class ConfigurationSource(ABC):
    @abstractmethod
    def load(self) -> HueriseConfig: ...


class ConfigurationStore(ConfigurationSource):
    @abstractmethod
    def load_hue(self) -> HueConfig | None: ...

    @abstractmethod
    def save_hue(self, hue: HueConfig) -> None: ...

    @abstractmethod
    def save_daylight_alarm(self, alarm: DaylightAlarmConfig) -> None: ...
