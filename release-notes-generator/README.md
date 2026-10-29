# AI Release Notes Generator

Turns a raw ticket export (Jira-style JSON or CSV) into **two** documents:
a client-friendly release note and a technical changelog, using the Claude API.

## Problem
Writing release notes by hand is repetitive and inconsistent. Ticket titles are written for
engineers, so they can't be sent to clients as-is. Breaking changes get buried, and
internal work leaks into client communication.

## Use cases
1. **Sprint demo / release day**: generate client-ready notes from a sprint's Done tickets.
2. **Hotfix with messy tickets**: produce notes safely; vague tickets are flagged for human review instead of guessed.
3. **Major migration**: breaking changes and known issues are surfaced first, with the required action.

## Setup (5 minutes)
```bash
cd release-notes-generator
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sk-ant-..."                  # Windows PowerShell: $env:ANTHROPIC_API_KEY="..."
```

## Run
```bash
# Offline (no key, deterministic mock - good for a first smoke test)
python main.py --input samples/sprint_24_payments.json --product PayHub --version 2.4.0 --mock

# Real AI
python main.py --input samples/sprint_24_payments.json --product PayHub --version 2.4.0
python main.py --input samples/hotfix_messy.json     --product OpsPortal --version 1.8.1
python main.py --input samples/migration_release.csv --product DataHub  --version 3.0.0 --out output/migration
```
Outputs in `output/`: `release_notes_client.md`, `changelog_technical.md`, `notes.json` (raw validated AI output), `run.log` (process log).

Override the model with `--model <id>` or `RNG_MODEL`.

## Test
```bash
python -m pytest -q
```
See `docs/TESTING.md` for the manual quality checks against the real model.

## Layout
| File | Role |
|---|---|
| `loader.py` | Parse JSON/CSV, normalise fields, dedupe, drop unshipped tickets |
| `prompts.py` | System prompt (rules, schema, few-shot), user/repair prompts |
| `llm.py` | Anthropic client (retries, error mapping) + offline mock |
| `validate.py` | Guardrails: no hallucinated/missing/duplicate tickets, valid enums |
| `render.py` | JSON -> Markdown (client and technical) |
| `main.py` | CLI, orchestration, one self-correction retry, logging, exit codes |

Exit codes: `0` ok, `2` bad input, `3` AI/API failure.

Docs: `docs/DESIGN.md`, `docs/TESTING.md`, `docs/AI_USAGE_LOG.md`.
