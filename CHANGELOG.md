# Changelog

## Unreleased

- Move Doctor diagnostics into a dedicated health feature while preserving the
  `/doctor` API and CLI contracts.
- Add public `/health` liveness and `/readiness` probes, bounded readiness checks
  with generic `503` failures, and a container liveness healthcheck.

## 0.2.0 — 2026-10-25

- Adopt Canon 0.7 feature composition, managed Dishka lifetimes, and declarative
  HTTP error and success contracts.
- Separate shared platform infrastructure, Hue domain ports, application
  workflows, concrete adapters, and explicit API response mappings.
- Replace handwritten exception routers with RFC 9457 Problem Details and
  stable error codes; regenerate the Go client from the same contracts.
- Add ty, four enforced architecture contracts, branch coverage, and shared Poe
  tasks used by local checks and Linux/Windows CI.
- Package the application distribution into the production container, reduce
  the build context, and fix the example environment and YAML setup.

### Migration from 0.1.x

Upgrade the server and CLI together. Routes, successful payloads, API keys, and
the YAML format remain compatible. Error responses now use
`application/problem+json` with `type`, `title`, `status`, and stable `code`.
Configuration failures retain sanitized `issues`; request validation now uses
`errors` with JSON pointers.

CLI JSON failures preserve server error codes such as `authentication_required`
and `configuration_invalid`. Exit codes remain `1` for general failures, `2`
for invalid input/configuration, and `3` for authentication failures. HTTP 422
request validation also returns exit code `2`.

The ASGI entry point is now `huerise.app:app`. Docker and `python -m huerise.main`
already use it; update custom Uvicorn commands accordingly.
