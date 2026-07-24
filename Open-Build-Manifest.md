---
name: build-manifest
description: Create, validate, compare, sign, gate, and audit immutable provenance manifests for corpus shards and datasets. Use when recording where training data came from, its license and access basis, contributors and processing agents, every applied cleaning script and configuration hash, content and manifest SHA-256 digests, token and language statistics, upstream normalization/LID/quality/dedup/PII/decontamination results, deterministic reruns, shard admission or blocking, corpus indexes, version lineage, revocation, or a visible step-by-step manifest log.
---

# Build Manifest

## Purpose

Build a system-of-record for a shard, not another text filter. A manifest records the
evidence and decisions produced by collection and cleaning stages, makes outputs
reproducible and comparable, and gates whether an immutable shard version may enter a
training corpus.

Use one manifest per immutable output-shard version. Build a corpus index that references
all admitted shard manifests. Never replace the shard-level records with one global
manifest.

## Non-negotiable distinctions

Keep these identities separate:

| Identity | Meaning | Determinism rule |
|---|---|---|
| `content_sha256` / `shard_id` | Exact emitted shard bytes | Same bytes produce the same digest |
| `logical_content_sha256` | Optional versioned canonical record view | Use only when its serialization specification is named |
| `recipe_sha256` | Deterministic processing recipe | Same ordered code, configuration, dependencies, and policies produce the same digest |
| `run_id` | One execution attempt | May be a UUID; never use it as content identity |
| `integrity.manifest_digest` | SHA-256 of canonical immutable manifest core | Any semantic lineage or decision change produces a new digest; volatile envelope fields do not |

A SHA-256 value detects a byte change only when compared with a trusted expected value.
It does not prove who produced the shard. Use a verified signed attestation when
authenticity is required.

Same bytes obtained from two sources have the same content digest but different lineage
manifests. A deterministic rerun must reproduce the content and recipe digests. Its run
timestamps, run identity, storage location, and display labels may differ without
changing the immutable manifest-core digest when all semantic lineage and decisions are
unchanged.

## Required operating rules

1. Preserve raw, extracted, normalized, filtered, and sharded outputs as distinct
   entities with distinct digests.
2. Snapshot mutable sources. A URL without a crawl/snapshot identifier and source digest
   is insufficient provenance.
3. Record every applied transformation in order. If ten of forty scripts ran, record ten
   entries. Absence means not applied.
4. Record a human-readable script name and immutable code identity. Also identify
   configuration, dependencies/container, models, policies, tokenizer, and parameters
   that can change the result.
5. Record observed license evidence separately from the organization's training-use
   decision. Public availability is not permission. A manifest records evidence and a
   policy decision; it does not itself determine legality.
6. Treat privacy clearance separately from copyright or license clearance.
7. Derive admission status from explicit gate checks. Do not accept a caller-supplied
   `"status": "clean"` without evidence.
8. Fail closed on missing, contradictory, unverifiable, or unsafe required evidence.
9. Keep admitted manifest cores immutable. Put later lifecycle changes in a separately
   signed append-only event ledger, or issue a new manifest version that references its
   immutable predecessor. Never silently edit an admitted record.
10. Never place raw shard text, PII, credentials, secrets, private URLs, signing keys, or
    unrestricted samples in the manifest or its logs.

## Inputs

Request or locate:

- exact output shard and media/serialization/compression format;
- source snapshots and locators such as dataset version, crawl ID, WARC URI and offset,
  repository commit, object version, or acquisition record;
- publisher, rights holder when known, collector, contributor, processing service, and
  reviewer identities as opaque IDs;
- license/terms evidence and the applicable organizational policy;
- ordered processing run records, code/configuration/model/dependency digests, and logs;
- counts and upstream results from normalization, language ID, quality filtering,
  deduplication, PII handling, and decontamination;
- tokenizer artifact and configuration for token counts;
- determinism policy, admission policy, signature requirements, and corpus target.

Do not fabricate missing evidence. Before the required fields exist, emit an incomplete
intake record and gate report, not a falsely valid shard manifest. Use
`evidence_state: UNKNOWN|UNVERIFIED|VERIFIED` and route it according to policy.

## Mandatory workflow

Showcase every step in the visible step log described below.

### 1. Define the contract

Name the manifest schema version, policy version, shard format, intended use, required
stages, and gate semantics. Use the field contract in
[references/schema.md](references/schema.md).

### 2. Freeze source evidence

Identify each source snapshot, retrieval time, immutable locator, exact source digest,
and extraction range. Hash raw HTML/PDF/WARC and extracted main content separately.

### 3. Identify provenance roles

Distinguish publisher/rights holder, source host, collector, contributor, processing
operator, software/service agent, reviewer, and signer. Do not collapse them into one
ambiguous `contributor`.

### 4. Resolve rights, access, and privacy basis

Record the observed license expression, terms snapshot, evidence digest, access class,
allowed uses, prohibitions, duties, reviewer, and policy decision. Prefer SPDX
expressions; use `LicenseRef-*` plus immutable evidence for custom terms. Unknown,
conflicting, private, or restricted material cannot be admitted without explicit review.

### 5. Establish raw-artifact identity

Compute SHA-256 over exact input bytes. Record algorithm, full 64-character lowercase
digest, size, media type, serialization, and compression. Short hash prefixes are display
labels only.

### 6. Inventory transformations

Create a strictly ordered entry for collection, extraction, normalization, language ID,
quality filtering, deduplication, PII handling, decontamination, sharding, tokenization,
and compression whenever applied. Record explicit `NOT_RUN` entries and reasons for
required stages that did not run.

### 7. Freeze executable recipes

For every transformation, capture code/bundle SHA-256, repository commit when available,
configuration SHA-256, model or ruleset version and digest, dependency-lock or container
digest, runtime, parameters digest, random seeds, and input/output artifact digests. A
script-file hash alone is insufficient when its environment or configuration affects
the result.

### 8. Import upstream decisions

Import, do not recompute, the outputs of `$normalization-steps`, `$language-skill`,
`$quality-filter`, `$deduplication`, `$pii-data`, and `$decontaminate` when available.
Record `reported_status`, `verification_status`, `evidence_completeness`, the derived
stage `status`, policy/model version, metrics reference, reason codes, input/output
counts, and evidence digest. A claimed pass without versioned evidence is
`verification_status: UNVERIFIED`, not a verified pass.

### 9. Make ordering and sharding deterministic

Use a stable sort with a complete tie-breaker, versioned record serialization, explicit
shard-boundary rules, fixed compression settings, pinned locale/timezone, and controlled
parallel reduction. Never use `row_number()`, filesystem enumeration order, monotonic
IDs, or random UUIDs as content identity.

### 10. Identify the output shard

Hash exact emitted bytes and create `shard_id = "sha256:<full_digest>"`. If logical
content identity is also needed, define its canonical serialization and version before
computing it; never silently substitute it for the byte digest.

### 11. Record composition

Record bytes, records/documents, characters, raw/retained/rejected counts, and tokens.
Attach tokenizer name, version, artifact digest, normalization/configuration, and special
token policy to every token count.

### 12. Record distributions and filter summaries

For language distribution, record counts plus unit (`tokens`, `characters`, or
`records`), LID model/version/digest, threshold, unknown/mixed share, and denominator.
For quality, deduplication, PII, and decontamination, record versioned summaries and
evidence references without exposing sensitive examples.

### 13. Reconcile cross-field totals

Check that input disposition reconciles, retained counts match the emitted artifact,
language counts plus unknown equal the declared denominator, stage input/output digests
form a valid chain, and every metric uses its declared definition. Do not compare
tokenizer-, model-, threshold-, or schema-dependent metrics as if they were identical.

### 14. Canonicalize the recipe and manifest

Serialize hashable JSON with RFC 8785 JSON Canonicalization Scheme. Compute:

- `recipe_sha256` over the normative deterministic recipe projection defined in
  [references/schema.md](references/schema.md);
- `integrity.manifest_digest` over the normative immutable-core projection defined there.

Version the projection. Do not hash pretty-printed or key-order-dependent JSON.

### 15. Evaluate admission gates

Apply the gate checks, routing matrix, and reason codes in
[references/gating-and-comparison.md](references/gating-and-comparison.md). Required
failures must prevent `ADMIT`. Route uncertain but potentially resolvable cases to
`REVIEW` or `QUARANTINE`; use `BLOCK` for policy violations or invalid evidence.

### 16. Sign or attest

When required, sign the immutable manifest digest using the approved attestation system.
Record signer identity, verification material reference, signature format, verification
status, and predicate type. Never store private keys.

### 17. Verify determinism

Rerun representative shards with the same frozen input and recipe. Compare exact output
bytes/content digest and recipe digest. If they differ, set `FAILED_REPRO`, block
admission, and locate the first transformation whose input/output digest diverges.

### 18. Emit records

Emit the immutable shard, shard manifest, safe step log, gate report, and a corpus-index
entry. The index should reference shard ID, manifest digest, corpus split/mix weight,
license class, token count, language distribution, admission state, and any superseding
or revocation event.

### 19. Compare manifests

Classify comparisons before interpreting deltas:

- `IDENTICAL_ARTIFACT_AND_LINEAGE`
- `SAME_CONTENT_DIFFERENT_LINEAGE`
- `SAME_SOURCE_DIFFERENT_PROCESSING`
- `DIFFERENT_CONTENT_COMPARABLE_PROFILE`
- `NOT_COMPARABLE`

Compare content, source, recipe, rights, composition, upstream stages, determinism, gate,
and lifecycle. Report changed fields and gate effects. Use only comparable metric
definitions. See [references/gating-and-comparison.md](references/gating-and-comparison.md).

### 20. Maintain lifecycle

Allow `DRAFT → PROCESSING → READY_FOR_REVIEW → ADMITTED`. Also support `BLOCKED`,
`QUARANTINED`, `FAILED_REPRO`, `SUPERSEDED`, and `REVOKED`. Append actor, timestamp,
reason, policy version, evidence, and affected downstream corpus/model references to a
signed lifecycle event ledger. The admitted manifest core keeps its emission-time state;
the current effective state is resolved by replaying valid ledger events. Propagate later
license, PII, source-integrity, or benchmark contamination revocations.

## Visible step log

The user asked to see what happens at every step. Emit a concise row for every workflow
step, including steps that did not run:

| Field | Required content |
|---|---|
| `step` | Number and stable step ID |
| `purpose` | What the step establishes |
| `inputs` | Artifact IDs/digests and evidence references, never raw sensitive content |
| `method` | Algorithm, code/config/model/policy versions and digests |
| `observed` | Safe counts, hashes, distributions, or metadata |
| `validation` | Exact invariant or gate check applied |
| `status` | Execution/validation state: `PASS`, `FAIL`, `WARNING`, `NOT_RUN`, or `BLOCKED` |
| `evidence_state` | `VERIFIED`, `UNVERIFIED`, `UNKNOWN`, or `NOT_APPLICABLE` |
| `decision_effect` | None, review, quarantine, block, admit, revoke, or supersede |
| `outputs` | Output IDs/digests and report/log references |
| `reason_codes` | Stable machine-readable codes plus concise explanation |

Begin with a run header containing schema/policy versions, run ID, subject ID, start time,
and declared environment. End with reconciliation totals, gate decision, signature
verification, determinism result, and emitted artifact references.

Never claim a step passed when evidence is unavailable. Use `NOT_RUN` for an execution
status and `UNKNOWN` or `UNVERIFIED` only for `evidence_state`.

## Validation

Use the supplied validator:

```bash
python scripts/validate_manifest.py shard.manifest.json
python scripts/validate_manifest.py shard.manifest.json --artifact shard.parquet
python scripts/validate_manifest.py shard.manifest.json --artifact shard.parquet \
  --require-admit --verified-manifest-digest --verified-signatures
python scripts/compare_manifests.py baseline.manifest.json candidate.manifest.json
python scripts/compare_manifests.py baseline.json candidate.json --verified-inputs
```

The validator checks final manifest candidates. An incomplete intake record is expected
to fail until required evidence is resolved. Treat the script as a structural and
semantic preflight, not a legal opinion, signature verifier, or substitute for
recomputing upstream filters. Comparison results are provisional unless artifact,
canonical-manifest, and signature verification was completed independently and
`--verified-inputs` is supplied. Review
[references/evidence.md](references/evidence.md) when designing interoperability,
canonicalization, licensing, provenance, or attestation behavior.

## Deliverables

Return:

1. the immutable per-shard manifest;
2. the complete visible step log;
3. the gate decision with checks and reason codes;
4. the determinism/reconciliation report;
5. a comparison report when a baseline manifest is supplied;
6. the corpus-index entry or revocation/supersession event when applicable.

State unresolved evidence, policy assumptions, and blocked fields explicitly.
