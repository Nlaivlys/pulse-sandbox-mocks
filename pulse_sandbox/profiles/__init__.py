"""Profile system — selects which fixture dataset is active.

The profile name comes from `PULSE_SANDBOX_PROFILE` (default `baseline`).
Each profile module under this package exports the full set of namespaced
fixtures (HUBSPOT_*, PRODUCTIVE_*) that hubspot/fixtures.py and
productive/fixtures.py re-export under their service-local names.

Available profiles:
- `baseline` — current happy-path data; what ships when nothing's set
- (others added in subsequent steps)

Changing the profile requires a server restart — env vars are read once
at module load.
"""

from __future__ import annotations

import importlib
import os


def load_active_profile():
    """Import and return the active profile module.

    Raises ModuleNotFoundError with a helpful message if the requested
    profile name doesn't exist.
    """
    name = (os.getenv("PULSE_SANDBOX_PROFILE") or "baseline").strip() or "baseline"
    try:
        return importlib.import_module(f"pulse_sandbox.profiles.{name}")
    except ModuleNotFoundError as exc:
        # Re-raise with a clearer message that includes available profiles
        available = _list_available_profiles()
        raise ModuleNotFoundError(
            f"PULSE_SANDBOX_PROFILE={name!r} could not be loaded. "
            f"Available profiles: {', '.join(available) or '(none)'}."
        ) from exc


def _list_available_profiles() -> list[str]:
    """Best-effort scan of profile module names in this package."""
    import pkgutil

    return sorted(
        modname
        for _, modname, ispkg in pkgutil.iter_modules(__path__)
        if not ispkg and not modname.startswith("_")
    )
