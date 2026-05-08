# Changelog

All notable changes to `pulse-sandbox-mocks` are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-05-08

Initial MVP release. Phase 1 of the Pulse local-sandbox project.

### Added

- HTTP mock server for HubSpot (FastAPI) — 7 endpoints:
  - `POST /crm/v3/objects/deals/search`
  - `GET /crm/v3/objects/deals` (health-check fallback)
  - `GET /crm/v3/owners`
  - `POST /crm/v4/associations/deals/companies/batch/read`
  - `POST /crm/v3/objects/companies/batch/read`
  - `GET /crm/v3/pipelines/deals`
  - `GET /crm/v3/properties/deals`
- HTTP mock server for Productive (FastAPI, JSON:API) — 9 endpoints:
  - `GET /ping`
  - `GET /people` (with `include=teams`)
  - `GET /teams`
  - `GET /custom_fields` (with `include=options`)
  - `GET /projects` (with `include=company,budget`)
  - `GET /projects/{id}`
  - `GET /bookings` (with `include=person,service,service.deal,service.deal.project`)
  - `GET /deals` (with `include=project`)
  - `GET /reports/budget_reports` (with full include chain)
  - `GET /reports/time_reports`
- SDK shim for OpenAI — `audio.transcriptions.create` + `chat.completions.create`
- SDK shim for Resend — module-level `api_key` + `Emails.send`
- SDK shim for Slack — `WebClient` with `conversations_create`, `conversations_invite`, `users_lookupByEmail`. Stateful in-memory channel store. `SlackApiError` inherits from `slack_sdk.errors.SlackApiError` when available.
- JSON:API serialization helpers: `make_resource`, `to_one_rel`, `to_many_rel`, `envelope`
- Synthetic-but-realistic fixture data: 8 deals across confidence/stage/lifecycle states, 7 people mixing FTE/Contractor/Placeholder, 5 projects with budgets, 8 time-report rows across 2 weeks. Servant production custom-field IDs (55149/55151/55153/55147) baked in.
- `pulse-sandbox` CLI entrypoint (binds to `127.0.0.1:9000`)
- pytest test suite — 59 tests, 92% coverage, ~80ms runtime
- Documentation: README, ARCHITECTURE.md, FIXTURES.md, CONTRIBUTING.md

### Notes

- **Default install** ships only the SDK shims (no FastAPI/pydantic-2 dependency) so the package is safe to install in Pulse's venv alongside `clerk-sdk-python` (which requires pydantic 1.x).
- **Server extras** (`pip install pulse-sandbox-mocks[server]`) include FastAPI/uvicorn/pydantic-2 — install in a separate venv.
- Sandbox mode in Pulse is opt-in via env vars (`PULSE_API_MODE`, `HUBSPOT_API_BASE`, `PRODUCTIVE_API_BASE`). Default behavior is unchanged from production.
- ImportError fallback: if Pulse is configured for sandbox mode but the package isn't installed, factories log a warning and fall back to real SDK clients. Production-safe.

### Known limitations (Phase 2 backlog)

- Sample data is synthetic only. Anonymized real-data fixtures coming.
- All state in-memory. Restart resets sandbox state. SQLite-backed persistence planned.
- No docker-compose wrapper.
- Tally webhook receiver and Clerk auth not mocked (out of scope).
