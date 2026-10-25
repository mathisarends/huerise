from dataclasses import dataclass

from huerise.platform.configuration import HueriseConfig
from huerise.platform.configuration.ports import ConfigurationSource


@dataclass
class FakeConfiguration(ConfigurationSource):
    config: HueriseConfig

    def load(self) -> HueriseConfig:
        return self.config
