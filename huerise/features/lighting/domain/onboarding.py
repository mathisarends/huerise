from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum


class OnboardingState(StrEnum):
    NOT_SELECTED = "not_selected"
    LINK_BUTTON_REQUIRED = "link_button_required"
    READY = "ready"


class OnboardingReadOnlyError(Exception):
    pass


class BridgeNotFoundError(Exception):
    def __init__(self, bridge_id: str) -> None:
        super().__init__(f"Hue Bridge not found: {bridge_id}")


class BridgeNotSelectedError(Exception):
    pass


class LinkButtonTimeoutError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class HueBridge:
    id: str
    ip_address: str


@dataclass(frozen=True, slots=True)
class DiscoveredBridge:
    id: str
    ip_address: str
    selected: bool


@dataclass(frozen=True, slots=True)
class OnboardingStatus:
    state: OnboardingState
    bridge_id: str | None
    ip_address: str | None
    read_only: bool


class OnboardingGateway(ABC):
    @abstractmethod
    async def discover(self) -> tuple[HueBridge, ...]: ...

    @abstractmethod
    async def register(self, bridge_ip: str) -> str: ...
