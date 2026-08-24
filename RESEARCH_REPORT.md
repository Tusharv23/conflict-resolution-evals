# Action vs. Restraint in LLM Memory Reflection

## A Cross-Model Evaluation of Letta's Conflict-Resolution Prompt

## Abstract

Long-term agent memory must decide not only what information to add or replace, but also when newer evidence is insufficient to justify changing an established fact. This study evaluates Letta's reflection prompt on four classes of implicit memory conflict: a direct update, compatible facts that require splitting, an inferential non-overwrite case, and a confidence-sensitive non-overwrite case. Ten models from five provider families were evaluated across 132 runs, with 33 runs per case.

The two action-type cases were handled without failure: the direct update and compatible split both passed 33 of 33 runs. The restraint-type cases were less reliable. The inferential case failed 10 of 33 runs (30.3%), while the confidence-preservation case failed 3 of 33 runs (9.1%). Across both restraint cases, 13 of 66 runs failed (19.7%), compared with 0 of 66 action runs. Failures were concentrated in particular model–case combinations and were not monotonically related to apparent model size. One safety-relevant failure weakened a confirmed severe shellfish allergy to a mild allergy after a single anecdotal counterexample.

These results suggest that a minimal recency-oriented conflict policy can handle explicit memory operations robustly while under-specifying when an existing fact should be preserved. The study is exploratory and does not isolate architecture or training as causal variables. An attempted context-load extension was methodologically confounded and is retained only as inconclusive future work.

## 1. Research Question

Letta's reflection prompt instructs the model to resolve contradictions in favor of the latest evidence. This is appropriate when a transcript explicitly establishes that a stored fact is stale. Real memory updates, however, also contain apparent contradictions in which the correct behavior is to preserve the existing fact.

This evaluation asks:

> Does a minimal conflict-resolution prompt distinguish between conflicts that require an action and conflicts that require restraint?

A secondary question is whether failure can be explained by a simple model-capability hierarchy in which smaller models fail more frequently than larger models.

## 2. Hypotheses

The study began with two hypotheses.

### H1 — Prompt insufficiency

The minimal "latest evidence" policy would mishandle nuanced conflicts, particularly compatible facts, inferential distinctions, and confidence asymmetry.

### H2 — Capability floor

If nuanced conflict resolution depends primarily on general model capability, smaller models should fail more consistently than larger models.

The evidence did not support either hypothesis in its original form. Compatible facts were handled robustly, and failure was not ordered by apparent model size. The results instead exposed a distinction between action-type and restraint-type memory operations.

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

The evaluation covers ten models from five provider families. Each case has 33 completed runs: three runs per model plus three valid earlier runs whose result format differs from the later matrix. The earlier runs were retained because the underlying reflections and memory decisions were valid.

The full evaluation therefore contains:

- 4 cases;
- 33 runs per case; and
- 132 total runs.

### 4.2 Two-stage harness

The harness separates memory reflection from measurement.

#### Stage 1 — Reflection

The model receives Letta's reflection prompt, the current memory, and a short transcript. Because the prompt normally expects editing tools, the harness adds a disclosed instruction asking the model to report the intended final memory state as text. The evaluated output is therefore the model's intended edit rather than an edit executed through a complete Letta runtime.

#### Stage 2 — Transcription

A second prompt converts the Stage 1 response into structured JSON containing the final memory lines and reported actions. This stage only transcribes the reflection decision. It is explicitly prohibited from judging, correcting, or improving that decision.

The raw Stage 1 response, Stage 2 transcription, and parsed output are retained for each run, allowing failures to be checked directly against the reflection model's reasoning.

### 4.3 Scoring and adjudication

Cases A–C use deterministic checks over the structured final memory, followed by visual verification of reported failures. Case D requires semantic judgment because an allergy can be weakened without being deleted. Its automatically flagged outputs were therefore reviewed visually.

The final adjudication rules are:

- **A passes** when the sister's Vancouver address replaces Surrey while unrelated facts remain intact.
- **B passes** when both the father's Delhi address and the mother's Gurgaon address remain represented.
- **C passes** when Bangalore remains and Pune is represented as a distinct fact; it fails when Pune replaces Bangalore.
- **D passes** when the severe allergy remains unweakened; it fails when the allergy is deleted or softened.

One D output could not be read by the analyzer. No memory modification was produced, and preservation of the existing allergy was the required behavior, so the run was adjudicated as a pass. This decision is disclosed rather than treated as an automatically parsed result.

## 5. Results

### 5.1 Aggregate results

| Case | Operation class | Pass | Fail | Pass rate | Failure rate |
|---|---|---:|---:|---:|---:|
| A — direct update | Action | 33 | 0 | 100.0% | 0.0% |
| B — compatible split | Action | 33 | 0 | 100.0% | 0.0% |
| C — inferential non-overwrite | Restraint | 23 | 10 | 69.7% | 30.3% |
| D — confidence preservation | Restraint | 30 | 3 | 90.9% | 9.1% |
| **Action total** | — | **66** | **0** | **100.0%** | **0.0%** |
| **Restraint total** | — | **53** | **13** | **80.3%** | **19.7%** |
| **Overall** | — | **119** | **13** | **90.2%** | **9.8%** |

Every observed behavioral failure occurred in a restraint case.

### 5.2 Inferential restraint

Case C produced the clearest cross-model separation. The ten failures were concentrated in a subset of models:

- Nova Pro failed 3 of 3 runs;
- Llama 4 Maverick failed 3 of 3 runs;
- Llama 3.1 8B failed 2 of 3 runs;
- Claude Haiku failed 1 run; and
- Pixtral failed 1 run.

Other tested models passed all C runs, including Nova Micro. This pattern contradicts a simple capability-floor explanation: the smaller Nova model preserved the distinction while Nova Pro overwrote it consistently.

A representative failure interpreted the user's current stay in Pune as proof that the Bangalore home was obsolete. It deleted Bangalore and produced only:

> `Home (tag: home): Pune`

This was not a scorer artifact. The raw reflection explicitly described Bangalore as stale and instructed its removal.

### 5.3 Confidence restraint

Case D produced three failures across 33 runs. The remaining 30 runs preserved the confirmed allergy after visual adjudication.

The most consequential failure changed the stored fact from a confirmed severe shellfish allergy to a mild allergy after one anecdotal exposure without a significant reaction. This is the exact failure mode the case was designed to detect: weak recent evidence silently reducing the severity of a safety-critical fact.

Successful models preserved the allergy, sometimes recording the new anecdote separately as unverified or recommending explicit confirmation rather than inferring a medical change.

## 6. Discussion

### 6.1 Action and restraint are different memory operations

The result is not adequately described by saying that models sometimes make memory mistakes. The errors are structurally concentrated.

Cases A and B reward decisive editing. The model identifies a change and performs an operation: replace or split. Cases C and D require a different policy. The model must recognize that newer evidence exists while deciding that the evidence does not justify destructive replacement.

The minimal prompt handles the first pattern robustly but supplies little explicit guidance for the second. It explains how to resolve stale facts, but not how to establish that a fact is sufficiently stale, contradicted, or weakly sourced to permit replacement.

### 6.2 Model size does not explain the pattern

The capability-floor hypothesis is falsified by the observed ordering. A small model can preserve a nuanced distinction that a larger model consistently removes. The defensible conclusion is not that model size is irrelevant in general, but that performance in this sample is not monotonically ordered by apparent size.

Failures are model-specific and cluster in particular model families. Differences in architecture, training, instruction tuning, or alignment are plausible explanations, but the current design does not isolate those variables. They remain hypotheses rather than demonstrated causes.

### 6.3 The prompt under-specifies non-overwrite behavior

The observed failures are consistent with an overwrite mechanism:

1. the prompt emphasizes identifying contradictions and replacing stale information;
2. the transcript provides newer evidence;
3. some models treat recency as sufficient authority; and
4. the existing fact is removed even when the evidence supports coexistence, uncertainty, or confirmation instead.

Because the study evaluates one prompt policy, it cannot prove that a particular phrase caused the failures. It does show that the existing policy did not prevent them.

### 6.4 Safety relevance

The allergy downgrade demonstrates why restraint is not merely a preference for conservative summarization. Long-term memory can influence future recommendations and actions. Weakening a safety-critical fact without explicit confirmation changes the operational risk represented by memory.

A robust memory policy should consider at least:

- evidence source;
- confidence or confirmation status;
- temporal scope;
- whether facts can coexist;
- safety criticality; and
- whether a proposed update should supersede or merely annotate an existing fact.

These are design implications from the observed behavior, not variables tested in the present experiment.

## 7. Threats to Validity

### 7.1 Limited case coverage

Each category is represented by one scenario. The results demonstrate failure modes in these cases but do not estimate performance across the full space of memory conflicts.

### 7.2 Conservative policy in Case C

Case C assumes that the established Bangalore home should remain unless a permanent move is explicit. This is a deliberate conservative memory policy. The transcript itself leaves some room for interpreting Pune as the user's new primary residence. The result should therefore be understood as aggressive replacement under ambiguity, not as failure on an objectively unambiguous fact.

### 7.3 Small per-model sample

Each model–case condition has three runs. A 3-of-3 result shows consistency in this sample but should not be interpreted as deterministic behavior or a precise population failure rate.

### 7.4 Prompt-level rather than runtime-level evaluation

The harness evaluates intended memory edits produced from the reflection prompt. It does not execute the complete memory-editing runtime. The results therefore characterize prompt interpretation and intended updates rather than end-to-end runtime reliability.

### 7.5 Mechanical scoring limitations

Deterministic scoring cannot recognize every semantic weakening or malformed relationship. Visual verification was necessary for nuanced outputs, especially Case D. The report therefore distinguishes mechanical parsing from final human adjudication.

### 7.6 Causal interpretation

The cross-model pattern does not isolate architecture, training data, alignment, model size, or inference configuration. Family- and training-related explanations are plausible but unproven.

## 8. Inconclusive Context-Load Extension

A follow-up condition attempted to place the conflicting fact inside a larger memory context. That extension did not produce a clean measurement. The offline reporting frame interacted with tool expectations, some responses were incomplete or unparseable, and the run did not isolate memory position from harness behavior.

No lost-in-the-middle conclusion is drawn from that condition. Context load remains future work requiring a faithful tool-execution harness and controlled variation of context length and fact position.

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

Across 132 runs, Letta's minimal reflection prompt handled action-type conflicts without failure: direct updates and compatible splits passed all 66 runs. Restraint-type conflicts were less reliable, failing 13 of 66 runs. The failures were concentrated in particular model–case combinations and were not predicted by a simple model-size hierarchy.

The strongest conclusion is:

> Action-type memory conflicts were robust across the evaluated models, while restraint-type conflicts exposed model-specific overwrite behavior that was not monotonically related to model size.

The safety-relevant allergy downgrade demonstrates that non-overwrite policy is not an edge concern. A conflict-resolution prompt must specify not only how to replace stale facts, but also what evidence is required before an established fact—especially a safety-critical one—may be weakened or removed.

## Data and Reproducibility

The evaluation cases, pinned reflection prompt, neutral transcription prompt, runner, scorer, and raw per-run outputs are included in this project. The context-load extension is retained as inconclusive evidence and is not included in the reported S0 result.