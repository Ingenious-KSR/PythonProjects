"""Automated tests (run offline with the mock). Real-model quality is checked manually, see docs/TESTING.md."""
import json

import pytest

from llm import LLMError, MockClient, extract_json
from loader import InputError, load_tickets
from main import generate, main
from validate import validate_notes

S = "samples/"


def test_loader_json_filters_and_dedupes():
    ids = [t["id"] for t in load_tickets(S + "hotfix_messy.json")]
    assert ids == ["OPS-31", "OPS-32", "OPS-33", "OPS-35"]  # dup, in-progress, no-id all dropped


def test_loader_csv_keeps_open_known_issue():
    ids = [t["id"] for t in load_tickets(S + "migration_release.csv")]
    assert "DATA-203" in ids and len(ids) == 7


def test_loader_errors():
    with pytest.raises(InputError):
        load_tickets("nope.json")


def test_extract_json_handles_fences_and_prose():
    assert extract_json('Sure!\n```json\n{"a": 1}\n```') == {"a": 1}
    with pytest.raises(LLMError):
        extract_json("no json here")


def test_validator_catches_hallucination_and_omission():
    tickets = load_tickets(S + "sprint_24_payments.json")
    notes = json.loads(MockClient().complete("", [{"role": "user", "content":
        "<tickets>\n" + json.dumps(tickets) + "\n</tickets>"}]))
    assert validate_notes(notes, tickets) == []
    notes["entries"][0]["ticket_id"] = "FAKE-999"
    problems = " ".join(validate_notes(notes, tickets))
    assert "hallucinated" in problems and "PAY-101 is missing" in problems


def test_retry_then_fail_when_model_keeps_returning_bad_json():
    class Bad:
        model = "bad"
        def complete(self, system, messages):
            return '{"summary": "x", "highlights": [], "entries": []}'
    with pytest.raises(LLMError):
        generate(Bad(), load_tickets(S + "sprint_24_payments.json"), "P", "1", "2026-01-01")


@pytest.mark.parametrize("sample,must_have", [
    ("sprint_24_payments.json", ["Breaking Changes", "Security", "Bug Fixes"]),
    ("hotfix_messy.json", ["Needs Human Review"]),       # OPS-32 is vague -> flagged
    ("migration_release.csv", ["Known Issues", "Breaking Changes"]),
])
def test_end_to_end_mock(tmp_path, sample, must_have):
    assert main(["--input", S + sample, "--mock", "--out", str(tmp_path)]) == 0
    client = (tmp_path / "release_notes_client.md").read_text()
    tech = (tmp_path / "changelog_technical.md").read_text()
    for section in must_have:
        assert section in client + tech
    assert "Internal" not in client  # internal work never leaks to clients
    assert (tmp_path / "run.log").exists()


def test_cli_exit_codes(tmp_path, monkeypatch):
    assert main(["--input", "missing.json", "--mock", "--out", str(tmp_path)]) == 2
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert main(["--input", S + "hotfix_messy.json", "--out", str(tmp_path)]) == 3
