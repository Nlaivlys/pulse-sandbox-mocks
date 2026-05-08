"""HubSpot mock routes — 6 endpoints + 1 health-check fallback."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request

from pulse_sandbox.hubspot.fixtures import (
    COMPANIES,
    DEAL_COMPANY_ASSOCIATIONS,
    DEAL_PROPERTIES,
    DEALS,
    OWNERS,
    PIPELINES,
)

router = APIRouter()


def _matches_filter(deal: dict, propertyName: str, operator: str, value: str | None) -> bool:
    """Tiny filter evaluator covering the operators Pulse actually uses."""
    actual = deal["properties"].get(propertyName, "")
    if operator == "EQ":
        return actual == value
    if operator == "NEQ":
        return actual != value
    if operator == "HAS_PROPERTY":
        return actual not in ("", None)
    if operator == "NOT_HAS_PROPERTY":
        return actual in ("", None)
    # Default: match anything (sandbox is forgiving — real HubSpot would error)
    return True


@router.post("/crm/v3/objects/deals/search")
async def search_deals(request: Request) -> dict[str, Any]:
    """Mock POST /crm/v3/objects/deals/search.

    Pulse uses this with filterGroups (AND-of-OR) on `confidence`, `hs_is_closed`, `pipeline`.
    Returns search results in {results, total, paging?} shape.
    """
    body = await request.json()
    filter_groups = body.get("filterGroups", [])
    requested_props = body.get("properties", [])
    limit = int(body.get("limit", 100))
    after = body.get("after")

    matched = []
    for deal in DEALS:
        # filterGroups semantics: each group is an OR of filters; groups themselves are ANDed.
        # If no groups, match all.
        if not filter_groups:
            matched.append(deal)
            continue

        all_groups_pass = True
        for group in filter_groups:
            filters = group.get("filters", [])
            if not filters:
                continue  # empty group passes
            group_pass = any(
                _matches_filter(deal, f.get("propertyName", ""), f.get("operator", "EQ"), f.get("value"))
                for f in filters
            )
            if not group_pass:
                all_groups_pass = False
                break

        if all_groups_pass:
            matched.append(deal)

    # Apply 'after' cursor (offset-based for simplicity)
    start_index = int(after) if after else 0
    page = matched[start_index : start_index + limit]
    total = len(matched)

    # Build response — only include requested properties if specified
    def _project(deal: dict) -> dict:
        if not requested_props:
            return deal
        projected_props = {k: v for k, v in deal["properties"].items() if k in requested_props}
        return {**deal, "properties": projected_props}

    response: dict[str, Any] = {
        "total": total,
        "results": [_project(d) for d in page],
    }

    next_after = start_index + limit
    if next_after < total:
        response["paging"] = {"next": {"after": str(next_after), "link": ""}}

    return response


@router.get("/crm/v3/objects/deals")
async def list_deals(limit: int = Query(default=100), after: str | None = Query(default=None)) -> dict[str, Any]:
    """Mock GET /crm/v3/objects/deals — used by app.py:160 health-check (limit=1)."""
    start_index = int(after) if after else 0
    page = DEALS[start_index : start_index + limit]
    response: dict[str, Any] = {"results": page}
    next_after = start_index + limit
    if next_after < len(DEALS):
        response["paging"] = {"next": {"after": str(next_after), "link": ""}}
    return response


@router.get("/crm/v3/owners")
async def list_owners(limit: int = Query(default=100), after: str | None = Query(default=None)) -> dict[str, Any]:
    """Mock GET /crm/v3/owners."""
    start_index = int(after) if after else 0
    page = OWNERS[start_index : start_index + limit]
    response: dict[str, Any] = {"results": page}
    next_after = start_index + limit
    if next_after < len(OWNERS):
        response["paging"] = {"next": {"after": str(next_after), "link": ""}}
    return response


@router.post("/crm/v4/associations/deals/companies/batch/read")
async def batch_read_deal_company_associations(request: Request) -> dict[str, Any]:
    """Mock POST /crm/v4/associations/deals/companies/batch/read.

    Body: {"inputs": [{"id": "9001"}, ...]}
    Returns: {"status": "COMPLETE", "results": [{"from": {"id": "9001"}, "to": [{"toObjectId": "5001", ...}]}]}
    """
    body = await request.json()
    inputs = body.get("inputs", [])
    results = []
    for inp in inputs:
        deal_id = str(inp.get("id"))
        company_id = DEAL_COMPANY_ASSOCIATIONS.get(deal_id)
        if company_id is None:
            # HubSpot omits unmatched inputs from results
            continue
        results.append(
            {
                "from": {"id": deal_id},
                "to": [
                    {
                        "toObjectId": int(company_id),
                        "associationTypes": [
                            {
                                "category": "HUBSPOT_DEFINED",
                                "typeId": 5,
                                "label": "Primary",
                            }
                        ],
                    }
                ],
            }
        )
    return {
        "status": "COMPLETE",
        "results": results,
        "startedAt": "2026-05-08T10:00:00.000Z",
        "completedAt": "2026-05-08T10:00:00.100Z",
    }


@router.post("/crm/v3/objects/companies/batch/read")
async def batch_read_companies(request: Request) -> dict[str, Any]:
    """Mock POST /crm/v3/objects/companies/batch/read.

    Body: {"properties": ["name"], "inputs": [{"id": "5001"}, ...]}
    Returns: {"status": "COMPLETE", "results": [{"id": "5001", "properties": {"name": "..."}, ...}]}
    """
    body = await request.json()
    inputs = body.get("inputs", [])
    requested_props = body.get("properties", [])
    company_by_id = {c["id"]: c for c in COMPANIES}

    results = []
    for inp in inputs:
        cid = str(inp.get("id"))
        company = company_by_id.get(cid)
        if company is None:
            continue
        if requested_props:
            projected = {k: v for k, v in company["properties"].items() if k in requested_props}
            results.append({**company, "properties": projected})
        else:
            results.append(company)

    return {
        "status": "COMPLETE",
        "results": results,
        "startedAt": "2026-05-08T10:00:00.000Z",
        "completedAt": "2026-05-08T10:00:00.100Z",
    }


@router.get("/crm/v3/pipelines/deals")
async def list_pipelines() -> dict[str, Any]:
    """Mock GET /crm/v3/pipelines/deals — returns pipeline definitions with stages."""
    return {"results": PIPELINES}


@router.get("/crm/v3/properties/deals")
async def list_deal_properties() -> dict[str, Any]:
    """Mock GET /crm/v3/properties/deals — returns custom property metadata for admin UI."""
    return {"results": DEAL_PROPERTIES}
