"""Productive mock routes — 9 JSON:API endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from pulse_sandbox.productive import fixtures
from pulse_sandbox.productive.jsonapi import envelope

router = APIRouter()


def _filter_included(
    primary: list[dict],
    relationship_key: str,
    pool: list[dict],
    pool_type: str,
) -> list[dict]:
    """Pull related resources out of a pool for sideloading.

    Walks each primary resource's `relationships[relationship_key].data` and
    collects matching items from the pool into an `included` array.
    """
    wanted_ids: set[str] = set()
    for resource in primary:
        rel = resource.get("relationships", {}).get(relationship_key, {})
        data = rel.get("data")
        if data is None:
            continue
        if isinstance(data, list):
            for item in data:
                if item.get("type") == pool_type:
                    wanted_ids.add(item.get("id"))
        else:
            if data.get("type") == pool_type:
                wanted_ids.add(data.get("id"))

    return [item for item in pool if item.get("id") in wanted_ids]


# ---------------------------------------------------------------------------
# Health-check + simple list endpoints
# ---------------------------------------------------------------------------
@router.get("/ping")
async def ping() -> dict[str, Any]:
    return {"status": "ok"}


@router.get("/people")
async def list_people(
    include: str | None = Query(default=None),
    page_size: int = Query(default=200, alias="page[size]"),
) -> dict[str, Any]:
    included: list[dict] = []
    if include and "teams" in include:
        included = _filter_included(fixtures.PEOPLE, "teams", fixtures.TEAMS, "teams")
    return envelope(fixtures.PEOPLE, included=included)


@router.get("/teams")
async def list_teams(page_size: int = Query(default=200, alias="page[size]")) -> dict[str, Any]:
    return envelope(fixtures.TEAMS)


@router.get("/custom_fields")
async def list_custom_fields(
    include: str | None = Query(default=None),
    page_size: int = Query(default=200, alias="page[size]"),
) -> dict[str, Any]:
    included: list[dict] = []
    if include and "options" in include:
        included = fixtures.CUSTOM_FIELD_OPTIONS_INCLUDED
    return envelope(fixtures.CUSTOM_FIELDS, included=included)


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------
@router.get("/projects")
async def list_projects(
    include: str | None = Query(default=None),
    page_size: int = Query(default=200, alias="page[size]"),
) -> dict[str, Any]:
    included: list[dict] = []
    if include:
        if "company" in include:
            included.extend(_filter_included(fixtures.PROJECTS, "company", fixtures.COMPANIES, "companies"))
        if "budget" in include:
            # Budgets reference projects, not the other way around — find budgets whose project is in our list
            project_ids = {p["id"] for p in fixtures.PROJECTS}
            for b in fixtures.BUDGETS:
                rel_data = b.get("relationships", {}).get("project", {}).get("data")
                if rel_data and rel_data.get("id") in project_ids:
                    included.append(b)
    return envelope(fixtures.PROJECTS, included=included)


@router.get("/projects/{project_id}")
async def get_project(
    project_id: str,
    include: str | None = Query(default=None),
) -> dict[str, Any]:
    project = next((p for p in fixtures.PROJECTS if p["id"] == project_id), None)
    if project is None:
        return envelope(data=[])  # JSON:API would return 404; Pulse handles missing gracefully
    included: list[dict] = []
    if include:
        if "company" in include:
            included.extend(_filter_included([project], "company", fixtures.COMPANIES, "companies"))
        if "budget" in include:
            for b in fixtures.BUDGETS:
                if b.get("relationships", {}).get("project", {}).get("data", {}).get("id") == project_id:
                    included.append(b)
    return {"data": project, "included": included, "links": {"next": None}}


# ---------------------------------------------------------------------------
# Bookings — chain include: person, service, service.deal, service.deal.project
# ---------------------------------------------------------------------------
@router.get("/bookings")
async def list_bookings(
    include: str | None = Query(default=None),
    page_size: int = Query(default=200, alias="page[size]"),
) -> dict[str, Any]:
    included: list[dict] = []
    if include:
        parts = [p.strip() for p in include.split(",")]
        if "person" in parts:
            included.extend(_filter_included(fixtures.BOOKINGS, "person", fixtures.PEOPLE, "people"))
        if "service" in parts or any(p.startswith("service") for p in parts):
            included.extend(_filter_included(fixtures.BOOKINGS, "service", fixtures.SERVICES, "services"))
        if "service.deal" in parts or "service.deal.project" in parts:
            # Sideload deals referenced by services we just included
            services_in_play = [s for s in fixtures.SERVICES]
            included.extend(_filter_included(services_in_play, "deal", fixtures.DEALS, "deals"))
        if "service.deal.project" in parts:
            # Sideload projects referenced by deals
            included.extend(_filter_included(fixtures.DEALS, "project", fixtures.PROJECTS, "projects"))
    return envelope(fixtures.BOOKINGS, included=included)


# ---------------------------------------------------------------------------
# Deals (Productive CRM)
# ---------------------------------------------------------------------------
@router.get("/deals")
async def list_deals(
    include: str | None = Query(default=None),
    page_size: int = Query(default=200, alias="page[size]"),
) -> dict[str, Any]:
    included: list[dict] = []
    if include and "project" in include:
        included = _filter_included(fixtures.DEALS, "project", fixtures.PROJECTS, "projects")
    return envelope(fixtures.DEALS, included=included)


# ---------------------------------------------------------------------------
# Reports — budget_reports + time_reports
# ---------------------------------------------------------------------------
@router.get("/reports/budget_reports")
async def budget_reports(
    include: str | None = Query(default=None),
    group_by: str | None = Query(default=None),
    page_size: int = Query(default=200, alias="page[size]"),
    filter_status: str | None = Query(default=None, alias="filter[status]"),
    filter_after: str | None = Query(default=None, alias="filter[after]"),
    filter_before: str | None = Query(default=None, alias="filter[before]"),
) -> dict[str, Any]:
    included: list[dict] = []
    if include:
        parts = [p.strip() for p in include.split(",")]
        if "project" in parts:
            included.extend(_filter_included(fixtures.BUDGET_REPORTS, "project", fixtures.PROJECTS, "projects"))
        # The `budget` relationship from a budget_report points to a Productive
        # `deal` (deals double as budgets in Productive's data model). Sideload
        # the matching deals — Pulse parses these to resolve project + company.
        if "budget" in parts or any(p.startswith("budget.") for p in parts):
            included.extend(_filter_included(fixtures.BUDGET_REPORTS, "budget", fixtures.DEALS, "deals"))
        if "budget.project" in parts:
            included.extend(_filter_included(fixtures.DEALS, "project", fixtures.PROJECTS, "projects"))
        if "budget.company" in parts:
            included.extend(_filter_included(fixtures.DEALS, "company", fixtures.COMPANIES, "companies"))
    return envelope(fixtures.BUDGET_REPORTS, included=included)


@router.get("/reports/time_reports")
async def time_reports(
    metrics: str | None = Query(default=None),
    group_by: str | None = Query(default=None),
    page_size: int = Query(default=200, alias="page[size]"),
    filter_after: str | None = Query(default=None, alias="filter[after]"),
    filter_before: str | None = Query(default=None, alias="filter[before]"),
) -> dict[str, Any]:
    rows = fixtures.TIME_REPORTS
    # Apply rough date filtering if provided
    if filter_after:
        rows = [r for r in rows if r["attributes"]["date"] >= filter_after]
    if filter_before:
        rows = [r for r in rows if r["attributes"]["date"] <= filter_before]
    return envelope(rows)


# ---------------------------------------------------------------------------
# Scenarios — Pulse hits this to count scenarios per deal
# (api/routes/hubspot.py:220 — get_high_confidence_deals)
# ---------------------------------------------------------------------------
@router.get("/scenarios")
async def list_scenarios(
    filter_deal_id: str | None = Query(default=None, alias="filter[deal_id]"),
    page_size: int = Query(default=200, alias="page[size]"),
) -> dict[str, Any]:
    """Mock GET /scenarios with optional filter[deal_id].

    Pulse uses this with `filter[deal_id]={id}&page[size]=1` and counts the
    `data` array length to decide whether a deal has scenarios.
    """
    rows = fixtures.SCENARIOS
    if filter_deal_id:
        rows = [
            s for s in rows
            if s.get("relationships", {}).get("deal", {}).get("data", {}).get("id") == filter_deal_id
        ]
    return envelope(rows[:page_size])


# ---------------------------------------------------------------------------
# Saved custom report — `/reports/{report_id}` and `/reports/{report_id}/budgets`
#
# Pulse code (and the legacy tests/test_saved_report_endpoint.py probe) accesses
# the Client Engagement Utilization Report via env var CLIENT_ENG_UTIL_REPORT_ID
# (default "1591877"). Both URL paths return budget-shaped data with company +
# project sideloads, mirroring `/reports/budget_reports` but pre-filtered by
# the saved view configured in Productive.
#
# Note: route ordering matters in FastAPI. /reports/{report_id}/budgets MUST be
# declared before /reports/{report_id} so the more specific path wins.
# ---------------------------------------------------------------------------
def _saved_report_response(include: str | None) -> dict[str, Any]:
    included: list[dict] = []
    if include:
        parts = [p.strip() for p in include.split(",")]
        if "company" in parts:
            included.extend(
                _filter_included(fixtures.SAVED_REPORT_BUDGETS, "company", fixtures.COMPANIES, "companies")
            )
        if "project" in parts:
            included.extend(
                _filter_included(fixtures.SAVED_REPORT_BUDGETS, "project", fixtures.PROJECTS, "projects")
            )
    return envelope(fixtures.SAVED_REPORT_BUDGETS, included=included)


@router.get("/reports/{report_id}/budgets")
async def saved_report_budgets(
    report_id: str,
    include: str | None = Query(default=None),
    page_size: int = Query(default=200, alias="page[size]"),
) -> dict[str, Any]:
    """Mock GET /reports/{report_id}/budgets — legacy path for saved reports."""
    if report_id != fixtures.CLIENT_ENG_UTIL_REPORT_ID:
        raise HTTPException(
            status_code=404,
            detail=f"saved report {report_id} not found in sandbox",
        )
    return _saved_report_response(include)


@router.get("/reports/{report_id}")
async def saved_report(
    report_id: str,
    include: str | None = Query(default=None),
    page_size: int = Query(default=200, alias="page[size]"),
) -> dict[str, Any]:
    """Mock GET /reports/{report_id} — modern path for saved reports."""
    if report_id != fixtures.CLIENT_ENG_UTIL_REPORT_ID:
        raise HTTPException(
            status_code=404,
            detail=f"saved report {report_id} not found in sandbox",
        )
    return _saved_report_response(include)
