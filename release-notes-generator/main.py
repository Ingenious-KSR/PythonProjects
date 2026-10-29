"""CLI entry point: tickets file -> validated JSON -> client + technical release notes.

Usage:
  python main.py --input samples/sprint_24_payments.json --product "PayHub" --version 2.4.0
  python main.py --input samples/hotfix_messy.json --mock          # no API key needed
"""
import argparse
import json
import logging
import sys
from datetime import date as _date
from pathlib import Path

from llm import AnthropicClient, LLMError, MockClient, extract_json
from loader import InputError, load_tickets
from prompts import SYSTEM_PROMPT, build_repair_prompt, build_user_prompt
from render import render_client, render_technical
from validate import validate_notes

log = logging.getLogger("rng.main")


def generate(client, tickets, product, version, rel_date) -> dict:
    """Call the model; if validation fails, show it its own errors and retry ONCE."""
    messages = [{"role": "user", "content": build_user_prompt(tickets, product, version, rel_date)}]
    raw = client.complete(SYSTEM_PROMPT, messages)
    notes = extract_json(raw)
    problems = validate_notes(notes, tickets)
    if problems:
        log.warning("Validation failed (%d problems) - retrying once: %s", len(problems), problems)
        messages += [{"role": "assistant", "content": raw},
                     {"role": "user", "content": build_repair_prompt(problems)}]
        notes = extract_json(client.complete(SYSTEM_PROMPT, messages))
        problems = validate_notes(notes, tickets)
        if problems:
            raise LLMError("Output still invalid after retry: " + "; ".join(problems))
    log.info("Validation passed: %d entries", len(notes["entries"]))
    return notes


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="AI Release Notes Generator")
    ap.add_argument("--input", required=True, help="tickets file (.json or .csv)")
    ap.add_argument("--product", default="MyProduct")
    ap.add_argument("--version", default="1.0.0")
    ap.add_argument("--date", default=_date.today().isoformat())
    ap.add_argument("--out", default="output", help="output directory")
    ap.add_argument("--mock", action="store_true", help="use the offline mock instead of the API")
    ap.add_argument("--model", default=None)
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(  # console + file so reviewers can see the process afterwards
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler(out / "run.log", mode="w")],
    )
    try:
        tickets = load_tickets(args.input)
        client = MockClient() if args.mock else (
            AnthropicClient(args.model) if args.model else AnthropicClient())
        notes = generate(client, tickets, args.product, args.version, args.date)
    except InputError as exc:
        log.error("Input problem: %s", exc)
        return 2
    except LLMError as exc:
        log.error("AI step failed: %s", exc)
        return 3

    (out / "notes.json").write_text(json.dumps(notes, indent=2, ensure_ascii=False), encoding="utf-8")
    args_ = (notes, args.product, args.version, args.date)
    (out / "release_notes_client.md").write_text(render_client(*args_), encoding="utf-8")
    (out / "changelog_technical.md").write_text(render_technical(*args_), encoding="utf-8")
    log.info("Done. Files written to %s/", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
