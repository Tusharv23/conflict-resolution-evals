# Context-load experiment — design log

**Status (Sep 3): superseded by Option A.** The hand-built memory files below were
built before discovering the runner never reads them — memory lines come from
`cases.json` and (for high load) `context_loader.build_s1_memory()`. Decision:
extend `context_loader.py` with a size parameter instead (see design questions).
Files kept as documentation of intent.

## Hand-built files (NOT consumed by the harness)
| File | Tokens (cl100k_base) | Ratio vs baseline (142) |
|---|---|---|
| `personal_assistant.md` (baseline/reference) | 142 | 1.00x |
| `personal_assistant_2x.md` | 303 | 2.13x |
| `personal_assistant_4x.md` (call it 5x) | ~704 | 4.96x |

## Design notes recorded pre-run (moved out of file frontmatter — contamination risk)
- Conflict-pair facts keep baseline relative positions; dietary/allergy section
  closes each file (recency position preserved across load conditions).
- **DELIBERATE PROBE (declared pre-run):** in the 5x file, Sneha's address
  (16 MG Road, Bangalore 560001) is one digit from Home (12 MG Road) —
  intentional confabulation stressor (cf. Nova baseline 12/17 MG Road merge
  failures). Any address-merge involving these lines scores per this note.
- Confounds found & fixed during build: "Me and Manu loves prawns" (in-file
  contradiction with allergy under test) → changed to drinking; "Sister -
  shifting house" calendar line (entangled with case A sister-address update)
  → changed to Sneha.

## Predictions (locked Sep 3, BEFORE any run) — llama3-8B conflict cases
**⚠️ SUPERSEDED Sep 5 (pre-run) — see revised prediction at bottom of file. Kept for the record; anchored to the tiny S0 baseline (142 tok) and to the old repetition-based scaling design, both replaced by the Sep 5 equal-token ladder.**
- ~~2x load → 60–70% fail~~
- ~~4–5x load → 100% fail~~
- Falsification clause (still active, carried into revision): if 8B holds ~current fail rate as load rises, position-driven
  arbitration takes a real hit; report becomes "load didn't matter."

## Design decision (ANSWERED Sep 3, before coding)
S1 plants the conflict fact MID-FILE (tests burial: load + position move
together). Hand-built files keep the fact at the END (tests load alone,
position held constant). The Hewitt hypothesis is position-driven arbitration →
position must be a controlled variable.

**DECISION: sequenced (option c).**
1. **Arm 1 (this week): LOAD only** — conflict fact at END at every load level
   (matches baseline position). Predictions above apply as locked.
2. **Arm 2 (later, only after Arm 1 results): POSITION** — move fact to
   MID-FILE at fixed load; compare against Arm 1 at same load.
Rationale: one variable per arm; predictions carry over cleanly; each arm
reportable on its own; result possible before the Sep 8 Hewitt send.

## Design decisions locked Sep 5
- **Scale = distinct-block selection, never repetition.** Repeated filler is
  unrealistic memory and models may discount duplicated text as noise
  (confound caught at design time). `* scale` multiply replaced by cumulative
  block tranches.
- **Equal-TOKEN ladder:** scale 1 = 589 tok (= original S1: BEFORE + conflict +
  AFTER), scale 2 = 1,129 tok (+ XL blocks 0–6), scale 3 = 1,670 tok (+ full
  15-block XL pool). Even ~540-tok spacing. Re-targeted Sep 5 (Sat) to the
  natural full-pool ceiling: the audited XL pool totals ~1,081 tok, so 1,890
  was unreachable without repetition or new unaudited content — either would
  violate the distinct-block rule. Verified by 6 guards in context_loader.
  (Filler set is FIXED per scale; only conflict placement varies by position,
  so position is a clean one-variable change — token count identical across
  start/mid/end at each scale.)
- **Second factor: PROMPT (v1 vs pr).** Run both the pinned baseline reflection
  prompt and the PR prompt (#4097 wording) at every load level → measures
  whether the PR's improvement HOLDS, GROWS, or COLLAPSES under load. Directly
  relevant to PR review; nobody has measured this.
- Filler realism validated informally: generated persona read as personally
  accurate to subject (Barnum-consistent) — distractors are plausibly
  memory-like rather than obviously synthetic.

## Pre-registered predictions — prompt × load interaction (locked Sep 5)
- **Full cross required for fairness: BOTH prompts (v1, pr) run at EVERY scale
  (1, 2, 3), same cases/models/repeats. No one-sided conditions.**
- **Headline prediction: B — SHRINKS BUT SURVIVES.** Load decreases accuracy for
  both prompts (per Lost in the Middle), but the PR prompt's restraint
  advantage persists at every scale: pr keeps beating v1 on C/D even at
  scale 3 (~1,670 tok), though the gap narrows.
- Falsification: pr ≈ v1 at scale 3 (~1,670 tok) (advantage collapses → prompt fixes are
  load-fragile) or pr advantage GROWS with load (structure matters more under
  load). Either failure is itself a reportable finding (PR follow-up comment).
- Models: llama3-1-8b (positional-arbitration), nova-micro (confabulator),
  sonnet (judgment). 2 × 3 × 4 × 3 = 72 runs/model, 216 total.
- Quantitative anchor (from locked Sep 3 predictions, 8B): v1 D-case fail
  60–70% at scale 2, ~100% at scale 3. PR D-case fail stays ≤ 2/6 per scale
  under prediction B.
- **REVISED PREDICTION — Sep 5, written PRE-RUN (evidence: Sep 5 session "lets do these tomorrow": pre-registration updated → matrix launched after; supersedes Sep 3 predictions above).** New calculations, referencing Lost in the Middle's U-curve: increasing load will have NO impact if the arbitrated fact is at the END (favored position — Arm 1). If the fact is at the BEGINNING/MID (Arm 2), increasing load should cost ~1% — 1–2 case failures at most for llama3-8B / Nova family (already fragile).

---

## RESULTS — Arm 1 mechanical tally (POST-RUN, recorded Sep 7; adjudication NOT yet complete)

**Matrix:** 216 runs — 2 prompts (v1, pr) × 3 scales (589/1129/1670 tok, END position) × 4 cases × 3 models (llama3-1-8b, nova-micro, sonnet) × 3 repeats. All `status: ok`.

Mechanical FAILs per 9-run cell (evaluate.py triage — NOT final; D is mostly NEEDS_REVIEW, C needs rubric pass):

| Case | v1 s1→s2→s3 (fails) | pr s1→s2→s3 (fails) |
|---|---|---|
| A true-update | 1→4→2 | 2→4→2 |
| B compat-split | 1→1→0 | 1→3→3 (incl. 1 INVALID s3) |
| C inferential | 3→1→1 | 1→4→3 |
| D confidence | 3→1→4 (+5–8 NEEDS_REVIEW/cell) | 2→2→1 (+7–8 NEEDS_REVIEW/cell) |

**Pre-run predictions vs outcome (mechanical, pending adjudication):**
1. **Sep 5 revised load prediction (no impact at END): SUPPORTED** — no monotone load gradient in any case within S1. The carried-over falsification clause fired: "load didn't matter" at END position. Arm 2 (position) is now the live hypothesis.
2. **Sep 5 headline prediction B (pr shrinks but survives, beats v1 at every scale): FALSIFIED** — opposite observed on B: v1 holds (1→1→0 fails), pr degrades under load (1→3→3). The pr advantage is load-fragile on B.
3. **A-case anomaly:** A was 0-fail at S0 but fails at all S1 scales (flat, no gradient). Confound note: S0→S1 changes memory content AND size together — only the within-S1 "load doesn't matter at END" claim is clean. Hand-checked examples (Sep 5 session): confabulated address merges ("4356 Surrey, British Columbia"), no-change fails — real model failures, not harness bugs (grader's "check harness" string is its default A-case reason, misleading here).

**Open before any external claim (Sep 5 to-do, still pending):**
- C rubric decision from pre-registered `pass_rule` in cases.json (strict vs lenient) — decide from commitment, not from rows
- Adjudicate C (54 runs), D (54 runs) blind, same rules doc
- Re-run truncated sonnet B/3x/pr/run2 (charity-pass withdrawn → counted FAIL/INVALID pending re-run)

---

## ADJUDICATION — A & B cases (Sep 8, human pass over all mechanical fails)

**Truncation addendum (rule logged Sep 8, model-agnostic, BEFORE C/D adjudication):**
If `parsed.final_memory_lines` contains the fact(s) the pass rule tests, score normally regardless of the `complete` flag. If truncation removed the decisive section (facts absent AND `complete: false`), verdict = **INVALID** — not FAIL, not charity-PASS. The `actions` narrative is never admissible as primary evidence (Aug 28 pre-registered rule; protected against Nova's false "replace" action in baseline). An earlier same-day "pass Sonnet on reputation" ruling was withdrawn as §4.3-style anchoring.

**A true-update — adjudicated. 15 mechanical fails → 8 real fails, 1 INVALID, 6 overturned to PASS:**
- Real fails (8): nova-micro ×6 (confabulated/wrong addresses — incl. fabricated "5678 Elm Street" [pr 1x run1] and Surrey+Vancouver coexisting-merge [v1 1x run3]; confabulation-under-load now a named recurring finding, 3rd distinct fabricated address after baseline "12/17 MG Road Pune"), llama3-1-8b ×1–2 (no-change freeze [pr 2x run3]).
- Overturned to PASS (6): llama rows where new address present AND old address absent (verified old-address-gone per A pass rule, not just new-address-present) + claude pr 2x run3 (clean replace).
- INVALID (1): nova pr 2x run3 "unclear output".
- **Verdict: NO monotonic load effect on control. Capable models hold true updates at all S1 scales; failures concentrate in nova-micro (confabulation) + occasional 8B freeze. Sep 3 prediction (60–70% fail @2x for 8B) CLEANLY FALSIFIED for A — 8B failed A ≈1× at 2x.**

**B compatible-split — adjudicated. 8 mechanical fails → 2 real fails, ~6 INVALID (truncation artifact):**
- Root cause found: Claude rewrites the ENTIRE memory file in its final-state block; at scale ≥2 (and once at 1x) it hits stage-1 `max_tokens` before reaching the Recipients section → substring scorer sees neither address → false FAIL. Verified via `complete:false` sweep across all 18 Claude B rows: 8 truncated-with-decisive-section-missing → INVALID; truncated-but-facts-present rows remain PASS (rule applies evidence-wise, not model-wise).
- Real fails (2): nova-micro v1 1x run3 (no update), llama pr 2x run1 (overwrote with mom's address — the predicted merge failure, but isolated).
- **Scorer failure mode #3 logged: truncation false-FAIL** (after #1 confabulated-merge false-PASS, #2 split-format). evaluate.py = triage, never judge.
- **HARNESS BUG (fix before any re-run): stage-1 max_tokens too small for full-file-rewrite models at scale ≥2.** Raise generously; optionally re-run the 8 INVALID Claude B cells to recover data.
- Prediction 2 (pr load-fragile on B) — REVISED by adjudication: the apparent pr degradation (1→3→3) was mostly truncation INVALIDs, not real failures. With INVALIDs excluded, B is ~clean under load for both prompts. Prediction-2 "falsified" verdict downgraded to "not evaluable on B without re-run at higher max_tokens."

**C & D: NOT yet adjudicated. Truncation addendum + `complete` check apply to every Claude row there too — check before trusting any C/D verdict.**