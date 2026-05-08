# Architecture

> Design rationale and how-to-extend for `pulse-sandbox-mocks`.
> Last updated 2026-05-08 (v0.1.0).

## Why this exists

Pulse depends on six external services (HubSpot, Productive, OpenAI, Resend, Slack, Clerk). Local development against live APIs has three problems:

1. **Cost** — every dashboard render burns API quota.
2. **Pollution** — local development creates real HubSpot deals, real Slack channels, real Productive bookings.
3. **Coupling** — when an external service rotates a token or changes a response shape, every developer's local environment breaks until the token/contract is updated.

The sandbox decouples Pulse from live APIs for local dev. It also doubles as a **portability proof** — if Pulse can run against a swappable mock layer, it can run against any client's data source via the same abstraction. That's a Pulse productization milestone.

## Two mocking strategies, one package

The sandbox uses a **hybrid approach** because the services Pulse calls split cleanly into two categories:

| Category | Services | Strategy |
|---|---|---|
| **HTTP REST clients** (Pulse hand-rolls the requests) | HubSpot, Productive | HTTP-level mock server — Pulse points its env-var-driven base URL at `localhost:9000`, the FastAPI mock answers |
| **Vendor SDK clients** (Pulse uses the vendor's Python SDK) | OpenAI, Resend, Slack | SDK-level shim — a Python class/module mimicking the vendor SDK's surface; Pulse's factory swaps in the shim when sandbox mode is active |

**Why split?** HTTP-mocking the OpenAI/Resend/Slack SDKs would require simulating the SDKs' HTTP layer (auth headers, retries, response object construction). At the SDK boundary, mocking is ~10 lines per method. The HTTP-mock approach makes sense when Pulse is doing the HTTP work itself — which it is for HubSpot and Productive.

## Repo layout

```
pulse_sandbox/
├── __init__.py              # version stamp
├── server.py                # FastAPI app, mounts HubSpot + Productive routers
├── cli.py                   # `pulse-sandbox` console entrypoint
├── hubspot/
│   ├── routes.py            # 7 HubSpot endpoints
│   └── fixtures.py          # synthetic data
├── productive/
│   ├── routes.py            # 9 Productive endpoints
│   ├── fixtures.py          # synthetic data
│   └── jsonapi.py           # JSON:API serialization helpers
└── shims/
    ├── openai.py            # OpenAI SDK shim
    ├── resend.py            # Resend SDK shim (module-level api_key)
    └── slack.py             # Slack WebClient shim + SlackApiError class

tests/
├── conftest.py              # FastAPI TestClient fixture
├── test_server.py           # mounts + health
├── test_hubspot_routes.py   # 13 tests across 7 endpoints
├── test_productive_routes.py # 17 tests across 9 endpoints
├── test_jsonapi_helper.py   # 9 tests on serialization helpers
└── test_shims.py            # 17 tests across 3 SDK shims
```

## Critical design decisions

### 1. SDK shims have zero heavy dependencies

The SDK shims are pure-stdlib (just `dataclasses`, `logging`, `threading`, `uuid`, `time`). They do NOT depend on FastAPI or pydantic 2.x.

**Why this matters:** Pulse depends on `clerk-sdk-python` 0.1.0, which pins pydantic to 1.x. If the sandbox package required pydantic 2.x (via FastAPI), installing it in Pulse's venv would break Clerk auth.

So the package is split:
- **Default install** (`pip install pulse-sandbox-mocks`) — shims only, safe for Pulse's venv
- **Server extras** (`pip install pulse-sandbox-mocks[server]`) — adds FastAPI for the HTTP mock server, must be installed in a separate venv

### 2. Slack shim's `SlackApiError` inherits from the real one

The shim's `SlackApiError` class tries to inherit from `slack_sdk.errors.SlackApiError` (using a try/except so it falls back to plain `Exception` when slack_sdk isn't installed in the sandbox repo's standalone venv).

**Why:** Pulse's call sites do `except SlackApiError as e:` against the **real** slack_sdk class. If the shim's exception didn't inherit from the real one, a shim-raised exception would NOT be caught, and the talent-pipeline flow would crash instead of degrading gracefully.

This was discovered during Pulse-side regression testing and is the most subtle correctness requirement in the codebase.

### 3. Sample data uses Servant production custom-field IDs

Productive's `/people` and `/custom_fields` endpoints reference custom fields by numeric IDs (55149, 55151, 55153, 55147). Pulse's parser hard-codes these IDs to extract Employee Type, Deployable Team, % Allocation, and Discipline.

The sandbox fixtures use the same IDs. Otherwise Pulse would render every person as "unclassified."

If a future client deployment uses different custom field IDs, the sandbox fixtures would need to be parameterized. That's a Phase 2 item (currently out of scope).

### 4. Pagination via explicit-null `links.next`

Productive's JSON:API responses include `links.next` for pagination. Pulse's `paginate_get()` walks the chain by reading `body.get("links", {}).get("next")`.

The sandbox sets `links.next` to **explicit `None`** rather than omitting the field. Pulse's pagination terminates correctly only when the value is falsy — omitting the field would also work, but explicit `None` matches the real Productive API's behavior more closely.

### 5. In-memory state for stateful endpoints

The Slack shim's `WebClient` keeps a per-instance `_channels` dict so `conversations_create` followed by `conversations_invite` round-trips correctly within the same process. State resets on process restart.

For Phase 2, this could move to SQLite for cross-restart durability. Today that complexity isn't worth it — Pulse doesn't need durable state for a local-dev sandbox.

### 6. Health-check route at `app.py:160`

Pulse's health-check endpoint hits HubSpot directly with a hardcoded URL: `requests.get("https://api.hubapi.com/crm/v3/objects/deals", limit=1)`. The original code bypassed the `hubspot.py` shared client.

The sandbox refactor introduces `HUBSPOT_API_BASE` as the single source of truth for the HubSpot base URL. The health-check now uses this constant, so sandbox mode covers it without a separate code path.

The sandbox includes a `GET /hubspot/crm/v3/objects/deals` endpoint specifically to satisfy this health-check.

## How to extend

### Add a new HubSpot endpoint

1. Add a route handler in `pulse_sandbox/hubspot/routes.py` matching the path Pulse calls
2. If new sample data is needed, extend `pulse_sandbox/hubspot/fixtures.py`
3. Add tests in `tests/test_hubspot_routes.py` for the happy path and at least one edge case

### Add a new Productive endpoint

Same pattern as HubSpot, but use the `pulse_sandbox.productive.jsonapi` helpers (`make_resource`, `to_one_rel`, `to_many_rel`, `envelope`) to keep response shapes consistent. Don't hand-roll JSON:API objects.

### Add a new SDK shim

1. Create `pulse_sandbox/shims/<service>.py` mirroring the vendor SDK's surface for the methods Pulse actually calls
2. Add a factory function in Pulse's `backend/api/services/_sandbox_factory.py` that returns the shim or the real SDK based on the env var
3. Refactor Pulse's call sites to go through the factory
4. Add tests in `tests/test_shims.py` (sandbox repo) and `tests/test_sandbox_factory.py` (Pulse repo)

### Update fixture data

Edit the `fixtures.py` files directly. There's no JSON loading layer in Phase 1 — sample data is Python dicts, version-controlled with the code.

For larger or anonymized-real datasets, Phase 2 will add a JSON loader keyed on env var (e.g., `PULSE_SANDBOX_FIXTURES_DIR`).

## Performance characteristics

The full test suite (59 tests) runs in **~80ms**. Mock endpoints respond in **<1ms**. The sandbox is fast enough that running it during local dev adds zero perceptible latency vs. live API calls (which are typically 100-500ms).

## What this is NOT

- **Not a security boundary.** The sandbox accepts any token. Don't run it on a public network.
- **Not an integration test.** It tests Pulse's *response-parsing* layer; it does NOT test the *contract* with the real APIs. If HubSpot changes a response shape, Pulse will pass against the sandbox but fail against production. Real-API integration tests are a separate concern (out of scope).
- **Not a load-test fixture.** All state is in-memory; running thousands of concurrent requests will saturate a single Python process.
