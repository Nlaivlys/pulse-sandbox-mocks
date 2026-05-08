"""Productive mock routes — 9 JSON:API endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

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
        if "budget" in parts or "budget.company" in parts:
            included.extend(_filter_included(fixtures.BUDGET_REPORTS, "budget", fixtures.BUDGETS, "budgets"))
        if "budget.company" in parts:
            # Companies referenced by budgets
            included.extend(_filter_included(fixtures.BUDGETS, "company", fixtures.COMPANIES, "companies"))
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
