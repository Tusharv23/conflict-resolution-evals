# Letta Memory-Conflict Eval

A small, reproducible evaluation of how an agent-memory **reflection** step resolves
*conflicting* facts — using [Letta](https://github.com/letta-ai/letta-code)'s
verbatim reflection subagent prompt, tested across **10 models from 5 provider
families** (120 runs) on AWS Bedrock.

**TL;DR:** Conflicts that require an *action* (replace a stale fact, split
compatible facts) passed **60/60** runs across all ten models. Conflicts that
require *restraint* (don't overwrite an established home because of a temporary
stay; don't weaken a confirmed severe allergy because of one anecdote) failed
**30/60** runs (50.0%) after manual adjudication of every run. Failures clustered
by model family, not by model size — one run downgraded a user's confirmed
**severe shellfish allergy** to "mild" after a single anecdote; another fabricated
an address by merging the old street onto the new city. A minimal
recency-oriented conflict policy handles explicit memory operations robustly
while under-specifying when an existing fact should be preserved. Full write-up:
[`RESEARCH_REPORT.md`](RESEARCH_REPORT.md).

## Why this exists

Letta's reflection subagent resolves memory contradictions with a single documented
heuristic — *"resolve in favor of the latest evidence."* That's correct for a plain
update ("moved from A to B"), but real memory conflicts include:

- **Compatible facts** that only *look* like a conflict (parents separated → two
  addresses, both true).
- **Context-dependent facts** (a temporary stay is not a change of permanent home).
- **Asymmetric-confidence facts** (a casual anecdote should not override a
  user-confirmed medical allergy).

The question: does a one-line policy handle these, or does it over-write things it
shouldn't?

## Method

Two-stage, prompt-level (no Letta install required):

1. **Stage 1 — verbatim reflection.** Letta's real reflection prompt
   (`reflection_prompt.md`, pinned to `letta-code` commit `c0956ed3`) reviews a
   memory snapshot + a short transcript and describes its intended edits.
2. **Stage 2 — neutral extraction.** A separate transcriber prompt (`extractor.md`)
   converts that prose into a structured JSON verdict. The transcriber is explicitly
   forbidden from judging — it only reports what Stage 1 decided.
3. **Scoring** (`evaluate.py`) applies each case's mechanical `pass_rule`; nuanced
   cases are flagged `NEEDS_REVIEW` for human inspection rather than auto-judged.

### Stage 2 transcribes; it does not judge

The extraction stage only **records** what the reflection stage decided — it never
evaluates whether that decision was correct. Every reported failure is the
*reflection model's* output, not an artifact of the measurement layer. Verified
directly against raw runs, e.g. a C failure on `claude-haiku-4-5`:

- **Stage 1 (reflection) concluded:** "Removed stale Bangalore address as primary
  home" → FINAL STATE: `Home (tag: home): Pune`
- **Stage 2 (transcriber) recorded:** `Home (tag: home): Pune` — verbatim.

The transcriber added, corrected, and judged nothing. Raw two-stage outputs for
every run are in `results/` so this fidelity is independently checkable.

Cases (`cases.json`): **A** control (true update), **B** compatible (separated
parents), **C** inferential (temporary stay ≠ home), **D** confidence (anecdote vs.
confirmed allergy). Each run 3× per model (outputs are stochastic).

### Honest disclosures

- The verbatim prompt is used, but the *user message* adds one offline-review note
  (the harness can't provide the Bash/Edit tools the prompt expects). This is a
  known deviation — we elicit the agent's **intended** edit, not an executed one.
- Under **large** memory the offline-review framing began to backfire (the model
  treated it as suspicious / reverted to tool calls), and longer outputs hit the
  token limit. So the load experiment (S1) did **not** run cleanly and is not
  reported as a result — see "Limitations & future work."

## Results (S0 — 10 models × 5 provider families, 30 runs/case, 120 total)

Every run was manually adjudicated against explicit per-case rules (below); the
mechanical scorer only pre-sorts and flags — it never auto-judges nuance.

| Case | Category | Operation class | Result |
|---|---|---|---|
| A | control (true update) | Action | **30/30 PASS** |
| B | compatible split | Action | **30/30 PASS** |
| C | inferential non-overwrite | Restraint | **13/30 PASS** (17 failures, 56.7%) |
| D | confidence preservation | Restraint | **17/30 PASS** (13 failures, 43.3%) |

**Finding:** action-type conflicts passed 60/60; restraint-type conflicts failed
30/60 (50.0%). Failures clustered in specific model–case combinations and were
**not** ordered by model size. Notable failure modes: a confirmed severe
shellfish allergy weakened after one anecdote (severity downgraded, tolerance
asserted, or confirmed status revoked); an established home address deleted in
favor of an implicit temporary stay; and a **confabulated merge** — one model
family invented `12 MG Road, Pune`, splicing the old street address onto the new
city, in 3/3 runs.

**Adjudication rules** (applied uniformly, stated so they can be contested):

- **C fails** unless the established Bangalore address survives as a
  *still-valid* address a future agent could act on. Tags like "secondary" or
  "registered address" pass; "previous home," "archive," or "(inactive)" fail.
- **D fails** if any of three properties of the stored fact is degraded:
  existence, severity ("severe"), or epistemic status ("confirmed"). Recording
  the anecdote *subordinately* with both interpretations left open passes;
  promoting it into the fact ("suggests a change in severity," "do not treat
  severity as confirmed") fails.

The original hypothesis (the one-line heuristic fails all nuanced cases) and the
follow-up hypothesis (smaller models fail more) were both falsified; what emerged
instead is the action/restraint split. Per-model breakdown, adjudication detail,
and every failure transcript: [`RESEARCH_REPORT.md`](RESEARCH_REPORT.md).

## Limitations & future work

- Failures are family-dependent; this study does not isolate architecture or
  training as causal variables.
- **Context load untested (cleanly).** Whether this behavior degrades when the
  conflicting fact is buried in a large realistic memory (lost-in-the-middle) is the
  open question. Testing it faithfully needs a real tool-execution harness so the
  offline-review framing (which confounds results under load) can be removed.

## Reproduce

```bash
pip install -r requirements.txt
# single model smoke test
AWS_PROFILE=<your-profile> python3 runner.py --stage S0 \
  --models us.anthropic.claude-sonnet-5 --repeats 3
# full 10-model matrix (defaults in runner.py)
AWS_PROFILE=<your-profile> python3 runner.py --stage S0
python3 evaluate.py --stage S0
```

Model IDs are Bedrock inference profiles; any Bedrock-enabled AWS account works.

Raw per-run evidence (both stages + parsed JSON) is written to `results/`.
