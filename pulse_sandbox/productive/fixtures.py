"""Productive mock fixtures — JSON:API resources tuned to match Pulse's parser expectations.

Custom field IDs match the Servant production tenant so Pulse's category lookups work:
- 55149 = Employee Type (options: 179224 FTE, 179228 Contractor, 179226 Freelance, 179230 Advisor, 263656 Placeholder)
- 55151 = Deployable Team
- 55153 = % Allocation
- 55147 = Discipline
"""

from __future__ import annotations

from datetime import date

# ---------------------------------------------------------------------------
# Custom field option IDs (must match Servant production for Pulse's lookups)
# ---------------------------------------------------------------------------
EMPLOYEE_TYPE_FIELD_ID = "55149"
DEPLOYABLE_TEAM_FIELD_ID = "55151"
ALLOCATION_FIELD_ID = "55153"
DISCIPLINE_FIELD_ID = "55147"

OPT_FTE = "179224"
OPT_CONTRACTOR = "179228"
OPT_FREELANCE = "179226"
OPT_ADVISOR = "179230"
OPT_PLACEHOLDER = "263656"
OPT_BILLABLE_TEAM = "179232"


# ---------------------------------------------------------------------------
# Custom fields metadata (returned by /custom_fields)
# ---------------------------------------------------------------------------
CUSTOM_FIELDS = [
    {
        "id": EMPLOYEE_TYPE_FIELD_ID,
        "type": "custom_fields",
        "attributes": {
            "name": "Employee Type",
            "data_type": "select",
            "aggregation_type": None,
        },
        "relationships": {
            "options": {
                "data": [
                    {"type": "custom_field_options", "id": OPT_FTE},
                    {"type": "custom_field_options", "id": OPT_CONTRACTOR},
                    {"type": "custom_field_options", "id": OPT_FREELANCE},
                    {"type": "custom_field_options", "id": OPT_ADVISOR},
                    {"type": "custom_field_options", "id": OPT_PLACEHOLDER},
                ]
            }
        },
    },
    {
        "id": DEPLOYABLE_TEAM_FIELD_ID,
        "type": "custom_fields",
        "attributes": {
            "name": "Deployable Team",
            "data_type": "select",
            "aggregation_type": None,
        },
        "relationships": {
            "options": {
                "data": [
                    {"type": "custom_field_options", "id": OPT_BILLABLE_TEAM},
                ]
            }
        },
    },
    {
        "id": ALLOCATION_FIELD_ID,
        "type": "custom_fields",
        "attributes": {
            "name": "% Allocation",
            "data_type": "number",
            "aggregation_type": None,
        },
        "relationships": {"options": {"data": []}},
    },
    {
        "id": DISCIPLINE_FIELD_ID,
        "type": "custom_fields",
        "attributes": {
            "name": "Discipline",
            "data_type": "select",
            "aggregation_type": None,
        },
        "relationships": {
            "options": {
                "data": [
                    {"type": "custom_field_options", "id": "300001"},
                    {"type": "custom_field_options", "id": "300002"},
                ]
            }
        },
    },
]

CUSTOM_FIELD_OPTIONS_INCLUDED = [
    # Employee Type options
    {
        "id": OPT_FTE,
        "type": "custom_field_options",
        "attributes": {"name": "FTE"},
        "relationships": {"custom_field": {"data": {"type": "custom_fields", "id": EMPLOYEE_TYPE_FIELD_ID}}},
    },
    {
        "id": OPT_CONTRACTOR,
        "type": "custom_field_options",
        "attributes": {"name": "Contractor"},
        "relationships": {"custom_field": {"data": {"type": "custom_fields", "id": EMPLOYEE_TYPE_FIELD_ID}}},
    },
    {
        "id": OPT_FREELANCE,
        "type": "custom_field_options",
        "attributes": {"name": "Freelance"},
        "relationships": {"custom_field": {"data": {"type": "custom_fields", "id": EMPLOYEE_TYPE_FIELD_ID}}},
    },
    {
        "id": OPT_ADVISOR,
        "type": "custom_field_options",
        "attributes": {"name": "Advisor"},
        "relationships": {"custom_field": {"data": {"type": "custom_fields", "id": EMPLOYEE_TYPE_FIELD_ID}}},
    },
    {
        "id": OPT_PLACEHOLDER,
        "type": "custom_field_options",
        "attributes": {"name": "Placeholder"},
        "relationships": {"custom_field": {"data": {"type": "custom_fields", "id": EMPLOYEE_TYPE_FIELD_ID}}},
    },
    # Deployable Team options
    {
        "id": OPT_BILLABLE_TEAM,
        "type": "custom_field_options",
        "attributes": {"name": "Billable"},
        "relationships": {"custom_field": {"data": {"type": "custom_fields", "id": DEPLOYABLE_TEAM_FIELD_ID}}},
    },
    # Discipline options
    {
        "id": "300001",
        "type": "custom_field_options",
        "attributes": {"name": "Engineering"},
        "relationships": {"custom_field": {"data": {"type": "custom_fields", "id": DISCIPLINE_FIELD_ID}}},
    },
    {
        "id": "300002",
        "type": "custom_field_options",
        "attributes": {"name": "Strategy"},
        "relationships": {"custom_field": {"data": {"type": "custom_fields", "id": DISCIPLINE_FIELD_ID}}},
    },
]


# ---------------------------------------------------------------------------
# Teams
# ---------------------------------------------------------------------------
TEAMS = [
    {
        "id": "401",
        "type": "teams",
        "attributes": {"name": "Engineering", "color": "#3F51B5"},
        "relationships": {},
    },
    {
        "id": "402",
        "type": "teams",
        "attributes": {"name": "PMO", "color": "#FF9800"},
        "relationships": {},
    },
    {
        "id": "403",
        "type": "teams",
        "attributes": {"name": "Strategy", "color": "#4CAF50"},
        "relationships": {},
    },
]


def _person(
    id_: str,
    first: str,
    last: str,
    email: str,
    employee_type_opt: str,
    team_id: str = "401",
    allocation: int = 100,
    archived: bool = False,
) -> dict:
    """Helper to build a person resource."""
    return {
        "id": id_,
        "type": "people",
        "attributes": {
            "first_name": first,
            "last_name": last,
            "email": email,
            "archived_at": None if not archived else "2026-01-15T00:00:00Z",
            "is_user": True,
            "title": "Consultant",
            "custom_fields": {
                EMPLOYEE_TYPE_FIELD_ID: employee_type_opt,
                DEPLOYABLE_TEAM_FIELD_ID: OPT_BILLABLE_TEAM if not archived else None,
                ALLOCATION_FIELD_ID: str(allocation),
                DISCIPLINE_FIELD_ID: "300001" if team_id == "401" else "300002",
            },
        },
        "relationships": {
            "teams": {"data": [{"type": "teams", "id": team_id}]},
        },
    }


PEOPLE = [
    _person("701", "Avery", "Chen", "avery.chen@example.com", OPT_FTE, "401", 100),
    _person("702", "Blake", "Park", "blake.park@example.com", OPT_FTE, "401", 100),
    _person("703", "Charlie", "Brooks", "charlie.brooks@example.com", OPT_CONTRACTOR, "401", 60),
    _person("704", "Devon", "Singh", "devon.singh@example.com", OPT_FTE, "402", 100),
    _person("705", "Emerson", "Liu", "emerson.liu@example.com", OPT_FREELANCE, "403", 40),
    _person("706", "Frankie", "Diaz", "frankie.diaz@example.com", OPT_PLACEHOLDER, "401", 0),
    _person("707", "Grey", "Marsh", "grey.marsh@example.com", OPT_ADVISOR, "403", 20),
]


# ---------------------------------------------------------------------------
# Companies (referenced by projects via budget.company)
# ---------------------------------------------------------------------------
COMPANIES = [
    {
        "id": "501",
        "type": "companies",
        "attributes": {"name": "Acme Ministries"},
        "relationships": {},
    },
    {
        "id": "502",
        "type": "companies",
        "attributes": {"name": "Bright Horizon Foundation"},
        "relationships": {},
    },
    {
        "id": "503",
        "type": "companies",
        "attributes": {"name": "Cedar Valley Co-op"},
        "relationships": {},
    },
]


# ---------------------------------------------------------------------------
# Projects (most are project_type_id=2 = client; some archived)
# ---------------------------------------------------------------------------
PROJECTS = [
    {
        "id": "801",
        "type": "projects",
        "attributes": {
            "name": "Acme Ministries — Strategic Consulting",
            "project_type_id": 2,
            "archived_at": None,
            "project_number": "PROJ-001",
            "project_color_id": 1,
        },
        "relationships": {
            "company": {"data": {"type": "companies", "id": "501"}},
        },
    },
    {
        "id": "802",
        "type": "projects",
        "attributes": {
            "name": "Bright Horizon — AI Support",
            "project_type_id": 2,
            "archived_at": None,
            "project_number": "PROJ-002",
            "project_color_id": 2,
        },
        "relationships": {
            "company": {"data": {"type": "companies", "id": "502"}},
        },
    },
    {
        "id": "803",
        "type": "projects",
        "attributes": {
            "name": "Cedar Valley Co-op — Pulse Deployment",
            "project_type_id": 2,
            "archived_at": None,
            "project_number": "PROJ-003",
            "project_color_id": 3,
        },
        "relationships": {
            "company": {"data": {"type": "companies", "id": "503"}},
        },
    },
    {
        "id": "804",
        "type": "projects",
        "attributes": {
            "name": "Internal — PMO Operations",
            "project_type_id": 1,  # internal
            "archived_at": None,
            "project_number": "INT-001",
            "project_color_id": 4,
        },
        "relationships": {"company": {"data": None}},
    },
    {
        "id": "805",
        "type": "projects",
        "attributes": {
            "name": "Lapsed Lead — Foundation Outreach",
            "project_type_id": 2,
            "archived_at": "2026-04-10T00:00:00Z",
            "project_number": "PROJ-004",
            "project_color_id": 5,
        },
        "relationships": {"company": {"data": None}},
    },
]


# ---------------------------------------------------------------------------
# Budgets (one per active client project)
# Budget amounts in CENTS — Pulse divides by 100 for dollars
# ---------------------------------------------------------------------------
BUDGETS = [
    {
        "id": "901",
        "type": "budgets",
        "attributes": {
            "name": "Acme — Discovery + Consulting",
            "budget_total": 12500000,  # $125,000
            "budget_used": 4200000,    # $42,000 used
            "date": "2026-02-01",
            "end_date": "2026-09-30",
            "status": 1,
        },
        "relationships": {
            "project": {"data": {"type": "projects", "id": "801"}},
            "company": {"data": {"type": "companies", "id": "501"}},
        },
    },
    {
        "id": "902",
        "type": "budgets",
        "attributes": {
            "name": "Bright Horizon — AI Support SOW 1",
            "budget_total": 3600000,   # $36,000
            "budget_used": 1800000,    # $18,000 used
            "date": "2026-02-09",
            "end_date": "2026-08-07",
            "status": 1,
        },
        "relationships": {
            "project": {"data": {"type": "projects", "id": "802"}},
            "company": {"data": {"type": "companies", "id": "502"}},
        },
    },
    {
        "id": "903",
        "type": "budgets",
        "attributes": {
            "name": "Cedar Valley — Pulse Deployment",
            "budget_total": 6500000,   # $65,000
            "budget_used": 800000,     # $8,000 used
            "date": "2026-04-15",
            "end_date": "2026-10-31",
            "status": 1,
        },
        "relationships": {
            "project": {"data": {"type": "projects", "id": "803"}},
            "company": {"data": {"type": "companies", "id": "503"}},
        },
    },
]


# ---------------------------------------------------------------------------
# Productive deals (CRM) — bridge to HubSpot via external_id
# ---------------------------------------------------------------------------
DEALS = [
    {
        "id": "601",
        "type": "deals",
        "attributes": {
            "name": "Acme Ministries — Strategic Consulting",
            "external_id": "9001",  # links to HubSpot deal 9001
            "budget_total": 12500000,
            "budget_used": 4200000,
            "date": "2026-02-01",
            "end_date": "2026-09-30",
        },
        "relationships": {
            "project": {"data": {"type": "projects", "id": "801"}},
        },
    },
    {
        "id": "602",
        "type": "deals",
        "attributes": {
            "name": "Bright Horizon — AI Support",
            "external_id": "9002",
            "budget_total": 3600000,
            "budget_used": 1800000,
            "date": "2026-02-09",
            "end_date": "2026-08-07",
        },
        "relationships": {
            "project": {"data": {"type": "projects", "id": "802"}},
        },
    },
    {
        "id": "603",
        "type": "deals",
        "attributes": {
            "name": "Cedar Valley — Pulse Deployment",
            "external_id": "9003",
            "budget_total": 6500000,
            "budget_used": 800000,
            "date": "2026-04-15",
            "end_date": "2026-10-31",
        },
        "relationships": {
            "project": {"data": {"type": "projects", "id": "803"}},
        },
    },
]


# ---------------------------------------------------------------------------
# Services (under deals)
# ---------------------------------------------------------------------------
SERVICES = [
    {
        "id": "1101",
        "type": "services",
        "attributes": {"name": "Strategic Consulting Hours"},
        "relationships": {"deal": {"data": {"type": "deals", "id": "601"}}},
    },
    {
        "id": "1102",
        "type": "services",
        "attributes": {"name": "AI Support Hours"},
        "relationships": {"deal": {"data": {"type": "deals", "id": "602"}}},
    },
    {
        "id": "1103",
        "type": "services",
        "attributes": {"name": "Deployment + Onboarding"},
        "relationships": {"deal": {"data": {"type": "deals", "id": "603"}}},
    },
]


# ---------------------------------------------------------------------------
# Bookings (person → service → deal → project chain)
# ---------------------------------------------------------------------------
BOOKINGS = [
    {
        "id": "1201",
        "type": "bookings",
        "attributes": {
            "started_on": "2026-04-01",
            "ended_on": "2026-09-30",
            "hours_per_day": 6.0,
            "approved": True,
        },
        "relationships": {
            "person": {"data": {"type": "people", "id": "701"}},
            "service": {"data": {"type": "services", "id": "1101"}},
        },
    },
    {
        "id": "1202",
        "type": "bookings",
        "attributes": {
            "started_on": "2026-02-09",
            "ended_on": "2026-08-07",
            "hours_per_day": 3.0,
            "approved": True,
        },
        "relationships": {
            "person": {"data": {"type": "people", "id": "702"}},
            "service": {"data": {"type": "services", "id": "1102"}},
        },
    },
    {
        "id": "1203",
        "type": "bookings",
        "attributes": {
            "started_on": "2026-05-01",
            "ended_on": "2026-10-31",
            "hours_per_day": 4.0,
            "approved": True,
        },
        "relationships": {
            "person": {"data": {"type": "people", "id": "703"}},
            "service": {"data": {"type": "services", "id": "1103"}},
        },
    },
    {
        "id": "1204",
        "type": "bookings",
        "attributes": {
            "started_on": "2026-04-15",
            "ended_on": "2026-08-15",
            "hours_per_day": 2.0,
            "approved": True,
        },
        "relationships": {
            "person": {"data": {"type": "people", "id": "704"}},
            "service": {"data": {"type": "services", "id": "1101"}},
        },
    },
]


# ---------------------------------------------------------------------------
# Time reports — per-person per-week with metrics in MINUTES
# id format: "weekly-YYYY-MM-DD-person-{person_id}" (Pulse parses by string split)
# ---------------------------------------------------------------------------
def _time_report(
    person_id: str,
    week_start: str,
    worked: int = 1800,
    client: int = 1500,
    internal: int = 300,
    scheduled_billable: int = 1800,
    capacity: int = 2400,
    holiday: int = 0,
    time_off: int = 0,
) -> dict:
    return {
        "id": f"weekly-{week_start}-person-{person_id}",
        "type": "time_reports",
        "attributes": {
            "worked_time": worked,
            "client_time": client,
            "internal_time": internal,
            "scheduled_billable_time": scheduled_billable,
            "capacity_time": capacity,
            "holiday_time": holiday,
            "time_off": time_off,
            "date": week_start,
        },
        "relationships": {
            "person": {"data": {"type": "people", "id": person_id}},
        },
    }


TIME_REPORTS = [
    # Week of 2026-04-27
    _time_report("701", "2026-04-27", worked=1800, client=1500, internal=300),
    _time_report("702", "2026-04-27", worked=900, client=900, internal=0),
    _time_report("703", "2026-04-27", worked=1200, client=1200, internal=0),
    _time_report("704", "2026-04-27", worked=600, client=600, internal=0),
    # Week of 2026-05-04 (current)
    _time_report("701", "2026-05-04", worked=1740, client=1440, internal=300, scheduled_billable=1800),
    _time_report("702", "2026-05-04", worked=900, client=900, internal=0),
    _time_report("703", "2026-05-04", worked=1200, client=1200, internal=0),
    _time_report("704", "2026-05-04", worked=480, client=480, internal=0),
]


# ---------------------------------------------------------------------------
# Budget reports — group_by=project, with project + budget + budget.company sideloads
# ---------------------------------------------------------------------------
BUDGET_REPORTS = [
    {
        "id": "br-801",
        "type": "budget_reports",
        "attributes": {
            "budget_used": 4200000,
            "budget_total": 12500000,
            "budget_remaining": 8300000,
            "scheduled_time": 240000,
            "name": "Acme Ministries — Strategic Consulting",
        },
        "relationships": {
            "project": {"data": {"type": "projects", "id": "801"}},
            "budget": {"data": {"type": "budgets", "id": "901"}},
        },
    },
    {
        "id": "br-802",
        "type": "budget_reports",
        "attributes": {
            "budget_used": 1800000,
            "budget_total": 3600000,
            "budget_remaining": 1800000,
            "scheduled_time": 90000,
            "name": "Bright Horizon — AI Support",
        },
        "relationships": {
            "project": {"data": {"type": "projects", "id": "802"}},
            "budget": {"data": {"type": "budgets", "id": "902"}},
        },
    },
    {
        "id": "br-803",
        "type": "budget_reports",
        "attributes": {
            "budget_used": 800000,
            "budget_total": 6500000,
            "budget_remaining": 5700000,
            "scheduled_time": 120000,
            "name": "Cedar Valley — Pulse Deployment",
        },
        "relationships": {
            "project": {"data": {"type": "projects", "id": "803"}},
            "budget": {"data": {"type": "budgets", "id": "903"}},
        },
    },
]


# ---------------------------------------------------------------------------
# Scenarios — Productive's forecast/budget scenarios per deal.
# Pulse hits GET /scenarios?filter[deal_id]={id}&page[size]=1 to count
# whether a deal has any scenarios attached (used in the HC-deals view).
#
# Each deal here has 1–2 scenarios so Pulse's `len(data) > 0` check returns
# truthy and the dashboard renders the "has scenarios" indicator.
# ---------------------------------------------------------------------------
SCENARIOS = [
    {
        "id": "1801",
        "type": "scenarios",
        "attributes": {
            "name": "Acme Strategic Consulting — Q3 forecast",
            "started_on": "2026-06-01",
            "ended_on": "2026-09-30",
            "color_id": 7,
        },
        "relationships": {"deal": {"data": {"type": "deals", "id": "601"}}},
    },
    {
        "id": "1802",
        "type": "scenarios",
        "attributes": {
            "name": "Acme Strategic Consulting — Stretch case",
            "started_on": "2026-06-01",
            "ended_on": "2026-12-31",
            "color_id": 8,
        },
        "relationships": {"deal": {"data": {"type": "deals", "id": "601"}}},
    },
    {
        "id": "1803",
        "type": "scenarios",
        "attributes": {
            "name": "Bright Horizon — AI Support continuation",
            "started_on": "2026-06-15",
            "ended_on": "2026-12-15",
            "color_id": 4,
        },
        "relationships": {"deal": {"data": {"type": "deals", "id": "602"}}},
    },
    {
        "id": "1804",
        "type": "scenarios",
        "attributes": {
            "name": "Cedar Valley — Pulse Phase 1 deployment",
            "started_on": "2026-07-01",
            "ended_on": "2026-10-31",
            "color_id": 2,
        },
        "relationships": {"deal": {"data": {"type": "deals", "id": "603"}}},
    },
]


# ---------------------------------------------------------------------------
# Saved custom report — the "Client Engagement Utilization Report".
# Pulse references this via env var CLIENT_ENG_UTIL_REPORT_ID (default 1591877).
# Two endpoints exposed:
#   GET /reports/{id}            — modern API path
#   GET /reports/{id}/budgets    — legacy API path
# Both return budget-shaped data with company + project sideloads, mirroring
# what /reports/budget_reports returns but pre-filtered by the saved view.
# ---------------------------------------------------------------------------
CLIENT_ENG_UTIL_REPORT_ID = "1591877"

SAVED_REPORT_BUDGETS = [
    {
        "id": "sr-901",
        "type": "budgets",
        "attributes": {
            "name": "Acme Ministries — Strategic Consulting",
            "budget_total": 12500000,  # cents = $125,000
            "budget_used": 8125000,    # 65% utilization
            "budget_remaining": 4375000,
            "date": "2026-02-01",
            "end_date": "2026-09-30",
            "status": 2,  # active
        },
        "relationships": {
            "project": {"data": {"type": "projects", "id": "801"}},
            "company": {"data": {"type": "companies", "id": "501"}},
        },
    },
    {
        "id": "sr-902",
        "type": "budgets",
        "attributes": {
            "name": "Bright Horizon — AI Support",
            "budget_total": 3600000,
            "budget_used": 2520000,    # 70% utilization
            "budget_remaining": 1080000,
            "date": "2026-02-09",
            "end_date": "2026-08-07",
            "status": 2,
        },
        "relationships": {
            "project": {"data": {"type": "projects", "id": "802"}},
            "company": {"data": {"type": "companies", "id": "502"}},
        },
    },
    {
        "id": "sr-903",
        "type": "budgets",
        "attributes": {
            "name": "Cedar Valley — Pulse Deployment",
            "budget_total": 6500000,
            "budget_used": 1300000,    # 20% utilization (under 50%, won't appear in >=50% filter)
            "budget_remaining": 5200000,
            "date": "2026-04-15",
            "end_date": "2026-10-31",
            "status": 2,
        },
        "relationships": {
            "project": {"data": {"type": "projects", "id": "803"}},
            "company": {"data": {"type": "companies", "id": "503"}},
        },
    },
]
