# AI usage log

> Keep this honest and specific. Replace/extend the entries below with your own real prompts and iterations.

## Tools used
- Claude (Anthropic): problem refinement, architecture review, code scaffolding, test-case and sample-data ideas.
- Claude API (`claude-sonnet-5-5`, configurable): the runtime AI step inside the product.

## Development-process log
| # | Phase | What I asked the AI | What I did with the answer |
|---|---|---|---|
| 1 | Problem | "Give me short problem statements for an engineering consultancy that suit a 200-500 line AI tool." | Picked release-notes generator over 5 alternatives: small, testable, two clear audiences. |
| 2 | Design | "Design a pipeline for ticket export -> release notes; where should AI be used and where plain code?" | Kept AI to one step; moved dedupe/filtering to code; added validator + one retry. |
| 3 | Prompt | "Draft a system prompt that avoids hallucination and outputs strict JSON." | Kept numbered rules and schema; added few-shot example and the `needs_attention` escape hatch. |
| 4 | Testing | "Create 3 realistic ticket sets including messy data, duplicates and a breaking change." | Became the 3 samples; wrote checklists from them. |
| 5 | Review | "Review my code for error handling gaps." | Added retries only for transient API errors; mapped auth errors to a clear message. |

## Prompt iterations (add your real ones)
| Version | Change | Reason | Observed effect |
|---|---|---|---|
| v1 | Plain "write release notes" | Baseline | Added ticket ids to client text; invented a benefit for vague tickets |
| v2 | Added rules 1, 2, 4, 7 | Fix the above | (record your result) |
| v3 | Added JSON schema and few-shot | Need machine-checkable output | (record your result) |
| v4 | Added repair prompt | Occasional missing ticket | (record your result) |

## Reflection
**Worked well:** hybrid design (code for deterministic work, AI for language); validator as a safety net; mock for repeatable tests.

**Would improve:** chunk very large releases; add a duplicate/related-ticket grouping step; read straight from the Jira API;
add an LLM-as-judge evaluation with a golden set; prompt caching for the static system prompt; support a team's style guide as extra context.

**Limits:** the mock only tests plumbing, not language quality; validation can't prove factual faithfulness, so a human still reviews the flagged items.
