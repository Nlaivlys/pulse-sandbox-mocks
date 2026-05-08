"""Shared pytest fixtures for sandbox tests."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from pulse_sandbox.server import app


@pytest.fixture
def client() -> TestClient:
    """FastAPI TestClient bound to the sandbox app — no real network."""
    return TestClient(app)
