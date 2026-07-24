---
name: deduplication
description: Detect, audit, cluster, and route exact, lexical near, partial-span, boilerplate, semantic, and synthetic-lineage duplicates in multilingual pretraining, SFT, web, news, OCR, PDF, code, legal, and evaluation corpora. Use when selecting MinHash/LSH shingles, signatures, bands, similarity thresholds, exact hashes, containment rules, suffix-array or Bloom-filter methods, semantic embeddings, representative-retention policies, duplicate caps, train-evaluation decontamination, or producing a visible step-by-step deduplication log with pair, cluster, removal, retention, and diversity metrics.
---

# Deduplication

## Objective

Remove redundant exposure without erasing legitimate linguistic, factual, temporal, source, or format diversity. Distinguish exact copies, lexical near-copies, copied spans, boilerplate, semantic paraphrases, and articles about the same event. Log every transformation, comparison, threshold, cluster edge, retained representative, removed record, exemption, and unresolved case.

## Required references

- Read `references/threshold-calibration.md` completely whenever choosing, tuning, changing, or defending a threshold, shingle size, LSH configuration, semantic cutoff, or cluster cap.
- Read `references/evidence.md` completely whenever explaining research precedents or adopting a published configuration.

## Non-negotiable principles

1. Preserve raw text and provenance. Create a separate normalized fingerprint view.
2. Never equate “same topic” or “same fact” with duplicate text.
3. Never treat translations as duplicates by default.
4. Never use MinHash similarity as semantic correctness or factuality.
5. Use LSH for candidate generation. Recompute exact similarity for candidate pairs when feasible.
6. Calibrate thresholds on labeled pairs and cluster samples; no universal threshold exists.
7. Select retained representatives deliberately. Do not keep the first arbitrary crawler record.
8. Protect low-resource languages, scripts, romanized forms, code, lists, recipes, legal templates, OCR, and other special formats.
9. Prefer reversible routing and cluster manifests over destructive deletion.
10. Freeze validation and test sets before training-data decontamination.
11. Version normalization, tokenization, hashing, shingling, LSH, embedding, and retention policies.
12. Reconcile every input record to exactly one final disposition.

## Correct the common conceptual mix-up

Keep these objects distinct:

- **Overlapping model chunks:** long windows such as 512 tokens with a 50-token overlap, usually created for processing or training.
- **Shingles:** short contiguous units such as 5 normalized words, constructed at every eligible position in a document.
- **MinHash signature:** a fixed-length vector that approximates the Jaccard similarity of two shingle sets.
- **LSH bands:** groups of rows from the MinHash signature used to generate likely-match candidates quickly.

For shingle sets `A` and `B`:

```text
Jaccard(A,B) = |A intersection B| / |A union B|
P(one MinHash position agrees) = Jaccard(A,B)
P(LSH candidate at similarity s) = 1 - (1 - s^r)^b
```

Here `r` is rows per band and `b` is the number of bands. Banding changes candidate probability; it does not change the true Jaccard similarity.

## Duplicate classes and allowed actions

| Class | Definition | Primary evidence | Default action |
|---|---|---|---|
| Exact raw | Byte-identical input | Raw cryptographic hash | Keep one according to scope and retention policy |
| Exact normalized | Identical fingerprint view | Normalized cryptographic hash | Keep one representative; preserve raw variants in manifest |
| Lexical near-duplicate | Substantially overlapping shingle sets | Verified Jaccard after MinHash/LSH candidate generation | Cluster and retain representative(s) |
| Containment/partial copy | Most of a shorter document or span appears in a longer one | Containment and longest/common-span evidence | Remove copied record or repeated span; preserve meaningful novel remainder |
| Boilerplate duplicate | Navigation, cookie, footer, template, or syndication shell repeats | Line/paragraph frequency and DOM/profile evidence | Strip or mask boilerplate before document-level comparison |
| Semantic paraphrase | Similar meaning with different wording | Calibrated embeddings plus corroborating evidence | Review, downsample, or cap; do not hard-delete by lexical rules |
| Event/topic repetition | Independent articles cover the same event | Entities, time, topic, source, and semantic evidence | Preserve source diversity; cap only with validated event policy |
| Translation/transliteration | Same content across languages or scripts | Cross-lingual or transliteration-aware evidence | Preserve by default; route separately if the mixture requires |
| Synthetic lineage | Multiple generated variants share one seed | Seed ID, prompt, generator, lexical and semantic novelty | Enforce lineage-aware quality and novelty cap |
| Train-evaluation overlap | Training record overlaps frozen evaluation material | Exact, span, lexical, and optionally semantic evidence | Remove or quarantine the training-side record |

## Mandatory run header

Record:

- Run ID, timestamp, operator, code/config versions, and random seeds.
- Corpus snapshot, source, crawl date, license metadata, and input manifest.
- Raw document, byte, character, word, and token totals.
- Normalization and tokenizer versions used only for fingerprints.
- Language-ID and content-profile versions.
- Deduplication scope: within file, shard, source, crawl, snapshot, all snapshots, or global corpus.
- Exact-hash algorithm and fields included.
- Shingle unit, size, stride, case/punctuation/number treatment, and stopword policy.
- MinHash permutations, hash family/seed, bands, rows, and candidate probability curve.
- Verification metrics and thresholds.
- Boilerplate, substring, semantic, event, synthetic, and split-decontamination settings.
- Canonical representative ranking and cluster-cap policy.
- Output paths and checksums.

Never fabricate unavailable values. Write `not measured`, `not available`, or `not run`.

## Mandatory step log

For every step, show:

1. Step number and name.
2. Purpose.
3. Input documents and tokens.
4. Scope and profile.
5. Algorithm and version.
6. Exact parameters and formulas.
7. Observed values and candidate counts.
8. Threshold or rule.
9. Status: `PASS`, `FAIL`, `WARNING`, `EXEMPT`, `REVIEW`, or `BLOCKED`.
10. Decision effect and reason code.
11. Output documents and tokens.
12. Runtime, memory, and warnings when available.
13. Representative evidence without exposing restricted content.

Also create three linked machine-readable logs:

- **Pair log:** candidate pair, evidence, estimated and verified similarity, decision, and edge reason.
- **Cluster log:** cluster ID, members, edge provenance, representative ranking, kept members, removed members, and cap.
- **Document log:** input ID, hashes, language/profile, cluster, final disposition, representative ID, and reason codes.

## Workflow

### Step 1 — Preserve inputs and provenance

- Store immutable raw text, stable document IDs, source URLs or file IDs, crawl times, language metadata, license data, and checksums.
- Preserve ordering and source boundaries.
- Block destructive processing when IDs or raw-to-output reconciliation is impossible.

### Step 2 — Define the deduplication contract

- State why duplicates are being removed: compute efficiency, memorization reduction, diversity, source balancing, contamination control, or all of these.
- Define what must survive: languages, scripts, sources, dates, profiles, translations, rare facts, and synthetic variants.
- Declare acceptable false-removal, duplicate-leakage, token-retention, and per-group retention limits.

### Step 3 — Create a fingerprint-normalized view

- Apply deterministic Unicode, whitespace, case, punctuation, URL, number, and boilerplate rules only to the fingerprint copy.
- Do not overwrite training text.
- Avoid over-normalization that merges distinct numbers, code identifiers, formulas, names, or Indic/Brahmic characters.
- Log raw and fingerprint checksums plus every normalization rule.

### Step 4 — Assign language, script, source, and content profile

- Use these labels to select tokenization, shingling, comparison scope, thresholds, and protections.
- Compare within language/script first unless cross-lingual or transliteration-aware matching is explicitly enabled.
- Route code, legal, list, recipe, table, OCR, chat, and very short documents to profile-specific logic.

### Step 5 — Detect exact duplicates

- Compute a cryptographic hash such as SHA-256 on the raw text and fingerprint view.
- Group equal hashes, then verify equality before removal.
- Log raw-exact and normalized-exact clusters separately.
- Treat hash equality as an index key, not permission to discard provenance.

### Step 6 — Detect repeated lines, paragraphs, and spans

- Measure globally repeated lines and paragraphs after boilerplate-aware normalization.
- Use suffix arrays, suffix-based matching, or multiresolution Bloom filters when long repeated substrings matter.
- Do not remove common short phrases, recipe ingredients, legal clauses, code imports, or navigation fragments without profile-aware minimum lengths.
- Prefer removing repeated spans over dropping an otherwise valuable document.

### Step 7 — Isolate boilerplate

- Identify cookie notices, headers, footers, menus, author boxes, social links, newsletter prompts, and site templates.
- Compare main content separately from boilerplate.
- Log boilerplate fraction and whether it was masked, stripped, retained, or caused review.
- Do not let common boilerplate create a false document-level duplicate edge.

### Step 8 — Construct shingles

- Use contiguous word shingles for prose; start with 5-word shingles as a candidate configuration.
- Use language-appropriate segmentation for scripts without whitespace.
- Consider character shingles for OCR or unstable segmentation and token/AST-aware fingerprints for code.
- Deduplicate shingle sets for Jaccard unless multiset weighting is explicitly chosen and versioned.
- Record shingle count; do not trust approximate signatures for documents with too few shingles.

### Step 9 — Compute MinHash signatures

- Apply every configured hash permutation to every shingle and retain the minimum value per permutation.
- Use deterministic seeds and stable serialization.
- Treat signature agreement as an estimator of Jaccard, not as a content verdict.
- Log signature length, estimator error on labeled pairs, and failed/empty signatures.

### Step 10 — Generate LSH candidates

- Split each signature into `b` bands of `r` rows.
- Candidate two documents when at least one complete band matches.
- Calculate and log the candidate probability curve using `1 - (1 - s^r)^b`.
- Record bucket sizes and detect pathological hot buckets caused by boilerplate or empty features.

### Step 11 — Verify candidate pairs

- Recompute exact shingle Jaccard whenever feasible.
- Also compute containment:

```text
containment(A,B) = |A intersection B| / min(|A|, |B|)
```

- Add length ratio, shared-span length, title-only difference, boilerplate fraction, language/script agreement, and source/date evidence.
- Never auto-remove solely because one LSH band matched.

### Step 12 — Build deterministic clusters

- Create an undirected graph from verified duplicate edges and form connected components.
- Log direct versus transitive edges. A chain `A~B` and `B~C` does not prove `A~C`.
- Measure cluster diameter or representative-to-member similarity.
- Split or review low-purity bridge clusters instead of allowing one weak edge to collapse unrelated documents.

### Step 13 — Detect semantic and event-level redundancy

- Run only after exact and lexical deduplication.
- Use an embedding model validated for every target language and profile.
- Generate nearest-neighbor candidates, then corroborate with entities, dates, sources, lexical overlap, or synthetic lineage.
- Separate “same wording,” “same meaning,” and “same event.”
- Treat cosine thresholds as model-specific. Never reuse them across embedding models without recalibration.

### Step 14 — Rank representatives

Rank eligible cluster members using declared criteria:

- License and use eligibility.
- Extraction completeness and low corruption.
- Quality-filter score.
- Main-content proportion and low boilerplate.
- Trusted or original-source evidence.
- Language/script and source-diversity requirements.
- Timestamp policy.
- Metadata completeness.

Do not infer that the earliest crawl is the original author. Resolve ties deterministically and log every component score.

### Step 15 — Apply retention and cap policy

- Keep one representative for confirmed exact and high-confidence lexical-copy clusters unless diversity constraints require more.
- Preserve distinct languages and translations by default.
- For event or semantic clusters, prefer downsampling or a calibrated cap over hard deletion.
- For synthetic data, enforce per-seed caps and minimum novelty; “many ways of saying the same thing” is useful only when quality and learning value are demonstrated.
- Log cluster size before/after, cap, selected members, and rejected members.

### Step 16 — Decontaminate dataset splits

- Freeze evaluation and validation manifests first.
- Give evaluation/validation priority and remove overlapping training records.
- Check exact documents, long copied spans, lexical near-duplicates, and task-specific semantic leakage.
- Keep contamination metrics separate from ordinary corpus deduplication metrics.

### Step 17 — Route every document

Assign exactly one:

- `KEEP_CANONICAL`
- `KEEP_DIVERSE_VARIANT`
- `KEEP_TRANSLATION`
- `KEEP_SYNTHETIC_VARIANT`
- `DOWNSAMPLE_EVENT_CLUSTER`
- `STRIP_DUPLICATE_SPAN`
- `REVIEW_CLUSTER`
- `QUARANTINE`
- `EXCLUDE_EXACT`
- `EXCLUDE_NEAR`
- `EXCLUDE_TRAIN_EVAL_OVERLAP`
- `BLOCKED`

Attach stable reason codes and representative or cluster IDs.

### Step 18 — Account, validate, and monitor

- Reconcile all records and tokens before and after every layer.
- Review stratified positive pairs, negative pairs, boundary pairs, bridge clusters, and retained/removed members.
- Calibrate using `references/threshold-calibration.md`.
- Train equal-token proxy models on viable policies when feasible.
- Monitor duplicate leakage, false removal, cluster drift, source bursts, and language/profile survival on new snapshots.

## Initial threshold profile

Use only as a starting candidate, never as a universal answer:

| Layer | Initial candidate | Action |
|---|---|---|
| Exact raw/normalized | Verified equality | Cluster; retain canonical member |
| MinHash features | 5-word shingles, 112 permutations, 14 bands × 8 rows | Candidate generation |
| Verified lexical Jaccard | `>=0.85` | High-confidence near-copy candidate |
| Verified lexical Jaccard | `>=0.80` and `<0.85` | Near-copy candidate; apply profile and containment checks |
| Verified lexical Jaccard | `>=0.70` and `<0.80` | Review/candidate region; do not hard-delete from MinHash alone |
| Verified lexical Jaccard | `<0.70` | Keep unless containment, repeated-span, or semantic evidence applies |
| Containment | Sweep `0.80`, `0.90`, `0.95` | Remove copied record/span only after novel-content check |
| Semantic cosine | Sweep `0.90`, `0.93`, `0.95`, `0.97` per model | Candidate/review only until calibrated |
| Event/synthetic cap | Sweep `1`, `2`, `4`, `8`, `16` representatives | Select by downstream utility and diversity constraints |

Treat `0.67` or `0.70` as a broad discovery boundary, not an automatic deletion rule. DCLM selected `0.8` after ablation, while FineWeb's LSH setup probabilistically targeted high recall around `0.75`; neither makes one number correct for every corpus.

## Required metrics

Compute overall and by language, script, source, domain, profile, length, crawl, and license:

```text
exact_duplicate_rate = exact_duplicate_documents / eligible_documents
near_duplicate_rate = verified_near_duplicate_documents / eligible_documents
pair_precision = correctly_predicted_duplicate_pairs / predicted_duplicate_pairs
pair_recall = correctly_predicted_duplicate_pairs / labeled_duplicate_pairs
false_removal_rate = unique_documents_removed / labeled_unique_documents
duplicate_leakage = duplicate_documents_retained / labeled_duplicate_documents
token_removal_rate = removed_tokens / eligible_input_tokens
document_removal_rate = removed_documents / eligible_input_documents
cluster_purity = valid_duplicate_edges_or_members / reviewed_cluster_edges_or_members
evaluation_leakage = contaminated_eval_items / evaluated_eval_items
```

Also report LSH candidate recall, MinHash estimation error, singleton rate, cluster count and size percentiles, largest clusters, representative-source distribution, removed/kept quality distributions, retained translations, retained synthetic variants, and runtime/storage cost.

## Required final report

End every run with:

1. Deduplication contract and scope.
2. Run-header configuration.
3. An 18-step status table.
4. Exact, lexical, containment, boilerplate, semantic, event, synthetic, and split-overlap findings.
5. Threshold sweep, labeled-pair metrics, constraints, and selected operating point.
6. Pair, cluster, and document decision-log summaries.
7. Cluster-size and source-burst statistics.
8. Representative-selection policy and examples.
9. Documents and tokens kept, downsampled, stripped, reviewed, quarantined, and excluded.
10. Per-language, script, source, profile, length, and license retention.
11. False-removal, duplicate-leakage, cluster-purity, and contamination results.
12. Proxy/downstream evaluation results or `not run`.
13. Known risks, blocked stages, and paths to machine-readable manifests.

Never say that two documents are duplicates without naming the duplicate class, fingerprint view, metric, exact value, threshold, scope, and resulting cluster/retention decision.
