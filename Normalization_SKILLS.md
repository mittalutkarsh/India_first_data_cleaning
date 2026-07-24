---
name: normalization-steps
description: Normalize multilingual pretraining, SFT, web, PDF-extracted, and mixed-format text while preserving Indic/Brahmic joiners and meaningful code or document structure. Use when cleaning or auditing corpus text, standardizing Unicode and whitespace, decoding HTML entities, removing controls or ghost special tokens, investigating normalization damage, or producing a visible step-by-step normalization log with before/after evidence and validation results.
---

# Normalization Steps

Normalize text conservatively and make every observable transformation auditable. Never apply one global whitespace or control-character regex to mixed prose, code, JSON, YAML, Markdown, or multilingual text.

## Non-negotiable behavior

1. Preserve the raw input unchanged. Write normalized text to a separate value or file.
2. Classify the document and meaningful spans before destructive cleanup.
3. Run every numbered stage in order. Log `NO CHANGE` when a stage makes no change; never omit a stage silently.
4. Protect U+200C ZERO WIDTH NON-JOINER and U+200D ZERO WIDTH JOINER before general format-character filtering.
5. Preserve meaningful structure in code, JSON, YAML, Markdown, tables, and dialogue.
6. Treat U+FFFD as evidence of corruption, not ordinary removable whitespace.
7. Use source-specific exact patterns for ghost tags. Never delete substrings such as `user` or `assistant` globally.
8. Run language identification after content extraction and normalization. Treat folder names as weak metadata.
9. Make the normalizer idempotent: `normalize(normalize(text)) == normalize(text)`.
10. Report observable evidence and concise policy rationales. Do not expose private chain-of-thought.

## Establish the run configuration

Determine or infer the following before changing text:

- Corpus purpose: `pretraining`, `SFT`, `evaluation`, or `unknown`.
- Source type: HTML, PDF, DOCX, plain text, Markdown, code, JSON, YAML, or mixed.
- Claimed language or languages, if available.
- Target language policy, especially whether languages using meaningful U+200B are included.
- Ghost-tag mapping, if the source has dialogue or instruction wrappers.
- Output format and location.

If information is missing, choose the most conservative reversible behavior and record the assumption. Ask the user only when an unresolved choice would materially alter meaning or structure.

Classify spans using these profiles:

| Profile | Whitespace policy | Structural policy |
| --- | --- | --- |
| Prose | Collapse redundant horizontal whitespace; repair clear layout wraps; preserve paragraphs | Preserve headings, lists, tables, and paragraph boundaries |
| Code | Normalize line endings only by default | Preserve indentation, tabs when meaningful, blank lines, comments, and strings |
| JSON | Parse and validate before reformatting | Never modify string values; serialize only after successful parsing |
| YAML | Preserve line structure and indentation | Do not globally collapse whitespace |
| Markdown | Preserve headings, lists, blockquotes, fences, tables, and meaningful blank lines | Do not treat Markdown syntax as noise |
| Mixed | Apply the appropriate policy per span | Default uncertain spans to preservation |

## Mandatory execution log

Create a run header and one log entry for every stage. Use the exact stage names in this skill.

### Run header

Report:

- Run identifier, if available.
- Source name and type.
- Corpus purpose.
- Claimed and detected languages.
- Selected profiles.
- Normalization policy version.
- Input and output locations, when files are used.
- Input size in characters and bytes when measurable.
- Assumptions and unresolved risks.

Never fabricate a hash, byte count, encoding, language, or timestamp. Write `not available` or `not measured` when necessary.

### Per-stage entry

For every stage, report:

```markdown
### Step NN — <stage name>

- Purpose:
- Rule applied:
- Status: CHANGED | NO CHANGE | SKIPPED | WARNING | BLOCKED
- Characters before:
- Characters after:
- Net character change:
- Items found:
- Items changed:
- Items preserved intentionally:
- Before → after examples:
- Validation performed:
- Warnings or decisions:
```

Requirements:

- Show up to three representative before/after examples.
- Escape invisible characters by name and code point, for example `\u200B [U+200B ZERO WIDTH SPACE]`.
- Include counts by character or marker type when measurable.
- Mask sensitive text in examples while leaving the transformed feature visible.
- For input up to 2,000 characters, show the complete stage output after each changed stage.
- For larger input, show bounded excerpts, counts, and the location of the full normalized output or full log.
- Explain why a stage is `SKIPPED` or `BLOCKED`.
- Record protected characters even when they remain unchanged.

Maintain a machine-readable event list when the user requests implementation output or when processing files:

```json
{
  "step": 7,
  "stage": "Preserve Indic joiners",
  "status": "NO CHANGE",
  "characters_before": 12500,
  "characters_after": 12500,
  "found": {"U+200C": 7, "U+200D": 11},
  "changed": {},
  "preserved": {"U+200C": 7, "U+200D": 11},
  "examples": [],
  "warnings": []
}
```

Use empty objects or arrays rather than inventing values.

## Normalization workflow

### Step 01 — Preserve raw input and provenance

- Keep the original bytes or original text unchanged.
- Record the source identifier, extraction method, declared encoding, claimed language, and original location when available.
- Write normalized content separately.
- Record input size and a checksum only when a tool can compute them.

Log whether provenance is complete and whether the original can be recovered.

### Step 02 — Decode source bytes

- Use the declared encoding when reliable; otherwise detect or recover the encoding with evidence.
- Prefer strict decoding.
- Never use `errors="ignore"`.
- If decoding fails, attempt a justified recovery from the original bytes.
- Quarantine materially unrecoverable input instead of pretending it is clean.
- Preserve emoji and valid non-ASCII characters.

Log the selected encoding, decoding errors, recovery attempts, and unresolved corruption.

### Step 03 — Extract useful content

- Use a parser appropriate to HTML, PDF, DOCX, or the source format.
- Remove known navigation, cookie banners, advertisements, repetitive headers or footers, and page furniture.
- Preserve paragraphs, headings, lists, tables, code blocks, quotations, and meaningful dialogue.
- Label spans by profile before later whitespace processing.
- Do not use regex as the primary raw-HTML parser.

Log each removed boilerplate category and representative bounded examples.

### Step 04 — Decode HTML entities once

- Decode named and numeric HTML references once.
- Examples: `&amp;` → `&`, `&iquest;` → `¿`, `&oelig;` → `œ`, and `&#8217;` → `’`.
- Do not repeatedly unescape values such as `&amp;lt;` without source-specific justification.
- Keep the resulting literal characters.

Run this before control filtering because an entity may decode into U+200B, U+FEFF, U+FFFD, or another character handled later.

### Step 05 — Apply Unicode NFC

- Apply `unicodedata.normalize("NFC", text)` or an equivalent Unicode-conformant operation.
- Use NFC, not NFKC, unless a separate compatibility-normalization policy is explicitly approved.
- Do not transliterate, lowercase, strip accents, repair mojibake, or normalize punctuation as part of NFC.

Log whether normalization changed the text and show code-point sequences for representative changes.

### Step 06 — Normalize line endings

- Convert CRLF and standalone CR to LF.
- Preserve LF until span-aware whitespace processing.
- Never remove all newlines before prose, code, and structured spans are separated.

Log CRLF, CR, and LF counts before and after.

### Step 07 — Preserve Indic joiners

Protect these characters before any general removal of Unicode format characters:

| Character | Code point | Required action |
| --- | --- | --- |
| ZERO WIDTH NON-JOINER | U+200C | Always preserve |
| ZERO WIDTH JOINER | U+200D | Always preserve |

- Do not replace them with spaces.
- Do not collapse across them.
- Do not delete them merely because language detection is uncertain.
- Flag suspicious placement if needed, but preserve the original sequence.

Log the count and context of each preserved joiner. Include code-point-level regression checks for Indic/Brahmic sequences.

### Step 08 — Handle ZERO WIDTH SPACE

Treat U+200B separately from U+200C and U+200D.

- For sources where U+200B is verified extraction noise, remove it and join adjacent characters.
- For broad multilingual corpora, use a language-aware rule.
- Preserve it for languages or source conventions where it represents a meaningful break opportunity unless evaluation approves removal.
- Do not replace it with a visible space by default.

Log the policy basis, counts, languages affected, and before/after examples.

### Step 09 — Filter C0 and C1 controls

Use these default rules:

| Character or range | Prose policy | Code/structured policy |
| --- | --- | --- |
| U+0000 NUL | Remove and flag | Remove and flag |
| U+0009 TAB | Convert to space | Preserve when meaningful |
| U+000A LF | Preserve for Step 13 | Preserve |
| U+000D CR | Already converted in Step 06 | Already converted |
| Other U+0000–U+001F | Remove and count | Remove unless format requires it |
| U+007F | Remove and count | Remove and count |
| U+0080–U+009F | Remove and count | Remove unless explicitly required |

Do not delete every Unicode `Cc` character without the newline and tab exceptions.

### Step 10 — Remove BOM contamination

- Remove a leading U+FEFF when it is an actual byte order mark.
- Remove and log U+FEFF introduced at known concatenation boundaries.
- Flag an interior U+FEFF as suspicious before applying a documented removal rule.
- Do not confuse U+FEFF with U+2060 WORD JOINER.
- Produce UTF-8 output without a BOM unless the output protocol requires one.

Log leading and interior occurrences separately.

### Step 11 — Handle bidirectional controls

For ordinary logical-order training text:

- Inspect and normally remove U+202A–U+202E explicit embeddings, overrides, and termination controls.
- Inspect and normally remove U+2066–U+2069 directional isolates.
- Do not reverse the underlying text.
- Preserve ordinary Arabic, Urdu, Hebrew, and other right-to-left letters.
- Treat U+200E, U+200F, and U+061C conservatively; preserve them initially for legitimate RTL or mixed-direction text unless a language-aware policy approves removal.

Log every code point by type and note the RTL-language preservation decision.

### Step 12 — Handle U+FFFD corruption

- Count every U+FFFD REPLACEMENT CHARACTER.
- Attempt recovery from original bytes or source material.
- If recovery succeeds, record the recovered character.
- If corruption is material and recovery fails, quarantine the document.
- Remove or replace U+FFFD only under a documented source-specific rule.
- Never silently delete it in a way that may concatenate unrelated text.

Log recovery evidence, unresolved positions, quarantine decisions, and any boundary-preserving replacement.

### Step 13 — Normalize whitespace by profile

For prose:

- Convert tabs to spaces.
- Normalize applicable non-breaking spaces to ordinary spaces when the non-breaking behavior is not meaningful.
- Collapse repeated horizontal whitespace.
- Join clear PDF layout wraps with one space.
- Preserve paragraph boundaries.
- Collapse excessive paragraph breaks to two LF characters.
- Trim whitespace at paragraph boundaries.
- Remove end-of-line hyphenation only when extraction evidence or contextual validation shows that the hyphen is artificial.

For code, JSON, YAML, Markdown, tables, and mixed spans, follow the profile table. Never apply global `\s+ → " "` to the complete document.

Log changes separately by profile and validate structured spans after the change.

### Step 14 — Remove or canonicalize ghost tags

First build a source-specific registry of exact role, instruction, response, end-of-turn, and end-of-text markers. Examples may include `[USER]` and `<|endoftext|>`, but do not assume this is the complete registry.

For pretraining:

- Remove artificial wrappers while preserving their linguistic content.
- Do not introduce SFT-only role tokens into ordinary prose.

For SFT:

- Map all source role markers to one approved system/user/assistant schema.
- Use one approved end-of-turn convention.
- Keep the dialogue boundaries needed by the target template.

Never:

- Delete `user`, `assistant`, or similar words as ordinary substrings.
- Modify marker examples inside protected code blocks, quotations, or discussions about tokens.
- Invent an unknown source mapping.

Log matches and actions by exact marker and distinguish removal from canonicalization.

### Step 15 — Assemble normalized output

- Reassemble spans in their original semantic order.
- Preserve required separators between headings, paragraphs, table cells, code blocks, and dialogue turns.
- Encode final text as UTF-8 without BOM unless another output contract is specified.
- Keep normalized content separate from the raw source.

Log output size, span count, and assembly warnings.

### Step 16 — Validate structure and meaning

Run applicable validations:

- Confirm U+200C and U+200D counts and sequences were preserved.
- Parse JSON again.
- Parse or lint YAML when a safe validator is available.
- Compile or parse code only when safe and appropriate.
- Confirm Markdown fences and table delimiters remain balanced.
- Check paragraph and heading retention.
- Verify that removals did not concatenate unrelated words.
- Compare representative before/after multilingual samples.
- Confirm no unintended transliteration, lowercasing, or accent stripping occurred.

Log each validation as `PASS`, `FAIL`, or `NOT RUN` with an explanation.

### Step 17 — Check idempotence

Run the complete normalizer on its own output and compare results.

- Require exact equality.
- If the second pass changes text, report the first differing positions and the responsible stage.
- Do not declare completion until idempotence passes or the failure is explicitly reported.

### Step 18 — Run language identification and quality review

- Run language identification on normalized content, preferably by paragraph or span for mixed documents.
- Compare detected languages with claimed language and source-folder metadata.
- Treat folder names as weak evidence.
- Flag major mismatches, mixed-language proportions, and boilerplate-dominated documents.
- Review the total removal ratio and per-stage change counts.
- Do not assume a target removal percentage such as 4%; establish corpus-specific baselines.

Log detected languages, confidence when available, mismatches, and the final disposition: `ACCEPT`, `ACCEPT WITH WARNINGS`, or `QUARANTINE`.

## Final report

End every run with:

1. A stage summary table containing all 18 stages and their statuses.
2. Total characters and bytes before and after when measurable.
3. Counts of HTML entities, NFC changes, controls, U+200B, preserved U+200C/U+200D, BOM, bidi controls, U+FFFD, whitespace changes, and ghost tags.
4. Structural validation results.
5. Idempotence result.
6. Language-identification result.
7. Final disposition and unresolved risks.
8. Links or paths to the raw input, normalized output, and machine-readable log when files exist.

Never report only “normalization completed.” Show what happened at every stage, including stages that changed nothing.
