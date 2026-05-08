# Fixtures

> Sample data structure and how to extend it.
> Last updated 2026-05-08 (v0.1.0).

## Philosophy

Phase 1 fixtures are **synthetic but realistic-shaped**. They cover the data variety Pulse needs to render dashboards correctly:

- Multiple deal stages (open, closed-won, closed-lost)
- Multiple confidence values (High, Low)
- Multiple employee types (FTE, Contractor, Freelance, Advisor, Placeholder)
- Multiple lifecycle states (active, archived)

They do NOT cover:
- Realistic anonymized real-client data (Phase 2)
- Edge cases like 1000+ records or pagination boundaries (Phase 2)
- Failure scenarios (rate limits, auth errors, partial failures) (Phase 2)

All data is hand-curated Python dicts in `pulse_sandbox/{service}/fixtures.py`. There is no JSON-file loader in Phase 1 — fixtures are version-controlled with the code.

## HubSpot fixtures

Located at `pulse_sandbox/hubspot/fixtures.py`.

### Deals — 8 total

| ID | Name | Stage | Confidence | Closed | Owner | Service Type |
|---|---|---|---|---|---|---|
| 9001 | Acme Ministries — Strategic Consulting | contractsent | High | false | 111111 | Strategic Consulting |
| 9002 | Bright Horizon — AI Support SOW 2 | qualifiedtobuy | High | false | 222222 | AI Support |
| 9003 | Cedar Valley Co-op — Pulse Deployment | presentationscheduled | High | false | 333333 | Product Build |
| 9004 | Delta Pastoral — Talent Placement | appointmentscheduled | Low | false | 111111 | Talent |
| 9005 | Acme Ministries — Initial Discovery | closedwon | High | true | 111111 | Strategic Consulting |
| 9006 | Lapsed Lead — Foundation Outreach | closedlost | Low | true | 222222 | Strategic Consulting |
| 9007 | Bright Horizon — Phase 2 Expansion | qualifiedtobuy | High | false | 222222 | Product Build |
| 9008 | Cedar Valley Co-op — Add-on Analytics | appointmentscheduled | High | false | 333333 | Strategic Consulting |

### Owners — 3

| ID | Name | Email |
|---|---|---|
| 111111 | Alex Morgan | alex.morgan@example.com |
| 222222 | Jordan Rivera | jordan.rivera@example.com |
| 333333 | Casey Lin | casey.lin@example.com |

### Companies — 4

| ID | Name |
|---|---|
| 5001 | Acme Ministries |
| 5002 | Bright Horizon Foundation |
| 5003 | Cedar Valley Co-op |
| 5004 | Delta Pastoral Network |

### Pipeline — 1 (`default`)

Six stages: appointmentscheduled → qualifiedtobuy → presentationscheduled → contractsent → closedwon | closedlost.

### Custom Properties

| Name | Type | Servant-custom? |
|---|---|---|
| `confidence` | enumeration (High/Low) | yes |
| `service_type` | enumeration (Strategic Consulting / Product Build / Talent / AI Support) | yes |
| `engagement_start_date` | date | yes |
| `engagement_end_date` | date | yes |
| `engagement_lead_name` | string | yes |

## Productive fixtures

Located at `pulse_sandbox/productive/fixtures.py`.

### People — 7

| ID | Name | Employee Type | Team | Allocation |
|---|---|---|---|---|
| 701 | Avery Chen | FTE | Engineering (401) | 100% |
| 702 | Blake Park | FTE | Engineering (401) | 100% |
| 703 | Charlie Brooks | Contractor | Engineering (401) | 60% |
| 704 | Devon Singh | FTE | PMO (402) | 100% |
| 705 | Emerson Liu | Freelance | Strategy (403) | 40% |
| 706 | Frankie Diaz | Placeholder | Engineering (401) | 0% |
| 707 | Grey Marsh | Advisor | Strategy (403) | 20% |

### Teams — 3

| ID | Name | Color |
|---|---|---|
| 401 | Engineering | #3F51B5 |
| 402 | PMO | #FF9800 |
| 403 | Strategy | #4CAF50 |

### Projects — 5

| ID | Name | Type | Archived | Company |
|---|---|---|---|---|
| 801 | Acme Ministries — Strategic Consulting | client (2) | no | Acme (501) |
| 802 | Bright Horizon — AI Support | client (2) | no | Bright Horizon (502) |
| 803 | Cedar Valley Co-op — Pulse Deployment | client (2) | no | Cedar Valley (503) |
| 804 | Internal — PMO Operations | internal (1) | no | none |
| 805 | Lapsed Lead — Foundation Outreach | client (2) | yes (2026-04-10) | none |

### Budgets — 3

All amounts in **cents** (Pulse divides by 100 for dollars).

| ID | Project | Total | Used | Date Range |
|---|---|---|---|---|
| 901 | 801 | 12,500,000 ($125k) | 4,200,000 ($42k) | 2026-02-01 → 2026-09-30 |
| 902 | 802 | 3,600,000 ($36k) | 1,800,000 ($18k) | 2026-02-09 → 2026-08-07 |
| 903 | 803 | 6,500,000 ($65k) | 800,000 ($8k) | 2026-04-15 → 2026-10-31 |

### Productive Deals (CRM) — 3

External-id linkage to mock HubSpot deals.

| ID | Name | external_id | Project |
|---|---|---|---|
| 601 | Acme Ministries — Strategic Consulting | 9001 (HubSpot) | 801 |
| 602 | Bright Horizon — AI Support | 9002 (HubSpot) | 802 |
| 603 | Cedar Valley — Pulse Deployment | 9003 (HubSpot) | 803 |

### Bookings — 4

Linking person → service → deal → project.

| ID | Person | Service | Hours/Day | Date Range |
|---|---|---|---|---|
| 1201 | 701 | 1101 | 6.0 | 2026-04-01 → 2026-09-30 |
| 1202 | 702 | 1102 | 3.0 | 2026-02-09 → 2026-08-07 |
| 1203 | 703 | 1103 | 4.0 | 2026-05-01 → 2026-10-31 |
| 1204 | 704 | 1101 | 2.0 | 2026-04-15 → 2026-08-15 |

### Scenarios — 4 rows across 3 deals

Productive's per-deal forecast scenarios. Pulse uses `GET /scenarios?filter[deal_id]={id}&page[size]=1` from `api/routes/hubspot.py:220` to count whether each HC deal has any scenarios attached.

| ID | Name | Deal |
|---|---|---|
| 1801 | Acme Strategic Consulting — Q3 forecast | 601 |
| 1802 | Acme Strategic Consulting — Stretch case | 601 |
| 1803 | Bright Horizon — AI Support continuation | 602 |
| 1804 | Cedar Valley — Pulse Phase 1 deployment | 603 |

Deal 601 has 2 scenarios on purpose so the count-distinct logic exercises >1.

### Saved Custom Report (id `1591877`) — 3 budget rows

Productive's "Client Engagement Utilization Report." Pulse references this via env var `CLIENT_ENG_UTIL_REPORT_ID` (default `1591877`).

Two URL paths exposed (Pulse falls through them):
- `GET /reports/1591877/budgets` — legacy path
- `GET /reports/1591877` — modern path

Both return the same data: 3 budgets with `budget_total`, `budget_used`, and `budget_remaining` in cents. One budget at 65% utilization, one at 70%, one at 20% — so Pulse's `>=50%` filter renders 2 rows in the dashboard.

| ID | Name | Total ($) | Used ($) | Util % |
|---|---|---|---|---|
| sr-901 | Acme Ministries — Strategic Consulting | 125,000 | 81,250 | 65% |
| sr-902 | Bright Horizon — AI Support | 36,000 | 25,200 | 70% |
| sr-903 | Cedar Valley — Pulse Deployment | 65,000 | 13,000 | 20% |

The `include=company,project` query param is supported and sideloads the matching companies + projects from the main fixture set (so Pulse's relationship-resolution logic works without changes).

If `CLIENT_ENG_UTIL_REPORT_ID` is overridden to anything other than `1591877`, the sandbox returns 404. To support custom IDs, override the constant `CLIENT_ENG_UTIL_REPORT_ID` in `pulse_sandbox/productive/fixtures.py`.

### Time Reports — 8 rows across 2 weeks

All metrics in **minutes** (Pulse divides by 60 for hours).

ID format: `weekly-YYYY-MM-DD-person-{person_id}` — Pulse parses this string by splitting on `-person-`.

Two weeks covered: 2026-04-27 and 2026-05-04. Persons 701, 702, 703, 704 each have one row per week.

### Custom Fields — Critical: IDs match Servant production

Pulse's parser hard-codes these IDs. **Do not change them** unless you also patch Pulse.

| Field ID | Name | Options |
|---|---|---|
| 55149 | Employee Type | 179224 (FTE), 179228 (Contractor), 179226 (Freelance), 179230 (Advisor), 263656 (Placeholder) |
| 55151 | Deployable Team | 179232 (Billable) |
| 55153 | % Allocation | (numeric) |
| 55147 | Discipline | 300001 (Engineering), 300002 (Strategy) |

## SDK shim "fixtures"

The SDK shims don't carry data fixtures in the traditional sense — they return canned responses tuned to satisfy Pulse's parser:

- **OpenAI shim** — returns a fixed PMO-style transcript ("We had a strong week. The CLT migration is on track..."), and inspects the chat-completion prompt to decide whether to return cleaned text or a JSON synthesis object.
- **Resend shim** — returns a fake `id` like `sandbox-{uuid}` and a `created_at` timestamp.
- **Slack shim** — has a 4-user pre-seeded directory for `users_lookupByEmail`. Channels are created on-demand and stored in process memory.

## How to extend

### Adding a new deal to HubSpot fixtures

In `pulse_sandbox/hubspot/fixtures.py`, append to the `DEALS` list using the `_deal_props()` helper:

```python
{
    "id": "9009",
    "properties": _deal_props(
        name="Your New Deal",
        amount="50000",
        stage="qualifiedtobuy",
        confidence="High",
        owner="111111",
        service_type="Strategic Consulting",
        # ... other params
    ),
    "createdAt": _iso(_NOW - timedelta(days=10)),
    "updatedAt": _iso(_NOW - timedelta(days=2)),
    "archived": False,
},
```

Don't forget to add a row to `DEAL_COMPANY_ASSOCIATIONS` if the new deal links to a company.

### Adding a new person to Productive fixtures

Use the `_person()` helper:

```python
_person("708", "Hayden", "Sims", "hayden.sims@example.com", OPT_FTE, "402", 100),
```

Then append to the `PEOPLE` list.

### Adding a new time-report week

Use the `_time_report()` helper:

```python
_time_report("701", "2026-05-11", worked=1740, client=1440, internal=300),
```

Then append to the `TIME_REPORTS` list.

### Anonymized real data (Phase 2)

Phase 2 will add a JSON loader. The current shape will stay the same — fixtures will be loaded from `~/path/to/anonymized.json` keyed on env var `PULSE_SANDBOX_FIXTURES_DIR`. Until then, hand-curate.

When Phase 2 lands, the anonymization rules:
- Replace all real names with synthetic names (use Faker)
- Replace company names with fictional ones
- Replace email domains with `@example.com`
- Round dollar amounts to nearest $1k to obscure exact deal values
- Keep custom field IDs and option IDs **unchanged** (those are config, not data)
