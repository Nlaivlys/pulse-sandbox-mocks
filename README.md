# pulse-sandbox-mocks

Local sandbox infrastructure for the [Pulse PMO platform](https://github.com/Nlaivlys/thepulse).
Provides mock HTTP servers and SDK shims so Pulse can run locally without hitting live external APIs.

## What it mocks

| Service | Mode | Endpoints / methods |
|---|---|---|
| HubSpot | HTTP server | 6 REST endpoints (deals search, owners, batch associations, batch company reads, pipelines, properties) |
| Productive | HTTP server | 9 REST endpoints (people, teams, custom fields, projects, bookings, deals, budget reports, time reports) |
| OpenAI | SDK shim | `audio.transcriptions.create`, `chat.completions.create` |
| Resend | SDK shim | `Emails.send` |
| Slack | SDK shim | `conversations_create`, `conversations_invite`, `users_lookupByEmail` |

## Install

```bash
git clone https://github.com/Nlaivlys/pulse-sandbox-mocks.git
cd pulse-sandbox-mocks
pip install -e .
```

Or install directly from GitHub:

```bash
pip install git+https://github.com/Nlaivlys/pulse-sandbox-mocks.git
```

## Run the HTTP mock server

```bash
pulse-sandbox        # binds to 127.0.0.1:9000
```

Or from source:

```bash
bash scripts/start.sh
```

## Wire it up in Pulse

In Pulse's `.env`:

```bash
# Master toggle (factories switch on this for SDK-based services)
PULSE_API_MODE=sandbox

# HTTP-based services — point at the mock server
HUBSPOT_API_BASE=http://localhost:9000/hubspot
PRODUCTIVE_API_BASE=http://localhost:9000/productive/api/v2

# SDK-based services — factories will pick up the master toggle
# (no per-service URLs needed)
```

Set `PULSE_API_MODE=live` (or unset) to go back to real APIs.

## Architecture

- `pulse_sandbox/server.py` — FastAPI app, mounts HubSpot + Productive routers under prefixes
- `pulse_sandbox/hubspot/` — HubSpot REST mock + fixtures
- `pulse_sandbox/productive/` — Productive JSON:API mock + fixtures + serialization helper
- `pulse_sandbox/shims/` — SDK shim classes for OpenAI / Resend / Slack
- `pulse_sandbox/cli.py` — `pulse-sandbox` console entrypoint

## What's NOT mocked

- Clerk authentication — out of scope; bypass auth at the Pulse layer when developing
- Supabase — use a separate test database
- Tally webhook receiver — Pulse is the receiver; trigger via curl if needed
- Write round-trips — sandbox is in-memory, not persisted; restart resets state

## Status

**Phase 1 (MVP) — 2026-05-08:** initial scaffold + 5 services mocked at shape level. Synthetic data only.

**Phase 2 — planned:** anonymized realistic data, persistence (SQLite), Docker compose wrapper, write round-trips.

## License

MIT.
