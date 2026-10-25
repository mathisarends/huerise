from fastapi_canon import Error, ErrorRegistry
from pydantic import BaseModel

from huerise.platform.configuration import ConfigurationError, ConfigurationIssue


class AuthenticationRequiredError(Exception):
    pass


class ConfigurationIssues(BaseModel):
    issues: list[ConfigurationIssue]


AUTHENTICATION_REQUIRED = Error(
    AuthenticationRequiredError,
    status=401,
    code="authentication_required",
    title="Authentication required",
    detail="Invalid or missing API key",
    headers={"WWW-Authenticate": 'ApiKey realm="huerise"'},
)

CONFIGURATION_INVALID = Error(
    ConfigurationError,
    status=422,
    code="configuration_invalid",
    title="Invalid configuration",
    detail="The YAML configuration is missing or invalid.",
    extensions_model=ConfigurationIssues,
    extensions=lambda error: ConfigurationIssues(issues=error.issues),
    description="The YAML configuration is missing or invalid.",
)

api_errors = ErrorRegistry(
    name="platform",
    errors=[AUTHENTICATION_REQUIRED, CONFIGURATION_INVALID],
)
