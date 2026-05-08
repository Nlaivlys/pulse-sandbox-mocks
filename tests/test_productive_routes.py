"""Tests for Productive mock routes — covers all 9 endpoints + JSON:API shape."""

from __future__ import annotations

from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# /ping (health check)
# ---------------------------------------------------------------------------
def test_ping(client: TestClient) -> None:
    resp = client.get("/productive/api/v2/ping")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# JSON:API envelope shape — every list endpoint must return data + links
# ---------------------------------------------------------------------------
def test_envelope_has_data_and_links(client: TestClient) -> None:
    resp = client.get("/productive/api/v2/people")
    body = resp.json()
    assert "data" in body
    assert "links" in body
    assert "next" in body["links"]
    # Pulse's pagination loop checks `links.next` — must be explicit None when no more pages
    assert body["links"]["next"] is None


# ---------------------------------------------------------------------------
# /people
# ---------------------------------------------------------------------------
def test_list_people(client: TestClient) -> None:
    resp = client.get("/productive/api/v2/people")
    body = resp.json()
    assert len(body["data"]) >= 5
    person = body["data"][0]
    assert person["type"] == "people"
    attrs = person["attributes"]
    assert "first_name" in attrs and "last_name" in attrs and "email" in attrs
    # Custom fields with Servant-production IDs
    assert "55149" in attrs["custom_fields"]  # Employee Type
    assert "55153" in attrs["custom_fields"]  # % Allocation


def test_list_people_with_teams_include(client: TestClient) -> None:
    resp = client.get("/productive/api/v2/people", params={"include": "teams"})
    body = resp.json()
    assert "included" in body
    # All included items should be teams
    assert all(item["type"] == "teams" for item in body["included"])


# ---------------------------------------------------------------------------
# /teams
# ---------------------------------------------------------------------------
def test_list_teams(client: TestClient) -> None:
    resp = client.get("/productive/api/v2/teams")
    body = resp.json()
    assert len(body["data"]) >= 3
    assert {t["attributes"]["name"] for t in body["data"]} >= {"Engineering", "PMO", "Strategy"}


# ---------------------------------------------------------------------------
# /custom_fields
# ---------------------------------------------------------------------------
def test_custom_fields_with_options_include(client: TestClient) -> None:
    resp = client.get("/productive/api/v2/custom_fields", params={"include": "options"})
    body = resp.json()
    # Must include the 4 Servant-production field IDs Pulse depends on
    field_ids = {f["id"] for f in body["data"]}
    assert {"55149", "55151", "55153", "55147"}.issubset(field_ids)
    # Options sideloaded with proper relationship-back to the custom field
    assert len(body["included"]) > 0
    fte = next(o for o in body["included"] if o["id"] == "179224")
    assert fte["attributes"]["name"] == "FTE"
    assert fte["relationships"]["custom_field"]["data"]["id"] == "55149"


def test_custom_fields_without_options_no_included(client: TestClient) -> None:
    resp = client.get("/productive/api/v2/custom_fields")
    body = resp.json()
    # No include param → no sideload
    assert "included" not in body or body.get("included") in ([], None)


# ---------------------------------------------------------------------------
# /projects
# ---------------------------------------------------------------------------
def test_list_projects(client: TestClient) -> None:
    resp = client.get("/productive/api/v2/projects")
    body = resp.json()
    assert len(body["data"]) >= 3


def test_list_projects_with_company_include(client: TestClient) -> None:
    resp = client.get("/productive/api/v2/projects", params={"include": "company"})
    body = resp.json()
    # At least the active client projects have company relationships
    company_ids = {item["id"] for item in body["included"]}
    assert "501" in company_ids  # Acme Ministries


def test_list_projects_with_budget_include(client: TestClient) -> None:
    resp = client.get("/productive/api/v2/projects", params={"include": "budget"})
    body = resp.json()
    types = {item["type"] for item in body["included"]}
    assert "budgets" in types


def test_get_project_by_id(client: TestClient) -> None:
    resp = client.get("/productive/api/v2/projects/801", params={"include": "company,budget"})
    body = resp.json()
    assert body["data"]["id"] == "801"
    assert body["data"]["attributes"]["name"] == "Acme Ministries — Strategic Consulting"


# ---------------------------------------------------------------------------
# /bookings — multi-level include chain
# ---------------------------------------------------------------------------
def test_bookings_with_full_include_chain(client: TestClient) -> None:
    resp = client.get(
        "/productive/api/v2/bookings",
        params={"include": "person,service,service.deal,service.deal.project"},
    )
    body = resp.json()
    types = {item["type"] for item in body["included"]}
    # All four levels of the chain should be sideloaded
    assert {"people", "services", "deals", "projects"}.issubset(types)


# ---------------------------------------------------------------------------
# /deals
# ---------------------------------------------------------------------------
def test_list_deals(client: TestClient) -> None:
    resp = client.get("/productive/api/v2/deals")
    body = resp.json()
    assert len(body["data"]) >= 3
    # external_id is the bridge to HubSpot — must be present
    assert "external_id" in body["data"][0]["attributes"]


def test_list_deals_with_project_include(client: TestClient) -> None:
    resp = client.get("/productive/api/v2/deals", params={"include": "project"})
    body = resp.json()
    types = {item["type"] for item in body["included"]}
    assert "projects" in types


# ---------------------------------------------------------------------------
# /reports/budget_reports
# ---------------------------------------------------------------------------
def test_budget_reports_with_full_include(client: TestClient) -> None:
    resp = client.get(
        "/productive/api/v2/reports/budget_reports",
        params={"include": "project,budget,budget.company", "group_by": "project"},
    )
    body = resp.json()
    types = {item["type"] for item in body["included"]}
    assert {"projects", "budgets", "companies"}.issubset(types)
    # Budget amounts should be in cents (Pulse divides by 100 for dollars)
    first_report = body["data"][0]
    assert first_report["attributes"]["budget_total"] >= 100000  # at least $1k


# ---------------------------------------------------------------------------
# /reports/time_reports
# ---------------------------------------------------------------------------
def test_time_reports_id_format(client: TestClient) -> None:
    """Pulse parses time-report IDs by string split on `weekly-YYYY-MM-DD-person-{id}` format."""
    resp = client.get("/productive/api/v2/reports/time_reports")
    body = resp.json()
    for row in body["data"]:
        assert row["id"].startswith("weekly-")
        assert "-person-" in row["id"]


def test_time_reports_filter_by_date(client: TestClient) -> None:
    resp = client.get(
        "/productive/api/v2/reports/time_reports",
        params={"filter[after]": "2026-05-01", "filter[before]": "2026-05-31"},
    )
    body = resp.json()
    for row in body["data"]:
        assert row["attributes"]["date"] >= "2026-05-01"
        assert row["attributes"]["date"] <= "2026-05-31"


def test_time_reports_metrics_in_minutes(client: TestClient) -> None:
    resp = client.get("/productive/api/v2/reports/time_reports")
    body = resp.json()
    first = body["data"][0]
    attrs = first["attributes"]
    # Time fields must be in MINUTES (Pulse divides by 60 for hours)
    expected_metrics = {"worked_time", "client_time", "internal_time", "scheduled_billable_time", "capacity_time"}
    assert expected_metrics.issubset(attrs.keys())
