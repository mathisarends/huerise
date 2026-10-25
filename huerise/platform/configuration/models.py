from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, IPvAnyAddress, StrictInt, StrictStr


class ConfigurationIssue(BaseModel):
    location: str
    message: str
    type: str


class ConfigurationError(Exception):
    def __init__(self, message: str, issues: list[ConfigurationIssue] | None = None):
        super().__init__(message)
        self.issues = issues or []


class NamedResourceConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    name: StrictStr = Field(min_length=1)


class AfterAlarmConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    room: NamedResourceConfig
    scene: NamedResourceConfig
    delay_seconds: StrictInt = Field(ge=0)


class DaylightAlarmConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    room: NamedResourceConfig
    scene: NamedResourceConfig
    duration_seconds: StrictInt = Field(gt=0)
    after_alarm: AfterAlarmConfig | None = None


class HueConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    bridge_id: StrictStr | None = Field(default=None, min_length=1)
    bridge_ip: IPvAnyAddress
    app_key: StrictStr | None = Field(default=None, min_length=20)


class HueriseConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    daylight_alarm: DaylightAlarmConfig
    hue: HueConfig | None = None
