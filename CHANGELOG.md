# Changelog

All notable changes to `pulse-sandbox-mocks` are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] — 2026-05-08

### Added

- **Profile system** — fixture data is now loaded from a profile module
  selected by `PULSE_SANDBOX_PROFILE` (default `baseline`). Restructure
  is a pure refactor in v0.2.0; existing routes/tests work unchanged.
  - `pulse_sandbox/profiles/baseline.py` — current happy-path data with
    namespaced constants (`HUBSPOT_*`, `PRODUCTIVE_*`)
  - `pulse_sandbox/profiles/rich.py` — extends baseline with 5
    deliberately-tuned HubSpot scenario deals + 1 company + 1 Productive
    scenario
  - `pulse_sandbox/profiles/__init__.py` — `load_active_profile()` loader
    with empty-string fallback and unknown-profile error message
- **`rich` profile scenario coverage:**
  - `9101` OVERDUE-OPEN — open + closedate 7d in past
  - `9102` STUCK-STAGE — open + 60d no movement (createdAt == updatedAt)
  - `9103` ORPHAN — open + missing engagement_lead_name + service_type
    (introduces new Echo Foundation company id 5005)
  - `9104` JUST-CREATED — createdate today
  - `9105` RECENT-WIN — closedwon + closedate yesterday
  - Productive scenario only added for 9102 — keeps the "Missing
    Productive Scenarios" warning testable across multiple deal types
- **Tests:** 20 new in `tests/test_profiles.py` — loader behavior,
  baseline counts, rich extensions, per-scenario data shape
- **Docs:** `docs/FIXTURES.md` and `docs/ARCHITECTURE.md` updated with
  profile system rationale and rich-profile inventory

### Notes

- Default behavior unchanged. Pulse loads `baseline` unless an operator
  sets `PULSE_SANDBOX_PROFILE=rich` and restarts the sandbox.
- A companion change in the Pulse repo (`api/services/_drift_history.py`)
  adds a sandbox-mode shim for `deal_closedate_history` drift data,
  with fake drift entries for deal IDs 9001/9003/9007/9101 to match the
  sandbox profiles. See Pulse commit `9a1ffb7`.

## [0.1.1] — 2026-05-08

### Added

- `GET /scenarios?filter[deal_id]={id}` — Productive's per-deal forecast
  scenarios. Pulse calls this from `api/routes/hubspot.py:220` to count
  whether each HC deal has any scenarios attached. Sandbox returns 4
  scenarios across deals 601 / 602 / 603 (deal 601 has 2 to exercise
  count > 1).
- `GET /reports/{report_id}` and `GET /reports/{report_id}/budgets` — saved
  custom report endpoints. Pulse references the "Client Engagement
  Utilization Report" via env var `CLIENT_ENG_UTIL_REPORT_ID` (default
  `1591877`). Sandbox returns 3 budget rows with utilization at 65% / 70%
  / 20%, matching Pulse's `>=50%` filter use case.
- 9 new tests bringing total to 68 passing, 92% coverage.
- Regression-guard tests confirming `/reports/budget_reports` and
  `/reports/time_reports` still match their specific handlers, not the
  new parametric `/reports/{report_id}` route.
- `FIXTURES.md` updated with the 4 new scenario rows and the saved-report
  budget table.

### Notes

- Live Pulse code paths surfaced these endpoints during the local dev
  smoke test on 2026-05-08. The legacy `tests/test_saved_report_endpoint.py`
  in Pulse uses `return True/False` instead of pytest assertions, so it
  silently "passed" against 404s before this fix. With the new sandbox
  endpoints in place, the test now passes against real data — though it
  remains a malformed pytest test that should be cleaned up Pulse-side.

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
