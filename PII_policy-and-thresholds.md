# PII Policy and Threshold Calibration

Use this procedure to choose detector confidence thresholds, source policies, document-density rules, replacement schemes, and release gates.

## Contents

1. Define the privacy contract
2. Build validation data
3. Calibrate by entity class
4. Calibrate context decisions
5. Select document-routing rules
6. Validate transformations
7. Select the operating point
8. Log the decision

## 1. Define the privacy contract

Record:

- Intended training purpose and why identity is or is not necessary.
- Approved sources, jurisdictions, licenses, retention periods, and processing boundary.
- Must-remove entity classes.
- Permitted public-interest attribution.
- Maximum residual, false-removal, and utility-loss limits.
- Required per-language and per-source performance floors.
- Human-review capacity and blocked-release conditions.

These are organizational and legal decisions, not facts to infer from the corpus.

## 2. Build validation data

Use real governed samples plus synthetic examples across:

- Every target language, script, dialect, romanized form, and code-mixed pattern.
- News, encyclopedic text, Reddit, social comments, email, support, logs, OCR, PDF, tables, and code.
- Public figures, private people, fictional names, organizations, locations, products, roles, and ambiguous words.
- Obfuscated emails, local phone formats, IPv4/IPv6, IDs, credentials, dates, addresses, and usernames.
- Sensitive and quasi-identifying combinations.
- Boundary examples immediately above and below each detector threshold.

Double-label a meaningful subset. Record span boundaries, entity class, public/private relevance, source tier, action, and adjudication.

## 3. Calibrate by entity class

Sweep confidence thresholds such as `0.50`, `0.70`, `0.80`, `0.90`, `0.95`, and `0.99`. Do not assume scores are calibrated across models or entity types.

Use these provisional release objectives only as candidates:

| Class | Candidate objective |
|---|---|
| Critical secrets and strong identifiers | Target recall `>=99.9%`; no observed critical residual in release validation |
| Direct contact identifiers | Target recall `>=99.5%` and precision `>=98%` |
| Usernames and contextual person names | Optimize risk-weighted F2 plus public/private decision accuracy |
| Organizations and locations | Prioritize precision to prevent destructive over-redaction |
| Quasi-identifiers | Evaluate combination-level re-identification risk, not isolated span recall |

The percentages are engineering starting points, not legal safe harbors or proof of zero risk. Report confidence intervals and sample counts. If the validation set is too small to support a target, say so.

## 4. Calibrate context decisions

Test complete context policies:

- `STRUCTURED_ONLY`
- `PRIVATE_SOURCE_AGGRESSIVE`
- `PUBLIC_ATTRIBUTION_PRESERVING`
- `MULTILINGUAL_BALANCED`
- `HIGH_RISK_QUARANTINE`

For names, begin with:

```text
private/conversational source + confidence >= 0.95 -> pseudonymize
private/conversational source + confidence 0.80–0.95 -> review
public-interest relevant + governed source -> retain name
unknown person status or vulnerable context -> review/quarantine
organization/location conflict -> keep unless corroborated as a person
```

Measure the policy, not only NER accuracy.

## 5. Select document-routing rules

Sweep:

| Signal | Candidate values |
|---|---|
| Direct identifier count | `1`, `3`, `6`, `10` |
| PII-token fraction | `0.01`, `0.05`, `0.10`, `0.25` |
| Sensitive-attribute count | `1`, `2`, `5` |
| Residual after first pass | `0`, `1`, `3` |
| Human-review sampling | `1%`, `5%`, `10%`, risk-stratified |

Use one validated critical secret as a quarantine trigger. For safely replaceable direct identifiers, prefer span masking to document deletion. Treat six identifiers as a published Dolma-style review/removal candidate, not a universal threshold.

## 6. Validate transformations

Check:

- No raw identifier appears in output, logs, metadata, filenames, or manifests.
- Typed placeholders preserve grammar and within-document co-reference.
- Pseudonyms cannot be linked across scopes unintentionally.
- Replacement tokens do not explode tokenizer fertility.
- Redaction does not merge words, corrupt Unicode, break code syntax, or erase required attribution.
- An independent detector and human sample find acceptable residuals.

## 7. Select the operating point

For every complete policy, report:

- Entity and span precision, recall, F1, and F2.
- Critical residual count and residual PII per million tokens.
- False removal of public figures, organizations, locations, and fictional names.
- Private-person and username leakage.
- Token and document retention.
- Utility, syntax, and co-reference preservation.
- Per-language/source performance.
- Runtime, review load, and quarantine volume.

Discard policies that violate approved constraints. From the viable set, select the least destructive policy that meets privacy requirements. Never trade a critical residual for a small token-efficiency gain.

## 8. Log the decision

Record every candidate threshold, validator, source policy, measured error, failed constraint, exception, selected bundle, confidence interval, and blocked stage. Recalibrate after any material change in source mix, languages, entity taxonomy, recognizer, tokenizer, or governing policy.
