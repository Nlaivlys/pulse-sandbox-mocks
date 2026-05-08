#!/usr/bin/env bash
# Run the Pulse sandbox mock server with auto-reload.
set -euo pipefail

cd "$(dirname "$0")/.."
exec python -m uvicorn pulse_sandbox.server:app --host 127.0.0.1 --port 9000 --reload
