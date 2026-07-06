# The Unknowns Playbook

Distilled and adapted from **"A Field Guide to Fable: Finding Your Unknowns"**
by Thariq Shihipar (Anthropic, Claude Code team), published July 3, 2026, and
its companion example gallery. All prompts below are paraphrased/adapted, not
verbatim. Sources:

- Original article: https://x.com/trq212/article/2073100352921215386
- Companion artifact gallery (11 worked examples):
  https://thariqs.github.io/html-effectiveness/unknowns/

## Contents

1. [The framework](#the-framework)
2. [The specificity dial](#the-specificity-dial)
3. [Pre-implementation techniques](#pre-implementation)
4. [During implementation](#during-implementation)
5. [Post-implementation](#post-implementation)
6. [The human/agent PR split](#the-humanagent-pr-split)
7. [Skills are maps too](#skills-are-maps-too)

---

## The framework

The map (prompt, context, skills, CLAUDE.md) is a representation of the work;
the territory is the actual codebase, data, and the user's real standards.
The gap between them is the unknowns. When the model hits an unknown, it
decides based on its best guess about intent — and the bigger the task, the
more unknowns are waiting. Fable is the first tool where the quality
bottleneck is the *user's* ability to clarify their own unknowns; when
emulating Fable, treat helping the user do that as part of the job.

Four quadrants (after Rumsfeld):

| Quadrant | What it is | How it surfaces |
|---|---|---|
| Known knowns | Explicit in the prompt | Already handled |
| Known unknowns | Named gaps, undecided choices | Ask / investigate |
| Unknown knowns | Unstated taste, conventions, quality bars — recognized on sight, never written down | Prototypes, options, brainstorms to react to |
| Unknown unknowns | Factors nobody considered | Blindspot pass; read the territory |

The best agentic programmers simply have fewer unknowns: they know precisely
what they want, and they stay in sync with both the codebase and the model's
behavior. Planning up front is never sufficient — some unknowns only appear
mid-implementation, sometimes revealing the problem needs a different
approach entirely. So working this way is iterative: uncover unknowns before,
during, and after implementation.

A crucial input for every technique below: **the user's starting point**.
Who are they, what do they already know, where are they in their thinking?
"I've never touched this auth module" and "I wrote this auth module" demand
different behavior from the same prompt.

---

## The specificity dial

Failing both ways:

- **Too specific** → the plan gets followed rigidly even when mid-task
  evidence says to change course. An unstated bad assumption gets executed
  thoroughly.
- **Too vague** → decisions get made from generic industry defaults that
  don't fit this task or this codebase.

The fix is not a perfect midpoint; it's accounting for unknowns explicitly.
State assumptions. Flag decisions you made by default. Invite correction on
the parts most likely to be wrong.

---

## Pre-implementation

Before any code/work exists is the cheapest place to find an unknown.

### 1. Blindspot pass

When: the territory is unfamiliar to the user (new part of a codebase, new
domain like color grading or infra).

What to do: scan the relevant territory and report the unknown unknowns as a
short list of discrete findings, each paired with a concrete fix — a line to
add to the prompt, or a decision to make. Then assemble an improved
implementation prompt from the accepted fixes.

Adapted prompt shapes (use the literal words "blindspot pass" and "unknown
unknowns" — they cue the right behavior):

> I'm adding a new authentication provider but I don't know this codebase's
> auth module at all. Do a blindspot pass: find my unknown unknowns here and
> help me write a better implementation prompt.

> I need to color-grade this video and know nothing about color grading.
> Teach me my unknown unknowns in this domain so I can prompt precisely.

### 2. Teach-me explainers

When: the user lacks the *vocabulary* to state what they want.

What to do: build a compact interactive or structured explainer — a
vocabulary ladder from novice terms to professional terms, with before/after
examples — so vague requests ("make it nicer") become precise ones ("lift
the shadows, cool the midtones").

### 3. Brainstorms & prototypes

When: unknown knowns — taste and standards the user will only recognize on
sight (visual design is the classic case).

What to do: generate several **radically different** directions, not
variations on one idea. E.g., the same UI rendered four wildly different
ways (ops console / editorial / kanban / terminal), or ten interventions
plotted from ship-this-afternoon to quarter-long bet. Make reacting cheap:
include steal/skip choices per element so the user's reply nearly writes
itself. Prototype throwaway mocks before touching real code. Start almost
every substantial session with an exploration/brainstorm phase to
consciously set scope.

### 4. Interviews

When: ambiguity remains after the above.

What to do: interview the user **one question at a time** (not a wall of
questions), ordered by architectural blast radius — ask first the questions
whose answers would change the structure of the solution. Finish by handing
back a decisions table plus a ready-to-run implementation prompt.

### 5. References

When: words run out; something existing already embodies the standard.

What to do: ask for or locate a concrete reference. Source code is the best
reference, even in a different language — reading a site's underlying code
beats reading a screenshot of it. Before porting from a reference, prove
comprehension: map its semantics, list its gotchas and edge cases, and show
matched excerpts, so misreadings surface before they're baked in.

### 6. The tweakable plan

When: any Deep-mode task, right before execution.

What to do: write the implementation plan sorted by
**likelihood-of-tweaking**, not by execution order. At the top: data models,
type interfaces, schema choices, and everything user-facing — each flagged
with its plausible alternatives. At the bottom, collapsed: the mechanical
work nobody needs to review. The user reviews the volatile 20%, not the
whole document.

---

## During implementation

No amount of planning finds every unknown; some live only in the territory.

### 7. Implementation notes

Keep a running `implementation-notes.md` during the build:

- Before each non-obvious step, note the assumption behind it.
- Every time the territory forces a deviation from the plan, log: what was
  expected, what was found, what call was made.
- On unexpected edge cases: take the **conservative** option, log the
  deviation, keep working — don't stall, don't silently improvise something
  bold.
- End with a handful of bullets to fold into attempt #2 or into memory.

These notes are what make the next attempt start smarter, and they feed the
post-implementation artifacts below.

---

## Post-implementation

Shipping means other people inherit your unknowns.

### 8. Pitches & explainers

Bundle the prototype, the specs, and the implementation notes into a
stakeholder-facing pitch: lead with a demo of the result, then pre-answer
each objection a reviewer would raise, with evidence, and name exactly who
needs to sign off on what.

### 9. Quizzes

Generate a change report (what changed, where, why, with context) that ends
in a short quiz the *user* must pass before merging — wrong answers point
back to the exact section they skimmed. The rule: don't merge until the quiz
is passed clean. When emulating: offer the quiz for significant changes; a
failed quiz means the report (the map) didn't transfer the territory.

---

## The human/agent PR split

Write PR/change descriptions in two sections for two different readers:

- **Human section** — screenshots, before/after images, short clips: the
  information that genuinely doesn't compress into text (layout shifts,
  animation timing, a color that's almost-but-not-quite right).
- **Agent section** — the precise textual map: what changed, invariants,
  edge cases, follow-ups — optimized for the next agent that reads it.

A description serving only one reader leaves the other working from an
incomplete territory.

---

## Skills are maps too

A skill is a codified shortcut standing in for territory the model would
otherwise rediscover each session. Valuable when accurate and repeatable; a
liability when stale, over-specified for a model that no longer needs the
hand-holding, or written for a subtly different problem. Corollaries:

- For a *more* capable model, prune prescriptive scaffolding — it can degrade
  output (Anthropic's guidance says skills written for prior models are
  often too prescriptive for Fable 5).
- For a *less* capable model (the situation of this skill), more explicit
  map is appropriate — but keep updating it against the territory, and let
  the territory win on conflict.
- Update skills and memory from what each run teaches; a map nobody updates
  drifts until it misleads.

Capability doesn't remove the need for a good map — it raises the price of a
bad one. A weak model's failures are loud and local; a strong model's are
quiet and compounding.
