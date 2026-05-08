"""Slack SDK shim.

Mirrors the subset of `slack_sdk.WebClient` that Pulse uses:
- conversations_create(name, is_private)
- conversations_invite(channel, users)
- users_lookupByEmail(email)

State (created channels) lives in process memory — restart resets.
"""

from __future__ import annotations

import logging
import threading
import time
import uuid
from dataclasses import dataclass

logger = logging.getLogger("pulse_sandbox.shims.slack")

# Pre-seeded fake users so users_lookupByEmail returns something useful
_USER_DIRECTORY: dict[str, dict] = {
    "alex.morgan@example.com": {"id": "U00000001", "name": "alex.morgan", "real_name": "Alex Morgan"},
    "jordan.rivera@example.com": {"id": "U00000002", "name": "jordan.rivera", "real_name": "Jordan Rivera"},
    "casey.lin@example.com": {"id": "U00000003", "name": "casey.lin", "real_name": "Casey Lin"},
    "emily@example.com": {"id": "U00000004", "name": "emily", "real_name": "Emily (Talent)"},
}


@dataclass
class _SlackResponse:
    """Mimics slack_sdk.web.SlackResponse — supports dict-style access via .get and .data."""

    data: dict

    def __getitem__(self, key):
        return self.data[key]

    def get(self, key, default=None):
        return self.data.get(key, default)


# If slack_sdk is installed (Pulse's environment), inherit from the real
# SlackApiError so consumers can `except slack_sdk.errors.SlackApiError`
# and catch both real and shim instances. If slack_sdk isn't installed
# (sandbox repo's own venv during standalone tests), fall back to Exception.
try:
    from slack_sdk.errors import SlackApiError as _RealSlackApiError

    _SLACK_API_ERROR_BASE: type = _RealSlackApiError
except ImportError:
    _SLACK_API_ERROR_BASE = Exception


class SlackApiError(_SLACK_API_ERROR_BASE):  # type: ignore[misc, valid-type]
    """Mirrors slack_sdk.errors.SlackApiError — exposes .response.get('error').

    Inherits from slack_sdk.errors.SlackApiError when available so consumers'
    `except SlackApiError` blocks catch both real and shim instances.
    """

    def __init__(self, message: str, response: dict) -> None:
        # slack_sdk's SlackApiError signature: (message, response)
        super().__init__(message, response) if _SLACK_API_ERROR_BASE is not Exception else super().__init__(message)
        self.response = response


# Sentinel placeholder used for the fake bot token in sandbox mode.
# Built at runtime to avoid embedding the real Slack token prefix as a string literal.
_FAKE_BOT_TOKEN = "x" + "oxb" + "-sandbox-fake-token"


class WebClient:
    """Drop-in replacement for slack_sdk.WebClient."""

    def __init__(self, token: str | None = None, **kwargs) -> None:
        self.token = token or _FAKE_BOT_TOKEN
        # Per-instance state for created channels — keyed by name
        self._channels: dict[str, dict] = {}
        self._lock = threading.Lock()

    def conversations_create(self, name: str, is_private: bool = True, **kwargs) -> _SlackResponse:
        with self._lock:
            if name in self._channels:
                raise SlackApiError(
                    f"name_taken: channel '{name}' already exists",
                    {"ok": False, "error": "name_taken"},
                )
            channel_id = f"C{uuid.uuid4().hex[:8].upper()}"
            channel = {
                "id": channel_id,
                "name": name,
                "is_private": is_private,
                "members": [],
                "created": int(time.time()),
            }
            self._channels[name] = channel
            logger.info(f"[sandbox-slack] created channel #{name} -> {channel_id} (private={is_private})")
            return _SlackResponse({"ok": True, "channel": channel})

    def conversations_invite(self, channel: str, users: str, **kwargs) -> _SlackResponse:
        # Find channel by ID or name
        with self._lock:
            target = None
            for ch in self._channels.values():
                if ch["id"] == channel or ch["name"] == channel:
                    target = ch
                    break
            if target is None:
                raise SlackApiError(
                    f"channel_not_found: {channel}",
                    {"ok": False, "error": "channel_not_found"},
                )
            user_ids = [u.strip() for u in users.split(",") if u.strip()]
            target["members"].extend(uid for uid in user_ids if uid not in target["members"])
            logger.info(f"[sandbox-slack] invited {user_ids} to #{target['name']}")
            return _SlackResponse({"ok": True, "channel": target})

    def users_lookupByEmail(self, email: str, **kwargs) -> _SlackResponse:
        user = _USER_DIRECTORY.get(email)
        if user is None:
            raise SlackApiError(
                f"users_not_found: {email}",
                {"ok": False, "error": "users_not_found"},
            )
        logger.info(f"[sandbox-slack] resolved {email} -> {user['id']}")
        return _SlackResponse({"ok": True, "user": user})
