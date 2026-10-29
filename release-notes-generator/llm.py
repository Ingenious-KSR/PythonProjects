"""LLM access: a real Anthropic client and a deterministic mock with the same interface.

The mock exists so reviewers (and CI) can run the entire pipeline with no API key.
It is rule-based, so it exercises loader -> prompt -> parse -> validate -> render,
but only the real model demonstrates prompt quality.
"""
import json
import logging
import os
import re
import time

log = logging.getLogger("rng.llm")

DEFAULT_MODEL = os.getenv("RNG_MODEL", "claude-sonnet-5-5")


class LLMError(Exception):
    """Raised when the model cannot be reached or returns unusable output."""


def extract_json(text: str) -> dict:
    """Models sometimes wrap JSON in prose or ``` fences; grab the outermost object."""
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        raise LLMError("No JSON object found in model response")
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError as exc:
        raise LLMError(f"Model returned invalid JSON: {exc}") from exc


class AnthropicClient:
    def __init__(self, model: str = DEFAULT_MODEL, max_retries: int = 3):
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise LLMError("ANTHROPIC_API_KEY is not set. Export it, or run with --mock.")
        try:
            import anthropic
        except ImportError as exc:
            raise LLMError("Run `pip install -r requirements.txt` first.") from exc
        self._anthropic = anthropic
        self.client = anthropic.Anthropic()
        self.model, self.max_retries = model, max_retries

    def complete(self, system: str, messages: list[dict]) -> str:
        a = self._anthropic
        for attempt in range(1, self.max_retries + 1):
            try:
                log.info("Calling %s (attempt %d)", self.model, attempt)
                resp = self.client.messages.create(
                    model=self.model, max_tokens=4000, temperature=0.2,  # low temp = consistent format
                    system=system, messages=messages,
                )
                log.info("Tokens in/out: %s/%s", resp.usage.input_tokens, resp.usage.output_tokens)
                return "".join(b.text for b in resp.content if b.type == "text")
            except (a.RateLimitError, a.APIConnectionError, a.InternalServerError) as exc:
                wait = 2 ** attempt  # exponential backoff for transient errors only
                log.warning("Transient API error (%s); retrying in %ss", type(exc).__name__, wait)
                time.sleep(wait)
            except a.AuthenticationError as exc:
                raise LLMError("Authentication failed - check ANTHROPIC_API_KEY.") from exc
            except a.APIStatusError as exc:  # 4xx etc: retrying will not help
                raise LLMError(f"API rejected the request: {exc.status_code} {exc.message}") from exc
        raise LLMError(f"Gave up after {self.max_retries} attempts")


class MockClient:
    """Deterministic stand-in. Classifies by ticket type/labels and reuses titles as text."""
    model = "mock"

    def complete(self, system: str, messages: list[dict]) -> str:
        user = messages[0]["content"]
        tickets = json.loads(re.search(r"<tickets>\n(.*)\n</tickets>", user, re.S).group(1))
        entries = []
        for t in tickets:
            labels = set(t["labels"])
            if "breaking" in labels:
                cat = "breaking"
            elif "security" in labels:
                cat = "security"
            elif "known-issue" in labels:
                cat = "known_issue"
            elif labels & {"internal", "refactor", "tech-debt"}:
                cat = "internal"
            elif t["type"] == "bug":
                cat = "fix"
            elif t["type"] in {"story", "feature"}:
                cat = "feature"
            else:
                cat = "improvement"
            vague = len(t["description"]) < 15
            entries.append({
                "ticket_id": t["id"], "category": cat,
                "impact": "low" if cat == "internal" else ("high" if cat in {"breaking", "security"} else "medium"),
                "business_text": t["title"].rstrip(".") + ".",
                "technical_text": f"{t['component'] or 'general'}: {t['description'] or t['title']}"[:200],
                "needs_attention": vague or cat == "breaking",
                "attention_reason": ("Action required by integrators." if cat == "breaking"
                                     else "Description too vague to verify." if vague else ""),
            })
        return json.dumps({"summary": f"[MOCK] {len(entries)} changes shipped.",
                           "highlights": [e["business_text"] for e in entries[:3]],
                           "entries": entries})
