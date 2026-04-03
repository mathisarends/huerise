from pydantic_settings import BaseSettings, SettingsConfigDict


class HueSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="HUE_",
    )

    app_key: str
    bridge_ip: str
