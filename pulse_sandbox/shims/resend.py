"""Resend SDK shim.

Resend's real Python SDK exposes `resend.api_key` (module-level) and `resend.Emails.send(payload)`.
This shim mirrors that surface and logs the payload instead of sending. Returns a fake send-success.
"""

from __future__ import annotations

import logging
import time
import uuid

logger = logging.getLogger("pulse_sandbox.shims.resend")

# Module-level api_key attribute, mirrors `resend.api_key = ...`
api_key: str | None = None


class Emails:
    """Mirrors `resend.Emails.send(payload)`."""

    @staticmethod
    def send(payload: dict) -> dict:
        log_lines = [
            "[sandbox-resend] Email NOT sent (sandbox mode)",
            f"  to:      {payload.get('to')}",
            f"  from:    {payload.get('from')}",
            f"  reply_to:{payload.get('reply_to')}",
            f"  subject: {payload.get('subject')}",
            f"  html len:{len(payload.get('html', '') or '')}",
            f"  text len:{len(payload.get('text', '') or '')}",
        ]
        for line in log_lines:
            logger.info(line)
        return {
            "id": f"sandbox-{uuid.uuid4()}",
            "from": payload.get("from"),
            "to": payload.get("to"),
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
