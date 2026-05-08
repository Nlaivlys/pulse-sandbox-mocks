# Contributing

> How to set up `pulse-sandbox-mocks` for development.

## Dev setup

```bash
git clone https://github.com/Nlaivlys/pulse-sandbox-mocks.git
cd pulse-sandbox-mocks
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[server,dev]"
```

The `[server]` extras add FastAPI + uvicorn (needed to run the mock server). The `[dev]` extras add pytest + httpx (needed to run the test suite).

> **Don't install `[server]` extras into Pulse's venv** — FastAPI pulls in pydantic 2.x, which conflicts with Pulse's `clerk-sdk-python` 0.1.0 (requires pydantic 1.x). For Pulse's venv, install just `pip install -e .` (shims only).

## Run tests

```bash
pytest                 # full suite (~80ms)
pytest -v              # verbose
pytest --cov           # with coverage report
pytest tests/test_hubspot_routes.py -k confidence  # filter by name
```

The coverage gate is set to **80%** in `pyproject.toml`. Currently at 92%.

## Run the mock server

```bash
pulse-sandbox          # binds to 127.0.0.1:9000

# With auto-reload during development:
bash scripts/start.sh

# Or directly:
python -m uvicorn pulse_sandbox.server:app --host 127.0.0.1 --port 9000 --reload
```

## Adding a new endpoint

See `docs/ARCHITECTURE.md` § "How to extend" for the per-service patterns.

Checklist:
- [ ] Route handler in `pulse_sandbox/{service}/routes.py`
- [ ] Sample data in `pulse_sandbox/{service}/fixtures.py` (if new entity types)
- [ ] Test in `tests/test_{service}_routes.py` covering happy path
- [ ] Test for at least one error/edge case
- [ ] Verify coverage stays above 80%

## Adding a new SDK shim

Checklist:
- [ ] Shim module in `pulse_sandbox/shims/{service}.py`
- [ ] Export from `pulse_sandbox/shims/__init__.py`
- [ ] Tests in `tests/test_shims.py`
- [ ] Add a factory function in **Pulse's** `backend/api/services/_sandbox_factory.py`
- [ ] Refactor Pulse call sites to use the factory
- [ ] Add tests in **Pulse's** `backend/tests/test_sandbox_factory.py` covering live mode, sandbox mode, and ImportError fallback

## Code style

- Python 3.9+ supported (Pulse runs on 3.9 — Railway constraint)
- `from __future__ import annotations` at the top of every module to allow PEP-604 union syntax (`str | None`) on 3.9
- 4-space indentation, no tabs
- Docstrings on public functions and classes
- Type hints on all public function signatures

No formatter is enforced in v0.1. Hand-format to match existing files.

## Conventional Commits

Per Sylvia's project rules:

```
<type>(scope): <description>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`, `build`.

Subject line ≤ 50 chars. Body explains the *why* (not the *what*). Reference issues when applicable.

## Pull requests

For now this is a one-developer project (Sylvia). Open an issue first to discuss any non-trivial change.

When PRs become a thing:
1. Branch from `main` with `feat/`, `fix/`, or `docs/` prefix
2. Tests pass + coverage gate met
3. CHANGELOG.md updated under `## [Unreleased]`
4. Squash-merge by default

## Releasing

For now: bump `__version__` in `pulse_sandbox/__init__.py` and `version` in `pyproject.toml`, update CHANGELOG.md, tag in git. No PyPI release yet.
