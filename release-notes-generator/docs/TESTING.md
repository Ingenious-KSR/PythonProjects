# Testing approach

## Layers
1. **Automated (offline)**: `python -m pytest -q` runs 10 tests using the mock: loader filtering/dedupe, JSON extraction,
   validator catches hallucinated and missing tickets, retry-then-fail, end-to-end on all 3 samples, CLI exit codes.
2. **Manual (real model)**: run each sample without `--mock` and compare against the "good output" checklists below.

## Samples and what "good output" looks like

### Sample 1: `samples/sprint_24_payments.json` (clean sprint, 8 tickets)
- [ ] PAY-104 (v1 -> v2 endpoint) is under **Breaking Changes**, mentions that integrators must update, and is in Needs Human Review.
- [ ] PAY-103 (TLS 1.2+) is under **Security**; the technical text says older TLS clients will fail.
- [ ] PAY-106 (refactor) appears ONLY in the technical changelog under Internal.
- [ ] PAY-102 is a **Fix**; client text says "charged twice" in plain words and does NOT say "idempotency key".
- [ ] PAY-105 technical text keeps the numbers 4.2s -> 1.1s (no invented figures).
- [ ] Client text contains no ticket ids; all 8 tickets appear exactly once in `notes.json`.

### Sample 2: `samples/hotfix_messy.json` (messy export)
- [ ] Only OPS-31, 32, 33, 35 are processed (log shows the duplicate, the In-Progress OPS-34 and the id-less row skipped).
- [ ] OPS-32 ("misc fixes", empty description) is **flagged needs_attention** and its text is NOT embellished.
- [ ] OPS-31 client text is readable English (not "login broken on safari"), technical text mentions SameSite.
- [ ] OPS-35 is Internal (not shown to clients).

### Sample 3: `samples/migration_release.csv` (migration, CSV, known issue)
- [ ] DATA-201 is Breaking, with the migration script name and ~10 min downtime in the technical text.
- [ ] DATA-203 (open, `known-issue`) is under **Known Issues**, mentions the date-filter workaround, and is not described as fixed.
- [ ] DATA-205 is Security; client text does NOT reveal details of the leaked key beyond "rotated / strengthened".
- [ ] DATA-206 (Node upgrade) is Internal.
- [ ] Section order: Breaking, Security, Features, Improvements, Fixes, Known Issues.

## Failure-path checks (manual)
| Action | Expected |
|---|---|
| `--input missing.json` | log "Input problem", exit code 2 |
| Run without `ANTHROPIC_API_KEY` (no `--mock`) | "ANTHROPIC_API_KEY is not set", exit code 3 |
| Wrong key | "Authentication failed", exit code 3 |
| File with only In-Progress tickets | "No releasable tickets found", exit code 2 |

## Results log (fill in after your runs)
| Date | Sample | Model | Checklist passed | Notes / prompt changes made |
|---|---|---|---|---|
| | | | | |
