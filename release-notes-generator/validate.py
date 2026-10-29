"""Guardrails on model output. LLM output is untrusted input: check it like any other.

Returns a list of human-readable problems (empty list == valid). The same list is fed
back to the model for one self-correction retry (see main.py).
"""
import re

from prompts import CATEGORIES, IMPACTS

TICKET_ID = re.compile(r"\b[A-Z][A-Z0-9]+-\d+\b")


def validate_notes(notes: dict, tickets: list[dict]) -> list[str]:
    problems = []
    for key in ("summary", "highlights", "entries"):
        if key not in notes:
            problems.append(f"Missing top-level key '{key}'")
    if problems:
        return problems

    expected = {t["id"] for t in tickets}
    seen = []
    for i, e in enumerate(notes["entries"]):
        tid = e.get("ticket_id")
        seen.append(tid)
        if tid not in expected:
            problems.append(f"Entry {i}: ticket_id '{tid}' is not in the input (hallucinated)")
        if e.get("category") not in CATEGORIES:
            problems.append(f"{tid}: invalid category '{e.get('category')}'")
        if e.get("impact") not in IMPACTS:
            problems.append(f"{tid}: invalid impact '{e.get('impact')}'")
        if not str(e.get("business_text", "")).strip():
            problems.append(f"{tid}: empty business_text")
        elif TICKET_ID.search(e["business_text"]):
            problems.append(f"{tid}: business_text must not contain ticket ids")
        if e.get("needs_attention") and not e.get("attention_reason"):
            problems.append(f"{tid}: needs_attention is true but attention_reason is empty")

    for tid in expected - set(seen):
        problems.append(f"Ticket {tid} is missing from the output")
    for tid in {x for x in seen if seen.count(x) > 1}:
        problems.append(f"Ticket {tid} appears more than once")
    return problems
