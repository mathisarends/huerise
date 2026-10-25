from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi_canon import CanonRouter, Composition, ErrorOptions, Feature

from huerise.platform.api.errors import CONFIGURATION_INVALID, api_errors
from huerise.platform.configuration import ConfigurationError, ConfigurationIssue


def test_preserves_configuration_issues_without_exposing_yaml_contents() -> None:
    router = CanonRouter(error_registry=api_errors)

    @router.get("/configuration", raises=[CONFIGURATION_INVALID])
    async def configuration() -> None:
        raise ConfigurationError(
            "Invalid YAML: app_key: secret-bridge-key",
            [
                ConfigurationIssue(
                    location="daylight_alarm.scene",
                    message="Field required",
                    type="missing",
                )
            ],
        )

    app = Composition(
        Feature(name="configuration", routers=[router]),
        errors=ErrorOptions(type_base="urn:huerise:problem"),
    ).apply(FastAPI())
    response = TestClient(app).get("/configuration")

    assert response.status_code == 422
    assert response.headers["content-type"] == "application/problem+json"
    assert response.json() == {
        "type": "urn:huerise:problem/configuration_invalid",
        "title": "Invalid configuration",
        "status": 422,
        "code": "configuration_invalid",
        "detail": "The YAML configuration is missing or invalid.",
        "issues": [
            {
                "location": "daylight_alarm.scene",
                "message": "Field required",
                "type": "missing",
            }
        ],
    }


def test_unexpected_errors_do_not_expose_exception_text() -> None:
    router = CanonRouter(error_registry=api_errors)

    @router.get("/failure")
    async def failure() -> None:
        raise RuntimeError("private upstream response")

    app = Composition(
        Feature(name="failure", routers=[router]),
        errors=ErrorOptions(type_base="urn:huerise:problem"),
    ).apply(FastAPI())
    response = TestClient(app, raise_server_exceptions=False).get("/failure")

    assert response.status_code == 500
    assert response.headers["content-type"] == "application/problem+json"
    assert response.json()["code"] == "internal_server_error"
    assert "private" not in response.text
