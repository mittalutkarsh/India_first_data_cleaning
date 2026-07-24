---
name: language-skill
description: Identify, validate, audit, and route languages in multilingual pretraining, SFT, evaluation, web, OCR, PDF, and parallel-translation corpora. Use when verifying claimed folder or dataset language labels, separating target from non-target languages, detecting Indic native-script or romanized text, handling shared scripts and code-mixed documents, validating translation-side languages, calibrating LID thresholds, quarantining uncertain data, measuring corpus composition, or producing a visible document/paragraph/span-level language decision log.
---

# Language Skill

Treat language identification as a corpus admission and accounting system, not as a single classifier call. Determine what language evidence is present, whether the detector supports it, whether it belongs in the target corpus, and why the document is accepted, routed, excluded, or quarantined.

## Core principles

1. Never trust a folder name, filename, URL, source label, or dataset description as ground truth.
2. Preserve claimed language metadata and compare it with detected evidence.
3. Run language ID after content extraction and normalization so boilerplate and encoding noise do not dominate.
4. Distinguish language, script, region, romanization, and content type.
5. Detect at document, paragraph, and span level; do not force every document into one language.
6. Allow the detector to abstain. Unknown data is not automatically non-target data.
7. Do not use a model's rejection when the model does not support the candidate language.
8. Treat code-mixed and translated data as explicit corpus categories, not accidental monolingual data.
9. Use per-language, script, length, and domain thresholds calibrated on gold data. Do not invent one universal confidence cutoff.
10. Retain excluded or quarantined raw data separately when policy permits; do not silently destroy it.
11. Version the model, label map, thresholds, target-language policy, and decision rules.
12. Log observable evidence and decisions without exposing private chain-of-thought.

## Correct transcript terminology

Interpret likely transcription errors as follows:

| Transcript wording | Intended term |
| --- | --- |
| Mongol or Mongols | Mongolian |
| Maui language | Māori |
| Asamis | Assamese |
| Udo | Urdu |
| Russia | Russian |
| Language ID at runtime | Language validation during corpus ingestion or processing |

Do not infer an exact dataset or source name from an unclear transcript.

## Why language ID controls the training recipe

Use language ID for all of these purposes:

- **Admission:** Keep intended languages and route non-target languages away from the active training mixture.
- **Tokenizer planning:** Avoid intentionally spending vocabulary capacity on languages and scripts outside the model's scope.
- **Token-budget accounting:** Measure how many characters, bytes, documents, and tokens belong to each language.
- **Mixture design:** Set and verify language sampling weights from detected data, not directory names.
- **Evaluation attribution:** Locate Hindi, Sanskrit, Urdu, French, Russian, and other evaluation data reliably.
- **Contamination control:** Detect English or unrelated content inside an Assamese or other language folder.
- **Parallel-data validation:** Confirm that both source and target languages exist and that translation sides were not omitted or swapped.
- **Resource control:** Avoid training compute on unidentified, unsupported, or unintended material.
- **Quality diagnosis:** Measure which sources create language mismatches, mixed content, or excessive abstentions.

Do not claim that a language is absent merely because the selected LID model cannot recognize it.

## Establish the language contract

Before classifying data, define:

- Target languages.
- Conditionally allowed languages, such as English inside code or technical terms.
- Non-target languages.
- Accepted scripts for each target language.
- Accepted native-script and romanized forms.
- Allowed code-mixed combinations.
- Whether translations, dictionaries, tables, code, and metadata are separate corpus buckets.
- Minimum usable linguistic content.
- The treatment of `unknown`, `multiple`, and `no linguistic content`.
- Review and quarantine rules.

Use standardized identifiers:

- Use BCP 47-compatible language tags for output when possible.
- Retain an ISO 639-3 language code for granular corpus accounting when available.
- Store script separately using ISO 15924-style codes.
- Use `und` for undetermined language.
- Use `mul` only when multiple languages are genuinely present and span labels are also retained.
- Use `zxx` for content with no linguistic language, such as symbol-only or numeric-only material.

Examples:

| Text class | Language | Script |
| --- | --- | --- |
| Hindi in Devanagari | `hi` | `Deva` |
| Romanized Hindi | `hi` | `Latn` |
| Urdu | `ur` | `Arab` |
| Assamese | `as` | `Beng` |
| Bengali | `bn` | `Beng` |
| Sanskrit in Devanagari | `sa` | `Deva` |

Do not infer language from script alone. Hindi, Marathi, Nepali, Sanskrit, and other languages can share Devanagari; Assamese and Bengali share the Bengali–Assamese script; Urdu shares Perso-Arabic script characteristics with other languages.

## Mandatory execution log

Create a run header and one log entry for every numbered stage. Report `NO CHANGE` or `NO ISSUE` when appropriate; never omit a stage silently.

### Run header

Report:

- Run identifier, if available.
- Dataset, source, and file identifiers.
- Corpus purpose: pretraining, SFT, evaluation, parallel data, or unknown.
- Claimed language metadata and its origin.
- Target-language policy version.
- LID model or ensemble names, versions, supported labels, and training-domain limitations when known.
- Threshold and calibration version.
- Normalization version.
- Input document, character, byte, and token counts when measurable.
- Assumptions and missing information.

Never fabricate confidence scores, language support, thresholds, counts, or model versions. Write `not available` or `not measured`.

### Per-stage log

Use:

```markdown
### Step NN — <stage name>

- Purpose:
- Evidence used:
- Status: PASS | NO ISSUE | WARNING | REVIEW | EXCLUDE | QUARANTINE | BLOCKED
- Claimed label:
- Predicted candidates and scores:
- Script evidence:
- Paragraph/span evidence:
- Threshold or rule applied:
- Decision:
- Reason code:
- Representative examples:
- Warnings:
```

Requirements:

- Show top candidates, not only the winning label, when scores are available.
- Show the top-1/top-2 margin when available.
- Show up to three bounded examples for each material decision.
- Mask sensitive content while retaining the linguistic feature.
- Show full span results for short documents; summarize large documents and link to the full result.
- Record disagreements between script, models, metadata, and span aggregation.
- Use concise evidence; do not provide hidden reasoning.

Maintain a machine-readable record when processing files:

```json
{
  "document_id": "doc-001",
  "claimed_language": "as",
  "claimed_label_source": "folder",
  "scripts": {"Beng": 0.91, "Latn": 0.09},
  "document_candidates": [
    {"language": "bn", "score": 0.61},
    {"language": "as", "score": 0.34}
  ],
  "span_distribution": {"bn": 0.72, "en": 0.18, "und": 0.10},
  "mixed_language": true,
  "model_supported_claimed_language": true,
  "decision": "QUARANTINE",
  "reason_codes": ["CLAIM_PREDICTION_MISMATCH", "MIXED_ABOVE_POLICY"],
  "model_version": "not available",
  "policy_version": "lid-policy-v1"
}
```

Scores and proportions must state their denominator and measurement basis: characters, words, spans, or model probability.

## Language identification workflow

### Step 01 — Preserve provenance and claimed labels

- Retain raw content and original metadata.
- Record every claimed label and where it came from: folder, filename, source manifest, HTML metadata, human annotation, or parallel-corpus schema.
- Keep contradictory claims rather than overwriting them.
- Treat all claims as hypotheses to validate.

Reason codes:

- `CLAIM_MISSING`
- `CLAIM_CONFLICT`
- `CLAIM_UNSUPPORTED_FORMAT`

### Step 02 — Normalize and extract content

- Run content extraction and normalization before LID.
- Use `$normalization-steps` when available for HTML unescape, NFC, controls, joiners, ghost tags, and structure-aware whitespace.
- Remove navigation, cookie banners, repetitive headers, and other boilerplate before classification.
- Preserve code, JSON, YAML, Markdown, Indic joiners, and paragraph boundaries.
- Keep both raw and normalized versions.

Do not run destructive language filtering on unnormalized OCR or mojibake without flagging the quality risk.

### Step 03 — Separate linguistic and non-linguistic spans

Identify:

- Natural-language prose.
- Code.
- URLs and email addresses.
- Numbers and punctuation.
- Named entities.
- Tables and metadata.
- Formulae.
- Repeated boilerplate.
- Empty or symbol-only content.

Run ordinary prose LID primarily on linguistic spans. Store code and metadata policies separately so English keywords in Python or URLs do not relabel the entire document.

Route content with no usable linguistic evidence to `zxx`, `und`, or `TOO_SHORT` according to the actual condition.

### Step 04 — Detect script distribution

- Measure scripts at document, paragraph, and span levels.
- Exclude or separately count punctuation, digits, emoji, inherited marks, and common characters when calculating script proportions.
- Compare observed scripts with scripts allowed for each candidate language.
- Use script as a high-precision routing signal, not a complete language classifier.
- Flag an impossible or unexpected language–script combination.

Reason codes:

- `SCRIPT_LANGUAGE_CONFLICT`
- `UNEXPECTED_SCRIPT`
- `MIXED_SCRIPT`
- `ROMANIZED_CANDIDATE`

### Step 05 — Run document-level LID

- Run the primary model on normalized linguistic content.
- Capture the supported label set before interpreting results.
- Store top-k candidates and scores.
- Record input length because confidence is length-dependent.
- Do not accept a top-1 label merely because one must be returned.
- Use a second independent model or adjudication path for high-impact disagreements, low-resource languages, and closely related language groups when available.

Record model training-domain limitations. A detector trained mainly on encyclopedic or formal text may behave differently on OCR, social media, code-mixed, or romanized text.

### Step 06 — Run paragraph- and span-level LID

- Segment by natural paragraphs and meaningful sentences.
- Use word- or subword-level labeling for code-switched text when supported.
- Avoid classifying extremely short fragments with unjustified certainty.
- Do not concatenate unrelated documents merely to make LID easier.
- Retain named-entity, borrowed-word, mixed, and unknown labels when the classifier supports them.

Aggregate results using an explicit basis such as linguistic characters or tokens. Do not use an unweighted majority of spans when one-line fragments and full paragraphs differ greatly in size.

### Step 07 — Resolve Indic and closely related language cases

Apply specialized handling for:

- Shared scripts.
- Closely related languages.
- Native-script versus romanized text.
- Inconsistent transliteration.
- Borrowed vocabulary.
- Named entities.
- Very short strings.

For romanized Indic text:

- Do not assume Latin script means English.
- Use a detector evaluated on romanized versions of the target languages.
- Check code-mixing with English.
- Keep native-script and romanized distributions separately.

For shared-script languages:

- Require lexical/model evidence beyond script.
- Inspect the confusion set and top-k margin.
- Route low-margin cases to review or quarantine.

### Step 08 — Detect code-mixed and multilingual documents

Classify a document as:

- Predominantly monolingual.
- Monolingual with incidental foreign material.
- Deliberately code-mixed.
- Parallel or translated.
- Boilerplate-mixed.
- Unresolved multilingual.

Store the full language distribution and span boundaries. A dominant label must not erase minority-language content.

Do not call useful code-mixed data “garbage.” The transcript's scheduling point is that mixed data should be admitted intentionally after the model and data recipe are ready for it, not accidentally mixed into monolingual buckets.

### Step 09 — Validate claimed folder and dataset labels

Compare claimed and detected evidence:

- Claimed and detected labels agree.
- Claimed language exists but is not dominant.
- Claimed language is absent.
- Claimed language is unsupported by the detector.
- Folder contains mostly another language.
- File is empty, untranslated, boilerplate-only, or non-linguistic.

Never silently rewrite the source label. Retain the claim, detected distribution, mismatch status, and decision.

Escalate high-volume source mismatches because they can contaminate an entire corpus partition.

### Step 10 — Validate parallel and translation data

For each source–target pair:

- Confirm both sides are present and non-empty.
- Detect each side independently.
- Confirm expected source and target languages.
- Detect swapped sides.
- Detect identical-language pairs when different languages are expected.
- Detect copied source text where the translation is missing.
- Detect English or boilerplate-only records in a target-language file.
- Keep LID validation separate from semantic translation-quality or alignment validation.

Reason codes:

- `TRANSLATION_SIDE_MISSING`
- `SOURCE_LANGUAGE_MISMATCH`
- `TARGET_LANGUAGE_MISMATCH`
- `TRANSLATION_SIDES_SWAPPED`
- `SAME_LANGUAGE_UNEXPECTED`
- `TRANSLATION_NOT_VERIFIED`

### Step 11 — Check target-language eligibility

Apply the declared language contract:

| Evidence | Default route |
| --- | --- |
| Supported target language with calibrated acceptance evidence | Accept into matching language bucket |
| Allowed target-target or target-English mixture | Route to approved code-mixed bucket |
| High-confidence non-target language | Exclude from active training mixture; retain separately when permitted |
| Claimed target but detected non-target | Quarantine and audit source |
| Unknown or insufficient evidence | Quarantine or `und`; do not force a label |
| Detector lacks the claimed language | Route to coverage-gap review |
| No linguistic content | Route to `zxx` or exclude under corpus policy |

Keep language admission separate from overall quality filtering. Correctly identified target-language text can still fail later quality checks.

### Step 12 — Apply calibrated confidence and abstention

Do not define one universal number such as `0.80` for every language.

Calibrate using held-out gold data by:

- Language.
- Confusion group.
- Script.
- Native versus romanized form.
- Text-length band.
- Source domain.
- Document versus span level.

Use, when available:

- Top-1 score.
- Top-1/top-2 margin.
- Model agreement.
- Script compatibility.
- Span consistency.
- Claimed-label agreement as weak supporting evidence only.

Abstain when evidence is insufficient. Record whether rejection came from low score, low margin, disagreement, unsupported labels, too little text, corruption, or mixed-language policy.

### Step 13 — Decide accept, review, exclude, or quarantine

Use exactly one final document disposition:

- `ACCEPT_MONOLINGUAL`
- `ACCEPT_CODE_MIXED`
- `ACCEPT_PARALLEL`
- `REVIEW`
- `EXCLUDE_NON_TARGET`
- `EXCLUDE_NON_LINGUISTIC`
- `QUARANTINE_UNKNOWN`
- `QUARANTINE_MISMATCH`
- `BLOCKED`

Attach one or more stable reason codes. Do not drop documents without a recorded disposition.

### Step 14 — Produce corpus accounting

Aggregate by:

- Source and source version.
- Claimed language.
- Detected language.
- Script.
- Native or romanized.
- Monolingual, mixed, parallel, unknown, or non-linguistic status.
- Decision and reason code.
- Document, character, byte, and token counts.
- Confidence and length bands.

Report both pre-filter and post-filter distributions. A document count alone can hide that a small number of very long files dominates the token budget.

Measure:

- Claimed/detected mismatch rate.
- Abstention and quarantine rate.
- Non-target token removal.
- Code-mixed share.
- Unknown share.
- Source-level contamination.
- Target-language retention.

Do not treat the transcript's statement that “a lot” may be discarded as a numeric target.

### Step 15 — Validate the LID system

Build a human-verified gold set stratified by:

- Language and confusion group.
- Source and domain.
- Text length.
- Script.
- Native and romanized text.
- Monolingual and code-mixed content.
- Clean and noisy/OCR text.
- Translation sides.
- In-domain and out-of-domain material.

Report:

- Per-language precision, recall, and F1.
- Macro F1 so high-resource languages do not hide low-resource failures.
- Confusion matrix.
- Target-language false rejection rate.
- Non-target false acceptance rate.
- Coverage after abstention.
- Accuracy or F1 among accepted items.
- Calibration quality when probabilities are used.
- Results by length, script, romanization, domain, and source.

Never evaluate only on labels inherited from the same noisy folders being audited.

### Step 16 — Sample for human review

Prioritize:

- Claimed/detected mismatches.
- Low top-1/top-2 margins.
- Model disagreement.
- Shared-script confusion groups.
- Romanized text.
- Code-mixed documents.
- Very short documents.
- Unexpected languages.
- High-volume sources.
- Low-resource target languages.
- Random accepted and rejected control samples.

Use review results to recalibrate thresholds and update source-specific rules. Do not silently change historical decisions; version and re-run them.

### Step 17 — Run reproducibility checks

- Re-run a stable sample and require identical results for deterministic components.
- Record intentional differences for nondeterministic services.
- Verify label-map consistency.
- Verify that every document has a disposition and reason code.
- Confirm corpus totals reconcile across accepted, reviewed, excluded, quarantined, and blocked buckets.
- Confirm no target language disappeared because of a model-support or label-mapping error.

## Required final report

End every run with:

1. A summary of the target-language contract.
2. A stage table covering all 17 stages.
3. Claimed versus detected language distributions.
4. Script and romanization distributions.
5. Document-, paragraph-, and span-level disagreement summaries.
6. Folder/source mismatch report.
7. Code-mixed and multilingual report.
8. Translation-pair validation report when applicable.
9. Accepted, reviewed, excluded, quarantined, and blocked counts and tokens.
10. Model coverage gaps.
11. Per-language confidence and threshold information.
12. Human-review sample plan.
13. Validation metrics or an explicit statement that gold evaluation was not run.
14. Links or paths to accepted data, quarantine data, exclusions, span annotations, and the machine-readable audit log when files exist.

Never report only a predicted language. Report whether that language belongs in the target corpus, how the decision was validated, and what happened to the document.
