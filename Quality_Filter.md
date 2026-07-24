---
name: quality-filter
description: Measure, audit, classify, and route document quality in multilingual pretraining, SFT, web, OCR, PDF, news, educational, code, list, recipe, legal, and conversational corpora. Use when applying Gopher/C4-style heuristics, detecting SEO spam or repetitive and low-value pages, tracing nine quality metrics, creating LLM educational-quality labels, training a cheaper quality classifier, tuning strictness and retention tradeoffs, protecting valid special-format or low-resource content, or producing a visible step-by-step quality-filter log with reasons and corpus-survival statistics.
---

# Quality Filter

Decide whether a document is useful for the intended training mixture. Use a transparent heuristic cascade first and an optional learned quality classifier second. Log every measurement, threshold, exemption, score, and routing decision.

## Core principles

1. Preserve raw input and provenance. Route documents; do not silently destroy them.
2. Run extraction, `$normalization-steps`, and `$language-skill` before quality filtering when available.
3. Separate text quality, educational value, factual accuracy, safety, licensing, privacy, and deduplication. Passing one does not prove the others.
4. Apply rules by language and content profile. English web-prose thresholds are not universal.
5. Treat the nine supplied thresholds as `user-baseline-v1`, not as universally optimal Gopher or C4 constants.
6. Define every numerator, denominator, tokenizer, punctuation set, and boundary operator.
7. Preserve useful recipes, lists, code, legal text, poetry, chats, and short definitions through profile-specific rules or routing.
8. Use a classifier score as evidence, not truth. Record its training labels, domain, language coverage, calibration, and bias.
9. Permit abstention and review. A strict filter can erase valuable domains and low-resource languages.
10. Select strictness using retention, quality, diversity, per-language survival, and downstream model evaluation.
11. Log unchanged and passing stages; never report only “quality filter passed.”
12. Report observable evidence without exposing private chain-of-thought.

## Interpret the transcript carefully

- “Gopher/C4 heuristics” means a family of transparent quality and repetition checks, not one interchangeable canonical rule set.
- “Educational quality” is one possible classifier objective. It is not identical to truthfulness, cultural value, conversational value, or general pretraining utility.
- A well-written news article can contain an incorrect claim. Quality filtering does not replace fact-checking.
- Within-document repeated lines and n-grams belong in this filter. Cross-document exact and near-duplicate removal is a separate deduplication stage.
- Code-mixed or romanized Indic text is not low quality merely because it contains English or Latin script.
- Statements such as “44% remains,” “7% is useful,” or “95% kept” are example run outcomes, not required targets.
- Claims about private companies’ raw token totals or unreleased pipelines are not operational evidence and must not become thresholds.

## Two-layer design

### Layer 1 — Heuristic cascade

Compute cheap, interpretable metrics for every document. Use hard failures only where the selected profile and calibration justify them. Retain every metric even after an early failure so the audit shows all reasons, unless compute policy explicitly enables early exit.

### Layer 2 — Learned quality classifier

Score a representative sample with a capable teacher model or qualified human annotators, train a cheaper model to reproduce the rubric, validate it on held-out gold data, and score the full eligible corpus. Retain the continuous score even when a threshold produces a keep/drop decision.

## Establish the quality contract

Define before filtering:

- Training purpose: general pretraining, educational pretraining, code, SFT, retrieval, evaluation, or another goal.
- Target languages and scripts.
- Content profiles and their allowed structures.
- Hard-fail, soft-fail, warning, and exemption rules.
- Heuristic threshold version.
- Educational-quality rubric.
- Classifier architecture, version, supported languages, and calibration.
- Strictness-to-threshold mapping.
- Per-language and per-domain minimum survival or review policy.
- Final dispositions and storage locations.

Use these profiles:

| Profile | Examples | Important protection |
| --- | --- | --- |
| `web-prose` | Articles, explanatory pages | Apply the complete baseline after calibration |
| `news` | Reporting, interviews | Do not equate style quality with factual accuracy |
| `educational` | Tutorials, textbooks | Use educational score while retaining topic diversity |
| `code` | Source code, notebooks | Exempt prose punctuation, stop-word, and symbol rules |
| `structured` | JSON, YAML, tables | Validate structure; do not apply prose ratios blindly |
| `list-recipe` | Ingredients, steps, directories | High bullet ratio can be legitimate |
| `legal-policy` | Statutes, contracts | Repeated clauses and long documents may be legitimate |
| `conversation` | Forums, dialogue, SFT | Ellipses and short turns can be intentional |
| `poetry-verse` | Poems, lyrics, verse | Terminal punctuation and word-count rules need overrides |
| `mixed` | Multiple span types | Score spans by profile and aggregate explicitly |

## User baseline: nine traced metrics

Apply these exact operators only under `user-baseline-v1`:

| Metric | Pass condition | Boundary behavior |
| --- | --- | --- |
| Mean word length | `3 <= value <= 10` | 3 and 10 pass |
| Symbol-to-word ratio | `value < 0.10` | 0.10 fails |
| Terminal-punctuation line ratio | `value >= 0.30` | 0.30 passes |
| Duplicate-line fraction | `value < 0.30` | 0.30 fails |
| Top 2-gram character fraction | `value < 0.20` | 0.20 fails |
| Common stop words | At least 2 distinct configured stop words | Exactly 2 passes |
| Bullet-line ratio | `value < 0.90` | 0.90 fails |
| Ellipsis-line ratio | `value < 0.30` | 0.30 fails |
| Document word count | `50 <= words <= 100000` | 50 and 100000 pass |

Record `pass_count`, `fail_count`, and all failure reasons. Do not copy the example values `5.1`, `0.00`, `1.00`, `89 words`, `95%`, or `2.6/5` into a new run.

## Metric definitions

### Word and line basis

- Use normalized text.
- Use non-empty lines after preserving meaningful structure.
- Record the word tokenizer and Unicode version.
- For multilingual text, prefer language-aware word segmentation.
- For Indic text, measure word length in grapheme clusters when possible; never use UTF-8 bytes as character length.
- For languages without ordinary spaces, do not apply an English whitespace tokenizer.

### Mean word length

Use:

```text
sum(length(word) for each eligible word) / eligible_word_count
```

Exclude standalone punctuation. State whether length uses grapheme clusters or Unicode code points.

### Symbol-to-word ratio

For the Gopher-style baseline, compute the hash and ellipsis ratios separately:

```text
hash_ratio = count("#") / word_count
ellipsis_ratio_to_words = count(ellipsis_tokens) / word_count
symbol_to_word_ratio = max(hash_ratio, ellipsis_ratio_to_words)
```

Recognize `...` and U+2026 consistently. If a broader symbol inventory is used, name every included Unicode category or character and version the rule.

### Terminal-punctuation line ratio

Use:

```text
eligible non-empty prose lines ending in configured terminal punctuation
---------------------------------------------------------------------------
all eligible non-empty prose lines
```

The baseline punctuation is `.`, `!`, and `?`. Extend it by language, including relevant forms such as `।`, `॥`, `؟`, and fullwidth punctuation. Exclude code and structured spans from the prose denominator.

### Duplicate-line fraction

Normalize comparison keys without changing stored text. Use:

```text
sum(max(line_frequency - 1, 0))
--------------------------------
eligible non-empty line count
```

Record case folding, punctuation handling, whitespace normalization, and whether boilerplate lines were removed first.

### Top 2-gram character fraction

Tokenize into words, identify the most frequent word bigram, calculate the number of document characters covered by its occurrences, and divide by eligible document characters. Do not double-count overlapping character coverage. Record the winning bigram, count, covered characters, and denominator.

Do not substitute `top_bigram_count / total_bigrams` while calling it a character fraction.

### Common stop words

Count distinct configured stop words present in eligible prose. For the English Gopher-style list, the source set is:

```text
the, be, to, of, and, that, have, with
```

Use language-specific lists for other languages. Disable this rule when no validated list exists. Do not fail code, names, short definitions, or languages merely because they lack English stop words.

### Bullet-line ratio

Use:

```text
lines starting with a configured bullet marker / eligible non-empty lines
```

Record the bullet markers. Route valid recipes, procedural lists, and structured lists to their profile instead of deleting them automatically.

### Ellipsis-line ratio

Use:

```text
eligible non-empty lines ending in `...` or U+2026 / eligible non-empty lines
```

Do not apply the prose default blindly to intentional conversation or dramatic writing.

### Document word count

Count eligible natural-language words with the configured tokenizer. Do not count raw HTML tags as words. Route short but valuable definitions, Q&A, captions, and examples to a short-form profile or review bucket. Segment exceptionally long coherent documents rather than discarding them solely for length when the corpus contract allows it.

## Mandatory execution log

Create a run header and one entry for every numbered stage. Use `NO ISSUE` when a stage passes without a problem; never omit a stage.

### Run header

Report:

- Run and document identifiers.
- Source, language, script, and content profile.
- Training purpose.
- Normalization and language-ID versions.
- Heuristic profile and threshold version.
- Teacher rubric, classifier version, and supported languages.
- Strictness value and its exact threshold mapping.
- Input characters, bytes, words, lines, and tokens when measurable.
- Assumptions, exemptions, and unavailable information.

Never fabricate measurements, scores, thresholds, or versions. Write `not measured` or `not available`.

### Per-stage entry

Use:

```markdown
### Step NN — <stage name>

- Purpose:
- Profile:
- Metric or evidence:
- Formula and denominator:
- Observed value:
- Threshold or rule:
- Status: PASS | NO ISSUE | WARNING | REVIEW | FAIL | EXEMPT | BLOCKED
- Decision effect:
- Reason code:
- Representative evidence:
- Warnings:
```

Requirements:

- Show the metric even when it passes.
- Show exact-versus-rounded values near a threshold.
- Show up to three bounded examples for failures or overrides.
- Mask sensitive text while preserving the quality feature.
- State why a rule is exempt.
- Keep teacher and classifier scores separate.
- Do not reveal hidden reasoning.

Maintain a machine-readable document record:

```json
{
  "document_id": "doc-001",
  "language": "hi",
  "profile": "web-prose",
  "heuristic_version": "user-baseline-v1",
  "metrics": {
    "mean_word_length": {"value": 5.1, "operator": "between_inclusive", "min": 3, "max": 10, "status": "PASS"},
    "duplicate_line_fraction": {"value": 0.0, "operator": "lt", "threshold": 0.3, "status": "PASS"}
  },
  "heuristic_pass_count": 9,
  "heuristic_fail_count": 0,
  "teacher_score": "not available",
  "classifier_score": 3.4,
  "classifier_threshold": 3.0,
  "strictness": 2.5,
  "decision": "ACCEPT_STANDARD",
  "reason_codes": ["HEURISTICS_PASS", "CLASSIFIER_PASS"],
  "policy_version": "quality-policy-v1"
}
```

## Quality-filter workflow

### Step 01 — Preserve raw input and provenance

- Retain raw and normalized text separately.
- Record source URL or identifier, crawl snapshot, extraction method, claimed language, and licensing metadata when available.
- Compute sizes and checksums only with tools that can measure them.

### Step 02 — Confirm prerequisites

- Confirm content extraction, normalization, and language identification ran.
- Block or quarantine materially corrupted text.
- Keep the detected language and content spans for language-aware metrics.

### Step 03 — Assign content profiles

- Classify document and spans using the profile table.
- Default uncertain spans to preservation or review.
- Record every heuristic exemption before calculating the cascade.

### Step 04 — Measure document word count

- Apply the profile-specific tokenizer and inclusive `[50, 100000]` baseline only where valid.
- Record short-form or long-document overrides separately.

### Step 05 — Measure mean word length

- Apply inclusive `[3, 10]` under the baseline.
- Flag abnormal tokenization, mojibake, concatenated text, or identifier-heavy content before assuming low quality.

### Step 06 — Measure symbol-to-word ratio

- Compute hash and ellipsis-to-word ratios separately and retain both.
- Apply `< 0.10` under the user baseline.
- Exempt code, math, and structured data when appropriate.

### Step 07 — Measure terminal-punctuation lines

- Apply `>= 0.30` using language-specific terminal punctuation and eligible prose lines.
- Do not treat headings, tables, code, and list items as failed prose lines.

### Step 08 — Measure duplicate lines

- Apply `< 0.30` under the baseline.
- Show the most repeated normalized lines.
- Distinguish SEO repetition from legitimate legal, poetic, navigational, or templated repetition.

### Step 09 — Measure top 2-gram repetition

- Apply `< 0.20` using the character-coverage definition.
- Show the winning bigram and covered-character fraction.
- Optionally compute the full Gopher repetition family: duplicate paragraphs, duplicate line/paragraph character fractions, top 3- and 4-gram character fractions, and duplicate 5- through 10-gram character fractions. Version any added thresholds.

### Step 10 — Check stop words and alphabetic content

- Require at least two distinct validated stop words under the baseline.
- Use language-specific lists.
- Optionally trace the Gopher-style proportion of words containing at least one alphabetic character; do not assume the English 80% rule is valid for every profile or language.

### Step 11 — Measure bullet-line ratio

- Apply `< 0.90` under the baseline.
- Route legitimate list-heavy content rather than failing it automatically.

### Step 12 — Measure ellipsis-line ratio

- Apply `< 0.30` under the baseline.
- Recognize both three dots and U+2026.
- Use conversation-specific rules for chat or SFT data.

### Step 13 — Detect web and spam failure modes

Trace separately:

- Residual HTML or markup.
- JavaScript or CSS fragments.
- Placeholder text such as lorem ipsum.
- Keyword stuffing and near-repeated SEO phrases.
- Link farms and doorway pages.
- Scraped search results.
- Navigation, cookie, and terms-of-use text.
- Username-only or trivial greeting exchanges.
- Identifier, voter-ID, city-name, or catalog dumps.
- Low-information template pages.
- Garbled OCR or mojibake.

Use C4-style signals only in appropriate profiles. A curly brace is not a web-junk signal inside code or JSON.

### Step 14 — Produce the heuristic-cascade verdict

- Report all nine statuses, pass count, fail count, exemptions, and warning count.
- Under strict cascade mode, any applicable hard failure produces `EXCLUDE_HEURISTIC`.
- Under review mode, borderline or profile-conflicted failures produce `REVIEW`.
- Never convert an exemption into an automatic pass without recording it.

### Step 15 — Create teacher quality labels

If a learned classifier is requested:

- Sample documents by language, source, domain, profile, length, and heuristic outcome.
- Prevent one high-resource language or domain from dominating.
- Use a documented 0–5 rubric:
  - `0`: unusable, corrupt, or pure spam.
  - `1`: barely coherent or almost no transferable information.
  - `2`: readable but limited, shallow, or weakly useful.
  - `3`: useful, coherent, and educational or informative.
  - `4`: strong explanation, organization, and substantive value.
  - `5`: exceptional clarity, depth, and pedagogical or informational value.
- Ask the teacher for a score plus concise evidence codes, not hidden chain-of-thought.
- Use a teacher that supports the document language; otherwise route to qualified human review.
- Measure agreement on an overlapping labeled subset.
- Keep factuality and safety labels separate.

### Step 16 — Train and validate the cheap classifier

- Split labels by source and near-duplicate group to prevent leakage.
- Compare suitable lightweight approaches such as fastText or a frozen multilingual embedding model plus a regression/classification head.
- Keep a held-out human-reviewed test set.
- Report per-language and per-profile precision, recall, F1, calibration, confusion, and false-rejection rates.
- Test whether the classifier merely learns source, length, language, or formatting shortcuts.
- Retain model score, not only the thresholded label.

FineWeb-Edu is a reference recipe, not a default: it used Llama-3-70B-Instruct labels on a 0–5 educational scale, a linear regressor over frozen Snowflake-arctic-embed-m representations, and threshold 3. DCLM found a fastText quality classifier effective in its experiments. Reproduce neither recipe without multilingual and domain-specific validation.

### Step 17 — Map classifier strictness

When choosing, changing, or defending thresholds, read `references/threshold-selection.md` completely and follow its calibration procedure. Never select thresholds from one aggregate metric or intuition.

Support a visible strictness control from `0` to `5`, where `0` means keep all eligible documents and `5` means keep none. Levels `1` through `4` must select named, prevalidated policy bundles rather than linearly tightening every metric. Define and log the exact mapping from strictness to heuristic rules, classifier threshold, percentile, or sampling probability.

Treat `user-baseline-v1` as a middle candidate to test, not the answer. Separate confirmed hard failures from soft quality evidence, preserve profile-aware exemptions, and sweep multiple complete policy candidates.

For every candidate setting, report:

- Corpus kept by documents and tokens.
- Average and distribution of survivor quality scores.
- Rejection precision, good-document false-rejection rate, and junk leakage.
- Per-language and per-profile retention.
- Domain and topic diversity.
- Heuristic/classifier disagreement.
- Human-review error rates.
- Estimated processing cost.
- Downstream evaluation results when available.

Do not assume that raising strictness always improves the final model. It raises average selected score while reducing volume and possibly diversity.

### Step 18 — Route each document

Use exactly one disposition:

- `ACCEPT_HIGH`
- `ACCEPT_STANDARD`
- `ACCEPT_SPECIAL_FORMAT`
- `DOWNSAMPLE`
- `REVIEW`
- `QUARANTINE`
- `EXCLUDE_HEURISTIC`
- `EXCLUDE_CLASSIFIER`
- `BLOCKED`

Attach stable reason codes and preserve all measured metrics.

### Step 19 — Produce corpus accounting

Report before and after each layer:

- Documents, characters, bytes, and tokens.
- Pass/fail counts by heuristic.
- Classifier score distribution.
- Retention and average quality.
- Language, script, source, domain, profile, and length distributions.
- Low-resource language survival.
- Special-format routing.
- Reasons for review, quarantine, and exclusion.

Use:

```text
corpus_kept = kept_tokens / eligible_input_tokens

average_quality_of_survivors =
    sum(classifier_score for kept documents) / kept_document_count
```

Also report token-weighted average quality when document lengths differ substantially.

### Step 20 — Validate, ablate, and monitor

- Manually review stratified accepted and rejected samples.
- Run threshold and complete-policy ablations using the procedure in `references/threshold-selection.md`.
- Reject dominated policies and retain the Pareto frontier.
- Train equal-token small proxy language models on viable candidate mixtures when feasible.
- Evaluate general capability, educational benchmarks, target-language performance, code, reasoning, and domain coverage.
- Select the least aggressive policy that maximizes downstream results while satisfying explicit false-rejection, junk-leakage, token-volume, language, and profile-retention constraints.
- Monitor source and score drift across crawl snapshots.
- Recalibrate rather than silently changing thresholds.
- Reconcile all input records to one final disposition.

## Required final report

End every run with:

1. Quality contract and selected profiles.
2. A stage table covering all 20 stages.
3. A table of all nine baseline metrics with formulas, exact values, thresholds, and statuses.
4. Pass/fail/exemption counts and reason codes.
5. SEO, residual markup, list, chat, OCR, and other failure-mode findings.
6. Teacher-label and classifier details, or an explicit statement that they were not run.
7. Threshold sweep, strictness mapping, Pareto frontier, constraints, and selected operating point.
8. Per-language, source, domain, profile, and length retention.
9. Accepted, downsampled, reviewed, quarantined, excluded, and blocked counts and tokens.
10. Bias, diversity, low-resource-language, and special-format risks.
11. Validation, ablation, and downstream evaluation results.
12. Links or paths to accepted data, special-format data, review samples, quarantine data, exclusions, and machine-readable logs when files exist.

Never describe a document as “good” or “bad” without showing which definition, metrics, profile, classifier, and threshold produced that decision.
