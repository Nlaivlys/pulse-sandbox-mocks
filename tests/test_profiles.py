"""Tests for the profile system — verifies the loader picks up
PULSE_SANDBOX_PROFILE correctly and that each profile module exposes the
expected fixture data.

Each scenario deal in the rich profile gets a focused test asserting the
specific Pulse warning/feature it's designed to exercise.
"""

from __future__ import annotations

import importlib

import pytest


def _reload_with_profile(monkeypatch, profile: str):
    """Set PULSE_SANDBOX_PROFILE and force fixture modules to re-import."""
    monkeypatch.setenv("PULSE_SANDBOX_PROFILE", profile)
    from pulse_sandbox import profiles
    from pulse_sandbox.hubspot import fixtures as hs_fix
    from pulse_sandbox.productive import fixtures as prod_fix

    importlib.reload(profiles)
    importlib.reload(hs_fix)
    importlib.reload(prod_fix)
    return hs_fix, prod_fix


# ---------------------------------------------------------------------------
# Loader behavior
# ---------------------------------------------------------------------------
class TestProfileLoader:
    def test_default_is_baseline(self, monkeypatch) -> None:
        monkeypatch.delenv("PULSE_SANDBOX_PROFILE", raising=False)
        from pulse_sandbox import profiles

        importlib.reload(profiles)
        active = profiles.load_active_profile()
        assert active.__name__ == "pulse_sandbox.profiles.baseline"

    def test_explicit_baseline(self, monkeypatch) -> None:
        monkeypatch.setenv("PULSE_SANDBOX_PROFILE", "baseline")
        from pulse_sandbox import profiles

        importlib.reload(profiles)
        active = profiles.load_active_profile()
        assert active.__name__ == "pulse_sandbox.profiles.baseline"

    def test_explicit_rich(self, monkeypatch) -> None:
        monkeypatch.setenv("PULSE_SANDBOX_PROFILE", "rich")
        from pulse_sandbox import profiles

        importlib.reload(profiles)
        active = profiles.load_active_profile()
        assert active.__name__ == "pulse_sandbox.profiles.rich"

    def test_unknown_profile_raises(self, monkeypatch) -> None:
        monkeypatch.setenv("PULSE_SANDBOX_PROFILE", "nonexistent")
        from pulse_sandbox import profiles

        importlib.reload(profiles)
        with pytest.raises(ModuleNotFoundError, match="Available profiles"):
            profiles.load_active_profile()

    def test_empty_string_falls_back_to_baseline(self, monkeypatch) -> None:
        monkeypatch.setenv("PULSE_SANDBOX_PROFILE", "")
        from pulse_sandbox import profiles

        importlib.reload(profiles)
        active = profiles.load_active_profile()
        assert active.__name__ == "pulse_sandbox.profiles.baseline"

    def test_list_available_profiles_includes_baseline_and_rich(self) -> None:
        from pulse_sandbox import profiles

        names = profiles._list_available_profiles()
        assert "baseline" in names
        assert "rich" in names


# ---------------------------------------------------------------------------
# Baseline profile content
# ---------------------------------------------------------------------------
class TestBaseline:
    def test_hubspot_deals_count(self, monkeypatch) -> None:
        hs, _ = _reload_with_profile(monkeypatch, "baseline")
        assert len(hs.DEALS) == 8

    def test_hubspot_companies_count(self, monkeypatch) -> None:
        hs, _ = _reload_with_profile(monkeypatch, "baseline")
        assert len(hs.COMPANIES) == 4

    def test_productive_scenarios_count(self, monkeypatch) -> None:
        _, prod = _reload_with_profile(monkeypatch, "baseline")
        assert len(prod.SCENARIOS) == 4

    def test_productive_people_count(self, monkeypatch) -> None:
        _, prod = _reload_with_profile(monkeypatch, "baseline")
        assert len(prod.PEOPLE) == 7


# ---------------------------------------------------------------------------
# Rich profile — adds 5 scenario-tuned deals (+1 company)
# ---------------------------------------------------------------------------
class TestRichProfileExtensions:
    def test_extends_hubspot_deals(self, monkeypatch) -> None:
        hs, _ = _reload_with_profile(monkeypatch, "rich")
        # baseline 8 + 5 scenario deals = 13
        assert len(hs.DEALS) == 13

    def test_extends_hubspot_companies(self, monkeypatch) -> None:
        hs, _ = _reload_with_profile(monkeypatch, "rich")
        assert len(hs.COMPANIES) == 5
        # New Echo Foundation must be present (id 5005)
        ids = {c["id"] for c in hs.COMPANIES}
        assert "5005" in ids

    def test_extends_productive_scenarios(self, monkeypatch) -> None:
        _, prod = _reload_with_profile(monkeypatch, "rich")
        assert len(prod.SCENARIOS) == 5

    def test_baseline_data_unchanged(self, monkeypatch) -> None:
        """Rich profile is purely additive — baseline entities all still present."""
        hs, prod = _reload_with_profile(monkeypatch, "rich")
        # Original HubSpot deal IDs (9001-9008) all still in DEALS
        ids = {d["id"] for d in hs.DEALS}
        for orig in ("9001", "9002", "9003", "9004", "9005", "9006", "9007", "9008"):
            assert orig in ids, f"baseline deal {orig} missing from rich profile"
        # Productive people, projects, time-reports unchanged
        assert len(prod.PEOPLE) == 7
        assert len(prod.PROJECTS) == 5


# ---------------------------------------------------------------------------
# Rich profile — each scenario deal pinned to a specific Pulse signal
# ---------------------------------------------------------------------------
class TestRichScenarios:
    """Each test asserts the data shape that triggers the corresponding
    Pulse warning or feature. Use these as anchors when building dashboards
    or alerts that depend on these states."""

    def _get_deal(self, deals: list, deal_id: str) -> dict:
        for d in deals:
            if d["id"] == deal_id:
                return d
        pytest.fail(f"deal {deal_id} not found in rich profile")

    def test_9101_overdue_open_deal(self, monkeypatch) -> None:
        """9101 — open deal whose closedate is in the past. Triggers Pulse's
        'Need Date Update' warning on the HC Deals page."""
        hs, _ = _reload_with_profile(monkeypatch, "rich")
        deal = self._get_deal(hs.DEALS, "9101")
        props = deal["properties"]
        assert props["hs_is_closed"] == "false", "must be open"
        # closedate should be in the past relative to fixture _NOW (2026-05-08 12:00)
        assert props["closedate"] < "2026-05-08", f"closedate {props['closedate']} must be in past"
        assert props["confidence"] == "High"

    def test_9102_stuck_stage(self, monkeypatch) -> None:
        """9102 — open deal with createdate == updatedate (no movement).
        Triggers staleness signal."""
        hs, _ = _reload_with_profile(monkeypatch, "rich")
        deal = self._get_deal(hs.DEALS, "9102")
        assert deal["createdAt"] == deal["updatedAt"], "createdAt and updatedAt should match (stuck)"
        # createdate must be at least 30 days old to be 'stuck'
        from datetime import datetime as _dt

        created = _dt.fromisoformat(deal["createdAt"].replace("Z", "+00:00"))
        now = _dt(2026, 5, 8, 12, 0, 0, tzinfo=created.tzinfo)
        days_old = (now - created).days
        assert days_old >= 30, f"stuck deal must be >=30 days old, got {days_old}"

    def test_9103_orphan_missing_lead_and_service_type(self, monkeypatch) -> None:
        """9103 — open deal with no engagement_lead_name + no service_type.
        Triggers data-quality alert."""
        hs, _ = _reload_with_profile(monkeypatch, "rich")
        deal = self._get_deal(hs.DEALS, "9103")
        props = deal["properties"]
        assert props["engagement_lead_name"] == "", "engagement_lead_name should be empty"
        assert props["service_type"] == "", "service_type should be empty"
        assert props["hs_is_closed"] == "false", "still open"

    def test_9104_just_created(self, monkeypatch) -> None:
        """9104 — createdate is today. Triggers freshness signal."""
        hs, _ = _reload_with_profile(monkeypatch, "rich")
        deal = self._get_deal(hs.DEALS, "9104")
        # createdate matches fixture _NOW (2026-05-08T12:00:00Z)
        assert deal["properties"]["createdate"].startswith("2026-05-08")

    def test_9105_recent_win(self, monkeypatch) -> None:
        """9105 — closedwon stage with closedate yesterday. Triggers
        recently-won pipeline accumulation."""
        hs, _ = _reload_with_profile(monkeypatch, "rich")
        deal = self._get_deal(hs.DEALS, "9105")
        props = deal["properties"]
        assert props["dealstage"] == "closedwon"
        assert props["hs_is_closed"] == "true"
        # closedate is yesterday (2026-05-07)
        assert props["closedate"].startswith("2026-05-07")


# ---------------------------------------------------------------------------
# Productive scenario coverage in rich profile
# ---------------------------------------------------------------------------
class TestRichScenarioCoverage:
    def test_only_9102_has_productive_scenario(self, monkeypatch) -> None:
        """Of the 5 new HubSpot deals in rich, only 9102 (stuck-stage) gets a
        Productive scenario. The other 4 lack scenarios so the 'Missing
        Productive Scenarios' warning fires across multiple deal types."""
        _, prod = _reload_with_profile(monkeypatch, "rich")
        # Look at scenario relationships — at least one must reference a deal
        # named with the stuck-negotiation signal
        new_scenario_names = [
            s["attributes"]["name"] for s in prod.SCENARIOS
            if "Stuck" in s["attributes"].get("name", "")
        ]
        assert len(new_scenario_names) == 1
