"""Tests for the SDK shims (OpenAI, Resend, Slack)."""

from __future__ import annotations

import io

import pytest

from pulse_sandbox.shims.openai import OpenAI as ShimOpenAI
from pulse_sandbox.shims.resend import Emails as ShimEmails
from pulse_sandbox.shims import resend as resend_module
from pulse_sandbox.shims.slack import SlackApiError, WebClient as ShimWebClient


# ---------------------------------------------------------------------------
# OpenAI shim
# ---------------------------------------------------------------------------
class TestOpenAIShim:
    def test_constructor_accepts_api_key(self) -> None:
        client = ShimOpenAI(api_key="anything")
        assert client.api_key == "anything"

    def test_constructor_provides_default_key(self) -> None:
        client = ShimOpenAI()
        assert client.api_key  # any non-empty default

    def test_transcribe_returns_text(self) -> None:
        client = ShimOpenAI()
        fake_file = io.BytesIO(b"fake audio bytes")
        result = client.audio.transcriptions.create(model="whisper-1", file=fake_file)
        assert hasattr(result, "text")
        assert isinstance(result.text, str)
        assert len(result.text) > 10  # Pulse asserts minimum length

    def test_chat_completion_basic(self) -> None:
        client = ShimOpenAI()
        result = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello"},
            ],
            temperature=0.2,
            max_tokens=500,
        )
        # Shape must match openai SDK response
        assert hasattr(result, "choices")
        assert len(result.choices) == 1
        assert hasattr(result.choices[0], "message")
        assert hasattr(result.choices[0].message, "content")
        assert isinstance(result.choices[0].message.content, str)
        # Usage object for token logging
        assert result.usage.prompt_tokens > 0
        assert result.usage.completion_tokens > 0
        assert result.usage.total_tokens > 0

    def test_chat_completion_returns_json_when_requested(self) -> None:
        """summarize_contributions in Pulse expects JSON output via response_format."""
        client = ShimOpenAI()
        result = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "synthesize check-ins"}],
            response_format={"type": "json_object"},
        )
        import json

        parsed = json.loads(result.choices[0].message.content)
        assert "summary" in parsed
        assert "ranking" in parsed


# ---------------------------------------------------------------------------
# Resend shim
# ---------------------------------------------------------------------------
class TestResendShim:
    def test_module_level_api_key_attribute(self) -> None:
        """Pulse code does `resend.api_key = RESEND_API_KEY` — module-level attr."""
        assert hasattr(resend_module, "api_key")
        resend_module.api_key = "test-key"
        assert resend_module.api_key == "test-key"

    def test_send_returns_success_dict(self) -> None:
        result = ShimEmails.send(
            {
                "from": "from@example.com",
                "to": "to@example.com",
                "subject": "Hello",
                "html": "<p>hi</p>",
                "text": "hi",
            }
        )
        # Resend SDK returns dict with 'id' on success
        assert "id" in result
        assert result["id"].startswith("sandbox-")

    def test_send_handles_missing_optional_fields(self) -> None:
        # No reply_to provided — must not crash
        result = ShimEmails.send(
            {"from": "a@b.com", "to": "x@y.com", "subject": "test", "html": "h", "text": "t"}
        )
        assert "id" in result


# ---------------------------------------------------------------------------
# Slack shim
# ---------------------------------------------------------------------------
class TestSlackShim:
    def test_create_channel_returns_id(self) -> None:
        client = ShimWebClient(token="anything")
        resp = client.conversations_create(name="hiring-acme-pm", is_private=True)
        assert resp["ok"] is True
        assert resp["channel"]["id"].startswith("C")
        assert resp["channel"]["name"] == "hiring-acme-pm"

    def test_create_channel_name_taken_raises(self) -> None:
        """name_taken is one of the error strings Pulse explicitly checks for."""
        client = ShimWebClient(token="anything")
        client.conversations_create(name="duplicate-name")
        with pytest.raises(SlackApiError) as exc_info:
            client.conversations_create(name="duplicate-name")
        assert exc_info.value.response.get("error") == "name_taken"

    def test_invite_to_channel(self) -> None:
        client = ShimWebClient(token="anything")
        ch = client.conversations_create(name="test-invite-channel")
        resp = client.conversations_invite(
            channel=ch["channel"]["id"],
            users="U00000001,U00000002",
        )
        assert resp["ok"] is True
        assert "U00000001" in resp["channel"]["members"]
        assert "U00000002" in resp["channel"]["members"]

    def test_invite_unknown_channel_raises(self) -> None:
        client = ShimWebClient(token="anything")
        with pytest.raises(SlackApiError) as exc_info:
            client.conversations_invite(channel="C-NONEXISTENT", users="U001")
        assert exc_info.value.response.get("error") == "channel_not_found"

    def test_lookup_user_by_email_known(self) -> None:
        client = ShimWebClient(token="anything")
        resp = client.users_lookupByEmail(email="emily@example.com")
        assert resp["ok"] is True
        assert resp["user"]["id"].startswith("U")

    def test_lookup_user_by_email_unknown_raises(self) -> None:
        """users_not_found is one of the error strings Pulse explicitly checks for."""
        client = ShimWebClient(token="anything")
        with pytest.raises(SlackApiError) as exc_info:
            client.users_lookupByEmail(email="nobody@nowhere.com")
        assert exc_info.value.response.get("error") == "users_not_found"

    def test_response_supports_dict_access(self) -> None:
        """slack_sdk responses are dict-accessible — Pulse does resp['channel'] etc."""
        client = ShimWebClient(token="anything")
        resp = client.conversations_create(name="dict-access-test")
        assert resp["ok"] is True  # __getitem__
        assert resp.get("ok") is True  # .get
        assert resp.get("nonexistent", "default") == "default"
