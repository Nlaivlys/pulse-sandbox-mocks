"""OpenAI SDK shim.

Provides a stand-in `OpenAI` class that mimics the subset of the SDK Pulse uses:
- client.audio.transcriptions.create(model, file)
- client.chat.completions.create(model, messages, temperature, max_tokens, response_format)

Returns shape-correct response objects (with `.text`, `.choices[0].message.content`, `.usage`).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class _Usage:
    prompt_tokens: int = 100
    completion_tokens: int = 80
    total_tokens: int = 180


@dataclass
class _Message:
    content: str
    role: str = "assistant"


@dataclass
class _Choice:
    message: _Message
    finish_reason: str = "stop"
    index: int = 0


@dataclass
class _ChatCompletion:
    choices: list[_Choice]
    usage: _Usage = field(default_factory=_Usage)
    model: str = "gpt-4o-mini"
    id: str = "chatcmpl-sandbox-1"


@dataclass
class _Transcription:
    text: str


class _Transcriptions:
    def create(self, model: str, file, **kwargs) -> _Transcription:  # noqa: ANN001 - file is BinaryIO
        # Closing the file if it's the SDK passing one — be tolerant
        try:
            if hasattr(file, "close"):
                file.close()
        except Exception:
            pass
        return _Transcription(
            text=(
                "We had a strong week. The CLT migration is on track for the May 21 cutover. "
                "Risk on the Parrott rollout: timeline is tight but the team is unblocked. "
                "Carey ingestion is healthy. No new escalations."
            )
        )


class _Audio:
    def __init__(self) -> None:
        self.transcriptions = _Transcriptions()


class _ChatCompletions:
    def create(
        self,
        model: str,
        messages: list[dict],
        temperature: float = 0.2,
        max_tokens: int = 1500,
        response_format: dict | None = None,
        **kwargs,
    ) -> _ChatCompletion:
        # Examine the system prompt to decide which canned response to return.
        system_prompt = ""
        user_content = ""
        for msg in messages:
            if msg.get("role") == "system":
                system_prompt = msg.get("content", "")
            if msg.get("role") == "user":
                user_content = msg.get("content", "")

        # If response_format requests JSON, return valid JSON.
        if response_format and response_format.get("type") == "json_object":
            content = (
                '{"summary": "Multi-PM check-in synthesis: CLT, Carey, and Parrott workstreams are '
                'all green or yellow. CLT migration is the highest-risk in-flight work. AI ingestion '
                "for Carey continues to land cleanly. Parrott portfolio has tight timeline pressure but "
                'no escalations.", "ranking": 4}'
            )
        elif "clean" in system_prompt.lower() or "filler" in system_prompt.lower():
            # Cleanup prompt — return a "cleaned" version of the user content
            content = (user_content or "").replace(" um, ", " ").replace(" uh, ", " ").strip() or (
                "We had a strong week. The CLT migration is on track for the May 21 cutover. "
                "Risk on the Parrott rollout: timeline is tight but the team is unblocked. "
                "Carey ingestion is healthy. No new escalations."
            )
        else:
            content = "Sandbox response — OpenAI SDK shim active. No real model was called."

        return _ChatCompletion(choices=[_Choice(message=_Message(content=content))])


class _Chat:
    def __init__(self) -> None:
        self.completions = _ChatCompletions()


class OpenAI:
    """Drop-in replacement for openai.OpenAI when running in sandbox mode."""

    def __init__(self, api_key: str | None = None, **kwargs) -> None:
        self.api_key = api_key or "sandbox-fake-key"
        self.audio = _Audio()
        self.chat = _Chat()
