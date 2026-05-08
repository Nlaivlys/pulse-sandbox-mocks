"""pulse-sandbox CLI — `pulse-sandbox` console entrypoint."""

from __future__ import annotations

import argparse

import uvicorn


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="pulse-sandbox",
        description="Run the Pulse sandbox mock server",
    )
    parser.add_argument("--host", default="127.0.0.1", help="bind host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=9000, help="bind port (default: 9000)")
    parser.add_argument("--reload", action="store_true", help="auto-reload on code changes (dev)")
    args = parser.parse_args()

    print(f"pulse-sandbox starting at http://{args.host}:{args.port}")
    print(f"  HubSpot mock     -> http://{args.host}:{args.port}/hubspot/*")
    print(f"  Productive mock  -> http://{args.host}:{args.port}/productive/api/v2/*")
    print()

    uvicorn.run(
        "pulse_sandbox.server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
