# Huerise

Huerise wakes you up with light. It drives a Philips Hue Bridge through a
gradual sunrise: the configured scene comes up at its dimmest, then brightens
smoothly to the brightness stored in that scene over the duration you choose.

A single YAML file describes the alarm, and an HTTP API plus a `huerise` CLI
start it, stop it, and check that everything is wired up. Scheduling stays with
whatever already runs on time for you — cron, a home automation system, a phone
shortcut — which calls `POST /daylight-alarm/start`.

## Contents

- [How it works](#how-it-works)
- [Installation](#installation)
- [Configuration](#configuration)
- [Run with Docker](#run-with-docker)
- [API](#api)
- [CLI](#cli)
- [Local development](#local-development)
- [Architecture](docs/architecture.md)

## How it works

Starting an alarm runs one linear brightness ramp:

1. The YAML file is read fresh, so the latest configuration always applies.
2. The room owning `scene_id` is resolved from the Bridge.
3. The Hue event stream is connected before changing the lights, so external
   control can be observed throughout the alarm.
4. The scene is activated at 1% brightness, setting its colors at their
   dimmest.
5. A background task then steps the room's brightness once per second, moving
   linearly from 1% to the brightness stored in the scene across
   `duration_seconds`.
6. When the ramp completes the lights simply stay where they are. Huerise sends
   no final command and never switches anything off.

Because the configuration is read at start time, a running alarm keeps the
snapshot it began with; editing the YAML mid-run affects only the next one.
Exactly one alarm can be active at a time, and `stop` cancels the ramp in place
— the lights hold their current brightness rather than jumping back.

Using a remote, app, or automation to change the alarm room implicitly stops
the alarm. Changes to power, brightness, color, scene, or an entertainment source
take priority; Huerise cancels both the remaining ramp and any delayed
after-alarm scene without sending a reset command. Other rooms are ignored.

The monitor recognizes acknowledgements of its own commands, including delayed
and quantized brightness updates. Hue events do not reliably identify who sent
a command, so an external command that leaves the same state as an expected
acknowledgement cannot always be distinguished. Dynamic scene effects can also
produce independent state changes.

During stream reconnection, further writes wait for the room's state to be
verified again. A changed state stops the alarm. If monitoring cannot be restored
within five seconds, the alarm ends instead of sending unobserved commands.
Starting also fails before the first light command if the stream cannot connect.

`GET /doctor` checks the configuration and REST prerequisites ahead of time:
the YAML parses and validates, Hue credentials exist, the Bridge answers and
accepts them, and the configured scene still exists.

## Installation

Huerise has two parts: the server (run as a container) and the optional
`huerise` CLI (a single binary) for talking to it. Pick what you need.

### Server

```bash
docker pull ghcr.io/mathisarends/huerise:latest
```

Or run [Run with Docker](#run-with-docker) below to build and start it
locally via Compose.

### CLI

Download the archive for your OS and architecture from the
[latest release](https://github.com/mathisarends/huerise/releases/latest),
then unpack it and put `huerise` on your `PATH`. On Linux/macOS:

```bash
curl -LO https://github.com/mathisarends/huerise/releases/latest/download/huerise_<version>_<os>_<arch>.tar.gz
tar -xzf huerise_<version>_<os>_<arch>.tar.gz
sudo mv huerise /usr/local/bin/
```

Replace `<version>` with the release tag without the leading `v` (e.g.
`0.1.1`), `<os>` with `linux` or `darwin`, and `<arch>` with `amd64` or
`arm64`. Windows builds ship as a `.zip` with the same naming.

```bash
huerise --help
```

See [`docs/cli.md`](docs/cli.md) for the full command reference.

## Configuration

Copy the examples:

```bash
cp .env.example .env
mkdir -p data
cp huerise.example.yml data/huerise.yml
```

Set a private API key in `.env`:

```dotenv
HUERISE_API_KEY=replace-with-a-long-random-key
HUERISE_LOG_LEVEL=INFO
HUERISE_PORT=8000
```

`HUERISE_PORT` controls the port published on the host. The application keeps
listening on port 8000 inside the container.

The alarm is fully described by `data/huerise.yml`:

```yaml
daylight_alarm:
  room:
    id: "00000000-0000-0000-0000-000000000000"
    name: Bedroom
  scene:
    id: "00000000-0000-0000-0000-000000000000"
    name: Sunrise
  duration_seconds: 1800
  after_alarm:
    room:
      id: "00000000-0000-0000-0000-000000000000"
      name: Bedroom
    scene:
      id: "00000000-0000-0000-0000-000000000000"
      name: Evening
    delay_seconds: 600
```

Hue onboarding writes the selected bridge and application key into the optional
`hue` section of the same file. As a read-only deployment alternative, set
`HUE_BRIDGE_IP` and `HUE_APP_KEY` together in `.env`.

The YAML file is read on every alarm start and Doctor check. A running alarm
continues with the snapshot it started with.

## Run with Docker

```bash
docker compose up --build -d
```

With the default `HUERISE_PORT`, the API and Swagger UI are available at
`http://localhost:8000` and `http://localhost:8000/docs`. Compose mounts
`./data` at `/config`; this YAML file is the application's only persistent
storage.

## API

Send the configured key as `X-API-Key` on application and diagnostic routes.
The `/health` and `/readiness` probes are public and return only a minimal status.

API failures use RFC 9457 `application/problem+json`, including `type`, `title`,
`status`, a stable `code`, and optional `detail`. YAML failures add sanitized
`issues`; invalid requests add `errors` with JSON pointers. For example, a
second alarm returns `409` with `code: "alarm_already_running"`. Server and
CLI should be upgraded together from `0.1.x`; see [the changelog](CHANGELOG.md).

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Liveness: answer without reading YAML or contacting Hue |
| `GET` | `/readiness` | Readiness: verify configuration and Hue prerequisites; return `503` if unavailable |
| `GET` | `/doctor` | Validate YAML, credentials, Bridge access, and configured scene |
| `POST` | `/daylight-alarm/start` | Start immediately, optionally overriding this run's duration |
| `POST` | `/daylight-alarm/stop` | Stop it without changing the current light state |
| `GET` | `/daylight-alarm/configuration` | Read the human-readable alarm configuration |
| `PUT` | `/daylight-alarm/configuration` | Save the selected room, scene, and duration |
| `GET` | `/hue/rooms` | List rooms with their scenes and reference brightness |
| `GET` | `/hue/bridges` | Discover Hue Bridges |
| `GET` | `/hue/bridge` | Read onboarding state |
| `PUT` | `/hue/bridge` | Select a discovered Bridge |
| `POST` | `/hue/bridge/register` | Register after pressing the Bridge link button |

The onboarding states are `not_selected`, `link_button_required`, and `ready`.
Registration waits up to 60 seconds for the physical link button. Environment
credentials report `ready` with `read_only: true`.

Both probes return `200` with `{"status":"ok"}` when successful. Readiness uses
the Doctor checks with a five-second deadline. Missing prerequisites or a timeout
return `503` with `code: "not_ready"` and `Retry-After: 5`; `/doctor` retains the
detailed protected diagnostics. These checks never change the lights.

The container's healthcheck uses `/health`, so a temporary Hue outage does not
mark the API process itself as unhealthy. Orchestrators can use `/readiness`
separately to decide whether the application is ready to run alarms.

Example:

```bash
curl -X POST http://localhost:8000/daylight-alarm/start \
  -H "X-API-Key: $HUERISE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"duration_seconds": 10}'
```

Omit the body to use the configured duration. The request may override only the
duration of that run. The scene comes from YAML, while its target brightness is
read fresh from the Hue Bridge when the alarm starts. A second start while an
alarm is running returns `409 Conflict`, and stopping is idempotent.

## CLI

The `huerise` CLI in [`cli/`](cli) talks to the same API and is documented in
[`docs/cli.md`](docs/cli.md).

```bash
huerise doctor
huerise start --duration-seconds 900
huerise stop
```

It reads `HUERISE_API_URL` and `HUERISE_API_KEY` from the environment or a
dotenv file (`--env-file`). Every command also prints machine-readable output
with `--json`.

When `HUERISE_API_URL` is unset, the CLI connects to localhost using
`HUERISE_PORT`, or port 8000 when neither setting is present. Set the full URL
when the container runs on another host:

```dotenv
HUERISE_API_URL=http://huerise.local:8080
```

## Local development

Huerise requires Python 3.14, Go 1.25 or newer, and
[`uv`](https://docs.astral.sh/uv/).

```bash
uv sync --locked
$env:HUERISE_API_KEY = "development-key"  # PowerShell
uv run python -m huerise.main
```

Quality checks:

```bash
uv run --locked poe check
uv run --locked poe ci
```

Releases are built from semantic-version Git tags. See
[`docs/release.md`](docs/release.md) for the complete release process.

Canon composes the `health`, `daylight_alarm`, `lighting`, and shared `platform`
features.
Application services depend on owned ports, and Dishka owns their lifetimes.
See [Architecture](docs/architecture.md) for the layout, HTTP contracts, and
enforced dependency boundaries.
