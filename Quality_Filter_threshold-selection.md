# Threshold Calibration and Selection
Use this procedure whenever a run must choose, tune, change, or justify quality-filter thresholds. There is no universal right threshold. The right operating point is where additional filtering no longer improves downstream model utility or begins deleting required languages, domains, profiles, diversity, or token volume.

## 1. Define the decision contract

Record before testing:

- Intended model, mixture, languages, scripts, domains, and content profiles.
- Quality meaning: educational value, clean prose, task usefulness, or another explicit rubric.
- Maximum good-document false-rejection rate.
- Maximum junk leakage.
- Minimum eligible-token retention.
- Per-language, per-script, and per-profile retention floors.
- Required downstream and diversity evaluations.

These limits are project requirements, not universal constants. Never invent them. If they are missing, report candidate tradeoffs and request a decision instead of declaring one threshold correct.

## 2. Build a representative labeled set

Sample across languages, native and romanized scripts, sources, domains, profiles, lengths, dates, random documents, and documents close to current boundaries. Include valid code, lists, recipes, legal text, OCR, tables, chat, and low-resource content.

For each sample, record:

- Human or trusted-teacher quality score on the declared scale.
- `keep`, `review`, or `reject`.
- Content profile and defect reason codes.
- Language, script, source, domain, and length bucket.

Keep factuality, safety, toxicity, and language identity as separate labels. Double-label a meaningful subset and report agreement and adjudication.

## 3. Separate hard and soft evidence

Candidate hard failures include confirmed empty or nonlinguistic content, severe repetition, unrecoverable mojibake or OCR corruption, residual HTML/JS/CSS payloads, lorem ipsum, and obvious SEO/template spam.

Soft evidence includes mean word length, terminal punctuation, stopword count, document length, bullet ratio, ellipsis ratio, and moderate symbol ratio. Shared-script, morphology, code, lists, recipes, legal clauses, OCR, and chat can change their meaning.

Use this provisional routing logic only as a starting candidate:

```text
confirmed hard failure        -> reject
one soft failure              -> keep with warning
two or more soft failures     -> classifier or review
profile-conflicted failure    -> special-format bucket
```

Do not convert a soft signal into a hard rejection until labeled and downstream evidence supports it.

## 4. Sweep candidate boundaries

The following are experiment grids, not recommended thresholds:

| Signal | Candidate values |
|---|---|
| Mean word length | `[2,12]`, `[3,10]`, `[3.5,9]` |
| Symbol-to-word ratio | `<0.20`, `<0.10`, `<0.05` |
| Terminal-punctuation line fraction | `>=0.10`, `>=0.20`, `>=0.30`, `>=0.50` |
| Duplicate-line fraction | `<0.50`, `<0.30`, `<0.20`, `<0.10` |
| Top 2-gram character fraction | `<0.30`, `<0.20`, `<0.15`, `<0.10` |
| Stopword count | `>=0`, `>=1`, `>=2`, language-specific |
| Bullet-line fraction | `<0.95`, `<0.90`, `<0.75` |
| Ellipsis-line fraction | `<0.50`, `<0.30`, `<0.10` |
| Minimum word count | `20`, `50`, `100` |
| Classifier threshold on a 0–5 scale | `2`, `2.5`, `3`, `3.5`, `4` |

Test both individual boundaries and complete policy bundles. Include `OFF`, `LOOSE`, `BALANCED_HIGH_RECALL`, `BALANCED_HIGH_QUALITY`, `STRICT_EDUCATIONAL`, and `KEEP_NONE_SANITY`. The strictness slider must select validated bundles; it must not imply equal linear increments.

## 5. Calculate decision metrics

For every candidate, log exact counts, denominators, formulas, and values:

```text
rejection_precision = correctly_rejected_low_quality / all_rejected
good_document_false_rejection_rate = good_documents_rejected / all_labeled_good_documents
junk_leakage = low_quality_documents_retained / all_labeled_low_quality_documents
token_retention = kept_eligible_tokens / eligible_input_tokens
document_retention = kept_eligible_documents / eligible_input_documents
```

Report confidence intervals when the labeled set permits them. Break all metrics down by language, script/romanization, profile, source, domain, length, and quality bucket. Also measure topic/source diversity and special-format survival.

## 6. Find viable and Pareto-optimal policies

First remove candidates that violate any declared constraint. A remaining policy is dominated when another policy has equal-or-better downstream results, useful-token retention, valid-document preservation, junk removal, and diversity, with at least one strict improvement. Retain the nondominated Pareto frontier and show why every discarded candidate failed or was dominated.

## 7. Run equal-token proxy-model experiments

When feasible, train small proxy language models on each viable dataset with the same architecture, tokenizer, training-token budget, optimization steps, and evaluation suite. Equalize consumed training tokens so a smaller filtered corpus does not win or lose merely because it supplied a different training budget.

Evaluate general language modeling, target-language capability, knowledge and reasoning, reading, code, cultural knowledge, long-form behavior, repetition, domain benchmarks, and profile-specific tasks. Report uncertainty and run-to-run variance when available.

## 8. Select and log the operating point

Choose:
```text
theta_star = argmax downstream_score(theta)
```

subject to all approved false-rejection, junk-leakage, token-retention, language-retention, profile-retention, and diversity constraints. If scores are statistically indistinguishable, choose the least aggressive viable policy.

The final decision statement must name the selected bundle, exact metric and classifier thresholds, exemptions, constraints, alternatives rejected, evidence used, and known risks. Log every candidate even when it is discarded. The decision criterion is: select the least aggressive threshold that reliably removes harmful data, improves downstream performance, preserves required token volume, and does not disproportionately erase valid languages, domains, or formats.
