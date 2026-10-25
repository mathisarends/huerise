import os
import tempfile
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ValidationError

from huerise.platform.configuration.models import (
    ConfigurationError,
    ConfigurationIssue,
    DaylightAlarmConfig,
    HueConfig,
    HueriseConfig,
)
from huerise.platform.configuration.ports import ConfigurationStore


class YamlConfiguration(ConfigurationStore):
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> HueriseConfig:
        return self._validate(HueriseConfig, self._read())

    def load_hue(self) -> HueConfig | None:
        raw = self._read(required=False)
        if "hue" not in raw:
            return None
        return self._validate(HueConfig, raw["hue"], prefix="hue")

    def save_hue(self, hue: HueConfig) -> None:
        raw = self._read(required=False)
        raw["hue"] = hue.model_dump(mode="json", exclude_none=True)
        self._write(raw)

    def save_daylight_alarm(self, alarm: DaylightAlarmConfig) -> None:
        raw = self._read(required=False)
        raw["daylight_alarm"] = alarm.model_dump(mode="json")
        self._write(raw)

    def _read(self, *, required: bool = True) -> dict[str, Any]:
        try:
            contents = self.path.read_text(encoding="utf-8")
        except FileNotFoundError as error:
            if not required:
                return {}
            raise ConfigurationError(
                f"Configuration file not found: {self.path}"
            ) from error

        try:
            raw = yaml.safe_load(contents)
        except yaml.YAMLError as error:
            raise ConfigurationError(f"Invalid YAML: {error}") from error

        if raw is None and not required:
            return {}
        if not isinstance(raw, dict):
            raise ConfigurationError("Configuration root must be a mapping")
        return raw

    @staticmethod
    def _validate(
        model: type[BaseModel], raw: Any, *, prefix: str | None = None
    ) -> Any:
        try:
            return model.model_validate(raw)
        except ValidationError as error:
            issues = [
                ConfigurationIssue(
                    location=".".join(
                        str(part)
                        for part in ((prefix,) if prefix else ()) + item["loc"]
                    ),
                    message=item["msg"],
                    type=item["type"],
                )
                for item in error.errors()
            ]
            raise ConfigurationError("Configuration is invalid", issues) from error

    def _write(self, raw: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="\n",
                dir=self.path.parent,
                prefix=f".{self.path.name}.",
                suffix=".tmp",
                delete=False,
            ) as temporary:
                yaml.safe_dump(raw, temporary, sort_keys=False)
                temporary_path = Path(temporary.name)
            os.replace(temporary_path, self.path)
        finally:
            if temporary_path is not None and temporary_path.exists():
                temporary_path.unlink()
