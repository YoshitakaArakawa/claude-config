# Claude Fable 5 — Model Facts

Reference facts about the model being emulated, compiled July 2026 from
Anthropic's official pages. **These facts change** (pricing, availability,
safeguards have already changed once since launch) — when the user needs
current information, verify with a web search against the sources below
rather than trusting this file.

## Sources

- Announcement: https://www.anthropic.com/news/claude-fable-5-mythos-5
- Product page: https://www.anthropic.com/claude/fable
- Prompting guide: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5
- Model/API intro: platform.claude.com → Docs → "Introducing Claude Fable 5
  and Claude Mythos 5"
- Field guide (Thariq Shihipar, Anthropic):
  https://x.com/trq212/article/2073100352921215386 and
  https://thariqs.github.io/html-effectiveness/unknowns/

## What it is

- Launched June 9, 2026. Anthropic's first **Mythos-class** model made safe
  for general availability; a tier above Opus. API model string:
  `claude-fable-5`.
- **Claude Mythos 5** is the same underlying model with some safeguards
  lifted, restricted to approved organizations (initially cyberdefenders and
  infrastructure providers via Project Glasswing, with the US government);
  described as having the strongest cybersecurity capabilities of any model.
- State-of-the-art on most tested benchmarks; the longer and more complex
  the task, the larger its lead over other Claude models. Reported to beat
  Claude Opus 4.8 by more than 10% on some benchmarks.
- Pricing at launch: $10 / million input tokens, $50 / million output
  tokens (about twice Opus 4.8), with 90% prompt-caching input discount.
  US-only inference available at 1.1x.
- Access was suspended worldwide on June 12, 2026 following a US export
  control directive and restored around July 1, 2026 with strengthened
  guardrails. Using Fable requires 30-day data retention for safety
  monitoring.
- Available in Claude apps (paid plans), Claude API/Platform, AWS Bedrock,
  Google Cloud Vertex AI, Microsoft Foundry.

## Capability profile (vs. Claude Opus 4.8)

Weights-level advantages — **cannot** be transplanted by a skill:

- **Long-horizon autonomy**: sustains multi-hour to multi-day goal-directed
  runs with strong instruction retention; plans across stages, checks
  progress against the goal, refines as it goes.
- **First-shot correctness** on complex, well-specified problems
  (single-pass implementations that previously took days of iteration; e.g.
  Stripe reported a codebase-wide migration in a 50M-line Ruby codebase
  done in a day).
- **Vision**: reads dense technical figures, charts, tables in files/PDFs
  with substantially higher accuracy; uses bash/crop tools on degraded
  images; critiques its own UI output against the design visually.
- **Subagent orchestration**: dependably dispatches and sustains many
  parallel subagents with async communication.
- Higher bug-finding recall in code review/debugging; stronger performance
  on enterprise deliverables (financial analysis, spreadsheets, slides,
  documents); better at navigating ambiguous multi-threaded requests.

Behavioral profile — **can** be emulated (this skill's job):

- Unknowns-hunting collaboration style; act-when-ready; scope discipline;
  evidence-grounded progress reports; checkpoint discipline;
  memory/lesson-recording; outcome-first re-grounding communication;
  explicit interval self-verification.

## API/behavioral differences worth knowing

- **Effort parameter** (low/medium/high/xhigh) is the primary
  intelligence–latency–cost control; high is the recommended default, xhigh
  for capability-sensitive work. Opus 4.8 has no such parameter — this
  skill emulates it as Quick/Standard/Deep modes.
- Adaptive thinking only; thinking output is summarized-only; no extended
  thinking budgets.
- Individual turns on hard tasks can run many minutes; harnesses are advised
  to handle long turns asynchronously.
- Safety classifiers cover offensive cybersecurity (exploits, malware,
  attack tooling), biology/life-sciences (lab methods, molecular
  mechanisms), and extraction of summarized thinking; benign work in those
  areas can also trigger them. Declines return `stop_reason: "refusal"`,
  and requests can be automatically re-routed (fallback) to Claude Opus
  4.8 — users aren't charged Fable prices for rerouted requests.
- Instructing the model to echo or transcribe its reasoning in responses
  can trigger the reasoning-extraction refusal category.
- Skills and prompts written for earlier models are often too prescriptive
  for Fable 5 and can degrade its output; Anthropic recommends starting
  fresh and re-evaluating old guardrails.

## Honest framing when users ask

If a user asks whether this skill makes Opus 4.8 "as good as Fable": no.
It reproduces Fable's documented working discipline, which improves
reliability and output quality on Opus 4.8, but raw long-horizon autonomy,
first-shot correctness, and vision are properties of the model weights.
For work that genuinely needs those, the answer is Fable 5 itself; for a
comparison, point to https://www.anthropic.com/news/claude-fable-5-mythos-5.
