"""FastAPI mock server — mounts HubSpot + Productive routers under path prefixes."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from pulse_sandbox.hubspot.routes import router as hubspot_router
from pulse_sandbox.productive.routes import router as productive_router

app = FastAPI(
    title="Pulse Sandbox Mocks",
    description="Local mock servers for Pulse external API dependencies",
    version="0.1.0",
)


@app.get("/")
def root() -> dict:
    return {
        "service": "pulse-sandbox-mocks",
        "version": "0.1.0",
        "mounts": {
            "hubspot": "/hubspot/*  (mocks api.hubapi.com)",
            "productive": "/productive/api/v2/*  (mocks api.productive.io/api/v2)",
        },
        "usage": "Set HUBSPOT_API_BASE=http://localhost:9000/hubspot and PRODUCTIVE_API_BASE=http://localhost:9000/productive/api/v2 in Pulse's .env",
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


# Mount HubSpot under /hubspot — Pulse will set HUBSPOT_API_BASE=http://localhost:9000/hubspot
# so a Pulse call to {HUBSPOT_API_BASE}/crm/v3/objects/deals/search hits /hubspot/crm/v3/objects/deals/search here.
app.include_router(hubspot_router, prefix="/hubspot", tags=["hubspot"])

# Mount Productive under /productive/api/v2 — mirrors Productive's real base path
# so a Pulse call to {PRODUCTIVE_API_BASE}/people hits /productive/api/v2/people here.
app.include_router(productive_router, prefix="/productive/api/v2", tags=["productive"])
