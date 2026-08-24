# Letta Memory-Conflict Eval

A small, reproducible evaluation of how an agent-memory **reflection** step resolves
*conflicting* facts — using [Letta](https://github.com/letta-ai/letta-code)'s
verbatim reflection subagent prompt, tested across **10 models from 5 provider
families** (132 runs) on AWS Bedrock.

**TL;DR:** Conflicts that require an *action* (replace a stale fact, split
compatible facts) passed **66/66** runs across all ten models. Conflicts that
require *restraint* (don't overwrite an established home because of a temporary
stay; don't weaken a confirmed severe allergy because of one anecdote) failed
**13/66** runs (19.7%). Failures clustered by model family, not by model size —
one run downgraded a user's confirmed **severe shellfish allergy** to "mild" after
a single anecdote. A minimal recency-oriented conflict policy handles explicit
memory operations robustly while under-specifying when an existing fact should be
preserved. Full write-up: [`RESEARCH_REPORT.md`](RESEARCH_REPORT.md).

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

## Results (S0 — 10 models × 5 provider families, 33 runs/case, 132 total)

| Case | Category | Operation class | Result |
|---|---|---|---|
| A | control (true update) | Action | **33/33 PASS** |
| B | compatible split | Action | **33/33 PASS** |
| C | inferential non-overwrite | Restraint | **23/33 PASS** (10 failures, 30.3%) |
| D | confidence preservation | Restraint | **30/33 PASS** (3 failures, 9.1%) |

**Finding:** action-type conflicts passed 66/66; restraint-type conflicts failed
13/66 (19.7%). Failures clustered in specific model–case combinations and were
**not** ordered by model size. The most safety-relevant failure weakened a
confirmed severe shellfish allergy to "mild" on the strength of one anecdote.

The original hypothesis (the one-line heuristic fails all nuanced cases) and the
follow-up hypothesis (smaller models fail more) were both falsified; what emerged
instead is the action/restraint split. Per-model breakdown, adjudication rules,
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
