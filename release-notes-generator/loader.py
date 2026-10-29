"""Load and normalise ticket exports (JSON or CSV) into a clean list of dicts.

Design decision: all cleaning happens here, in plain Python, BEFORE the LLM is
called. Deterministic work (dedupe, status filtering, truncation) is cheaper,
faster and more reliable in code than in a prompt.
"""
import csv
import json
import logging
from pathlib import Path

log = logging.getLogger("rng.loader")

DONE_STATUSES = {"done", "closed", "resolved", "released"}
MAX_DESC_CHARS = 800  # keeps token usage predictable on very long tickets


class InputError(Exception):
    """Raised when the input file is missing, malformed or has nothing releasable."""


def _split_labels(value) -> list[str]:
    if isinstance(value, list):
        items = value
    else:
        items = str(value or "").replace(";", ",").split(",")
    return [str(x).strip().lower() for x in items if str(x).strip()]


def _normalise(raw: dict) -> dict | None:
    """Map Jira-style / CSV field names onto one internal shape."""
    r = {str(k).strip().lower(): v for k, v in raw.items()}
    tid = str(r.get("id") or r.get("key") or "").strip()
    title = str(r.get("title") or r.get("summary") or "").strip()
    if not tid or not title:
        return None  # unusable row; caller logs it
    return {
        "id": tid,
        "title": title,
        "description": str(r.get("description") or "").strip()[:MAX_DESC_CHARS],
        "type": str(r.get("type") or r.get("issuetype") or "task").strip().lower(),
        "status": str(r.get("status") or "").strip().lower(),
        "labels": _split_labels(r.get("labels")),
        "component": str(r.get("component") or "").strip(),
        "priority": str(r.get("priority") or "").strip().lower(),
    }


def _read_rows(path: Path) -> list[dict]:
    try:
        if path.suffix.lower() == ".csv":
            with path.open(newline="", encoding="utf-8") as f:
                return list(csv.DictReader(f))
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, csv.Error) as exc:
        raise InputError(f"Could not parse {path.name}: {exc}") from exc
    rows = data.get("tickets") if isinstance(data, dict) else data
    if not isinstance(rows, list):
        raise InputError("JSON must be a list of tickets or {'tickets': [...]}")
    return rows


def load_tickets(path: str) -> list[dict]:
    p = Path(path)
    if not p.is_file():
        raise InputError(f"Input file not found: {path}")

    tickets, seen = [], set()
    for raw in _read_rows(p):
        t = _normalise(raw) if isinstance(raw, dict) else None
        if t is None:
            log.warning("Skipping row without id/title: %r", raw)
            continue
        if t["id"] in seen:  # exports often contain duplicates
            log.warning("Duplicate ticket %s ignored", t["id"])
            continue
        seen.add(t["id"])
        # Only shipped work belongs in release notes; open 'known-issue' tickets
        # are the one exception because we WANT to tell customers about them.
        if t["status"] in DONE_STATUSES or "known-issue" in t["labels"]:
            tickets.append(t)
        else:
            log.info("Excluded %s (status=%r, not shipped)", t["id"], t["status"])

    if not tickets:
        raise InputError("No releasable tickets found (need Done/Closed/Resolved status).")
    log.info("Loaded %d releasable tickets from %s", len(tickets), p.name)
    return tickets
