# Evals — regression tests for fable-mode

These test the *skill*, not a user task: does giving Claude this skill
actually shift behavior in the direction the skill promises? Re-run after
editing the skill, and when the underlying model changes (SKILL.md itself
directs re-evaluating guardrails on model change). Maintenance-only: the
skill never reads this directory at runtime.

## How to run (skill-creator loop)

1. Snapshot the current skill version as the baseline (`cp -r`).
2. Apply your edits. For each eval in `evals.json`, run two fresh
   subagents on the same prompt — one pointed at the edited skill, one at
   the snapshot — saving all produced files plus the exact final
   user-facing message as `report.md`.
3. Grade each run against the eval's `assertions` with a fresh-context
   grader (evidence required — a bare claim of verification fails a
   verification assertion), aggregate pass rates, and review the outputs
   qualitatively.

The `skill-creator` skill automates this (workspace layout
`eval-*/with_skill/run-N/` + `grading.json` + benchmark aggregation +
review viewer).

## What each eval targets

- **0 ambiguous-build-unknowns-hunting** — SKILL.md Phases 0–1 and 3:
  assumptions/unknowns surfaced before building, deliverable connected to
  the stated intent, artifact verified by actually executing/rendering it.
- **1 described-problem-scope-discipline** — behavior-spec §6: a
  *described* problem gets an evidence-backed diagnosis and a stop, not an
  unrequested fix or refactor.
- **2 fable-facts-honest-recommendation** — model-facts honesty:
  weights-level vs emulable distinction, fact-freshness caveat, and a
  recommendation rather than a catalog.

## Fixtures (files/)

- `dedupe.py` contains a **deliberate bug** (all empty-email rows collapse
  onto key `""` and get dropped after the first). It is eval-1's test
  subject, not real code — do not "fix" it.
- `contacts.csv` (7 rows → correct dedupe keeps 6) and `team_metrics.csv`
  are synthetic.

## History & known issues

- **2026-07-06, iteration 1** (post-examples/templates version vs
  pre-): new 12/12, old 11/12. The only discriminating assertion was
  eval-0's "verifies by actually executing/rendering" (old version
  claimed verification without evidence). Evals 1 and 2 passed under
  BOTH versions — no discriminating power yet. Next iteration: tighten
  (e.g., require quoted execution output) or replace with harder cases.
