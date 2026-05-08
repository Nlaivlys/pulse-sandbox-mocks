"""HubSpot fixture re-export layer.

Reads the active profile (via PULSE_SANDBOX_PROFILE) and re-exports the
HubSpot subset of its namespaced constants under service-local names.
Routes import from this module — they don't need to know which profile
is active.

The actual fixture data lives in `pulse_sandbox/profiles/{name}.py`.
"""

from __future__ import annotations

from pulse_sandbox.profiles import load_active_profile

_p = load_active_profile()

OWNERS = _p.HUBSPOT_OWNERS
COMPANIES = _p.HUBSPOT_COMPANIES
DEALS = _p.HUBSPOT_DEALS
DEAL_COMPANY_ASSOCIATIONS = _p.HUBSPOT_DEAL_COMPANY_ASSOC
PIPELINE_STAGES = _p.HUBSPOT_PIPELINE_STAGES
PIPELINES = _p.HUBSPOT_PIPELINES
DEAL_PROPERTIES = _p.HUBSPOT_DEAL_PROPERTIES
