# Threshold Calibration

Use this procedure for lexical thresholds, LSH parameters, containment cutoffs, semantic cutoffs, substring lengths, and event or synthetic cluster caps.

## Contents

1. Define constraints
2. Build labeled validation data
3. Sweep feature configurations
4. Evaluate pair and cluster behavior
5. Test complete policies
6. Select the operating point
7. Log the decision

## 1. Define constraints

Record approved limits for:

- False removal of genuinely unique documents.
- Duplicate leakage.
- Eligible-token and document retention.
- Per-language, script, source, profile, and license retention.
- Evaluation contamination.
- Compute, memory, and runtime.

If limits are missing, report the tradeoff frontier and request a decision. Do not invent a “correct” threshold.

## 2. Build labeled validation data

Sample random pairs plus:

- Exact copies with metadata or formatting changes.
- Headline-only and location-order changes.
- Syndicated press releases.
- News articles about the same event but independently written.
- Boilerplate-only overlap.
- Short and long documents.
- Native-script, romanized, code-mixed, and translated pairs.
- Code, legal, recipes, lists, OCR, PDFs, and synthetic variants.
- Pairs immediately above and below every candidate boundary.

Label each pair as `EXACT`, `LEXICAL_NEAR`, `CONTAINMENT`, `BOILERPLATE`, `SEMANTIC_PARAPHRASE`, `SAME_EVENT_UNIQUE`, `TRANSLATION`, `UNIQUE`, or `UNCERTAIN`. Double-label a meaningful subset and report agreement.

## 3. Sweep feature configurations

Treat these as experiment grids:

| Parameter | Candidate values |
|---|---|
| Word-shingle size | `3`, `5`, `7`, `9`, `13` |
| Character-shingle size | language/profile-specific grid |
| MinHash permutations | `112`, `128`, `256`, `512` |
| LSH bands × rows | configurations matching signature length |
| Verified Jaccard | `0.70`, `0.75`, `0.80`, `0.85`, `0.90`, `0.95` |
| Containment | `0.80`, `0.90`, `0.95`, `0.98` |
| Minimum repeated span | `13`, `20`, `50` tokens |
| Semantic cosine | `0.90`, `0.93`, `0.95`, `0.97`, model-specific |
| Event/synthetic cap | `1`, `2`, `4`, `8`, `16` |

Do not compare LSH configurations only by their nominal threshold. Plot:

```text
P(candidate | s) = 1 - (1 - s^r)^b
```

at similarities `0.50` through `1.00`, and measure actual candidate recall and precision.

## 4. Evaluate pair and cluster behavior

For every configuration, report:

```text
pair_precision = true_duplicate_predicted_pairs / predicted_duplicate_pairs
pair_recall = true_duplicate_predicted_pairs / labeled_duplicate_pairs
false_removal_rate = unique_documents_removed / labeled_unique_documents
duplicate_leakage = duplicate_documents_retained / labeled_duplicate_documents
```

Also measure:

- Precision and recall by duplicate class.
- MinHash estimated-versus-exact Jaccard error.
- LSH candidate recall before exact verification.
- Cluster purity, bridge-edge error, and cluster diameter.
- Token/document removal.
- Per-language, script, source, profile, length, and license retention.
- Translation and independent-news survival.
- Runtime, memory, shuffle, and index size.

## 5. Test complete policies

Create named bundles such as:

- `OFF`
- `EXACT_ONLY`
- `CONSERVATIVE_NEAR`
- `BALANCED_NEAR`
- `AGGRESSIVE_LEXICAL`
- `LEXICAL_PLUS_SEMANTIC_CAP`

Specify every component. Do not linearly tighten all thresholds behind a single slider.

## 6. Select the operating point

Remove policies that violate any approved constraint. A policy is dominated if another viable policy has equal-or-better downstream performance, duplicate removal, unique-document preservation, retention, diversity, and cost, with at least one strict improvement.

When feasible, train proxy language models with the same architecture, tokenizer, consumed training tokens, steps, and evaluation suite. Evaluate general capability, target languages, knowledge, reasoning, code, long-form behavior, cultural knowledge, memorization, and contamination.

Choose:

```text
policy_star = argmax downstream_utility(policy)
```

subject to all false-removal, duplicate-leakage, contamination, token, language, profile, diversity, and cost constraints. If viable policies are statistically tied, choose the least aggressive one.

## 7. Log the decision

Record every candidate, parameter, measured metric, failed constraint, dominated alternative, selected bundle, confidence interval, unresolved risk, and downstream result. Recalibrate when the corpus, tokenizer, normalization, language mixture, embedding model, scope, or crawl distribution changes.
