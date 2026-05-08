"""HubSpot mock fixtures — synthetic data tuned to look realistic for a PMO/agency portfolio.

Custom properties used:
- confidence (Servant-custom): "High" / "Low" — Pulse filters deals on this
- service_type (Servant-custom): "Strategic Consulting" / "Product Build" / "Talent" / "AI Support"
- engagement_start_date, engagement_end_date, engagement_lead_name (Servant-custom)
- hs_is_closed: "true" / "false"
- pipeline: "default" or another pipeline ID
"""

from __future__ import annotations

from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Owners — Pulse uses these to resolve hubspot_owner_id → "First Last"
# ---------------------------------------------------------------------------
OWNERS: list[dict] = [
    {
        "id": "111111",
        "email": "alex.morgan@example.com",
        "firstName": "Alex",
        "lastName": "Morgan",
        "userId": 11001,
        "createdAt": "2024-01-15T09:00:00Z",
        "updatedAt": "2026-04-20T14:30:00Z",
        "archived": False,
    },
    {
        "id": "222222",
        "email": "jordan.rivera@example.com",
        "firstName": "Jordan",
        "lastName": "Rivera",
        "userId": 11002,
        "createdAt": "2024-02-01T09:00:00Z",
        "updatedAt": "2026-04-18T10:15:00Z",
        "archived": False,
    },
    {
        "id": "333333",
        "email": "casey.lin@example.com",
        "firstName": "Casey",
        "lastName": "Lin",
        "userId": 11003,
        "createdAt": "2024-03-12T09:00:00Z",
        "updatedAt": "2026-05-01T08:00:00Z",
        "archived": False,
    },
]

# ---------------------------------------------------------------------------
# Companies — referenced by deal-company associations
# ---------------------------------------------------------------------------
COMPANIES: list[dict] = [
    {
        "id": "5001",
        "properties": {
            "name": "Acme Ministries",
            "domain": "acmeministries.example",
            "createdate": "2025-08-12T00:00:00Z",
            "hs_lastmodifieddate": "2026-04-15T12:00:00Z",
        },
        "createdAt": "2025-08-12T00:00:00Z",
        "updatedAt": "2026-04-15T12:00:00Z",
        "archived": False,
    },
    {
        "id": "5002",
        "properties": {
            "name": "Bright Horizon Foundation",
            "domain": "brighthorizon.example",
            "createdate": "2025-09-20T00:00:00Z",
            "hs_lastmodifieddate": "2026-04-22T09:30:00Z",
        },
        "createdAt": "2025-09-20T00:00:00Z",
        "updatedAt": "2026-04-22T09:30:00Z",
        "archived": False,
    },
    {
        "id": "5003",
        "properties": {
            "name": "Cedar Valley Co-op",
            "domain": "cedarvalley.example",
            "createdate": "2026-01-10T00:00:00Z",
            "hs_lastmodifieddate": "2026-05-01T11:00:00Z",
        },
        "createdAt": "2026-01-10T00:00:00Z",
        "updatedAt": "2026-05-01T11:00:00Z",
        "archived": False,
    },
    {
        "id": "5004",
        "properties": {
            "name": "Delta Pastoral Network",
            "domain": "deltapastoral.example",
            "createdate": "2025-11-05T00:00:00Z",
            "hs_lastmodifieddate": "2026-04-28T16:45:00Z",
        },
        "createdAt": "2025-11-05T00:00:00Z",
        "updatedAt": "2026-04-28T16:45:00Z",
        "archived": False,
    },
]


def _deal_props(
    name: str,
    amount: str,
    stage: str,
    pipeline: str = "default",
    confidence: str = "High",
    closed: str = "false",
    owner: str = "111111",
    service_type: str = "Strategic Consulting",
    start: str = "",
    end: str = "",
    lead: str = "",
    priority: str = "MEDIUM",
    next_step: str = "",
    description: str = "",
    closedate: str = "",
    createdate: str = "",
) -> dict:
    """Helper to build a deal's properties dict with every field Pulse reads."""
    return {
        "dealname": name,
        "amount": amount,
        "dealstage": stage,
        "pipeline": pipeline,
        "closedate": closedate,
        "createdate": createdate,
        "confidence": confidence,
        "hs_deal_stage_probability": "0.7" if confidence == "High" else "0.3",
        "hs_is_closed": closed,
        "hubspot_owner_id": owner,
        "description": description,
        "dealtype": "newbusiness",
        "hs_priority": priority,
        "hs_forecast_amount": amount,
        "hs_forecast_probability": "0.7" if confidence == "High" else "0.3",
        "hs_next_step": next_step,
        "hs_lastmodifieddate": "2026-05-06T10:00:00Z",
        "notes_last_updated": "2026-05-05T15:30:00Z",
        "num_notes": "5",
        "num_associated_contacts": "3",
        "hs_analytics_source": "DIRECT_TRAFFIC",
        "hs_deal_amount_calculation_preference": "default",
        "service_type": service_type,
        "engagement_start_date": start,
        "engagement_end_date": end,
        "engagement_lead_name": lead,
    }


# ---------------------------------------------------------------------------
# Deals — varied across stages, confidence, pipelines, lifecycle states
# ---------------------------------------------------------------------------
_NOW = datetime(2026, 5, 8, 12, 0, 0)


def _iso(d: datetime) -> str:
    return d.strftime("%Y-%m-%dT%H:%M:%SZ")


DEALS: list[dict] = [
    # 3 high-confidence open deals
    {
        "id": "9001",
        "properties": _deal_props(
            name="Acme Ministries — Strategic Consulting",
            amount="125000",
            stage="contractsent",
            confidence="High",
            owner="111111",
            service_type="Strategic Consulting",
            start="2026-06-01",
            end="2026-09-30",
            lead="Alex Morgan",
            next_step="Contract review with legal",
            description="12-week strategic consulting on portfolio rationalization",
            closedate=_iso(_NOW + timedelta(days=14)),
            createdate=_iso(_NOW - timedelta(days=21)),
        ),
        "createdAt": _iso(_NOW - timedelta(days=21)),
        "updatedAt": _iso(_NOW - timedelta(days=2)),
        "archived": False,
    },
    {
        "id": "9002",
        "properties": _deal_props(
            name="Bright Horizon — AI Support SOW 2",
            amount="36000",
            stage="qualifiedtobuy",
            confidence="High",
            owner="222222",
            service_type="AI Support",
            start="2026-06-15",
            end="2026-12-15",
            lead="Jordan Rivera",
            next_step="SOW draft sent",
            description="Continuation of AI support engagement, 180h over 6 months",
            closedate=_iso(_NOW + timedelta(days=30)),
            createdate=_iso(_NOW - timedelta(days=45)),
        ),
        "createdAt": _iso(_NOW - timedelta(days=45)),
        "updatedAt": _iso(_NOW - timedelta(days=5)),
        "archived": False,
    },
    {
        "id": "9003",
        "properties": _deal_props(
            name="Cedar Valley Co-op — Pulse Deployment",
            amount="65000",
            stage="presentationscheduled",
            confidence="High",
            owner="333333",
            service_type="Product Build",
            start="2026-07-01",
            end="2026-10-31",
            lead="Casey Lin",
            priority="HIGH",
            next_step="Discovery workshop scheduled 5/22",
            description="Pulse PMO platform deployment + onboarding",
            closedate=_iso(_NOW + timedelta(days=45)),
            createdate=_iso(_NOW - timedelta(days=12)),
        ),
        "createdAt": _iso(_NOW - timedelta(days=12)),
        "updatedAt": _iso(_NOW - timedelta(days=1)),
        "archived": False,
    },
    # 1 low-confidence open deal
    {
        "id": "9004",
        "properties": _deal_props(
            name="Delta Pastoral — Talent Placement",
            amount="22000",
            stage="appointmentscheduled",
            confidence="Low",
            owner="111111",
            service_type="Talent",
            start="",
            end="",
            lead="",
            priority="LOW",
            next_step="Awaiting hiring manager availability",
            description="Two senior placements on contingency",
            closedate=_iso(_NOW + timedelta(days=60)),
            createdate=_iso(_NOW - timedelta(days=30)),
        ),
        "createdAt": _iso(_NOW - timedelta(days=30)),
        "updatedAt": _iso(_NOW - timedelta(days=10)),
        "archived": False,
    },
    # 1 closed-won deal
    {
        "id": "9005",
        "properties": _deal_props(
            name="Acme Ministries — Initial Discovery",
            amount="15000",
            stage="closedwon",
            confidence="High",
            closed="true",
            owner="111111",
            service_type="Strategic Consulting",
            start="2026-02-01",
            end="2026-04-30",
            lead="Alex Morgan",
            description="Completed discovery engagement, transitioned to consulting SOW",
            closedate=_iso(_NOW - timedelta(days=8)),
            createdate=_iso(_NOW - timedelta(days=120)),
        ),
        "createdAt": _iso(_NOW - timedelta(days=120)),
        "updatedAt": _iso(_NOW - timedelta(days=8)),
        "archived": False,
    },
    # 1 closed-lost deal
    {
        "id": "9006",
        "properties": _deal_props(
            name="Lapsed Lead — Foundation Outreach",
            amount="40000",
            stage="closedlost",
            confidence="Low",
            closed="true",
            owner="222222",
            service_type="Strategic Consulting",
            description="Budget reallocated to internal hire",
            closedate=_iso(_NOW - timedelta(days=22)),
            createdate=_iso(_NOW - timedelta(days=90)),
        ),
        "createdAt": _iso(_NOW - timedelta(days=90)),
        "updatedAt": _iso(_NOW - timedelta(days=22)),
        "archived": False,
    },
    # 2 forecast/early-stage deals
    {
        "id": "9007",
        "properties": _deal_props(
            name="Bright Horizon — Phase 2 Expansion",
            amount="180000",
            stage="qualifiedtobuy",
            confidence="High",
            owner="222222",
            service_type="Product Build",
            start="2026-09-01",
            end="2027-03-01",
            lead="Jordan Rivera",
            priority="HIGH",
            next_step="Statement of Work drafting",
            description="Six-month build extension following Phase 1 acceptance",
            closedate=_iso(_NOW + timedelta(days=75)),
            createdate=_iso(_NOW - timedelta(days=18)),
        ),
        "createdAt": _iso(_NOW - timedelta(days=18)),
        "updatedAt": _iso(_NOW - timedelta(days=3)),
        "archived": False,
    },
    {
        "id": "9008",
        "properties": _deal_props(
            name="Cedar Valley Co-op — Add-on Analytics",
            amount="28000",
            stage="appointmentscheduled",
            confidence="High",
            owner="333333",
            service_type="Strategic Consulting",
            start="2026-08-01",
            end="2026-10-15",
            lead="Casey Lin",
            description="Analytics scoping conversation initiated post-discovery",
            closedate=_iso(_NOW + timedelta(days=50)),
            createdate=_iso(_NOW - timedelta(days=6)),
        ),
        "createdAt": _iso(_NOW - timedelta(days=6)),
        "updatedAt": _iso(_NOW - timedelta(days=1)),
        "archived": False,
    },
]


# ---------------------------------------------------------------------------
# Deal → Company associations (v4 batch read shape)
# ---------------------------------------------------------------------------
DEAL_COMPANY_ASSOCIATIONS: dict[str, str] = {
    "9001": "5001",
    "9002": "5002",
    "9003": "5003",
    "9004": "5004",
    "9005": "5001",
    "9006": "5004",
    "9007": "5002",
    "9008": "5003",
}


# ---------------------------------------------------------------------------
# Pipeline + stages
# ---------------------------------------------------------------------------
PIPELINE_STAGES: list[dict] = [
    {
        "id": "appointmentscheduled",
        "label": "Appointment Scheduled",
        "displayOrder": 0,
        "metadata": {"isClosed": "false", "probability": "0.2"},
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-01T00:00:00Z",
        "archived": False,
    },
    {
        "id": "qualifiedtobuy",
        "label": "Qualified To Buy",
        "displayOrder": 1,
        "metadata": {"isClosed": "false", "probability": "0.4"},
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-01T00:00:00Z",
        "archived": False,
    },
    {
        "id": "presentationscheduled",
        "label": "Presentation Scheduled",
        "displayOrder": 2,
        "metadata": {"isClosed": "false", "probability": "0.6"},
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-01T00:00:00Z",
        "archived": False,
    },
    {
        "id": "contractsent",
        "label": "Contract Sent",
        "displayOrder": 3,
        "metadata": {"isClosed": "false", "probability": "0.8"},
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-01T00:00:00Z",
        "archived": False,
    },
    {
        "id": "closedwon",
        "label": "Closed Won",
        "displayOrder": 4,
        "metadata": {"isClosed": "true", "probability": "1.0"},
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-01T00:00:00Z",
        "archived": False,
    },
    {
        "id": "closedlost",
        "label": "Closed Lost",
        "displayOrder": 5,
        "metadata": {"isClosed": "true", "probability": "0.0"},
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-01T00:00:00Z",
        "archived": False,
    },
]

PIPELINES: list[dict] = [
    {
        "id": "default",
        "label": "Sales Pipeline",
        "displayOrder": 0,
        "stages": PIPELINE_STAGES,
        "createdAt": "2024-01-01T00:00:00Z",
        "updatedAt": "2024-01-01T00:00:00Z",
        "archived": False,
    }
]


# ---------------------------------------------------------------------------
# Custom property metadata (for /properties/deals admin discovery)
# ---------------------------------------------------------------------------
DEAL_PROPERTIES: list[dict] = [
    {
        "name": "confidence",
        "label": "Confidence",
        "type": "enumeration",
        "fieldType": "select",
        "groupName": "dealinformation",
        "options": [
            {"label": "High", "value": "High", "displayOrder": 0, "hidden": False},
            {"label": "Low", "value": "Low", "displayOrder": 1, "hidden": False},
        ],
    },
    {
        "name": "service_type",
        "label": "Service Type",
        "type": "enumeration",
        "fieldType": "select",
        "groupName": "dealinformation",
        "options": [
            {"label": "Strategic Consulting", "value": "Strategic Consulting", "displayOrder": 0, "hidden": False},
            {"label": "Product Build", "value": "Product Build", "displayOrder": 1, "hidden": False},
            {"label": "Talent", "value": "Talent", "displayOrder": 2, "hidden": False},
            {"label": "AI Support", "value": "AI Support", "displayOrder": 3, "hidden": False},
        ],
    },
    {
        "name": "engagement_start_date",
        "label": "Engagement Start Date",
        "type": "date",
        "fieldType": "date",
        "groupName": "dealinformation",
        "options": [],
    },
    {
        "name": "engagement_end_date",
        "label": "Engagement End Date",
        "type": "date",
        "fieldType": "date",
        "groupName": "dealinformation",
        "options": [],
    },
    {
        "name": "engagement_lead_name",
        "label": "Engagement Lead",
        "type": "string",
        "fieldType": "text",
        "groupName": "dealinformation",
        "options": [],
    },
]
