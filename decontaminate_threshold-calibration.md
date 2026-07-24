# Threshold calibration

Read this file completely before selecting or defending any contamination threshold, minimum span, review band, clean-subset minimum, or release gate.

## Principle

There is no universal contamination threshold. Published n-gram settings are precedents tied to particular normalization, tokenization, corpora, tasks, and objectives. A threshold must be selected against labeled examples and evaluation-validity constraints.

## 1. Define the unit and harm

Specify:

- Unit: field, item, paragraph, record, document, group, source, lineage, or benchmark.
- Direction: evaluation-to-training, training-to-evaluation, or evaluation-time access.
- Leakage target: input only, source passage, answer, rationale, solution, tests, metadata, or generator lineage.
- Task harm: what knowledge would let the model bypass the capability being measured?
- Action: candidate, review, remove, re-split, block, quarantine, or retire.

The same overlap can have different consequences. A source paragraph seen before a closed-book factual test may matter; the same paragraph supplied in a reading-comprehension prompt may be legitimate. A question with its correct answer is higher risk than its background passage alone.

## 2. Build a labeled calibration set

Stratify pairs across:

- Benchmark and version.
- Language, script, romanization, and translation direction.
- Task profile: prose, QA, multiple choice, code, math, table, chat, tool, OCR.
- Item and record length.
- Exact, substring, paraphrase, translation, source-only, same-topic, template, lineage, and clean negatives.
- Common phrases, legal boilerplate, citations, code imports, formulas, and public facts.
- Boundary scores for every detector.

Use at least two reviewers for ambiguous task-equivalence labels. Record adjudication rules and disagreement. Keep a final blind audit set out of threshold selection.

Label more than “duplicate/not duplicate”:

- `EXACT_ITEM`
- `TASK_EQUIVALENT`
- `GROUND_TRUTH_LINKED`
- `TRANSLATED_EQUIVALENT`
- `SOURCE_ONLY`
- `SAME_TOPIC`
- `TEMPLATE_RELATED`
- `CLEAN`
- `POISON_SUSPECTED`
- `POISON_VALIDATED`

## 3. Version the fingerprint

Thresholds are inseparable from:

- Unicode normalization.
- Case, whitespace, punctuation, digit, URL, and markup handling.
- Word, Unicode-word, subword, character, or AST tokenization.
- Stopword policy.
- N-gram size and stride.
- Shingle set versus multiset.
- Embedding model, pooling, truncation, and similarity function.
- Translation or transliteration model.
- LLM adjudication prompt and model.

Changing any component requires recalibration.

## 4. Measure detector outputs

For every pair, retain:

```text
longest_match_tokens
matched_eval_tokens / eligible_eval_tokens
matched_train_tokens / eligible_train_tokens
intersection_shingles / union_shingles
intersection_shingles / min(eval_shingles, train_shingles)
edit_similarity
semantic_similarity
answer_linkage
structure_equivalence
lineage_evidence
source_frequency
```

Do not replace these with one blended score unless the blending model is itself calibrated and interpretable.

## 5. Sweep candidate settings

Start with a wide sweep:

| Component | Candidate sweep |
|---|---|
| Exact token span | `8`, `13`, `20`, `50` |
| Evaluation-token coverage | `0.20`, `0.50`, `0.70`, `0.80`, `0.90` |
| 5-word Jaccard | `0.70`, `0.75`, `0.80`, `0.85`, `0.90` |
| Containment | `0.80`, `0.90`, `0.95` |
| Semantic cosine | `0.90`, `0.93`, `0.95`, `0.97` |
| Clean-subset coverage | `0.70`, `0.80`, `0.90` |

These values are starting candidates, not recommendations. Add profile-specific points when the score distribution requires them.

For short items, whole-item equality, linked ground truth, answer/structure equivalence, or human review is safer than a generic n-gram rule. For code and math, use task-specific canonicalization and execution/symbolic evidence rather than prose settings.

## 6. Calculate operating metrics

```text
precision = true_positive_pairs / predicted_positive_pairs
recall = true_positive_pairs / labeled_positive_pairs
false_removal_rate = clean_records_removed / labeled_clean_records
residual_leakage = missed_leaking_pairs / labeled_leaking_pairs
review_rate = review_pairs / all_candidates
clean_subset_coverage = clean_items / original_items
group_survival = clean_items_in_group / original_items_in_group
```

Estimate confidence intervals by bootstrap or an appropriate exact method. Report denominators. Macro-average across benchmarks and protected groups in addition to micro-averaging.

## 7. Select by explicit constraints

Write constraints before viewing downstream benchmark differences. Example candidate constraints:

- Ground-truth-leak recall `>= 0.999`.
- Verified-pair precision `>= 0.98`.
- False-removal rate `<= 0.02`.
- Boundary review rate within operational capacity.
- Clean-subset coverage `>= 0.80`.
- Per-language and per-domain clean-subset survival above a declared minimum.
- Zero unresolved disallowed tool or cache exposures.
- Zero validated poisoned records in release data.

These are examples, not universal limits. Select a Pareto-feasible configuration. If none is feasible, improve the detectors or retire the benchmark; do not quietly relax the critical integrity constraints.

## 8. Prevent threshold overfitting

- Select thresholds on calibration data and confirm on the blind audit set.
- Do not tune a threshold solely to maximize the difference between clean and contaminated model scores; that can overfit the benchmark and conflate difficulty with contamination.
- Compare multiple model sizes/checkpoints only as supporting evidence.
- Check whether “dirty” and “clean” subsets differ in difficulty, length, topic, language, source, or answer distribution.
- Do not conclude that contamination is harmless merely because full and clean scores are similar.

## 9. Calibrate semantic and cross-lingual decisions

Use semantic retrieval for recall, then corroborate with:

- Same entities, quantities, constraints, answer, and solution structure.
- Cross-lingual alignment.
- Independent reviewer or model adjudication with blinded fields.
- Stable result across more than one embedding or adjudication method.

Require at least two evidence types for automatic removal unless a human verifies the pair. Record detector disagreement.

## 10. Calibrate poisoning alerts separately

Do not derive a universal “poison score.” Define threat-specific indicators:

- Integrity mismatch between collection-time and training-time content.
- Coordinated source or time burst.
- Rare trigger strongly associated with a target output.
- Unexpected label flips or benchmark-answer injection.
- Targeted belief/preference skew.
- Behavioral effect under isolated trigger testing.

Estimate baselines by source, language, topic, and time. Correct for multiple testing when scanning many triggers or targets. Require provenance/coordination or behavioral corroboration before calling intent validated.

## 11. Select clean-subset and retirement gates

A numeric coverage minimum is insufficient. Check:

- Size and statistical power.
- Language, domain, difficulty, length, and answer balance.
- Source, template, and lineage diversity.
- Confidence-interval width.
- Whether development decisions already used the benchmark.

If the clean subset is small, biased, or repeatedly used for model selection, retire the benchmark and use a fresh, private, rotating, or dynamic holdout.

## 12. Record the selection

Log:

- Candidate grid.
- Labeled-set construction and adjudication.
- Metrics with confidence intervals.
- Constraint table.
- Feasible configurations.
- Selected setting and tie-breaker.
- Blind-audit results.
- Per-group survival and errors.
- Known blind spots and recalibration triggers.

Recalibrate when the corpus, benchmark version, language mix, task profile, normalization, tokenizer, detector, embedding model, or threat model changes.
