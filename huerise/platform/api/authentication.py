import secrets

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Security
from fastapi.security import APIKeyHeader

from huerise.platform.api.errors import AuthenticationRequiredError
from huerise.platform.settings import AppSettings

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


@inject
async def require_api_key(
    settings: FromDishka[AppSettings],
    supplied: str | None = Security(_api_key_header),
) -> None:
    expected = settings.api_key.get_secret_value()
    if supplied is None or not secrets.compare_digest(supplied, expected):
        raise AuthenticationRequiredError
