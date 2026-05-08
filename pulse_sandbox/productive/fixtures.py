"""Productive fixture re-export layer.

Reads the active profile (via PULSE_SANDBOX_PROFILE) and re-exports the
Productive subset of its namespaced constants under service-local names.
Routes import from this module — they don't need to know which profile
is active.

The actual fixture data lives in `pulse_sandbox/profiles/{name}.py`.
"""

from __future__ import annotations

from pulse_sandbox.profiles import load_active_profile

_p = load_active_profile()

PEOPLE = _p.PRODUCTIVE_PEOPLE
TEAMS = _p.PRODUCTIVE_TEAMS
COMPANIES = _p.PRODUCTIVE_COMPANIES
PROJECTS = _p.PRODUCTIVE_PROJECTS
BUDGETS = _p.PRODUCTIVE_BUDGETS
DEALS = _p.PRODUCTIVE_DEALS
SERVICES = _p.PRODUCTIVE_SERVICES
BOOKINGS = _p.PRODUCTIVE_BOOKINGS
TIME_REPORTS = _p.PRODUCTIVE_TIME_REPORTS
BUDGET_REPORTS = _p.PRODUCTIVE_BUDGET_REPORTS
CUSTOM_FIELDS = _p.PRODUCTIVE_CUSTOM_FIELDS
CUSTOM_FIELD_OPTIONS_INCLUDED = _p.PRODUCTIVE_CUSTOM_FIELD_OPTIONS_INCLUDED
SCENARIOS = _p.PRODUCTIVE_SCENARIOS
SAVED_REPORT_BUDGETS = _p.PRODUCTIVE_SAVED_REPORT_BUDGETS
CLIENT_ENG_UTIL_REPORT_ID = _p.PRODUCTIVE_CLIENT_ENG_UTIL_REPORT_ID
