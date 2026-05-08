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
    """Sideload chain: budget_reports → deals (via budget rel) → project + company.

    Pulse's parser at api/routes/resources.py:286-326 looks for `deals` in
    `included` (not `budgets`) — Productive treats deals as budgets in this
    response. The deal's project + company relationships then resolve names.
    """
    resp = client.get(
        "/productive/api/v2/reports/budget_reports",
        params={"include": "budget,budget.project,budget.company", "group_by": "budget"},
    )
    body = resp.json()
    types = {item["type"] for item in body["included"]}
    assert {"deals", "projects", "companies"}.issubset(types), (
        f"included must contain deals/projects/companies; got {types}"
    )
    # Budget rows must expose Pulse's expected attribute names
    first_report = body["data"][0]
    attrs = first_report["attributes"]
    assert "average_budget_usage" in attrs, "Pulse skips rows missing average_budget_usage"
    assert "total_budget_total" in attrs and attrs["total_budget_total"] >= 100000  # cents
    assert "total_budget_used" in attrs


def test_budget_reports_two_thirds_pass_50pct_filter(client: TestClient) -> None:
    """Tuned utilizations: 65% / 70% / 20% — the >=50% filter should yield 2 rows."""
    resp = client.get(
        "/productive/api/v2/reports/budget_reports",
        params={"include": "budget,budget.project,budget.company", "group_by": "budget"},
    )
    body = resp.json()
    over_50 = [
        r for r in body["data"]
        if float(r["attributes"]["average_budget_usage"]) >= 50.0
    ]
    assert len(over_50) == 2, f"expected 2 budgets >=50%, got {len(over_50)}"


def test_budget_reports_deal_relationships_resolve_to_company(client: TestClient) -> None:
    """Verify the sideloaded deals carry both `project` and `company` rels —
    Pulse needs both to populate company_name on the engagement."""
    resp = client.get(
        "/productive/api/v2/reports/budget_reports",
        params={"include": "budget,budget.project,budget.company"},
    )
    body = resp.json()
    deals_in_included = [item for item in body["included"] if item["type"] == "deals"]
    assert len(deals_in_included) >= 3
    for deal in deals_in_included:
        rels = deal.get("relationships", {})
        assert "project" in rels, f"deal {deal['id']} missing project relationship"
        assert "company" in rels, f"deal {deal['id']} missing company relationship"


# ---------------------------------------------------------------------------
# /reports/time_reports
# ---------------------------------------------------------------------------
def test_time_reports_id_format(client: TestClient) -> None:
    """Pulse's strict parser at resource_dashboard.py:307 splits the id on '-'
    and rejects records where parts[2] != 'person'. The id must be:
        time-report-person-{person_id}-{compact_date}
    so split gives parts[0]='time' parts[1]='report' parts[2]='person' parts[3]={id}.
    Date is compacted (no dashes) so it doesn't pollute the split."""
    resp = client.get("/productive/api/v2/reports/time_reports")
    body = resp.json()
    for row in body["data"]:
        parts = row["id"].split("-")
        assert len(parts) >= 4, f"id must have ≥4 dash-separated parts: {row['id']}"
        assert parts[2] == "person", f"parts[2] must be 'person': {row['id']}"
        # parts[3] is the person_id and must match the relationship
        rel_person_id = row["relationships"]["person"]["data"]["id"]
        assert parts[3] == rel_person_id


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


# ---------------------------------------------------------------------------
# /scenarios — Pulse hits this from api/routes/hubspot.py:220 to count
# scenarios per HC deal. Pulse only checks `len(data) > 0`; sandbox just
# needs to return shape-correct rows filtered by deal_id.
# ---------------------------------------------------------------------------
def test_scenarios_no_filter_returns_all(client: TestClient) -> None:
    resp = client.get("/productive/api/v2/scenarios")
    body = resp.json()
    assert len(body["data"]) >= 4
    assert body["data"][0]["type"] == "scenarios"


def test_scenarios_filter_by_deal_id_returns_subset(client: TestClient) -> None:
    """Pulse uses filter[deal_id]=601&page[size]=1 to count scenarios per deal."""
    resp = client.get(
        "/productive/api/v2/scenarios", params={"filter[deal_id]": "601", "page[size]": 1}
    )
    body = resp.json()
    # Deal 601 has 2 scenarios in fixtures, but page[size]=1 caps the response
    assert len(body["data"]) == 1
    rel = body["data"][0]["relationships"]["deal"]["data"]
    assert rel["id"] == "601"


def test_scenarios_filter_unknown_deal_returns_empty(client: TestClient) -> None:
    """Pulse counts len(data) — empty array means deal has no scenarios."""
    resp = client.get(
        "/productive/api/v2/scenarios", params={"filter[deal_id]": "9999999"}
    )
    body = resp.json()
    assert body["data"] == []


# ---------------------------------------------------------------------------
# Saved custom report — /reports/{report_id} and /reports/{report_id}/budgets
# Pulse references this via env var CLIENT_ENG_UTIL_REPORT_ID (default 1591877)
# ---------------------------------------------------------------------------
def test_saved_report_budgets_legacy_path(client: TestClient) -> None:
    resp = client.get(
        "/productive/api/v2/reports/1591877/budgets",
        params={"page[size]": 200, "include": "company,project"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["data"]) >= 3
    # Pulse parses budget_total + budget_used in cents
    first = body["data"][0]
    assert "budget_total" in first["attributes"]
    assert "budget_used" in first["attributes"]
    # Sideloads
    types = {item["type"] for item in body["included"]}
    assert {"companies", "projects"}.issubset(types)


def test_saved_report_modern_path(client: TestClient) -> None:
    resp = client.get(
        "/productive/api/v2/reports/1591877",
        params={"page[size]": 200, "include": "company,project"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["data"]) >= 3


def test_saved_report_unknown_id_returns_404(client: TestClient) -> None:
    resp = client.get("/productive/api/v2/reports/9999999")
    assert resp.status_code == 404


def test_saved_report_data_has_50pct_utilization_examples(client: TestClient) -> None:
    """The report's purpose is to surface budgets >= 50% utilization. Sandbox
    fixtures include at least one budget at >=50% so Pulse's filter renders
    a non-empty result."""
    resp = client.get("/productive/api/v2/reports/1591877/budgets")
    body = resp.json()
    over_50 = [
        b for b in body["data"]
        if b["attributes"]["budget_total"]
        and (b["attributes"]["budget_used"] / b["attributes"]["budget_total"]) >= 0.5
    ]
    assert len(over_50) >= 1, "fixtures should include >=1 budget at >=50% utilization"


def test_pre_existing_budget_reports_endpoint_still_works(client: TestClient) -> None:
    """Regression guard: /reports/budget_reports must still match its specific
    handler, not be captured by the new /reports/{report_id} parametric route."""
    resp = client.get("/productive/api/v2/reports/budget_reports")
    assert resp.status_code == 200
    body = resp.json()
    # budget_reports endpoint returns budget_reports type, not budgets
    assert body["data"][0]["type"] == "budget_reports"


def test_pre_existing_time_reports_endpoint_still_works(client: TestClient) -> None:
    """Regression guard: /reports/time_reports must still match its specific
    handler, not be captured by the new /reports/{report_id} parametric route."""
    resp = client.get("/productive/api/v2/reports/time_reports")
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"][0]["type"] == "time_reports"
