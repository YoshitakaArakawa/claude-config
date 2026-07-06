# Worked Examples

Compact worked examples showing what each technique's *output should look
like*. Examples 1–3 are adapted (condensed, not verbatim) from the companion
gallery to "A Field Guide to Fable" — 11 full artifacts at
https://thariqs.github.io/html-effectiveness/unknowns/ — which shows the
exact prompt at the top of each page and the artifact Claude produced below
it. Examples 4–6 are constructed for this skill from the patterns in
`fable-behavior-spec.md`. Read this file when about to *produce* one of
these artifacts and unsure what good looks like.

## Contents

1. [Blindspot pass](#1-blindspot-pass) — findings + prompt-fix per finding
2. [Tweakable plan](#2-tweakable-plan) — volatile decisions on top
3. [Interview](#3-interview) — one question, blast-radius order
4. [Evidence-grounded report](#4-evidence-grounded-report) — bad vs good
5. [Re-grounding summary](#5-re-grounding-summary) — before/after
6. [Pre-handoff quiz](#6-pre-handoff-quiz)

---

## 1. Blindspot pass

User prompt (gallery example 01):

> I'm adding a new SSO auth provider to Acme but I've never touched the
> auth module. Do a blindspot pass: find my unknown unknowns in this part
> of the codebase, explain each one, and tell me how to prompt you better
> for the implementation.

Shape of a good output — three parts:

**(a) Expectation vs territory, up front.** One paragraph contrasting what
the task *sounds like* ("implement an interface, register it, done — a
two-day task") with what the scan actually found ("a module mid-migration
on session storage, one provider that quietly bypasses the middleware, a
reverted previous attempt at exactly this task").

**(b) Discrete findings, each with a copyable fix.** Classify each finding
(landmine / unwritten convention / missing concept / history) and give it
three fields — what it is, why it bites, and the prompt line that defuses
it. Two condensed findings from the gallery artifact:

> **Landmine — sessions are double-written.** Acme is mid-migration from
> Postgres sessions to Redis (stalled since March); writes fan out through
> `SessionBridge.write()` to both stores, but reads still come from
> Postgres. *Why it bites:* grepping "session" surfaces `RedisSessionStore`
> first — it looks canonical. Write to it directly and logins work in dev
> and silently fail in prod.
> *Prompt fix:* "Route all session writes through SessionBridge — never
> RedisSessionStore or pg_sessions directly."
>
> **History — someone already tried this.** PR #2841 added an OIDC
> provider and was reverted nine days later: strict redirect-URI matching
> broke workspace-scoped invite links. The agreed fix (a signed
> state-parameter workspace claim) was designed in the revert thread but
> never built. *Why it bites:* nothing in the current code hints at this;
> you'd re-implement the reverted approach and pass every local test.
> *Prompt fix:* "Read the revert of PR #2841 first; implement the signed
> state-parameter claim instead of tenant-suffixed callback URLs."

**(c) The improved implementation prompt.** Fold every accepted fix into
one numbered prompt the user can run, ending with an execution order and a
checkpoint ("stop and show me the plan after the walkthrough before
writing code").

The gallery's closing line captures the standard: each constraint in the
final prompt is "a sentence you couldn't have written this morning — each
one bought with someone else's half-day."

---

## 2. Tweakable plan

Task: "CLI tool that dedupes our contacts CSV." Plan sorted by
likelihood-of-change (gallery example 08 does this with toggleable
alternatives; this is the plain-Markdown equivalent):

> ## Volatile decisions (review these)
>
> - **Dedupe key: normalized email** (lowercase, trimmed).
>   Alternatives: fuzzy name+phone match (catches more dupes, risks false
>   merges); exact full-row match (never wrong, catches almost nothing).
>   Chose email: your CSV has 98% email coverage.
>   ⚠ Rows with *empty* email are kept as-is, never merged — flag if wrong.
> - **Collision policy: keep first occurrence, log the rest.**
>   Alternatives: merge non-empty fields across dupes; interactive prompt.
>   Keep-first is reversible (the log preserves losers); merge isn't.
> - **Output: new file `contacts.deduped.csv`**, source untouched.
>   Alternative: in-place with `.bak`. New-file chosen: reversibility.
>
> ## Assumptions & open unknowns
>
> - Assuming UTF-8 with header row; not validated against the real export.
>
> ## Mechanical work (low review value)
>
> - argparse CLI, csv reader/writer, unit tests for key normalization,
>   README.

The user reviews the three decisions at the top — three minutes — instead
of the whole plan. Every volatile decision states its alternatives and why
this one; the mechanical bottom is deliberately boring.

---

## 3. Interview

Ambiguity remains after a blindspot pass; interview one question at a time,
biggest architectural blast radius first (gallery example 06):

> Before I plan, a few questions — one at a time, biggest consequences
> first.
>
> **Q1.** When two contacts collide, should the tool *merge* their fields
> into one record, or *drop* all but one? This changes the data model —
> merge needs field-level conflict rules; drop needs only an ordering.

(User answers. Then Q2 — collision ordering; Q3 — output location. Only
after the questions:)

> Decisions so far:
>
> | Decision | Your call | Consequence |
> |---|---|---|
> | Collision behavior | drop, keep newest | no merge rules needed |
> | "Newest" defined by | `last_modified` column | tie-break: row order |
>
> Ready-to-run prompt: "Build a CLI that dedupes contacts.csv on
> normalized email, keeping the row with the latest last_modified…"

Anti-pattern: a wall of six questions at once — the user answers the easy
ones, skips the structural one, and the plan gets built on the gap.

---

## 4. Evidence-grounded report

**Bad** (claims without session evidence):

> Migration complete! All modules now use the new logger and all tests
> pass. Also cleaned up some legacy config.

**Good** (every claim points to something that happened in the session;
failures reported as failures):

> Migration done for 3 of 4 modules; the 4th is blocked — details below.
>
> - `ingest/`, `api/`, `worker/`: migrated. Evidence: `pytest` this
>   session — 42 passed, 0 failed (output above).
> - `payments/`: **not migrated**. It pins `structlog 19.x`, incompatible
>   with the new adapter. I stopped rather than force-upgrade a payments
>   dependency — needs your call.
> - Unverified: behavior under real traffic; I only ran the unit suite.

The bad version contains three unevidenced claims ("all", "all", plus an
unrequested cleanup). The good version leads with the outcome, separates
verified / failed / unverified, and turns the blocker into a decision.

---

## 5. Re-grounding summary

The final message after a long unwatched run is the user's *first look* —
write it for a reader who saw none of the work.

**Before** (working shorthand leaks out):

> Done. auth→JWT shim removed, NEW_SESS flag gone, bridge writes
> single-path now, see c7f2e1a + tests green.

**After** (re-grounded):

> Login sessions now use a single storage path, and old sessions keep
> working. Three things changed: the temporary compatibility layer that
> wrote sessions to two databases is removed; the feature flag that
> selected between them (`NEW_SESS`) is deleted, since nothing reads it
> now; and the whole change is in one commit (`c7f2e1a`). I verified it by
> running the auth test suite — 31 passed — and by logging in against a
> session created before the change.
>
> One thing needs your eyes: sessions older than 30 days are dropped
> rather than migrated. That matches the retention policy, but confirm it
> before this deploys.

Every file/commit/flag gets one plain-language clause; invented labels are
either dropped or reintroduced; clear beats short.

---

## 6. Pre-handoff quiz

For a significant change, end the change report with a short quiz the user
should pass before merging (gallery example 11 does this over a 14-file
diff). Rule: wrong answer → back to the report section they skimmed; don't
merge until clean.

> Before you merge, three questions:
>
> 1. A user's session was created *before* this deploy. What happens on
>    their next request? (§ "Compatibility window")
> 2. Which config value must exist in prod before deploy, and what fails
>    if it's missing? (§ "New configuration")
> 3. Rollback: is reverting the commit enough, or is there state to
>    clean up? (§ "Rollback")

A failed quiz is signal, not embarrassment: the report (the map) didn't
transfer the territory. Rewrite that section, don't just tell the answer.
