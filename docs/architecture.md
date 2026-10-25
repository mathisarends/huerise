# Architecture

Huerise follows [Canon](https://github.com/mathisarends/canon)'s feature slices
and uses `fastapi-canon` 0.7 for application composition, Dishka lifetimes, and
HTTP contracts. The composition and platform layout follow Maximus Trading's
separation of shared mechanisms from business features.

```text
huerise/
  app.py                 FastAPI factory and Canon composition
  composition.py         Ordered feature descriptors
  main.py                Local development entry point
  platform/
    api/                 Authentication and shared Problem Details contracts
    configuration/       YAML boundary models, owned ports, and file adapter
    settings.py          Environment settings
    provider.py          Shared Dishka bindings
    feature.py           Platform assembly and logging lifespan
  features/
    health/
      application/       Doctor diagnostics and bounded readiness checks
      infrastructure/    Dishka provider
      presentation/      Probe and diagnostic routers, schemas, mappers, errors
      feature.py         Feature descriptor
    lighting/
      domain/            Hue values, errors, and abstract gateway contracts
      application/       Onboarding and scene workflows
      infrastructure/    Hueify adapters and Dishka provider
      presentation/      Canon routers, response schemas, mappers, errors
      feature.py         Feature descriptor
    daylight_alarm/
      application/       Alarm lifecycle and configuration workflows
      infrastructure/    Dishka provider and alarm cleanup
      presentation/      Canon router, schemas, mappers, errors
      feature.py         Feature descriptor
```

Add a domain layer when a feature has domain behavior worth separating. The
configuration models deliberately use Pydantic because YAML validation is an
application boundary. The Hue domain itself uses plain dataclasses and ABCs.

## Dependencies and ownership

Application services accept owned ports through their constructors. The YAML
adapter implements `ConfigurationStore`; its read-only parent
`ConfigurationSource` is enough for the alarm and Doctor. Hue adapters implement
the domain's client, credential, and onboarding ABCs. Providers bind those ports
to concrete implementations.

Presentation calls application services and maps their results explicitly.
Infrastructure owns external SDK calls and persistence. Domain code stays free
of framework dependencies. Platform code never imports business features.
Import Linter checks these boundaries, including indirect imports.

The package facades expose a small public vocabulary. Feature roots stay empty,
so importing domain types does not assemble HTTP routers or infrastructure.
`feature.py` is the explicit assembly entry point.

`Composition` creates one Dishka container per application and closes it during
shutdown. The alarm provider owns its task's lifetime and stops a resolved alarm
before the container closes. Tests add features with explicit provider overrides
through `create_app(*extra_features)`.

The alarm also owns a concurrent override watcher. The Hue adapter maps Hueify's
event stream into that port, correlates its own commands with light updates, and
watches only the alarm room's resources and entertainment areas. Reconnection
blocks writes until fresh snapshots match the last commanded state. External
control or a failed monitoring recovery cancels the fade and its pending
after-alarm scene; both tasks are drained before the client is closed.

## HTTP contracts

Every route declares a stable operation ID, success response, and relevant
failures. Protected `CanonRouter` instances apply the shared authentication
dependency and declare its problem alongside operation-specific errors.
`Composition` merges the registries and installs their runtime handlers.

The health feature owns the protected `/doctor` diagnostics and the public
`/health` and `/readiness` probes. Liveness touches no configuration or external
dependency. Readiness runs the Doctor prerequisites under a five-second deadline
and converts expected dependency failures into one generic `503` problem with a
retry hint. Detailed failures stay available through `/doctor`. The container
healthcheck uses liveness; readiness is a separate signal for orchestrators.

Errors use RFC 9457 `application/problem+json` with a stable `code`. Configuration
errors include sanitized `issues`; request validation uses Canon's `errors`
with JSON pointers. Multiple problems with the same HTTP status use a
discriminated `oneOf`. Unhandled exceptions return a generic problem, and raw
YAML parser messages stay out of public responses.

Canon 0.7 does not add request validation to an explicit domain-error 422
response. `platform/api/openapi.py` adds that alternative for operations with
inputs. `scripts/export_openapi.py` expresses `const` as a single-value `enum`
and type arrays as `anyOf`, preserving their meaning for ogen. The runtime
document retains the canonical OpenAPI 3.1 schemas. The Go client is generated
from the checked-in export; regenerate it with `uv run --locked poe codegen`.

Further Canon transports compose through the same feature descriptors and
registries. Add the corresponding Streams, RPC, or WebRTC package when adding
an actual stream, socket protocol, or media-session contract.

## Checks

`uv run --locked poe check` runs formatting, Ruff, ty, and the four import
contracts. `uv run --locked poe ci` also checks the lockfile, Python tests with
branch coverage, Go tests and vet, and generated-contract drift. CI runs this
same command on Linux and Windows; release verification uses it as well.

The final container installs the built application distribution into its
environment. Shared development caches, local credentials, and data are excluded
from its build context.
