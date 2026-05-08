"""Tests for the FastAPI app root + health-check + mount points."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_root_describes_mounts(client: TestClient) -> None:
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["service"] == "pulse-sandbox-mocks"
    assert "hubspot" in body["mounts"]
    assert "productive" in body["mounts"]


def test_health(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_unknown_path_404s(client: TestClient) -> None:
    resp = client.get("/this-path-does-not-exist")
    assert resp.status_code == 404
