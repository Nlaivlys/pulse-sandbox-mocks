"""Tests for HubSpot mock routes — covers all 7 endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# /crm/v3/owners
# ---------------------------------------------------------------------------
def test_list_owners_returns_results(client: TestClient) -> None:
    resp = client.get("/hubspot/crm/v3/owners")
    assert resp.status_code == 200
    body = resp.json()
    assert "results" in body
    assert len(body["results"]) >= 3
    first = body["results"][0]
    assert {"id", "firstName", "lastName", "email"}.issubset(first.keys())


def test_list_owners_paginates(client: TestClient) -> None:
    resp = client.get("/hubspot/crm/v3/owners", params={"limit": 1})
    body = resp.json()
    assert len(body["results"]) == 1
    assert "paging" in body
    assert body["paging"]["next"]["after"] == "1"


# ---------------------------------------------------------------------------
# /crm/v3/objects/deals (health-check fallback)
# ---------------------------------------------------------------------------
def test_list_deals_for_healthcheck(client: TestClient) -> None:
    resp = client.get("/hubspot/crm/v3/objects/deals", params={"limit": 1})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["results"]) == 1
    assert "id" in body["results"][0]


# ---------------------------------------------------------------------------
# POST /crm/v3/objects/deals/search
# ---------------------------------------------------------------------------
def test_search_deals_no_filters_returns_all(client: TestClient) -> None:
    resp = client.post("/hubspot/crm/v3/objects/deals/search", json={})
    body = resp.json()
    assert body["total"] == 8
    assert len(body["results"]) == 8


def test_search_deals_filter_high_confidence_open(client: TestClient) -> None:
    payload = {
        "filterGroups": [
            {"filters": [{"propertyName": "confidence", "operator": "EQ", "value": "High"}]},
            {"filters": [{"propertyName": "hs_is_closed", "operator": "EQ", "value": "false"}]},
        ],
    }
    resp = client.post("/hubspot/crm/v3/objects/deals/search", json=payload)
    body = resp.json()
    # Fixtures: 5 high-confidence open + 1 high-confidence closed-won
    # filterGroups are AND'd → only high-confidence AND not-closed = 5
    assert body["total"] == 5
    for deal in body["results"]:
        assert deal["properties"]["confidence"] == "High"
        assert deal["properties"]["hs_is_closed"] == "false"


def test_search_deals_property_projection(client: TestClient) -> None:
    payload = {"properties": ["dealname", "amount"], "limit": 2}
    resp = client.post("/hubspot/crm/v3/objects/deals/search", json=payload)
    body = resp.json()
    deal = body["results"][0]
    assert set(deal["properties"].keys()) == {"dealname", "amount"}


def test_search_deals_pagination_cursor(client: TestClient) -> None:
    payload = {"limit": 3}
    resp = client.post("/hubspot/crm/v3/objects/deals/search", json=payload)
    body = resp.json()
    assert len(body["results"]) == 3
    assert body["paging"]["next"]["after"] == "3"

    # Follow the cursor
    payload2 = {"limit": 3, "after": body["paging"]["next"]["after"]}
    resp2 = client.post("/hubspot/crm/v3/objects/deals/search", json=payload2)
    body2 = resp2.json()
    assert len(body2["results"]) == 3


# ---------------------------------------------------------------------------
# POST /crm/v4/associations/deals/companies/batch/read
# ---------------------------------------------------------------------------
def test_deal_company_batch_associations(client: TestClient) -> None:
    resp = client.post(
        "/hubspot/crm/v4/associations/deals/companies/batch/read",
        json={"inputs": [{"id": "9001"}, {"id": "9002"}]},
    )
    body = resp.json()
    assert body["status"] == "COMPLETE"
    assert len(body["results"]) == 2
    first = body["results"][0]
    assert first["from"]["id"] == "9001"
    assert first["to"][0]["toObjectId"] == 5001
    assert first["to"][0]["associationTypes"][0]["label"] == "Primary"


def test_deal_company_batch_associations_unknown_id_omitted(client: TestClient) -> None:
    resp = client.post(
        "/hubspot/crm/v4/associations/deals/companies/batch/read",
        json={"inputs": [{"id": "9001"}, {"id": "9999999"}]},
    )
    body = resp.json()
    # HubSpot omits unmatched inputs from results
    assert len(body["results"]) == 1
    assert body["results"][0]["from"]["id"] == "9001"


# ---------------------------------------------------------------------------
# POST /crm/v3/objects/companies/batch/read
# ---------------------------------------------------------------------------
def test_companies_batch_read(client: TestClient) -> None:
    resp = client.post(
        "/hubspot/crm/v3/objects/companies/batch/read",
        json={"properties": ["name"], "inputs": [{"id": "5001"}, {"id": "5002"}]},
    )
    body = resp.json()
    assert body["status"] == "COMPLETE"
    assert len(body["results"]) == 2
    first = body["results"][0]
    assert first["id"] == "5001"
    assert first["properties"]["name"] == "Acme Ministries"
    # Property projection should drop everything else
    assert set(first["properties"].keys()) == {"name"}


# ---------------------------------------------------------------------------
# /crm/v3/pipelines/deals
# ---------------------------------------------------------------------------
def test_list_pipelines(client: TestClient) -> None:
    resp = client.get("/hubspot/crm/v3/pipelines/deals")
    body = resp.json()
    assert len(body["results"]) >= 1
    pipeline = body["results"][0]
    assert pipeline["id"] == "default"
    assert len(pipeline["stages"]) >= 5
    closedwon = next(s for s in pipeline["stages"] if s["id"] == "closedwon")
    assert closedwon["metadata"]["isClosed"] == "true"


# ---------------------------------------------------------------------------
# /crm/v3/properties/deals
# ---------------------------------------------------------------------------
def test_list_deal_properties_includes_servant_custom(client: TestClient) -> None:
    resp = client.get("/hubspot/crm/v3/properties/deals")
    body = resp.json()
    names = {p["name"] for p in body["results"]}
    # Servant-custom props that Pulse depends on
    assert "confidence" in names
    assert "service_type" in names
    assert "engagement_start_date" in names


def test_confidence_property_has_high_low_options(client: TestClient) -> None:
    resp = client.get("/hubspot/crm/v3/properties/deals")
    body = resp.json()
    confidence = next(p for p in body["results"] if p["name"] == "confidence")
    values = {o["value"] for o in confidence["options"]}
    assert values == {"High", "Low"}
