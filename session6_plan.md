# Session 6 — Training Data Execution System — Delivery Plan

*Generated from `generate_assignment.py` — mirrors the Assignment page (`assignment.html`). We build strictly one **epic** (micro-step) at a time.*

## Hierarchy & conventions

| Level | Meaning | Size |
|---|---|---|
| **Feature** | a top-level capability = one pipeline stage (16 total) | large |
| **Epic** | a micro-step inside a feature = one web-Claude prompt → one small module + test | small |
| **Story** | the detail / acceptance criteria inside an epic | tiny |

One epic at a time; an epic is **Done** only when its acceptance criteria are proven by a passing test or generated evidence — never hardcoded. `run_demo.py` and `run.log` are born at Feature 1 and grow one stage per feature.

## Locked decisions

| Area | Decision |
|---|---|
| **Corpus pool** | ~10,000,000 tokens (collected, tokenized, sharded). |
| **Training budget** | ~3,000,000 tokens (keep-fraction ≈ 0.3 of the pool — demonstrates OPUS selection). A single config knob. |
| **Tests** | run on a tiny slice; only the one hero run_demo does the full 3M. |
| **Stack** | Python 3.11, PyTorch on CPU with determinism pinned, NumPy allowed. |
| **Model** | tiny Mixture-of-Experts transformer, pluggable at Feature 10 (after the data plane). |
| **Tokenizer** | self-contained frozen byte-level BPE, vocab + merges committed and content-hashed. |
| **Method** | contrastive perspective lane + F1/F2 surprisal in the learning ledger + ΔS as an OPUS signal. F3–F7 geometry = documented hook (contrastive_perspective_corpus.md). |
| **Repo** | new standalone GitHub repository (name TBD — placeholder v5-execution-system). |
| **Invariant** | a seed + a ledger offset reconstructs any batch byte-for-byte — the basis of resume, replay, and fork. |

## Feature map (16)

| # | Feature | Area | Pts | Status |
|---|---|---|---|---|
| 1 | Collecting data | Tokenizer integrity / data | 100 | ◐ |
| 2 | Clean & filter | Shards/manifests | 100 | ☐ |
| 3 | Frozen BPE tokenizer | Tokenizer integrity | 100 | ☐ |
| 4 | Immutable shards + manifests | Shards/manifests | 100 | ☐ |
| 5 | Evaluation firewall | Firewall | 50 | ☐ |
| 6 | Mixture / curriculum | Mixture | 150 | ☐ |
| 7 | OPUS selector | Mixture/OPUS | 150 | ☐ |
| 8 | Packer (masks, position ids) | Packing/masks | 150 | ☐ |
| 9 | Batch stream + consumption ledger | Ledgers | 150 | ☐ |
| 10 | Trainer (MoE) + learning ledger | Ledgers | 150 | ☐ |
| 11 | Checkpoints | Checkpoint | 150 | ☐ |
| 12 | Crash + resume | Checkpoint | 150 | ☐ |
| 13 | Replay | Checkpoint | 150 | ☐ |
| 14 | Fork | Checkpoint | 150 | ☐ |
| 15 | Throughput / packing efficiency | Throughput | 50 | ☐ |
| 16 | Audit + evidence + one-command + tests + README | Evidence/tests/docs + end-to-end | 200 | ☐ |

## Feature 1 — Collecting data  ◐

Assemble a ~10M-token pool across lanes plus a hand-authored contrastive set and a quarantined eval split, all reproducible, in one clean data model.

### Epic 1.1 — Corpus data model  ◐
- Document frozen dataclass: id, lane∈{web,code,math,indic,multilingual}, provenance_tier∈{T0,T1,T2,T3}, split∈{train,eval}, source, text.
- ContrastivePair frozen dataclass: id, topic, prefix, y_plus, y_minus, vantage, chauvinism.
- validate_document / validate_contrastive raise ValueError on bad enum, empty required string, or chauvinism != none.
- Module-level EXAMPLES (2 Documents, 1 ContrastivePair) + pytest (examples validate; bad lane raises; chauvinism≠none raises).
- **Acceptance:** stdlib only; no I/O; tests pass.

### Epic 1.2 — Sources manifest  ☐
- Config listing, per lane, the pinned dataset id + snapshot/revision + license + target token count.
- Validator: lane targets sum to ~10M and every source has a license.
- **Acceptance:** data only, no downloads yet; test asserts totals and license presence.

### Epic 1.3 — Fetch one lane (web/English)  ☐
- Downloader pulls the pinned English source to data/raw/web/, streaming to a token/byte cap.
- Record each raw file's sha256 in a fetch log.
- **Acceptance:** re-running yields identical file hashes; respects the cap.

### Epic 1.4–1.7 — Fetch code / math / indic / multilingual  ☐
- Same shape as 1.3, one lane per epic.
- **Acceptance:** per-lane caps respected; file hashes recorded.

### Epic 1.8 — Author contrastive pairs  ☐
- ~30–50 hand-authored ContrastivePairs on contested topics; factual y_plus; chauvinism none.
- **Acceptance:** all validate; committed as source, not downloaded.

### Epic 1.9 — Eval held-out split  ☐
- Carve a ~1–2% quarantined slice, mark split=eval, keep provenance.
- **Acceptance:** eval docs disjoint from train; recorded separately.

### Epic 1.10 — Corpus loader  ☐
- Iterate all raw files → Documents in the schema; attach a byte→token estimate.
- **Acceptance:** loads deterministically; counts stable across runs.

### Epic 1.11 — Corpus summary report  ☐
- Write data/corpus_summary.json (docs + est. tokens per lane/split, contrastive count).
- **Acceptance:** report regenerates identically; totals ≈ 10M.

### Epic 1.12 — Wire load_corpus into run_demo.py  ☐
- Minimal run_demo.py creates submission_artifacts/run.log, runs load_corpus, logs per-lane [INFO] lines and a final [PASS] corpus_loaded total=N eval=M contrastive=K; end-to-end test.
- **Acceptance:** python run_demo.py runs clean; test asserts the PASS event.

## Features 2–16 — epic outline (stories elaborated just-in-time)

### Feature 2 — Clean & filter
2.1 canonical normalization (Unicode NFC, whitespace, strip control chars) · 2.2 content-hasher (sha256 over canonical bytes) — born here — + exact-duplicate removal · 2.3 quality filter (min length, symbol/word ratio, repetition heuristics) · 2.4 near-duplicate dedup (MinHash / LSH) · 2.5 PII scrub (emails, phone numbers → redact) · 2.6 decontamination (n-gram overlap of train vs eval + contrastive; drop leaked docs) · 2.7 cleaning report (per-stage drop counts) + test

### Feature 3 — Frozen BPE tokenizer
3.1 BPE trainer on a pool sample · 3.2 freeze (serialize vocab+merges) + tokenizer content hash · 3.3 encode/decode with round-trip test · 3.4 tokenizer manifest (hash, vocab size, special tokens) + test

### Feature 4 — Immutable shards + manifests
4.1 shard writer (fixed-size token shards, content-addressed, immutable) · 4.2 per-shard manifest (hash, token count, lane, provenance, tags, source doc ids) · 4.3 shard-set index · 4.4 immutability / re-hash verification + test

### Feature 5 — Evaluation firewall
5.1 mark eval shards · 5.2 firewall gate (eval shard ids can never enter a train batch) · 5.3 [PASS] eval_shard_blocked event + test

### Feature 6 — Mixture / curriculum
6.1 mixture config (lane weights, protected floors, phases) · 6.2 compiler → planned per-lane token targets per phase · 6.3 floor-enforcement logic · 6.4 planned-shares report + test

### Feature 7 — OPUS selector
7.1 candidate scoring interface · 7.2 accept/reject/defer rule · 7.3 protected-floor override · 7.4 ΔS surprisal signal hook · 7.5 decision ledger + test

### Feature 8 — Packer (masks, position ids)
8.1 sequence packing to seq_len with doc boundaries · 8.2 loss mask (eval/padding + contrastive framing-span-only) · 8.3 attention mask (block cross-document attention) · 8.4 position ids (reset per document) · 8.5 contrastive-pair packing policy · 8.6 packed-batch report + mask correctness tests

### Feature 9 — Batch stream + consumption ledger
9.1 deterministic RNG (born here) + shard sampling per mixture · 9.2 batch iterator (batch id, token spans, shard offsets) · 9.3 batch content hash · 9.4 append-only consumption ledger · 9.5 determinism test (same seed → same batch ids/hashes)

### Feature 10 — Trainer (MoE) + learning ledger
10.1 tiny MoE model (embedding, 1–2 layers, top-k experts, head) using masks + position ids · 10.2 deterministic training step · 10.3 per-token loss = F1 surprisal → learning ledger · 10.4 F2 ΔS per contrastive pair · 10.5 learning ledger links loss → source · 10.6 tests (loss decreases; determinism)

### Feature 11 — Checkpoints
11.1 checkpoint writer (model + optimizer + RNG snapshot + ledger offset) · 11.2 checkpoint manifest + hash · 11.3 restore · 11.4 restore round-trip test

### Feature 12 — Crash + resume
12.1 deliberate crash hook (raise at a set batch) · 12.2 resume from checkpoint · 12.3 prove next batch == expected (no skip/repeat) · 12.4 [PASS] resume_next_batch_matched + test

### Feature 13 — Replay
13.1 replay interval [a,b] from ledger · 13.2 reconstruct batch ids/token spans/hashes · 13.3 prove match vs original + [PASS] replay_hash_matched + test

### Feature 14 — Fork
14.1 fork from an earlier checkpoint (new branch id) · 14.2 divergent run on the branch · 14.3 lineage recorded + test

### Feature 15 — Throughput / packing efficiency
15.1 packing-utilization metric · 15.2 useful loss-bearing tokens/sec · 15.3 performance.json + test

### Feature 16 — Audit + evidence + one-command + tests + README
16.1 audit pass (cross-check ledgers vs manifests) · 16.2 evidence.json from real artifacts · 16.3 evidence.md summary · 16.4 run.log completeness check · 16.5 full run_demo.py wiring (one command) · 16.6 README + invariant test suite

## Open decisions

| Decision | Needed by | Default / candidate |
|---|---|---|
| Repo name | before first commit | v5-execution-system |
| Pinned datasets + licenses per lane | Epic 1.2 / 1.3 | web: FineWeb/C4 · code: The Stack (permissive) · math: open math set · indic: Sangraha/IndicCorp/Indic-Wiki · multilingual: small sample |
| Tokenizer vocab size | Feature 3 | ~8k–16k |
| seq_len, batch size | Feature 8/9 | seq 256, batch 8 (≈2,048 tokens/batch) |
| MoE dims (d_model, layers, #experts, top-k) | Feature 10 | d_model 128, 2 layers, 4 experts, top-2 |
| Provenance tiers usage | Feature 2/4 | T0 verified · T1 web · T2 synthetic · T3 translated |

## Current epic — 1.1 · Corpus data model

Prompt (paste into web Claude) is on the Assignment page and returns `corpus_schema.py` + its test.

