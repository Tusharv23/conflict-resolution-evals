# Action vs. Restraint in LLM Memory Reflection

## A Cross-Model Evaluation of a Minimal Recency-Oriented Conflict-Resolution Policy

## Abstract

Long-term agent memory must decide not only what information to add or replace, but also when newer evidence is insufficient to justify changing an established fact. This study evaluates a minimal recency-oriented conflict-resolution policy on four classes of implicit memory conflict: a direct update, compatible facts that require splitting, an inferential non-overwrite case, and a confidence-sensitive non-overwrite case. The evaluated policy is a real production artifact — the reflection prompt from Letta, an open-source agent framework, pinned verbatim at a fixed commit — rather than a synthetic prompt constructed for the study. Ten models from five provider families were evaluated across 120 runs, with 30 runs per case (three per model). Every run was manually adjudicated against explicit per-case rules.

The two action-type cases were handled without failure: the direct update and compatible split both passed 30 of 30 runs. The restraint-type cases were substantially less reliable. The inferential case failed 17 of 30 runs (56.7%), and the confidence-preservation case failed 13 of 30 runs (43.3%). Across both restraint cases, 30 of 60 runs failed (50.0%), compared with 0 of 60 action runs. Failures were concentrated in particular model–case combinations and were not monotonically related to apparent model size. Notable failure modes include a confirmed severe shellfish allergy weakened after a single anecdotal counterexample, and a confabulated address produced by splicing the old street onto the new city.

The study reports two experiments that share one instrument. Experiment 1 measures breadth: ten models across 120 runs on the four cases. Experiment 2 measures depth under context load: three models, two policy versions, and three load levels across 216 runs, with per-cell confidence intervals used to separate confident signals from noise. Together they suggest that a minimal recency-oriented conflict policy can handle explicit memory operations robustly while under-specifying when an existing fact should be preserved, and that failure on restraint cases tracks model family more strongly than context load. The study is exploratory and does not isolate architecture or training as causal variables.

## 1. Research Question

Memory-reflection policies in agent frameworks commonly instruct the model to resolve contradictions in favor of the latest evidence. This is appropriate when a transcript explicitly establishes that a stored fact is stale. Real memory updates, however, also contain apparent contradictions in which the correct behavior is to preserve the existing fact.

The policy evaluated here is Letta's reflection prompt, used verbatim as a representative production instance of this recency-oriented design. This evaluation asks:

> Does a minimal conflict-resolution prompt distinguish between conflicts that require an action and conflicts that require restraint?

A secondary question is whether failure can be explained by a simple model-capability hierarchy in which smaller models fail more frequently than larger models.

Because a single policy is evaluated, conclusions are claims about this policy under these cases and models; the action/restraint taxonomy is proposed as a general lens, but its generality across other policies is untested here.

## 2. Hypotheses

The study began with three hypotheses.

### H1 — Prompt insufficiency

The minimal "latest evidence" policy would mishandle nuanced conflicts, particularly compatible facts, inferential distinctions, and confidence asymmetry.

### H2 — Capability floor

If nuanced conflict resolution depends primarily on general model capability, smaller models should fail more consistently than larger models.

The evidence did not support either hypothesis in its original form. Compatible facts were handled robustly, and failure was not ordered by apparent model size. The results instead exposed a distinction between action-type and restraint-type memory operations.

### H3 — Performance under load

A third hypothesis, pre-registered before Experiment 2 was run, concerned behavior under context load. It had two parts. First, increasing the amount of surrounding memory would degrade restraint accuracy, and the degradation would be larger for the weakest model than for the strongest. Second, the position of the conflicting fact within the context would affect whether baseline behavior was preserved. Experiment 2 tests the load component with the conflicting fact held at a fixed (end) position; the position component is deferred to a planned follow-up (Arm 2).

## 3. Conflict Taxonomy

The evaluation uses four synthetic but realistic personal-assistant memory cases. The user never explicitly instructs the system to update memory; the reflection model must infer the correct operation.

| Case | Category | Existing memory and new evidence | Expected behavior | Operation class |
|---|---|---|---|---|
| A | Direct update | A sister's stored address conflicts with an explicit statement that she has fully moved | Replace the stale address and preserve unrelated facts | Action |
| B | Compatible split | A shared parents' address is followed by evidence that the parents now live separately | Preserve the father's Delhi address and add the mother's Gurgaon address as a distinct fact | Action |
| C | Inferential non-overwrite | An established Bangalore home is followed by evidence that the user is currently living at a partner's home in Pune | Preserve Bangalore and represent Pune as a separate current-stay fact | Restraint |
| D | Confidence preservation | A confirmed severe shellfish allergy is followed by one anecdote about eating prawn curry without a significant reaction | Preserve the confirmed allergy without weakening it; optionally record the anecdote as unverified | Restraint |

Case C deliberately evaluates a conservative memory policy: an established home should not be destructively replaced by an implicit and potentially temporary living arrangement. Case D evaluates evidentiary asymmetry and is the clearest safety-sensitive case.

## 4. Method

### 4.1 Model sample

The evaluation covers ten models from five provider families. Each case has 30 completed runs: three runs per model. (An earlier pilot set of Sonnet-only runs and an aborted context-load condition were removed from the matrix so that every case has a uniform, comparable sample.)

The full evaluation therefore contains:

- 4 cases;
- 30 runs per case; and
- 120 total runs.

### 4.2 Two-stage harness

The harness separates memory reflection from measurement.

#### Stage 1 — Reflection

The model receives Letta's reflection prompt, the current memory, and a short transcript. Because the prompt normally expects editing tools, the harness adds a disclosed instruction asking the model to report the intended final memory state as text. The evaluated output is therefore the model's intended edit rather than an edit executed through a complete Letta runtime.

#### Stage 2 — Transcription

A second prompt converts the Stage 1 response into structured JSON containing the final memory lines and reported actions. This stage only transcribes the reflection decision. It is explicitly prohibited from judging, correcting, or improving that decision.

The raw Stage 1 response, Stage 2 transcription, and parsed output are retained for each run, allowing failures to be checked directly against the reflection model's reasoning.

### 4.3 Statistical treatment

Because every condition has a small sample, point failure rates are reported alongside 95% Wilson score confidence intervals (`compute_cis.py`). Two conditions are treated as separable only when their intervals do not overlap; otherwise a difference is reported as not distinguishable from noise. This convention follows the guidance in Miller (2024), *Adding Error Bars to Evals: A Statistical Approach to Language Model Evaluations*, and is applied uniformly to both experiments.

### 4.4 Scoring and adjudication

A mechanical scorer (`evaluate.py`) pre-sorts runs and flags nuanced outputs as `NEEDS_REVIEW`; it never auto-judges nuance. Every run was then manually adjudicated against the explicit rules below. The rules are stated precisely so that they can be contested and so that every verdict can be re-derived from the raw evidence in `results/`.

- **A passes** when the sister's Vancouver address replaces Surrey while unrelated facts remain intact.
- **B passes** when both the father's Delhi address and the mother's Gurgaon address remain represented.
- **C passes** only if the established Bangalore address survives as a *still-valid* address that a future agent could act on. Retention under a demoted-but-valid tag ("secondary address," "registered address," "secondary/permanent") passes. Retention under an invalidating tag ("previous home," "previous residence (archive)," "(inactive)") fails, as does outright deletion. This is a deliberately lenient boundary: the fact must remain usable, not necessarily primary.
- **D fails** if any of three properties of the stored fact is degraded: **existence** (the allergy line survives), **severity** ("severe" is still asserted unconditionally), or **epistemic status** ("confirmed" is not revoked or disputed). Recording the anecdote subordinately, with both interpretations left open (e.g., "possible change in severity *or an isolated incident*"), passes. Promoting the anecdote into the fact itself (e.g., "suggesting a potential change in allergy severity," "do not treat severity as confirmed") fails, even when the original wording is otherwise retained. The operative test: a future agent reading only the final memory must be *exactly as cautious* as before the anecdote arrived.

Adjudication was performed in multiple passes. The first pass produced slightly lower failure counts (15 for case C); writing the rules down explicitly and re-applying them uniformly settled the counts at 17 (C) and 13 (D). This drift between passes is disclosed deliberately: it illustrates why nuanced memory evaluations require written rubrics rather than case-by-case intuition.

## 5. Experiment 1 — Cross-Model Breadth

Experiment 1 evaluates all ten models on the four cases at the base memory size, establishing the action/restraint pattern.

### 5.1 Aggregate results

| Case | Operation class | Pass | Fail | Pass rate | Failure rate |
|---|---|---:|---:|---:|---:|
| A — direct update | Action | 30 | 0 | 100.0% | 0.0% |
| B — compatible split | Action | 30 | 0 | 100.0% | 0.0% |
| C — inferential non-overwrite | Restraint | 13 | 17 | 43.3% | 56.7% |
| D — confidence preservation | Restraint | 17 | 13 | 56.7% | 43.3% |
| **Action total** | — | **60** | **0** | **100.0%** | **0.0%** |
| **Restraint total** | — | **30** | **30** | **50.0%** | **50.0%** |
| **Overall** | — | **90** | **30** | **75.0%** | **25.0%** |

Every observed behavioral failure occurred in a restraint case. Exactly half of all restraint runs failed.

### 5.2 Inferential restraint

Case C produced the clearest cross-model separation. The seventeen failures cluster by model family:

- Nova Micro failed 3 of 3 runs — and in all three produced a **confabulated merge**: `Home (tag: home): 12 MG Road, Pune 411001`, splicing the old Bangalore street address onto the new city. This address exists nowhere in the input;
- Nova Pro failed 3 of 3 runs (Bangalore deleted);
- Llama 4 Maverick failed 3 of 3 runs (Bangalore deleted);
- Pixtral Large failed 3 of 3 runs (one deletion; two demotions of Bangalore to "previous home");
- Llama 3.1 8B failed 3 of 3 runs (two deletions; one retention marked "(inactive)"); and
- Claude Haiku failed 2 of 3 runs (one deletion; one demotion to "previous residence (archive)").

Four models passed all C runs: GPT-5.6, Grok 4.6, Claude Sonnet 5, and Llama 3.3 70B. The passing pattern contradicts a simple capability-floor explanation only partially — the C failures do skew toward smaller models, but Pixtral Large (a large model) failed 3 of 3 while much smaller models in other families were split. Llama 3.3 70B passed under the adjudication rule but produced a latent tag contradiction in all three runs: Bangalore retained the `home` tag while Pune was simultaneously tagged "primary residence," leaving two facts that a downstream consumer could reasonably read as conflicting.

A representative deletion failure interpreted the user's current stay in Pune as proof that the Bangalore home was obsolete. It deleted Bangalore and produced only:

> `Home (tag: home): Pune`

This was not a scorer artifact. The raw reflection explicitly described Bangalore as stale and instructed its removal.

### 5.3 Confidence restraint

Case D produced thirteen failures across 30 runs under the three-property rule (existence, severity, epistemic status). The failures cluster by family:

- Llama 3.1 8B failed 3 of 3 runs (two deleted the allergy outright; one downgraded severe to mild);
- Pixtral Large failed 3 of 3 runs (severity updated or "recently tolerated shellfish" asserted);
- Nova Pro failed 1 of 3 runs ("suggesting a potential change in allergy severity" promoted into the fact);
- Claude Haiku failed 2 of 3 runs (severity marked variable / "may be resolved");
- Llama 3.3 70B failed 2 of 3 runs (a tolerance claim added to the fact); and
- Grok 4.6 failed 2 of 3 runs ("do not treat severity as confirmed" — epistemic status explicitly revoked).

The most consequential failures either deleted a confirmed severe shellfish allergy entirely or downgraded it to mild after one anecdotal exposure without a significant reaction. This is the exact failure mode the case was designed to detect: weak recent evidence silently reducing the severity of a safety-critical fact.

The passing pattern illustrates the boundary precisely. One Nova Pro run passed while its sibling runs failed: the passing run kept the fact fully intact ("Severe shellfish allergy — confirmed by the user, carries an EpiPen") and appended the anecdote subordinately with both interpretations open ("suggesting possible change in allergy severity **or an isolated incident**"). The failing run asserted only the directional interpretation. The difference between pass and fail is whether the anecdote is quarantined as an observation or promoted into the fact's own confidence.

Successful models preserved the allergy, sometimes recording the new anecdote separately as unverified or recommending explicit confirmation rather than inferring a medical change.

## 6. Experiment 2 — Context Load (Arm 1)

Experiment 2 asks whether the Experiment 1 pattern holds when the conflicting fact is embedded in a larger memory context, and whether the revised policy submitted upstream changes behavior. An earlier context-load attempt did not produce a clean measurement: the offline reporting frame interacted with tool expectations, some responses were incomplete or unparseable, and the run did not isolate memory position from harness behavior. That attempt is superseded by the controlled arm reported here. Per-cell confidence intervals (Section 4.3) are used to separate confident signals from noise.

### 6.1 Design 

This arm ran on three models (Sonnet, Llama-3 8B, Nova Micro), two prompt versions (v1, the older Letta prompt, and pr, the revised policy submitted upstream), and three load levels (1x, 2x, 3x). Every run was manually adjudicated against the same rules as Experiment 1. For this arm, the conflicting fact was held at the end position for all cases.

### 6.2 Findings

- F1 Capability Axis: Two pooled buckets were compared on Cases C+D. Sonnet failed 1/36 (CI 0–14%) and Llama failed 26/36 (CI 56–84%). The intervals do not overlap, so the fail rates are separable.  

- F2 Safety: Llama-3 8B weakened or deleted the confirmed allergy in 15 of 18 runs (CI 61–94%), compared with Nova Micro at 1/18 and Sonnet at 0/18.

- F3 Llama Case-C surprise: predicted to worsen under load, Llama-C instead improved — failure fell from 6/6 (CI 61–100%) at 1x to 1/6 (CI 3–56%) at 3x (n=6 per cell). The endpoints are separable but the direction is opposite to the pre-registered prediction; the mechanism is unknown and is carried as a hypothesis for Arm 2.

### 6.3 Claims that did not survive uncertainty quantification

Two tempting claims did not hold up once intervals were attached. First, Nova Micro shows signs of confabulation under load, but the relevant intervals overlap, so "confabulation emerges under load" is not supported (only "confabulation observed under load"). Second, the apparent worsening of Llama on Case D (67% to 83%) overlaps the small-sample baseline interval (n=3, CI 21–94%) and is therefore not distinguishable from noise.

### 6.4 Limitation of this arm

This arm does not yet provide a clean single-variable comparison against the Experiment 1 baseline: prompt version, repeat count, and model sample all differ simultaneously. Isolating the position variable at a fixed load is the purpose of the planned follow-up (Arm 2).

## 7. Discussion

### 7.1 Action and restraint are different memory operations

The result is not adequately described by saying that models sometimes make memory mistakes. The errors are structurally concentrated.

Cases A and B reward decisive editing. The model identifies a change and performs an operation: replace or split. Cases C and D require a different policy. The model must recognize that newer evidence exists while deciding that the evidence does not justify destructive replacement.

The minimal prompt handles the first pattern robustly but supplies little explicit guidance for the second. It explains how to resolve stale facts, but not how to establish that a fact is sufficiently stale, contradicted, or weakly sourced to permit replacement.

### 7.2 Model size does not explain the pattern

The capability-floor hypothesis is falsified by the observed ordering. Pixtral Large — a large model — failed every C and D run, while smaller models in other families passed some or all restraint runs; Grok 4.6 passed C perfectly yet explicitly revoked the allergy's confirmed status in two D runs. The defensible conclusion is not that model size is irrelevant in general, but that performance in this sample is not monotonically ordered by apparent size: family membership predicts failure better than scale does.

Failures are model-specific and cluster in particular model families. Differences in architecture, training, instruction tuning, or alignment are plausible explanations, but the current design does not isolate those variables. They remain hypotheses rather than demonstrated causes.

### 7.3 The prompt under-specifies non-overwrite behavior

The observed failures are consistent with an overwrite mechanism:

1. the prompt emphasizes identifying contradictions and replacing stale information;
2. the transcript provides newer evidence;
3. some models treat recency as sufficient authority; and
4. the existing fact is removed even when the evidence supports coexistence, uncertainty, or confirmation instead.

Because the study evaluates one prompt policy, it cannot prove that a particular phrase caused the failures. It does show that the existing policy did not prevent them.

### 7.4 Safety relevance

The allergy downgrade demonstrates why restraint is not merely a preference for conservative summarization. Long-term memory can influence future recommendations and actions. Weakening a safety-critical fact without explicit confirmation changes the operational risk represented by memory.

A robust memory policy should consider at least:

- evidence source;
- confidence or confirmation status;
- temporal scope;
- whether facts can coexist;
- safety criticality; and
- whether a proposed update should supersede or merely annotate an existing fact.

These are design implications from the observed behavior, not variables tested in the present experiment.

## 8. Threats to Validity

### 8.1 Limited case coverage

Each category is represented by one scenario. The results demonstrate failure modes in these cases but do not estimate performance across the full space of memory conflicts.

### 8.2 Conservative policy in Case C

Case C assumes that the established Bangalore home should remain unless a permanent move is explicit. This is a deliberate conservative memory policy. The transcript itself leaves some room for interpreting Pune as the user's new primary residence. The result should therefore be understood as aggressive replacement under ambiguity, not as failure on an objectively unambiguous fact.

### 8.3 Small per-model sample

Each model–case condition has three runs. A 3-of-3 result shows consistency in this sample but should not be interpreted as deterministic behavior or a precise population failure rate.

### 8.4 Prompt-level rather than runtime-level evaluation

The harness evaluates intended memory edits produced from the reflection prompt. It does not execute the complete memory-editing runtime. The results therefore characterize prompt interpretation and intended updates rather than end-to-end runtime reliability.

### 8.5 Mechanical scoring limitations

Deterministic scoring cannot recognize every semantic weakening or malformed relationship. Visual verification was necessary for nuanced outputs, especially Case D. The report therefore distinguishes mechanical parsing from final human adjudication.

### 8.6 Causal interpretation

The cross-model pattern does not isolate architecture, training data, alignment, model size, or inference configuration. Family- and training-related explanations are plausible but unproven.

## 9. Implications for Memory-System Design

The evaluation suggests that memory systems should treat replacement as an evidentiary decision rather than a default response to recency. A future design could attach structured metadata to each fact, such as:

- source or speaker;
- observation and update time;
- confidence or confirmation status;
- safety criticality;
- temporal scope;
- supersession relationships; and
- active, disputed, or historical state.

A second design question is whether memory should destructively store only the current state or retain an event history from which the current state is derived. An event history preserves provenance and makes contested updates reversible, while a current-state view remains efficient for retrieval.

These proposals are motivated by the findings but are not evaluated in this study.

## 10. Conclusion

Across 120 runs, the evaluated minimal reflection policy handled action-type conflicts without failure: direct updates and compatible splits passed all 60 runs. Restraint-type conflicts failed exactly half of the time — 30 of 60 runs — after manual adjudication of every run against explicit rules. The failures were concentrated in particular model–case combinations and were not predicted by a simple model-size hierarchy.

The strongest conclusion is:

> Action-type memory conflicts were robust across the evaluated models, while restraint-type conflicts exposed model-specific overwrite behavior that was not monotonically related to model size.

The safety-relevant allergy downgrade demonstrates that non-overwrite policy is not an edge concern. A conflict-resolution prompt must specify not only how to replace stale facts, but also what evidence is required before an established fact—especially a safety-critical one—may be weakened or removed.

## Data and Reproducibility

The evaluation cases, the evaluated policy (Letta's reflection prompt, pinned verbatim at the commit recorded in this repository), the neutral transcription prompt, runner, scorer, confidence-interval script (`compute_cis.py`), and raw per-run outputs for both the primary matrix and the context-load extension (Arm 1) are included in this project.