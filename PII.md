---
name: pii-data
description: Detect, classify, minimize, redact, pseudonymize, quarantine, and audit personally identifiable information, personal data, sensitive attributes, quasi-identifiers, online identifiers, contact details, credentials, and secrets in multilingual pretraining, SFT, web, news, Reddit, social, email, support, chat, OCR, PDF, code, and evaluation corpora. Use when designing a PII scrubber, deciding whether to retain public names or attribution, tuning regex/NER/context thresholds, protecting usernames and GitHub metadata, measuring residual PII and over-redaction, handling regulated or private data, selecting typed placeholders, or producing a safe step-by-step decision log that never exposes raw identifiers.
---

# PII Data

## Objective

Minimize privacy and security risk while preserving legitimate educational, historical, attributional, linguistic, and structural value. Detect direct and indirect identifiers, decide from entity type plus context and source risk, transform only the necessary spans, re-scan independently, and log every decision without reproducing raw PII.

## Required references

- Read `references/policy-and-thresholds.md` completely whenever selecting, tuning, changing, or defending source tiers, detector thresholds, document-routing rules, placeholder policies, or release gates.
- Read `references/evidence.md` completely whenever explaining privacy definitions, regulatory examples, published corpus practices, or memorization risk.

## Non-negotiable principles

1. Treat raw PII as restricted data from ingestion onward.
2. Never write raw PII into logs, prompts, screenshots, error messages, examples, or ordinary reports.
3. Never send raw sensitive text to an external model, API, search engine, or telemetry system unless that processing is explicitly approved and governed.
4. Do not assume public availability, a news source, or frequent repetition makes personal data safe or useful.
5. Do not blanket-remove all person names. Distinguish private people, public-interest figures, historical figures, fictional characters, bylines, quotations, usernames, organizations, and locations.
6. Distinguish redaction, masking, pseudonymization, generalization, de-identification, and anonymization. Do not call pseudonymized data anonymous.
7. Treat health, financial, biometric, precise-location, children’s, sexual, political, religious, genetic, and government-identifier data as higher risk.
8. Treat credentials, API keys, access tokens, passwords, and private keys as critical secrets even when they are not legally defined as PII.
9. Preserve required license, copyright, and source attribution in controlled metadata even when removing it from training text.
10. Use language-, script-, region-, source-, and profile-specific detectors and thresholds.
11. Prefer reversible quarantine and typed replacements over destructive deletion.
12. Reconcile every input document and every detected span to one final disposition.

## Core distinctions

| Category | Examples | Primary risk | Default posture |
|---|---|---|---|
| Critical secret | Password, API key, private key, session token | Account/system compromise | Quarantine immediately; never emit value |
| Strong identifier | Government ID, passport, bank/account number, valid payment card, biometric template | Identity theft or unique linkage | Redact or exclude; one valid occurrence is sufficient |
| Direct contact | Personal email, phone, fax, street address, precise GPS, public IP | Contact, stalking, network exposure | Redact when validated |
| Online identifier | Username, Reddit handle, GitHub ID, device/cookie ID, UUID | Cross-site or behavioral linkage | Pseudonymize by source and purpose |
| Contextual identity | Person name, employer, school, title, byline | Identifiability depends on context | Apply private/public-interest decision |
| Quasi-identifier | Age, date, ZIP, rare occupation, small location | Re-identification in combination | Score combinations, not isolated fields only |
| Sensitive attribute | Health, race/ethnicity, religion, politics, sexuality, union membership | Discrimination or harm | Quarantine or governed use when linked to a person |
| Public attribution | Public official, historical figure, quoted speaker, relevant author | Knowledge and provenance value | Retain only when relevant and governed |
| Organization/location | Company, city, country, data center | Usually not a natural person | Do not remove merely because NER is uncertain |

## Source and context rule

Use source risk as evidence, not as an exemption:

- **Curated reference, official publication, or reputable news:** consider retaining relevant public-interest names and quotations; still redact personal contact details, precise addresses, credentials, victims/minors, and incidental private-person data.
- **Public forum, Reddit, social media, comments, or chat:** pseudonymize handles and ordinary-person names by default; aggressively redact contact and linkage data.
- **Email, support ticket, internal log, customer transcript, private repository, or leaked data:** quarantine first; require explicit authorization, purpose, and stronger scrubbing.
- **Health, finance, education, children, employment, or legal case data:** apply the applicable governed standard; do not infer compliance from generic masking.
- **Code repository:** scan code, comments, history, commit metadata, configuration, and notebooks for secrets and PII; preserve license/attribution obligations separately.

## Safe audit contract

### Run header

Record:

- Run ID, timestamp, operator, environment, and approved processing boundary.
- Corpus snapshot, source, license, collection basis, intended training purpose, and retention policy.
- Jurisdictions and governing policies identified by the data owner; write `not provided` when absent.
- Raw document and token counts without raw content samples.
- Languages, scripts, profiles, source-risk tiers, and vulnerable-population flags.
- Detector versions, entity taxonomy, recognizers, validators, NER models, calibration data, and thresholds.
- Replacement-token scheme, tokenizer version, and pseudonymization scope.
- Human-review and escalation policy.
- Output, quarantine, and restricted-raw locations.

### Per-stage log

For every stage, record:

1. Step number and purpose.
2. Input documents and tokens.
3. Source tier, language, profile, and governing policy.
4. Detector or rule version.
5. Entity types searched.
6. Thresholds and validators.
7. Counts by entity and action.
8. Status: `PASS`, `FAIL`, `WARNING`, `EXEMPT`, `REVIEW`, or `BLOCKED`.
9. Decision effect and reason codes.
10. Output documents and tokens.
11. Residual-scan findings.
12. Runtime and warnings when available.

### Safe span log

Record only:

- Random detection ID.
- Document ID or approved opaque ID.
- Entity type.
- Character offsets or token offsets when permitted.
- Detector, confidence, validator result, context/risk tier, and action.
- Typed masked preview such as `<EMAIL>` or `P••••N`.
- Review status and reason code.

Do not store the raw value or an unsalted ordinary hash of it. If stable linkage is required, use a scoped keyed pseudonym under approved key management and keep the mapping separate.

## Workflow

### Step 1 — Secure ingestion

- Restrict access to raw data before inspection.
- Encrypt and retain raw data only according to the declared policy.
- Assign stable opaque document IDs.
- Block the run if raw PII would enter uncontrolled logs, caches, analytics, or external services.

### Step 2 — Establish purpose and governance

- State the training purpose and why any personal data is necessary.
- Record legal/governance review status without inventing a lawful basis.
- Apply data minimization: retain only information necessary for the declared purpose.
- Route ambiguous regulated data to privacy, security, or legal review.

### Step 3 — Classify source and exposure risk

- Assign source tier, public/private status, conversationality, authorship type, and vulnerable-population risk.
- Treat scraped public text as personal data when a person remains identifiable.
- Do not infer that a website already removed private information.

### Step 4 — Prepare a protected detection view

- Preserve raw text separately.
- Normalize Unicode and whitespace without changing offsets irreversibly.
- Decode obfuscation forms such as `name [at] domain [dot] com`.
- Preserve scripts, diacritics, and Indic/Brahmic characters.
- Keep offset maps from detection view to raw and output views.

### Step 5 — Detect structured direct identifiers

- Use regex plus semantic validation, not regex alone.
- Validate email syntax, IP ranges, phone-region plausibility, payment-card checksum, government-ID structure, and date/address context.
- Distinguish examples, placeholders, reserved IPs, version numbers, order IDs, and random digit strings.
- Apply exact span boundaries and log the validator result.

### Step 6 — Detect credentials and secrets

- Scan code, prose, metadata, notebooks, configuration, URLs, and logs.
- Identify private keys, access tokens, API keys, passwords, connection strings, signed URLs, and session identifiers.
- Quarantine on one validated critical secret.
- Never place the matched value in a report.

### Step 7 — Detect names, usernames, and contextual entities

- Combine multilingual NER, dictionaries, metadata fields, pattern recognizers, and local context.
- Separate `PERSON`, `USERNAME`, `PUBLIC_FIGURE`, `FICTIONAL_PERSON`, `ORGANIZATION`, `LOCATION`, and `ROLE`.
- Do not equate high-frequency occurrence with public-figure status.
- Preserve byline or attribution requirements in metadata even if the training-text span is removed.

### Step 8 — Detect quasi-identifiers and linkage combinations

- Measure combinations such as exact age plus small location plus occupation plus date.
- Flag rare combinations and precise temporal or geographic trails.
- Generalize dates, ages, and locations when their exactness is unnecessary.
- Do not claim de-identification after removing names alone.

### Step 9 — Detect sensitive attributes and vulnerable contexts

- Detect health, disability, finance, education records, employment actions, religion, political views, sexuality, race/ethnicity, union membership, biometrics, genetics, criminal allegations, and children’s data when linked to an identifiable person.
- Route to high-risk review or exclusion even when direct identifiers are absent.
- Keep public-policy discussion that is not linked to a private person.

### Step 10 — Resolve public-interest and attribution cases

- Retain a public or historical person’s name only when central to the educational, historical, journalistic, or attributional value.
- Retain quotations only when the speaker relationship matters.
- Remove incidental personal contact details even for public figures.
- Apply stronger protection to private people, victims, witnesses, minors, and ordinary commenters.
- Use a versioned curated policy or allowlist; do not guess from fame.

### Step 11 — Consolidate overlapping detections

- Merge exact overlapping spans and preserve the highest-risk classification.
- Resolve nested entities, such as a name inside an email address.
- Prefer a validated structured identifier over a conflicting generic NER label.
- Send unresolved conflicts to review rather than deleting adjacent content.

### Step 12 — Assign risk and action

Use entity sensitivity, validation strength, source tier, public-interest relevance, repetition, vulnerable context, and linkage risk. Assign one span action:

- `KEEP_RELEVANT_PUBLIC`
- `KEEP_NON_PERSON`
- `MASK_TYPED`
- `PSEUDONYMIZE_LOCAL`
- `GENERALIZE`
- `REMOVE_SPAN`
- `REVIEW_SPAN`
- `QUARANTINE_DOCUMENT`
- `EXCLUDE_DOCUMENT`
- `BLOCKED`

### Step 13 — Transform safely

- Use typed placeholders such as `<EMAIL>`, `<PHONE>`, `<IP_ADDRESS>`, `<PERSON_1>`, and `<USERNAME_1>`.
- Preserve within-document or within-thread co-reference when useful.
- Do not create a corpus-global person pseudonym unless explicitly required and governed.
- Do not replace private names with realistic names that could implicate another person.
- Measure placeholder fertility with the actual tokenizer; add special tokens only when tokenizer/model design permits.

### Step 14 — Re-scan with an independent layer

- Re-run structured validators after transformation.
- Use a second detector family or human-reviewed sample to catch correlated misses.
- Scan outputs, metadata, filenames, URLs, logs, and manifests—not only the text field.
- Block release on any unresolved critical secret or governed high-risk identifier.

### Step 15 — Route documents

- Keep a document when safe transformations preserve its purpose.
- Quarantine or exclude when it is primarily a personal record, high-density directory, doxxing content, credential dump, private conversation, or cannot be scrubbed reliably.
- Do not reject a valuable document merely because it contains one safely replaceable email.
- Treat identifier count and PII-token fraction as supporting signals, not sole verdicts.

### Step 16 — Integrate with the corpus pipeline

- Run an early restricted PII/secrets scan before external processing or broad analyst access.
- Scrub before generating embeddings, publishing samples, or training.
- Coordinate with deduplication because repeated identifiers increase exposure and redaction changes fingerprints.
- Preserve both secure pre-redaction exact hashes and post-redaction deduplication fingerprints when governed.
- Keep PII detection distinct from language ID, quality, toxicity, factuality, and copyright checks.

### Step 17 — Account for privacy and utility

- Report entity counts, affected documents, actions, residuals, token removal, placeholder tokens, and document survival.
- Measure by language, script, source tier, profile, and entity class.
- Compare educational/structural utility before and after redaction.
- Never call removed tokens “wasted compute” without measuring whether useful context was also lost.

### Step 18 — Validate, calibrate, and monitor

- Follow `references/policy-and-thresholds.md`.
- Review stratified true positives, false positives, false negatives, boundary cases, public/private names, and quasi-identifier combinations.
- Run memorization and extraction-oriented evaluations when feasible.
- Monitor source drift, new identifier formats, detector drift, residual PII, and over-redaction.
- Recalibrate after changes to languages, sources, tokenizer, detectors, or policy.

## Initial operating policy

Use only as a starting candidate:

| Evidence | Initial action |
|---|---|
| One validated credential, private key, payment card, or high-risk government identifier | Quarantine, remove value, and escalate |
| Validated personal email, phone, precise address/GPS, or public IP | Typed masking |
| Username/handle in forum or conversational data | Thread-local pseudonymization |
| Private-person name in email, support, chat, Reddit, or similar source | Pseudonymize when confidence is high; otherwise review |
| Relevant public/historical figure in curated/news/reference context | Keep name; remove unrelated contact details |
| City, country, organization, ordinary role, or fictional character | Keep unless other evidence shows identifiability |
| Sensitive attribute linked to a private person | Quarantine or governed review |
| Six or more direct identifiers in one document | High-risk document review; published precedent, not universal rule |
| Residual critical identifier after scrubbing | Block release |

Do not make the entity-confidence score the risk score. Confidence estimates whether the detector label is correct; risk also depends on sensitivity, context, source, identifiability, and harm.

## Required metrics

Compute overall and by entity, language, script, source tier, profile, and action:

```text
precision = true_positive_spans / predicted_spans
recall = true_positive_spans / gold_spans
F_beta = (1 + beta^2) * precision * recall / ((beta^2 * precision) + recall)
residual_pii_per_million_tokens = missed_pii_spans * 1_000_000 / output_tokens
over_redaction_rate = non_pii_tokens_removed / useful_input_tokens
affected_document_rate = documents_with_pii / eligible_documents
quarantine_rate = quarantined_documents / eligible_documents
token_retention = output_training_tokens / eligible_input_tokens
placeholder_token_delta = output_placeholder_tokens - removed_pii_tokens
```

Use `F2` when recall is deliberately weighted more heavily. Also report entity-level exact and partial-span scores, critical residual count, false-positive examples using synthetic or masked text, pseudonym consistency, public-figure false removal, private-person leakage, quasi-identifier review findings, and log-leakage count. The required log-leakage count is zero.

## Required final report

End every run with:

1. Purpose, source tiers, governance status, and minimization contract.
2. Run-header configuration.
3. An 18-step status table.
4. Counts by entity, risk tier, source, language, and action.
5. Threshold sweep, validation set, precision, recall, F2, and selected policy.
6. Public-figure, private-person, username, organization, location, and ambiguous-name decisions.
7. Critical-secret and regulated-data findings without raw values.
8. Residual PII, false-removal, over-redaction, and token-impact results.
9. Documents kept, transformed, reviewed, quarantined, excluded, and blocked.
10. Independent re-scan and human-review results.
11. Known gaps, unsupported languages, drift risks, and unreviewed quasi-identifiers.
12. Paths to sanitized data, restricted quarantine, and safe machine-readable logs.

Never claim that a corpus is anonymous, compliant, or free of PII solely because automated detectors found no remaining spans.
