"""Rich profile — extends baseline with deliberately-tuned scenario deals.

Each deal in EXTRA_HS_DEALS is pinned to a specific Pulse warning or
behavior we want to exercise during local development:

| Deal  | Scenario       | Triggers                                           |
|-------|----------------|----------------------------------------------------|
| 9101  | OVERDUE-OPEN   | open + closedate 7 days in past → "Need Date Update" warning |
| 9102  | STUCK-STAGE    | open + 60d in same stage + lastmodified=createdate → staleness signal |
| 9103  | ORPHAN         | open + missing engagement_lead_name + service_type → data-quality alert |
| 9104  | JUST-CREATED   | createdate=today → freshness signal in pipeline analytics |
| 9105  | RECENT-WIN     | closedwon + closedate yesterday → recently-won pipeline accumulation |

Productive scenario coverage is asymmetric on purpose: only 9102 has a
scenario, so the "Missing Productive Scenarios" warning fires for 4 of
the 5 new deals (mirrors the baseline behavior where most HC deals lack
Productive scenarios).

Activate via:
    PULSE_SANDBOX_PROFILE=rich
"""

from __future__ import annotations

from datetime import timedelta

from pulse_sandbox.profiles.baseline import (  # noqa: F401  (re-exported)
    HUBSPOT_OWNERS as _BASE_HS_OWNERS,
    HUBSPOT_COMPANIES as _BASE_HS_COMPANIES,
    HUBSPOT_DEALS as _BASE_HS_DEALS,
    HUBSPOT_DEAL_COMPANY_ASSOC as _BASE_ASSOC,
    HUBSPOT_PIPELINES,
    HUBSPOT_PIPELINE_STAGES,
    HUBSPOT_DEAL_PROPERTIES,
    PRODUCTIVE_PEOPLE,
    PRODUCTIVE_TEAMS,
    PRODUCTIVE_COMPANIES,
    PRODUCTIVE_PROJECTS,
    PRODUCTIVE_BUDGETS,
    PRODUCTIVE_DEALS,
    PRODUCTIVE_SERVICES,
    PRODUCTIVE_BOOKINGS,
    PRODUCTIVE_TIME_REPORTS,
    PRODUCTIVE_BUDGET_REPORTS,
    PRODUCTIVE_CUSTOM_FIELDS,
    PRODUCTIVE_CUSTOM_FIELD_OPTIONS_INCLUDED,
    PRODUCTIVE_SCENARIOS as _BASE_PROD_SCENARIOS,
    PRODUCTIVE_SAVED_REPORT_BUDGETS,
    PRODUCTIVE_CLIENT_ENG_UTIL_REPORT_ID,
    _NOW,
    _iso,
    _deal_props,
)


# ---------------------------------------------------------------------------
# New HubSpot company for the orphan-deal scenario (9103)
# ---------------------------------------------------------------------------
_EXTRA_HS_COMPANIES = [
    {
        "id": "5005",
        "properties": {
            "name": "Echo Foundation",
            "domain": "echofoundation.example",
            "createdate": "2025-12-01T00:00:00Z",
            "hs_lastmodifieddate": _iso(_NOW - timedelta(days=2)),
        },
        "createdAt": "2025-12-01T00:00:00Z",
        "updatedAt": _iso(_NOW - timedelta(days=2)),
        "archived": False,
    },
]


# ---------------------------------------------------------------------------
# Scenario deals — each pinned to a specific Pulse signal or warning
# ---------------------------------------------------------------------------
_EXTRA_HS_DEALS = [
    # 9101 — OVERDUE-OPEN: open deal whose closedate is in the past
    {
        "id": "9101",
        "properties": _deal_props(
            name="Acme Ministries — Overdue Engagement",
            amount="48000",
            stage="contractsent",
            confidence="High",
            owner="111111",
            service_type="Strategic Consulting",
            start="2026-03-01",
            end="2026-08-30",
            lead="Alex Morgan",
            priority="HIGH",
            next_step="Awaiting client signature — 7 days overdue",
            description="High-confidence contract with closedate in the past — needs HubSpot update",
            closedate=_iso(_NOW - timedelta(days=7)),
            createdate=_iso(_NOW - timedelta(days=45)),
        ),
        "createdAt": _iso(_NOW - timedelta(days=45)),
        "updatedAt": _iso(_NOW - timedelta(days=2)),
        "archived": False,
    },
    # 9102 — STUCK-STAGE: 60d in same stage, lastmodified == createdate
    {
        "id": "9102",
        "properties": _deal_props(
            name="Bright Horizon — Stuck in Negotiation",
            amount="72000",
            stage="qualifiedtobuy",
            confidence="High",
            owner="222222",
            service_type="AI Support",
            start="2026-08-01",
            end="2027-01-31",
            lead="Jordan Rivera",
            priority="MEDIUM",
            next_step="Awaiting feedback from client legal",
            description="Has not advanced since createdate — staleness signal",
            closedate=_iso(_NOW + timedelta(days=20)),
            createdate=_iso(_NOW - timedelta(days=60)),
        ),
        "createdAt": _iso(_NOW - timedelta(days=60)),
        "updatedAt": _iso(_NOW - timedelta(days=60)),
        "archived": False,
    },
    # 9103 — ORPHAN: missing engagement_lead_name + service_type
    {
        "id": "9103",
        "properties": _deal_props(
            name="Echo Foundation — Discovery (Untagged)",
            amount="18000",
            stage="appointmentscheduled",
            confidence="High",
            owner="333333",
            service_type="",
            start="",
            end="",
            lead="",
            priority="LOW",
            description="Data quality test: no service_type, no engagement_lead",
            closedate=_iso(_NOW + timedelta(days=40)),
            createdate=_iso(_NOW - timedelta(days=15)),
        ),
        "createdAt": _iso(_NOW - timedelta(days=15)),
        "updatedAt": _iso(_NOW - timedelta(days=4)),
        "archived": False,
    },
    # 9104 — JUST-CREATED: createdate today, no movement yet
    {
        "id": "9104",
        "properties": _deal_props(
            name="Cedar Valley — New Inbound Inquiry",
            amount="22000",
            stage="appointmentscheduled",
            confidence="Low",
            owner="333333",
            service_type="Strategic Consulting",
            start="",
            end="",
            lead="Casey Lin",
            priority="LOW",
            description="Fresh inbound — created today, no movement",
            closedate=_iso(_NOW + timedelta(days=90)),
            createdate=_iso(_NOW),
        ),
        "createdAt": _iso(_NOW),
        "updatedAt": _iso(_NOW),
        "archived": False,
    },
    # 9105 — RECENT-WIN: closedwon + closedate yesterday
    {
        "id": "9105",
        "properties": _deal_props(
            name="Bright Horizon — Phase 1.5 Add-on (Won)",
            amount="42000",
            stage="closedwon",
            confidence="High",
            closed="true",
            owner="222222",
            service_type="AI Support",
            start="2026-05-15",
            end="2026-08-15",
            lead="Jordan Rivera",
            priority="MEDIUM",
            description="Recently won — closed yesterday",
            closedate=_iso(_NOW - timedelta(days=1)),
            createdate=_iso(_NOW - timedelta(days=35)),
        ),
        "createdAt": _iso(_NOW - timedelta(days=35)),
        "updatedAt": _iso(_NOW - timedelta(days=1)),
        "archived": False,
    },
]

_EXTRA_DEAL_COMPANY_ASSOC = {
    "9101": "5001",  # Acme Ministries
    "9102": "5002",  # Bright Horizon Foundation
    "9103": "5005",  # NEW Echo Foundation (only deal for this co)
    "9104": "5003",  # Cedar Valley Co-op
    "9105": "5002",  # Bright Horizon Foundation
}


# ---------------------------------------------------------------------------
# Productive scenarios — asymmetric on purpose so "Missing Productive
# Scenarios" warning fires for 4 of the 5 new deals.
# Only 9102 (stuck-stage) gets one. The orphan/overdue/fresh/won don't.
# ---------------------------------------------------------------------------
_EXTRA_PROD_SCENARIOS = [
    {
        "id": "1805",
        "type": "scenarios",
        "attributes": {
            "name": "Bright Horizon — Stuck negotiation forecast",
            "started_on": "2026-08-01",
            "ended_on": "2027-01-31",
            "color_id": 5,
        },
        # No matching Productive deal exists yet for HubSpot 9102 — relationship null
        "relationships": {"deal": {"data": None}},
    },
]


# ---------------------------------------------------------------------------
# Final exports — extend baseline lists/dicts and re-export everything.
# Names not extended (e.g., HUBSPOT_OWNERS, PRODUCTIVE_PEOPLE) are imported
# above and re-exported as-is.
# ---------------------------------------------------------------------------
HUBSPOT_OWNERS = _BASE_HS_OWNERS
HUBSPOT_COMPANIES = _BASE_HS_COMPANIES + _EXTRA_HS_COMPANIES
HUBSPOT_DEALS = _BASE_HS_DEALS + _EXTRA_HS_DEALS
HUBSPOT_DEAL_COMPANY_ASSOC = {**_BASE_ASSOC, **_EXTRA_DEAL_COMPANY_ASSOC}
PRODUCTIVE_SCENARIOS = _BASE_PROD_SCENARIOS + _EXTRA_PROD_SCENARIOS
