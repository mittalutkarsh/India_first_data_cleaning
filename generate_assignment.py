"""Generate assignment.html AND session6_plan.md from one data source, so the
living tracker page and the plan document cannot drift. Reuses the house CSS.
Update the data structures below as epics advance (status) or get elaborated."""
import html
import generate_v5_playbook as P

CSS = P.CSS

NAV = (
    '<div class="nav"><div class="nav-in">\n'
    '  <span class="brand">India-First 40B</span>\n'
    '  <a href="overview.html">Overview</a>\n'
    '  <a href="data.html">Data</a>\n'
    '  <a href="index.html">Cleaning</a>\n'
    '  <a href="language.html">Language</a>\n'
    '  <a href="quality.html">Quality</a>\n'
    '  <a href="dedup.html">Dedup</a>\n'
    '  <a href="pii.html">PII</a>\n'
    '  <a href="decontam.html">Decontam</a>\n'
    '  <a href="tokenizer.html">Tokenizer</a>\n'
    '  <a href="manifest.html">Manifest</a>\n'
    '  <a href="v5_brief.html">V5 Plan</a>\n'
    '  <a href="v5_playbook.html">V5 Plan — Proposal</a>\n'
    '  <a href="assignment.html" class="active">Assignment</a>\n'
    '</div></div>\n'
)

CONV = [
    ("Feature", "a top-level capability = one pipeline stage (16 total)", "large"),
    ("Epic", "a micro-step inside a feature = one web-Claude prompt → one small module + test", "small"),
    ("Story", "the detail / acceptance criteria inside an epic", "tiny"),
]

LOCKED = [
    ("Corpus pool", "~10,000,000 tokens (collected, tokenized, sharded)."),
    ("Training budget", "~3,000,000 tokens (keep-fraction ≈ 0.3 of the pool — demonstrates OPUS selection). A single config knob."),
    ("Tests", "run on a tiny slice; only the one hero run_demo does the full 3M."),
    ("Stack", "Python 3.11, PyTorch on CPU with determinism pinned, NumPy allowed."),
    ("Model", "tiny Mixture-of-Experts transformer, pluggable at Feature 10 (after the data plane)."),
    ("Tokenizer", "self-contained frozen byte-level BPE, vocab + merges committed and content-hashed."),
    ("Method", "contrastive perspective lane + F1/F2 surprisal in the learning ledger + ΔS as an OPUS signal. F3–F7 geometry = documented hook (contrastive_perspective_corpus.md)."),
    ("Repo", "new standalone GitHub repository (name TBD — placeholder v5-execution-system)."),
    ("Invariant", "a seed + a ledger offset reconstructs any batch byte-for-byte — the basis of resume, replay, and fork."),
]

# num, name, area, points, status (done|active|pending)
FEATURES = [
    (1, "Collecting data", "Tokenizer integrity / data", 100, "done"),
    (2, "Clean & filter", "Shards/manifests", 100, "done"),
    (3, "Frozen BPE tokenizer", "Tokenizer integrity", 100, "active"),
    (4, "Immutable shards + manifests", "Shards/manifests", 100, "pending"),
    (5, "Evaluation firewall", "Firewall", 50, "pending"),
    (6, "Mixture / curriculum", "Mixture", 150, "pending"),
    (7, "OPUS selector", "Mixture/OPUS", 150, "pending"),
    (8, "Packer (masks, position ids)", "Packing/masks", 150, "pending"),
    (9, "Batch stream + consumption ledger", "Ledgers", 150, "pending"),
    (10, "Trainer (MoE) + learning ledger", "Ledgers", 150, "pending"),
    (11, "Checkpoints", "Checkpoint", 150, "pending"),
    (12, "Crash + resume", "Checkpoint", 150, "pending"),
    (13, "Replay", "Checkpoint", 150, "pending"),
    (14, "Fork", "Checkpoint", 150, "pending"),
    (15, "Throughput / packing efficiency", "Throughput", 50, "pending"),
    (16, "Audit + evidence + one-command + tests + README", "Evidence/tests/docs + end-to-end", 200, "pending"),
]

# id, title, status, [stories], acceptance
FEATURE1 = [
    ("1.1", "Corpus data model", "done", [
        "Document frozen dataclass: id, lane∈{web,code,math,indic,multilingual}, provenance_tier∈{T0,T1,T2,T3}, split∈{train,eval}, source, text.",
        "ContrastivePair frozen dataclass: id, topic, prefix, y_plus, y_minus, vantage, chauvinism.",
        "validate_document / validate_contrastive raise ValueError on bad enum, empty required string, or chauvinism != none.",
        "Module-level EXAMPLES (2 Documents, 1 ContrastivePair) + pytest (examples validate; bad lane raises; chauvinism≠none raises).",
    ], "stdlib only; no I/O; tests pass."),
    ("1.2", "Sources manifest", "done", [
        "LaneSource: source_id (unique), lane, dataset, config, revision, license, provenance_tier, target_tokens, gated, notes.",
        "SOURCES for all five lanes summing to ~10M; Wikipedia sources tier T1 (eval-eligible), crawl sources T2 (train-only).",
        "validate_sources: lanes/tiers valid, source_ids unique, licenses present, no gated sources, all five lanes covered, total ~10M; eval_eligible() returns the T0/T1 sources.",
    ], "data only, no downloads; test asserts totals, uniqueness, tier/eval-eligibility, and rejects gated / empty-license / zero-token / dup-id / bad-tier."),
    ("1.3", "Fetch one lane (web/English)", "done", [
        "Downloader pulls the pinned English source to data/raw/web/, streaming to a token/byte cap.",
        "Record each raw file's sha256 in a fetch log.",
    ], "re-running yields identical file hashes; respects the cap."),
    ("1.4–1.7", "Fetch code / math / indic / multilingual", "done", [
        "Same shape as 1.3, one lane per epic.",
    ], "per-lane caps respected; file hashes recorded."),
    ("1.8", "Author contrastive pairs", "done", [
        "~30–50 hand-authored ContrastivePairs on contested topics; factual y_plus; chauvinism none.",
    ], "all validate; committed as source, not downloaded."),
    ("1.9", "Eval held-out split", "done", [
        "Carve a ~1–2% quarantined slice, mark split=eval, keep provenance.",
    ], "eval docs disjoint from train; recorded separately."),
    ("1.10", "Corpus loader", "done", [
        "Iterate all raw files → Documents in the schema; attach a byte→token estimate.",
    ], "loads deterministically; counts stable across runs."),
    ("1.11", "Corpus summary report", "done", [
        "Write data/corpus_summary.json (docs + est. tokens per lane/split, contrastive count).",
    ], "report regenerates identically; totals ≈ 10M."),
    ("1.12", "Wire load_corpus into run_demo.py", "done", [
        "Minimal run_demo.py creates submission_artifacts/run.log, runs load_corpus, logs per-lane [INFO] lines and a final [PASS] corpus_loaded total=N eval=M contrastive=K; end-to-end test.",
    ], "python run_demo.py runs clean; test asserts the PASS event."),
]

# id, title, status, [stories], acceptance — elaborated when the feature became current
FEATURE2 = [
    ("2.1", "Canonical normalization", "done", [
        "normalize_text(text) -> str: Unicode NFC, strip control chars (keep \\n and \\t), collapse runs of whitespace, trim ends.",
        "Deterministic and idempotent: normalize_text(normalize_text(x)) == normalize_text(x).",
        "normalize_document(doc) -> Document: normalized text, all other fields (id/lane/tier/split/source) unchanged.",
        "pytest: NFC composition, control-char removal, whitespace collapse, idempotence, and pass-through of the non-text fields.",
    ], "stdlib (unicodedata); pure, no I/O; idempotent; tests pass."),
    ("2.2", "Content hash + exact-duplicate removal", "done", [
        "content_hash(text) -> str: sha256 over the NFC-normalized UTF-8 bytes — stable across runs and machines (the content-hasher is born here).",
        "dedup_exact(docs) -> (kept, drops): keep the first occurrence of each content_hash in deterministic order; each later exact duplicate becomes a drop {id, stage:'exact_dup', duplicate_of}.",
        "pytest: identical texts hash-equal; re-ordering keeps the same survivor; drop records name the survivor; the hash is order/clock-independent.",
    ], "stdlib (hashlib); deterministic; content hash independent of dict order or wall-clock."),
    ("2.3", "Quality filter", "done", [
        "quality_ok(text) -> (bool, reason|None): heuristics with named thresholds — min length (chars/words), max symbol-to-word ratio, max non-text-char fraction, max line/word repetition.",
        "filter_quality(docs) -> (kept, drops): drop failing docs recording {id, stage:'quality', reason} (the specific failing heuristic).",
        "pytest: a normal doc passes; a too-short, a symbol-spam, and a repetition-spam doc each fail with the right reason; thresholds exercised at the boundary.",
    ], "stdlib; deterministic; thresholds documented; a test per rejection reason."),
    ("2.4", "Near-duplicate dedup (MinHash / LSH)", "done", [
        "A pure-Python MinHash over char/token n-gram shingles (fixed num_perm, fixed seed) + a Jaccard estimate — deterministic, no external library.",
        "dedup_near(docs, threshold=0.8) -> (kept, drops): cluster near-duplicates (LSH buckets, or all-pairs at toy scale), keep the first of each cluster in deterministic order; drops record {id, stage:'near_dup', near:survivor_id, est_jaccard}.",
        "pytest: two near-identical docs -> one dropped naming its survivor; two unrelated docs -> both kept; determinism; behaviour at the threshold boundary.",
    ], "stdlib only (hand-rolled MinHash); deterministic (fixed seed/permutations); tests pass."),
    ("2.5", "PII scrub", "done", [
        "scrub_pii(text) -> (text, n_redactions): regex-redact emails and phone numbers to fixed placeholders ([EMAIL], [PHONE]); conservative patterns to avoid over-redaction.",
        "scrub_document(doc) -> (Document, n): a Document with scrubbed text and a redaction count.",
        "pytest: an email and a phone are redacted; ordinary numbers/text are left alone; idempotent (scrubbing twice adds nothing); the count is correct.",
    ], "stdlib (re); deterministic; idempotent; no over-redaction of benign cases."),
    ("2.6", "Decontamination (train vs eval + contrastive)", "done", [
        "Build the set of n-grams (e.g. 13-grams) from the eval docs + the contrastive continuations; a train doc is contaminated if it shares at least K of them.",
        "decontaminate(train_docs, eval_docs, contrastive_pairs, n=13) -> (kept, drops): drop contaminated train docs recording {id, stage:'decontam', overlap_with}; eval and contrastive are never dropped.",
        "pytest: a train doc copying an eval span is dropped; an unrelated train doc is kept; eval/contrastive are protected; determinism.",
    ], "stdlib; deterministic; only train docs can be dropped; eval/contrastive protected."),
    ("2.7", "Clean pipeline + report + run_demo stage", "done", [
        "clean_corpus(...) composes 2.1–2.6 in order over the loader's train docs (eval passes through untouched), writing cleaned train docs to data/clean/<source_id>/documents.jsonl (raw untouched) + a cleaning_report with per-stage {input, kept, dropped} counts and a drops manifest {id, stage, reason}.",
        "Deterministic + idempotent: a second run yields a byte-identical cleaned set and report.",
        "Wire a clean stage into run_demo: log per-stage [INFO] drop counts and a final [PASS] corpus_cleaned kept=… dropped=…; end-to-end test.",
    ], "reads raw + eval, writes only under data/clean and submission_artifacts; deterministic; run_demo emits [PASS] corpus_cleaned; tests pass."),
]

# id, title, status, [stories], acceptance — elaborated when the feature became current
FEATURE3 = [
    ("3.1", "Byte-level alphabet + pre-tokenization", "active", [
        "byte_encode(text) -> list[int] / byte_decode(list[int]) -> str over UTF-8 bytes: the base alphabet is the 256 byte values, so EVERY lane — including Devanagari, Bengali and Tamil — is representable with no <unk> and nothing to fragment (the byte-level choice is what makes an India-first tokenizer safe).",
        "A reversible byte<->printable-symbol view (GPT-2 style) so merge rules can be stored and diffed as text while staying lossless.",
        "Pre-tokenize on a single fixed regex so merges never cross a whitespace boundary; deterministic and stdlib-only.",
    ], "byte round-trip is lossless on a sample from every lane; no wall-clock / dict-order dependence; tests pass."),
    ("3.2", "Deterministic BPE trainer", "pending", [
        "train_bpe(corpus_iter, *, vocab_size, special_tokens) -> (vocab, merges): count adjacent symbol-pair frequencies inside pre-tokens, merge the most frequent pair, repeat until the target vocab size (a single knob; ~8k for the toy).",
        "A total, fixed tie-break (highest count, then lexicographically smallest pair) so the learned merges are reproducible regardless of dict iteration order.",
        "Train on a bounded, lane-balanced, deterministic sample of the CLEANED corpus (data/clean from Feature 2) so it is fast and representative of every lane.",
    ], "training the same sample + params twice yields identical (vocab, merges), ordered by learn-step; deterministic; tests pass."),
    ("3.3", "Freeze: serialize vocab + merges (immutable artifact)", "pending", [
        "Write tokenizer/vocab.json (token->id) and tokenizer/merges.txt (ordered merge rules) with deterministic bytes: ranked where order is semantic, sorted where it is not, ensure_ascii=False, newline=\"\\n\".",
        "The artifact is written ONCE and treated as immutable — no later stage rewrites it (the same immutability discipline as raw and eval).",
    ], "serialize -> load -> serialize is byte-identical, and identical across machines; tests pass."),
    ("3.4", "Encoder", "pending", [
        "Tokenizer.load(dir) reads the frozen vocab+merges; encode(text) -> list[int] applies the merges greedily by rank within each pre-token.",
        "Pure function of the frozen artifact — no training-time state; a byte-level fallback guarantees unknown bytes can never occur.",
    ], "encoding is deterministic; known strings map to expected id sequences; no <unk> on any lane; tests pass."),
    ("3.5", "Decoder + lossless round-trip", "pending", [
        "decode(ids) -> str inverts encode through the byte-level mapping.",
        "Round-trip invariant: decode(encode(x)) == x for a sample from every lane, including Indic combining sequences, emoji and code punctuation, plus a property test over random Unicode.",
    ], "exact round-trip on every lane sample and the property test; tests pass."),
    ("3.6", "Special tokens + integrity checks", "pending", [
        "Reserve special tokens with fixed ids (<pad>, <bos>, <eos>, <doc>) that never collide with learned tokens and never arise from encoding ordinary text.",
        "Integrity checks: the vocab covers all 256 base bytes, every merge references tokens that exist, ids are a contiguous 0..N-1, and special ids are disjoint.",
    ], "the integrity check passes on the frozen tokenizer and rejects a corrupted vocab (missing byte / duplicate id); tests pass."),
    ("3.7", "Tokenizer manifest + content hash (the freeze contract)", "pending", [
        "content_hash over the canonical (vocab + merges + special tokens) bytes; write tokenizer/tokenizer_manifest.json {hash, vocab_size, n_merges, special_tokens, base=\"bytes\", trained_on (cleaned-corpus reference), tokenizer_version}.",
        "This hash is the tokenizer's identity — every downstream stage (shards, batches) references it, so re-freezing the same corpus must reproduce the same hash.",
    ], "the manifest regenerates identically and the hash is stable across runs/machines; a one-token change changes the hash; tests pass."),
    ("3.8", "Wire the tokenizer stage into run_demo", "pending", [
        "Load the frozen tokenizer, VERIFY its content hash matches the manifest, then encode+decode a sample from every lane and assert the round-trip.",
        "Log [INFO] tokenizer lines and a final [PASS] tokenizer_frozen vocab=… merges=… hash=…; run.log stays deterministic (basename-only, no timestamps or absolute paths).",
    ], "python run_demo.py emits [PASS] tokenizer_frozen after corpus_cleaned, the hash matches the manifest, and the end-to-end test passes."),
]

# feature num -> provisional epic outline (features not yet elaborated)
OUTLINE = {
    4: "4.1 shard writer (fixed-size token shards, content-addressed, immutable) · 4.2 per-shard manifest (hash, token count, lane, provenance, tags, source doc ids) · 4.3 shard-set index · 4.4 immutability / re-hash verification + test",
    5: "5.1 mark eval shards · 5.2 firewall gate (eval shard ids can never enter a train batch) · 5.3 [PASS] eval_shard_blocked event + test",
    6: "6.1 mixture config (lane weights, protected floors, phases) · 6.2 compiler → planned per-lane token targets per phase · 6.3 floor-enforcement logic · 6.4 planned-shares report + test",
    7: "7.1 candidate scoring interface · 7.2 accept/reject/defer rule · 7.3 protected-floor override · 7.4 ΔS surprisal signal hook · 7.5 decision ledger + test",
    8: "8.1 sequence packing to seq_len with doc boundaries · 8.2 loss mask (eval/padding + contrastive framing-span-only) · 8.3 attention mask (block cross-document attention) · 8.4 position ids (reset per document) · 8.5 contrastive-pair packing policy · 8.6 packed-batch report + mask correctness tests",
    9: "9.1 deterministic RNG (born here) + shard sampling per mixture · 9.2 batch iterator (batch id, token spans, shard offsets) · 9.3 batch content hash · 9.4 append-only consumption ledger · 9.5 determinism test (same seed → same batch ids/hashes)",
    10: "10.1 tiny MoE model (embedding, 1–2 layers, top-k experts, head) using masks + position ids · 10.2 deterministic training step · 10.3 per-token loss = F1 surprisal → learning ledger · 10.4 F2 ΔS per contrastive pair · 10.5 learning ledger links loss → source · 10.6 tests (loss decreases; determinism)",
    11: "11.1 checkpoint writer (model + optimizer + RNG snapshot + ledger offset) · 11.2 checkpoint manifest + hash · 11.3 restore · 11.4 restore round-trip test",
    12: "12.1 deliberate crash hook (raise at a set batch) · 12.2 resume from checkpoint · 12.3 prove next batch == expected (no skip/repeat) · 12.4 [PASS] resume_next_batch_matched + test",
    13: "13.1 replay interval [a,b] from ledger · 13.2 reconstruct batch ids/token spans/hashes · 13.3 prove match vs original + [PASS] replay_hash_matched + test",
    14: "14.1 fork from an earlier checkpoint (new branch id) · 14.2 divergent run on the branch · 14.3 lineage recorded + test",
    15: "15.1 packing-utilization metric · 15.2 useful loss-bearing tokens/sec · 15.3 performance.json + test",
    16: "16.1 audit pass (cross-check ledgers vs manifests) · 16.2 evidence.json from real artifacts · 16.3 evidence.md summary · 16.4 run.log completeness check · 16.5 full run_demo.py wiring (one command) · 16.6 README + invariant test suite",
}

OPEN_DECISIONS = [
    ("Repo name", "before first commit", "v5-execution-system"),
    ("Pinned datasets + licenses per lane", "Epic 1.2 / 1.3", "web: FineWeb/C4 · code: The Stack (permissive) · math: open math set · indic: Sangraha/IndicCorp/Indic-Wiki · multilingual: small sample"),
    ("Tokenizer vocab size", "Feature 3", "~8k–16k"),
    ("seq_len, batch size", "Feature 8/9", "seq 256, batch 8 (≈2,048 tokens/batch)"),
    ("MoE dims (d_model, layers, #experts, top-k)", "Feature 10", "d_model 128, 2 layers, 4 experts, top-2"),
    ("Provenance tiers usage", "Feature 2/4", "T0 verified · T1 web · T2 synthetic · T3 translated"),
]

# label, when-to-use, the copy-paste instruction the USER gives to Claude Code
TEMPLATES = [
    ("A · Expand a feature",
     "when a feature is still just an outline and we're ready to work it",
     "Expand Feature <N> (<name>) into full epics and stories. For each epic give: an id, "
     "a title, its stories (concrete tasks), and acceptance criteria. Keep every epic micro "
     "(one small module + one test each). Update the plan (session6_plan.md + assignment.html "
     "regenerate together). Do NOT send anything to the web yet."),
    ("B · Prepare an epic for the web",
     "when an epic is next and we want the code prompt",
     "Write the web-Claude prompt for Epic <N.M> (<title>). Make it self-contained (web Claude "
     "has no repo context), scoped to ONLY this epic, with the exact module name, the "
     "function/class signatures, and the acceptance test it must satisfy; end by asking for the "
     "complete code + test + a one-line note. Put it in the 'Current epic' section of the page."),
    ("C · Integrate & advance",
     "when web Claude has returned the code",
     "Here is web Claude's output for Epic <N.M>: <paste code>. Review it against the acceptance "
     "criteria, integrate it into the v5-execution-system repo, run the test, then mark Epic "
     "<N.M> done and set the next epic active in the plan."),
]

PROMPT_1_4_7 = r'''CONTEXT: reproducible "Training Data Execution System", Python 3.11, built in small
steps. The repo already has these WORKING modules (46 offline tests pass):
  * corpus_schema.py — Document(id, lane, provenance_tier, split, source, text),
    validate_document, LANES, PROVENANCE_TIERS.
  * sources_manifest.py — frozen dataclass LaneSource(source_id, lane, dataset, config,
    revision, license, provenance_tier, target_tokens, gated, notes); a tuple SOURCES of 8
    entries; POOL_TARGET_TOKENS, POOL_TOLERANCE, EVAL_TIERS; lane_totals(sources),
    eval_eligible(sources), validate_sources(sources).
  * fetch.py — estimate_tokens(text)=max(1,len(utf8)//4);
    fetch_source(source, *, out_root="data/raw", doc_iter=None, force=False) -> summary
    dict (streams docs, caps at source.target_tokens, writes
    out_root/<source_id>/documents.jsonl one JSON Document per line, appends a sha256
    record to out_root/fetch_log.jsonl, caches on re-run). Internal helpers:
    _extract_text(item, *, index) [str, or dict with "text"], _sha256, _last_log_record,
    _resolve_revision(source, doc_iter) [uses source.revision, else resolves via
    huggingface_hub only when doc_iter is None], _stream_hf(source, revision)
    [load_dataset(..., streaming=True), yields row["text"]]. datasets/huggingface_hub are
    imported lazily only on the real path. main() fetches only web-fineweb.

THIS IS EPIC 1.4–1.7: generalize the fetcher to handle ALL lanes, and account for datasets
that expose their text under a different column name (FineWeb "text",
codeparrot/github-code-clean "content", Wikipedia "text"). Keep everything offline-testable
and DO NOT break the 46 passing tests.

CHANGES:
1. sources_manifest.py — add a field text_field: str to LaneSource (the upstream text
   column name). Set it on every SOURCES entry: "content" for source_id="code-github",
   "text" for all others. validate_sources must also reject an empty/whitespace text_field.
   Everything else unchanged. Return the FULL updated sources_manifest.py.
2. fetch.py:
   - _extract_text(item, *, text_field, index): if item is a str, return it; if a dict,
     return item[text_field] IF that key exists and its value is a str (EVEN an empty
     string — the caller skips blanks); if the key is missing or the value is not a str,
     raise ValueError; otherwise raise. (Do NOT raise on empty string.)
   - _stream_hf(source, revision): yield the RAW rows from load_dataset (do not pre-extract
     a field).
   - In the write loop, get text via _extract_text(item, text_field=source.text_field,
     index=index).
   - Add fetch_all(sources, *, out_root="data/raw", force=False, doc_iters=None) ->
     list[dict]: call validate_sources(sources); for each source in order call
     fetch_source(source, out_root=out_root, force=force,
     doc_iter=(doc_iters or {}).get(source.source_id)); return the list of summaries.
     doc_iters is an optional dict mapping source_id -> iterable, used ONLY by tests to
     inject offline; in production it is None so every source uses the real stream.
   - main(): call fetch_all(SOURCES) and print the summaries.
   Return the FULL updated fetch.py.
3. Tests — return only the NEW test functions to ADD (not whole files):
   - test_sources_manifest.py: every SOURCES entry has a non-empty text_field;
     code-github has text_field="content"; a source with text_field="" raises.
   - test_fetch.py (offline): a source with text_field="content" and a doc_iter of
     {"content": "..."} dicts fetches correctly and yields valid Documents; a dict missing
     the declared text_field raises ValueError; and a fetch_all test that, given two fake
     pinned LaneSources with small targets and a doc_iters mapping, writes both sources'
     documents.jsonl and returns two summaries.

REQUIREMENTS: preserve existing behavior and all 46 passing tests (the current fetch tests
inject {"text": ...} dicts with a web source whose text_field will be "text", so they must
still pass). Deterministic JSON, lazy datasets/huggingface_hub imports, stdlib +
corpus_schema/sources_manifest otherwise. Return: full sources_manifest.py, full fetch.py,
the new test functions to add, and a one-line note.'''


PROMPT_1_8 = r'''CONTEXT: reproducible "Training Data Execution System", Python 3.11, built in small
steps. corpus_schema.py already exists and defines: a frozen dataclass
ContrastivePair(id, topic, prefix, y_plus, y_minus, vantage, chauvinism); a validator
validate_contrastive(pair) that raises ValueError on any empty field, on vantage != VANTAGE,
on chauvinism != CHAUVINISM, and on y_plus == y_minus; and the constants
VANTAGE = "indian_plus_western_minus" and CHAUVINISM = "none".

THIS IS EPIC 1.8 ONLY — author the contrastive perspective corpus. It is HAND-WRITTEN, not
downloaded. No fetching, no tokenizer, no file I/O, no network.

METHOD (from the project's B.4 spec): minimal contrastive pairs on contested,
globally-framed topics. Same prefix; two continuations that differ ONLY in a localized
framing span. y_plus = the Indian-vantage continuation; y_minus = the Western-default
continuation. DESIGN GUARD: y_plus must be a FACTUAL, historically defensible Indian
framing, NEVER a chauvinistic one (the contrast is about vantage point, not about
disparaging anyone); that is what chauvinism="none" asserts. Model example:
  prefix : "The economic impact of British colonial rule on India was"
  y_plus : "a large-scale wealth transfer that deindustrialised Bengal's textile economy
            and lowered per-capita income for decades."
  y_minus: "a mixed legacy that introduced railways, a civil service, and modern
            administrative institutions."

TASK: Create contrastive_pairs.py.
 - Import ContrastivePair, validate_contrastive, VANTAGE, CHAUVINISM from corpus_schema.
 - A module-level tuple CONTRASTIVE_PAIRS of 30-40 ContrastivePair instances on DISTINCT
   contested topics where an Indian vantage and a Western-default framing genuinely
   diverge -- for example: colonial economic impact, the financial year, Partition,
   non-alignment / the Cold War, the spice and textile trade, traditional medicine
   (Ayurveda/Siddha), the lakh/crore numbering system, date and measurement conventions,
   cricket, staple foods and spice, festivals, how particular historical figures or events
   are framed, "mother tongue" vs "vernacular", the monsoon and agriculture, the space
   programme. Choose a good, varied set.
 - Each pair: a unique id ("pair-0001", ...), a short topic, a shared prefix, a factual
   Indian-vantage y_plus, a plausible Western-default y_minus (both defensible, differing
   only in framing), vantage=VANTAGE, chauvinism=CHAUVINISM. Keep each continuation 1-2
   sentences; y_plus and y_minus must not be identical.
 - A helper validate_all(pairs=CONTRASTIVE_PAIRS) that runs validate_contrastive on each
   and also raises ValueError on any duplicate id; returns the pairs.
 - A pytest test asserting: at least 30 pairs; validate_all(CONTRASTIVE_PAIRS) passes; all
   ids unique; every vantage==VANTAGE and chauvinism==CHAUVINISM; y_plus != y_minus for
   every pair; and a duplicate-id list is rejected by validate_all.

REQUIREMENTS: standard library only plus corpus_schema; deterministic; no file I/O, no
network. Return contrastive_pairs.py and its test, plus a one-line note.'''


PROMPT_1_9 = r'''CONTEXT: reproducible "Training Data Execution System", Python 3.11, built in small
steps. Existing modules: corpus_schema.py (Document(id, lane, provenance_tier, split,
source, text), validate_document, PROVENANCE_TIERS); sources_manifest.py (SOURCES,
eval_eligible(sources) -> the T0/T1 sources, EVAL_TIERS = {"T0","T1"}); fetch.py
(estimate_tokens(text)=max(1,len(utf8)//4); fetched data lives at
data/raw/<source_id>/documents.jsonl, one JSON Document per line with split="train";
data/raw/fetch_log.jsonl records per-source est_tokens). All five lanes are on disk
(~10M tokens); the eval-eligible sources are the Wikipedia lanes (tier T1).

THIS IS EPIC 1.9 ONLY — carve a small, quarantined EVAL split. Rule 3 (corpus_schema):
eval may be drawn ONLY from T0/T1 sources. The fetched documents.jsonl are IMMUTABLE — do
NOT modify them; instead RECORD which document ids are eval, deterministically, so the
loader (a later epic) routes them to split="eval" and everything else to train
(a document is eval XOR train).

TASK: Create eval_split.py.
 - EVAL_TARGET_FRACTION = 0.015  (about 1.5% of the pool).
 - A PURE function select_eval(candidates, *, total_pool_tokens,
   target_fraction=EVAL_TARGET_FRACTION, seed="v5-eval-2026") -> dict:
   * candidates: iterable of dicts with keys id, source_id, lane, provenance_tier,
     est_tokens (int).
   * RULE-3 GUARD: if any candidate's provenance_tier not in EVAL_TIERS (import from
     sources_manifest), raise ValueError.
   * Deterministic, NO RNG: key each candidate by
     sha256(f"{seed}:{id}".encode()).hexdigest(); sort by that key; take in that order,
     accumulating est_tokens, until the cumulative first reaches/exceeds
     round(target_fraction * total_pool_tokens); stop.
   * Return {"eval_ids": tuple of selected ids sorted by id, "selected_tokens",
     "target_tokens", "candidate_tokens", "seed",
     "fingerprint": sha256 of "\n".join(sorted eval_ids)}.
   * Selected ids are a subset of candidate ids; everything not selected is train.
 - A wrapper carve_eval(*, raw_root="data/raw", eval_root="data/eval", sources=SOURCES,
   seed="v5-eval-2026") -> dict that:
   * gets eval-eligible source_ids via eval_eligible(sources) (do NOT call
     validate_sources — a subset must work);
   * builds candidates by reading raw_root/<source_id>/documents.jsonl for each eligible
     source (source_id is the directory name; est_tokens = estimate_tokens(doc["text"]);
     carry id, lane, provenance_tier);
   * computes total_pool_tokens = sum of est_tokens over ALL records in
     raw_root/fetch_log.jsonl;
   * calls select_eval;
   * writes eval_root/eval_manifest.jsonl: a header line
     {"kind":"header", seed, target_fraction, target_tokens, candidate_tokens,
     selected_tokens, selected_count, fingerprint}, then one line per eval doc
     {id, source_id, lane, provenance_tier, split:"eval", est_tokens};
   * also writes the eval documents to eval_root/<source_id>/documents.jsonl with split
     flipped to "eval" (construct a Document and validate_document it — this re-checks
     rule 3); deterministic JSON (sort_keys=True, ensure_ascii=False,
     separators=(",",":")), newline="\n";
   * idempotent: if eval_root/eval_manifest.jsonl exists with a matching fingerprint,
     skip and return cached=True;
   * returns a summary (selected_count, selected_tokens, fingerprint, sources).

TESTS — test_eval_split.py, offline (no network):
 * select_eval on ~50 fake T1 candidates with a known total: stops at/just past
   target_fraction*total; eval_ids subset of candidates; same seed => identical eval_ids
   and fingerprint; two different seeds => different fingerprints; selected token sum is
   within one candidate of the target.
 * a candidate with provenance_tier "T2" makes select_eval raise ValueError.
 * disjointness: non-selected candidates share no id with eval_ids.
 * carve_eval on a tmp_path raw_root you build: two fake eval-eligible source dirs (e.g.
   indic-wiki-hi, mling-wiki-es) each with a documents.jsonl of a few T1 Document lines,
   plus a fetch_log.jsonl with est_tokens; pass sources = a small tuple of matching
   T1 LaneSource so eval_eligible returns those two; assert eval_manifest.jsonl has a
   header + eval lines, every eval doc has split="eval" and validate_document passes,
   eval ids come only from the eligible sources, and a second call returns cached=True.

REQUIREMENTS: stdlib (hashlib, json, pathlib) + corpus_schema + sources_manifest + fetch;
deterministic; no network. Return eval_split.py and test_eval_split.py, plus a one-line
note that the fetched files are never mutated — eval is recorded, not moved.'''


PROMPT_1_10 = r'''CONTEXT: reproducible "Training Data Execution System", Python 3.11, built in small
steps. Existing modules:
 - corpus_schema.py: Document(id, lane, provenance_tier, split, source, text),
   validate_document, ContrastivePair, LANES.
 - sources_manifest.py: SOURCES (each LaneSource has source_id, lane, provenance_tier, ...).
 - fetch.py: estimate_tokens(text)=max(1,len(utf8)//4). Fetched data at
   data/raw/<source_id>/documents.jsonl (one JSON Document per line, split="train").
 - contrastive_pairs.py: CONTRASTIVE_PAIRS (a tuple of 36 ContrastivePair).
 - eval_split.py wrote data/eval/eval_manifest.jsonl: a header line {"kind":"header",...}
   then one line per eval doc {id, source_id, lane, provenance_tier, split:"eval",
   est_tokens}. Eval ids are RECORDED, not moved; the raw files still say split="train".

THIS IS EPIC 1.10 ONLY — the corpus loader. One deterministic reader that yields every
Document across the lanes with split routed by the eval manifest (a recorded id ->
split="eval", else "train"; a document is eval XOR train), and that also exposes the
contrastive pairs. It reads only; it writes nothing.

TASK: Create corpus_loader.py.
 - A frozen dataclass LoadedDocument with fields: document: Document, est_tokens: int.
 - load_eval_ids(eval_root="data/eval") -> frozenset[str]: read
   eval_root/eval_manifest.jsonl, skip the header line (the one whose "kind" == "header"),
   return the set of entry "id"s. A missing manifest -> empty frozenset.
 - iter_documents(*, raw_root="data/raw", eval_root="data/eval", sources=SOURCES) ->
   Iterator[LoadedDocument]:
   * eval_ids = load_eval_ids(eval_root).
   * For each source in sources sorted by source_id, read
     raw_root/<source_id>/documents.jsonl in file order (skip a source whose file is
     absent). For each row build a Document with split = "eval" if row["id"] in eval_ids
     else "train" (override whatever the file says); other fields from the row; call
     validate_document (this also re-checks rule 3 for any eval doc); yield
     LoadedDocument(document, estimate_tokens(row["text"])).
   * Track which eval_ids were actually seen; after the loop, if any eval id was never
     seen, raise ValueError (the manifest references a document absent from raw — a
     consistency bug).
 - Re-export CONTRASTIVE_PAIRS from contrastive_pairs.
 - corpus_counts(*, raw_root="data/raw", eval_root="data/eval", sources=SOURCES) -> dict:
   iterate iter_documents once and tally, per lane, {"train_docs","eval_docs",
   "train_tokens","eval_tokens"}; add a "contrastive" entry {"pairs": len(CONTRASTIVE_PAIRS),
   "est_tokens": sum over each pair of estimate_tokens(prefix+" "+y_plus) +
   estimate_tokens(prefix+" "+y_minus)}; and a "totals" entry {"docs","tokens",
   "eval_docs","eval_tokens"}. Deterministic.
 - load_corpus(*, raw_root="data/raw", eval_root="data/eval", sources=SOURCES) ->
   CorpusView: a small frozen dataclass bundling a documents() method that returns
   iter_documents(...), a contrastive tuple (CONTRASTIVE_PAIRS), and a counts() method
   returning corpus_counts(...).

TESTS — test_corpus_loader.py, offline, building a fake raw_root + eval manifest in
tmp_path:
 * lay out two source dirs (a T2 web-like and a T1 wiki-like) with a few Document lines
   each (split="train"), and an eval_root/eval_manifest.jsonl with a header + a couple of
   entries whose ids are real T1 docs.
 * iter_documents yields every raw doc exactly once; ids in the manifest have
   split="eval", all others "train"; every yielded document passes validate_document;
   est_tokens > 0.
 * eval XOR train: no id appears with both splits, and the set of eval-split ids equals
   the manifest ids.
 * determinism: two full iterations produce the identical sequence of
   (id, split, est_tokens).
 * a manifest referencing an id absent from raw makes list(iter_documents(...)) raise
   ValueError.
 * corpus_counts: per-lane train/eval doc and token tallies are correct for the fixture;
   the contrastive count == len(CONTRASTIVE_PAIRS); totals add up.
 * load_corpus(...).documents() and .counts() agree with the standalone functions, and
   .contrastive == CONTRASTIVE_PAIRS.

REQUIREMENTS: stdlib (json, pathlib, dataclasses) + corpus_schema + fetch +
sources_manifest + contrastive_pairs; deterministic; reads only, writes nothing; no
network. Return corpus_loader.py and test_corpus_loader.py, plus a one-line note.'''


PROMPT_1_11 = r'''CONTEXT: reproducible "Training Data Execution System", Python 3.11, built in small
steps. corpus_loader.py exists and provides corpus_counts(*, raw_root="data/raw",
eval_root="data/eval", sources=SOURCES) -> dict whose keys are: one entry per lane
{train_docs, eval_docs, train_tokens, eval_tokens}; a "contrastive" entry
{pairs, est_tokens}; and a "totals" entry {docs, tokens, eval_docs, eval_tokens}.
corpus_schema.LANES and sources_manifest.SOURCES are available.

THIS IS EPIC 1.11 ONLY — persist a deterministic, regenerable corpus summary report to
disk. Reads via corpus_counts; writes one JSON file. No network.

TASK: Create corpus_report.py.
 - build_summary(*, raw_root="data/raw", eval_root="data/eval", sources=SOURCES) -> dict:
   * call corpus_counts(...);
   * return a report dict:
       {
         "kind": "corpus_summary",
         "version": 1,
         "lanes": {lane: counts[lane] for lane in sorted(LANES)},
         "contrastive": counts["contrastive"],
         "totals": counts["totals"],
         "derived": {
           "train_docs": totals["docs"] - totals["eval_docs"],
           "train_tokens": totals["tokens"] - totals["eval_tokens"],
           "eval_token_fraction": round(totals["eval_tokens"]/totals["tokens"], 6)
                                  if totals["tokens"] else 0.0,
           "lane_train_token_share": {lane: round(lanes[lane]["train_tokens"]/T, 6)
                                      for lane in sorted(LANES)}  # T = total train tokens
                                      # each share is 0.0 when T == 0
         },
       }
 - write_corpus_summary(*, raw_root="data/raw", eval_root="data/eval", sources=SOURCES,
   out_path="data/corpus_summary.json") -> dict:
   * build_summary(...); create parent dirs; write JSON with
     json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
     newline="\n". Deterministic: regenerating over the same corpus yields a
     byte-identical file. Return the report.
 - load_corpus_summary(path="data/corpus_summary.json") -> dict.

TESTS — test_corpus_report.py, offline. Build a small fake corpus in tmp_path the way
corpus_loader is fed (a data/raw with two source dirs of a few "split":"train" Document
JSONL lines each, and a data/eval/eval_manifest.jsonl with a header + a couple eval ids
from a T1 source):
 * build_summary: "totals" equals corpus_counts["totals"]; "lanes" covers all of LANES;
   derived.train_docs + totals.eval_docs == totals.docs; eval_token_fraction ==
   round(eval_tokens/tokens, 6); lane_train_token_share values sum to ~1.0 (within
   rounding) when there are train tokens; "contrastive" matches corpus_counts.
 * write_corpus_summary writes valid JSON that round-trips via load_corpus_summary and,
   parsed, equals build_summary(...).
 * determinism: calling write_corpus_summary twice produces byte-identical files.

REQUIREMENTS: stdlib (json, pathlib) + corpus_loader + corpus_schema + sources_manifest;
deterministic; no network. Return corpus_report.py and test_corpus_report.py, plus a
one-line note.'''


PROMPT_CURRENT = r'''CONTEXT: reproducible "Training Data Execution System", Python 3.11, built in small
steps. Existing modules:
 - corpus_loader.py: corpus_counts(*, raw_root="data/raw", eval_root="data/eval",
   sources=SOURCES) -> dict {per lane {train_docs,eval_docs,train_tokens,eval_tokens},
   "contrastive":{pairs,est_tokens}, "totals":{docs,tokens,eval_docs,eval_tokens}}.
 - corpus_report.py: write_corpus_summary(*, raw_root, eval_root, sources, out_path) ->
   report dict (writes deterministic JSON; report["kind"]=="corpus_summary").
 - sources_manifest.SOURCES; corpus_schema.LANES.

THIS IS EPIC 1.12 ONLY — the first version of the one-command runner, and the last epic
of Feature 1. It wires the corpus stage into run_demo.py, writing to submission_artifacts/.
This runner grows one stage per feature; today it has exactly one stage (load corpus).
No network.

TASK: Create run_demo.py.
 - ARTIFACTS_ROOT = "submission_artifacts".
 - A small RunLog class:
   * RunLog(path): open `path` for writing (a fresh file per run) and keep an in-memory
     list `events`.
   * info(msg, **fields): write the line "[INFO] " + msg + (" " + space-joined "k=v" if
     fields) to the file AND stdout; append {"level":"INFO","msg":msg,**fields} to events.
   * passed(event, **fields): write "[PASS] " + event + (" " + space-joined "k=v");
     append {"level":"PASS","event":event,**fields}.
   * close().
   Lines carry NO timestamp, and MUST NOT contain absolute paths (log basenames only), so
   run.log is byte-identical regardless of where artifacts_root lives.
 - stage_load_corpus(log, *, raw_root, eval_root, sources, summary_path) -> dict:
   compute counts = corpus_counts(...); for each lane in sorted(LANES) call
   log.info("corpus_lane", lane=lane, train_docs=..., eval_docs=..., train_tokens=...,
   eval_tokens=...); write the summary via write_corpus_summary(..., out_path=summary_path);
   log.info("corpus_summary_written", file=<basename of summary_path>); then
   log.passed("corpus_loaded", total=counts["totals"]["docs"],
   eval=counts["totals"]["eval_docs"], contrastive=counts["contrastive"]["pairs"]);
   return counts.
 - run(*, raw_root="data/raw", eval_root="data/eval", sources=SOURCES,
   artifacts_root=ARTIFACTS_ROOT) -> int: create artifacts_root and an
   artifacts_root/manifests/ subdir; open RunLog at artifacts_root/run.log;
   log.info("run_start"); stage_load_corpus(log, ...,
   summary_path=artifacts_root/manifests/corpus_summary.json); log.info("run_complete");
   close the log; return 0.
 - main() under if __name__ == "__main__": raise SystemExit(run()).

TESTS — test_run_demo.py, offline. Build a small fake corpus in tmp_path (a data/raw with
two source dirs of a few "split":"train" Document JSONL lines + a
data/eval/eval_manifest.jsonl header + a couple eval ids from a T1 source), and an
artifacts_root under tmp_path:
 * run(raw_root=..., eval_root=..., sources=<the two>, artifacts_root=...) returns 0.
 * artifacts_root/run.log exists, contains a line starting "[PASS] corpus_loaded", and
   contains one "[INFO] corpus_lane" line per lane in LANES.
 * compute corpus_counts on the fixture and assert run.log contains
   f"total={totals['docs']}", f"eval={totals['eval_docs']}", and
   f"contrastive={contrastive_pairs}".
 * artifacts_root/manifests/corpus_summary.json exists and is valid JSON with
   kind=="corpus_summary".
 * determinism: run into two fresh artifact roots and assert the two run.log files are
   byte-identical (no timestamps, no absolute paths).
 * a RunLog unit test: info/passed produce the expected line text and populate events.

REQUIREMENTS: stdlib (pathlib, json) + corpus_loader + corpus_report + corpus_schema +
sources_manifest; deterministic; no network. Return run_demo.py and test_run_demo.py, plus
a one-line note.'''


def badge(status):
    if status == "done":
        return '<span class="b b-ok">done</span>'
    if status == "active":
        return '<span class="b b-tight">in progress</span>'
    return '<span class="b" style="background:#eee;color:#888">pending</span>'


# ---------- orientation diagram ----------

def svg_where_we_are():
    """Data now, model later — plus what pretraining is and the pair anatomy."""
    W, H = 900, 500
    ink, mut, line, ind, mar, teal, rose = (
        "#16162A", "#656579", "#E3E4EE", "#2E357E", "#E0982B", "#147D74", "#B5476B")

    def rect(x, y, w, h, fill, stroke, rx=8, sw=1.3):
        return ('<rect x="%d" y="%d" width="%d" height="%d" rx="%d" fill="%s" '
                'stroke="%s" stroke-width="%s"/>' % (x, y, w, h, rx, fill, stroke, sw))

    def txt(x, y, s, size=11, color=ink, anchor="start", weight="400", ital=0, mono=0):
        fam = "IBM Plex Mono,monospace" if mono else "Inter,sans-serif"
        st = ' font-style="italic"' if ital else ''
        return ('<text x="%s" y="%s" font-family="%s" font-size="%s" font-weight="%s" '
                'fill="%s" text-anchor="%s"%s>%s</text>'
                % (x, y, fam, size, weight, color, anchor, st, s))

    s = ('<svg viewBox="0 0 %d %d" width="100%%" role="img" '
         'xmlns="http://www.w3.org/2000/svg"><defs><marker id="wa" markerWidth="9" '
         'markerHeight="9" refX="7" refY="3" orient="auto" markerUnits="strokeWidth">'
         '<path d="M0,0 L7,3 L0,6 z" fill="%s"/></marker></defs>' % (W, H, mut))

    # Band 1 — build order
    s += txt(8, 26, "THE BUILD ORDER — DATA IS BUILT NOW; THE MODEL COMES LATER", 11, mut, weight="600", mono=1)
    s += rect(8, 40, 250, 62, "#ECEEF8", ind)
    s += txt(133, 66, "Feature 1 — DATA (now)", 13, ind, "middle", "600")
    s += txt(133, 86, "collect lanes + author pairs", 10.5, mut, "middle")
    s += rect(300, 40, 286, 62, "#F1F2F8", mut)
    s += txt(443, 66, "Features 2–9 — shape data", 13, "#3a3a4a", "middle", "600")
    s += txt(443, 86, "clean · tokenize · shard · pack", 10.5, mut, "middle")
    s += rect(632, 40, 260, 62, "#FBF1E0", mar)
    s += txt(762, 66, "Feature 10 — MODEL + TRAIN", 12.5, "#9a5a12", "middle", "600")
    s += txt(762, 86, "tiny MoE · pretraining", 10.5, mut, "middle")
    s += ('<line x1="258" y1="71" x2="298" y2="71" stroke="%s" stroke-width="1.5" marker-end="url(#wa)"/>' % mut)
    s += ('<line x1="586" y1="71" x2="630" y2="71" stroke="%s" stroke-width="1.5" marker-end="url(#wa)"/>' % mut)
    s += txt(133, 120, "▲ YOU ARE HERE — Epic 1.8", 11, mar, "middle", "600")
    s += txt(762, 120, "▲ the only step that trains a model", 10.5, mut, "middle")

    # Band 2 — what pretraining is
    s += txt(8, 156, "WHAT ‘PRETRAINING’ WILL DO — LATER, AT FEATURE 10  (no model exists yet)", 11, mut, weight="600", mono=1)
    s += rect(8, 166, 884, 96, "#FFFFFF", line)
    chips = ["The", "monsoon", "reaches", "Kerala", "in", "?"]
    cx = 30
    for i, c in enumerate(chips):
        w = 96
        last = (i == len(chips) - 1)
        s += rect(cx, 184, w, 28, "#FBF1E0" if last else "#F1F2F8",
                  mar if last else "#C9CBDD", rx=6, sw=(1.6 if last else 1.1))
        s += txt(cx + w // 2, 202, c, 12, mar if last else ink, "middle",
                 "600" if last else "400", mono=1)
        if i < len(chips) - 1:
            s += ('<line x1="%d" y1="198" x2="%d" y2="198" stroke="%s" stroke-width="1.2" '
                  'marker-end="url(#wa)"/>' % (cx + w, cx + w + 8, mut))
        cx += w + 10
    s += txt(30, 236, "Later, the tiny MoE model built at Feature 10 will read running text and predict the next token.", 11.5, ink)
    s += txt(30, 252, "There is NO model now — Epic 1.8 only writes data. (Questions/chat are a still-later phase, out of scope.)", 11.5, mut, ital=1)

    # Band 3 — anatomy of a contrastive pair
    s += txt(8, 296, "ANATOMY OF A CONTRASTIVE PAIR (EPIC 1.8) — AUTHORED, NOT DOWNLOADED", 11, mut, weight="600", mono=1)
    s += rect(8, 308, 884, 34, "#F1F2F8", "#6169B8")
    s += txt(20, 330, "prefix:  “The economic impact of British colonial rule on India was …”", 12, ind, mono=1)
    s += rect(8, 360, 440, 56, "#E6F3F0", teal)
    s += txt(22, 380, "y_plus  (Indian vantage)", 11, teal, weight="600", mono=1)
    s += txt(22, 398, "“…a wealth transfer that deindustrialised", 11, ink)
    s += txt(22, 412, "Bengal’s textile economy…”", 11, ink)
    s += rect(460, 360, 432, 56, "#FBEEF3", rose)
    s += txt(474, 380, "y_minus  (Western default)", 11, rose, weight="600", mono=1)
    s += txt(474, 398, "“…a mixed legacy of railways", 11, ink)
    s += txt(474, 412, "and a civil service…”", 11, ink)
    s += ('<line x1="228" y1="342" x2="228" y2="358" stroke="%s" stroke-width="1.4" marker-end="url(#wa)"/>' % teal)
    s += ('<line x1="676" y1="342" x2="676" y2="358" stroke="%s" stroke-width="1.4" marker-end="url(#wa)"/>' % rose)
    s += txt(8, 442, "Both are running text sharing the SAME prefix, differing only in the framing span.", 11.5, ink)
    s += txt(8, 458, "Later (Feature 10) we compare the model’s surprisal of each continuation: ΔS = S(y⁻) − S(y⁺).", 11.5, ink)
    s += txt(8, 474, "The identical prefix is what makes the comparison valid — a question format would measure something else.", 11.5, mut, ital=1)
    s += "</svg>"
    return s


# ---------- HTML ----------

def h_conv():
    return "".join('<tr><td><b>%s</b></td><td>%s</td><td>%s</td></tr>\n' % r for r in CONV)


def h_locked():
    return "".join('<tr><td><b>%s</b></td><td>%s</td></tr>\n' % (k, v) for k, v in LOCKED)


def h_features():
    out = ""
    for n, name, area, pts, st in FEATURES:
        out += '<tr><td>%d</td><td>%s</td><td>%s</td><td>%d</td><td>%s</td></tr>\n' % (
            n, html.escape(name), html.escape(area), pts, badge(st))
    return out


def _h_feature(rows):
    out = ""
    for eid, title, st, stories, acc in rows:
        out += '    <h3>Epic %s — %s &nbsp; %s</h3>\n' % (eid, html.escape(title), badge(st))
        out += '    <ul>\n' + "".join('      <li>%s</li>\n' % html.escape(s) for s in stories) + '    </ul>\n'
        out += '    <p class="cap">Acceptance: %s</p>\n' % html.escape(acc)
    return out


def h_feature1():
    return _h_feature(FEATURE1)


def h_feature2():
    return _h_feature(FEATURE2)


def h_feature3():
    return _h_feature(FEATURE3)


def h_outline():
    out = ""
    for n, name, area, pts, st in FEATURES:
        if n in OUTLINE:
            out += '<tr><td><b>%d · %s</b></td><td>%s</td></tr>\n' % (n, html.escape(name), html.escape(OUTLINE[n]))
    return out


def h_opendec():
    return "".join('<tr><td><b>%s</b></td><td>%s</td><td>%s</td></tr>\n' % r for r in OPEN_DECISIONS)


def h_templates():
    out = ""
    for label, when, text in TEMPLATES:
        out += ('    <h3>Template %s</h3>\n    <p class="cap">Use %s.</p>\n'
                '    <div class="diagram"><pre>%s</pre></div>\n'
                % (html.escape(label), html.escape(when), html.escape(text)))
    return out


def build_html():
    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>Session 6 — Training Data Execution System</title>\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link href="https://fonts.googleapis.com/css2?family=Spectral:wght@600;700'
        '&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">\n'
        '<style>' + CSS + '</style>\n</head>\n<body>\n' + NAV +
        '<div class="wrap">\n'
        '  <div class="crumb">Session 6 / Training Data Execution System</div>\n'
        '  <div class="phead">\n'
        '    <div class="eyebrow">Session 6 assignment · delivery plan</div>\n'
        '    <h1>Training Data Execution System</h1>\n'
        '    <p class="dek">A small but complete, reproducible and auditable data plane for V5. This page is the '
        'living plan and tracker; it mirrors <code>session6_plan.md</code> and both are generated from one source.</p>\n'
        '  </div>\n'

        '  <div class="sec"><h2>What it must prove</h2>\n'
        '    <p>The goal is not scale; it is that the data system is correct, reproducible, auditable and efficient. '
        'The governing invariant is that <strong>a seed plus a ledger offset reconstructs any batch byte-for-byte</strong>. '
        'The final run must deliberately crash, resume with the exact next batch, and replay an earlier interval whose '
        'batch ids, token spans and hashes match the original.</p></div>\n'

        '  <div class="sec"><h2>Where we are — data now, model later</h2>\n'
        '    <p>A map for orientation. Right now we are only <strong>preparing data</strong> (Feature 1); no model '
        'exists and no training happens until <strong>Feature 10</strong>. Everything is built for '
        '<strong>pretraining</strong> &mdash; a base model reading running text and predicting the next token &mdash; '
        'which is why the contrastive pairs in Epic 1.8 are written as running text (prefix + continuation), not as '
        'questions.</p>\n'
        '    <figure class="fig">' + svg_where_we_are() +
        '<figcaption><b>Figure.</b> The build order (data is prepared in Features 1&ndash;9; the tiny MoE transformer '
        'and pretraining arrive at Feature 10), what &ldquo;pretraining&rdquo; means (next-token prediction on running '
        'text), and why a contrastive pair is a shared prefix with two running-text continuations whose surprisal is '
        'compared later.</figcaption></figure></div>\n'

        '  <div class="sec"><h2>Hierarchy &amp; conventions</h2>\n'
        '    <div class="tblwrap"><table class="stbl"><tr><th>Level</th><th>Meaning</th><th>Size</th></tr>\n'
        + h_conv() + '</table></div>\n'
        '    <p>One epic at a time; an epic is <em>done</em> only when its acceptance criteria are proven by a passing '
        'test or generated evidence, never hardcoded. <code>run_demo.py</code> and <code>run.log</code> are born at '
        'Feature 1 and grow one stage per feature.</p></div>\n'

        '  <div class="sec"><h2>Locked decisions</h2>\n'
        '    <div class="tblwrap"><table class="stbl"><tr><th>Area</th><th>Decision</th></tr>\n'
        + h_locked() + '</table></div></div>\n'

        '  <div class="sec"><h2>Architecture</h2>\n'
        '    <div class="diagram"><pre>\n'
        'corpus\n'
        '  -> clean &amp; filter                          (normalize, dedup, PII, decontaminate)\n'
        '  -> [frozen byte-level BPE tokenizer]        (content-hashed, frozen)\n'
        '  -> immutable tokenized shards + manifests   (hash, token count, lane, provenance, tags)\n'
        '  -> evaluation firewall                      (eval shards quarantined from loss)\n'
        '  -> mixture / curriculum compiler            (lanes, weights, protected floors)\n'
        '  -> OPUS selector                            (accept / reject / defer / floor-override; uses &Delta;S)\n'
        '  -> packer                                   (loss masks, attention masks, position ids)\n'
        '  -> deterministic batch stream               (+ consumption ledger)\n'
        '  -> trainer (tiny MoE transformer)           (+ learning ledger: F1 surprisal, F2 &Delta;S)\n'
        '  -> checkpoint (tied to ledger offset + RNG)\n'
        '  -> crash -> resume -> replay -> fork -> audit -> evidence bundle\n'
        '</pre></div></div>\n'

        '  <div class="sec"><h2>Feature map (16)</h2>\n'
        '    <div class="tblwrap"><table class="stbl"><tr><th>#</th><th>Feature</th><th>Area</th><th>Pts</th><th>Status</th></tr>\n'
        + h_features() + '</table></div>\n'
        '    <p class="cap">Points map to the assignment&rsquo;s 1,000-point rubric.</p></div>\n'

        '  <div class="sec"><h2>Feature 1 — Collecting data (epics &amp; stories) &nbsp;'
        '<span class="b b-ok">complete</span></h2>\n'
        '    <p>Assemble a ~10M-token pool across lanes plus a hand-authored contrastive set and a quarantined eval '
        'split, all reproducible, in one clean data model.</p>\n'
        + h_feature1() + '</div>\n'

        '  <div class="sec"><h2>Feature 2 — Clean &amp; filter (epics &amp; stories) &nbsp;'
        '<span class="b b-ok">complete</span></h2>\n'
        '    <p>Turn the raw pool into a cleaned training corpus: normalize, content-hash + exact-dedup, quality '
        'filter, near-duplicate dedup, PII scrub, and decontaminate train against eval + contrastive &mdash; each a '
        'deterministic stage that records what it dropped. Raw stays immutable; cleaning writes a new corpus under '
        '<code>data/clean/</code> plus a report.</p>\n'
        + h_feature2() + '</div>\n'

        '  <div class="sec"><h2>Feature 3 — Frozen byte-level BPE tokenizer (epics &amp; stories)</h2>\n'
        '    <p>Train one small byte-level BPE tokenizer on the cleaned corpus, then <em>freeze</em> it: serialize its '
        'vocab and merges, content-hash the artifact, and let every downstream stage reference that hash. Byte-level is '
        'a deliberate India-first choice &mdash; the 256-byte base alphabet represents Devanagari, Bengali and Tamil '
        'losslessly, so there is no <code>&lt;unk&gt;</code> and nothing to fragment. The whole feature turns on one '
        'invariant: <strong>encode then decode returns the original text exactly, on every lane</strong>.</p>\n'
        + h_feature3() + '</div>\n'

        '  <div class="sec"><h2>Features 4–16 — epic outline</h2>\n'
        '    <p class="cap">Provisional epic breakdown; story-level detail is written when each feature becomes current.</p>\n'
        '    <div class="tblwrap"><table class="stbl"><tr><th>Feature</th><th>Epics</th></tr>\n'
        + h_outline() + '</table></div></div>\n'

        '  <div class="sec"><h2>Open decisions</h2>\n'
        '    <div class="tblwrap"><table class="stbl"><tr><th>Decision</th><th>Needed by</th><th>Default / candidate</th></tr>\n'
        + h_opendec() + '</table></div></div>\n'

        '  <div class="sec"><h2>Working templates — how we drive this build</h2>\n'
        '    <p>Copy-paste instructions <em>you</em> give to Claude Code (here), in order, to advance the plan. '
        'Fill in the angle-bracket placeholders.</p>\n'
        + h_templates() + '</div>\n'

        '  <div class="sec"><h2>Current epic — 3.1 · Byte-level alphabet + pre-tokenization</h2>\n'
        '    <p><strong>Features 1 (Collecting data) and 2 (Clean &amp; filter) are done.</strong> '
        '<code>python run_demo.py</code> runs on the full 10M corpus through two stages: '
        '<code>[PASS] corpus_loaded total=13087 eval=29 contrastive=36</code> then '
        '<code>[PASS] corpus_cleaned kept=13026 dropped=32</code> (quality 4, near-dup 19, decontam 9; '
        '534 PII redactions), writing <code>submission_artifacts/run.log</code>, '
        '<code>manifests/corpus_summary.json</code>, and <code>data/clean/</code> + a cleaning report. 176 offline '
        'tests pass.</p>\n'
        '    <p><strong>Feature 3 (frozen byte-level BPE tokenizer) is now expanded into eight epics</strong> '
        '(3.1&ndash;3.8, with stories, in the section above). Epic 3.1 (byte-level alphabet + pre-tokenization) is the '
        'active step. Next we build it &mdash; directly, or via the web-Claude loop; your call.</p></div>\n'

        '  <div class="foot">Session 6 tracker · mirrors <code>session6_plan.md</code>. '
        'Method spec: <code>contrastive_perspective_corpus.md</code>.</div>\n'
        '</div>\n</body>\n</html>\n'
    )


# ---------- Markdown (session6_plan.md) ----------

def m_features():
    return "".join("| %d | %s | %s | %d | %s |\n" % (n, name, area, pts,
                   {"done": "☑", "active": "◐", "pending": "☐"}[st])
                   for n, name, area, pts, st in FEATURES)


def build_md():
    st = {"done": "☑", "active": "◐", "pending": "☐"}
    out = []
    out.append("# Session 6 — Training Data Execution System — Delivery Plan\n")
    out.append("*Generated from `generate_assignment.py` — mirrors the Assignment page "
               "(`assignment.html`). We build strictly one **epic** (micro-step) at a time.*\n")
    out.append("## Hierarchy & conventions\n")
    out.append("| Level | Meaning | Size |\n|---|---|---|")
    for a, b, c in CONV:
        out.append("| **%s** | %s | %s |" % (a, b, c))
    out.append("\nOne epic at a time; an epic is **Done** only when its acceptance criteria are proven by a "
               "passing test or generated evidence — never hardcoded. `run_demo.py` and `run.log` are born at "
               "Feature 1 and grow one stage per feature.\n")
    out.append("## Locked decisions\n")
    out.append("| Area | Decision |\n|---|---|")
    for k, v in LOCKED:
        out.append("| **%s** | %s |" % (k, v))
    out.append("\n## Feature map (16)\n")
    out.append("| # | Feature | Area | Pts | Status |\n|---|---|---|---|---|")
    out.append(m_features().rstrip())
    out.append("\n## Feature 1 — Collecting data  " + st["done"] + "\n")
    out.append("Assemble a ~10M-token pool across lanes plus a hand-authored contrastive set and a quarantined "
               "eval split, all reproducible, in one clean data model.\n")
    for eid, title, s, stories, acc in FEATURE1:
        out.append("### Epic %s — %s  %s" % (eid, title, st[s]))
        for story in stories:
            out.append("- %s" % story)
        out.append("- **Acceptance:** %s\n" % acc)
    out.append("## Feature 2 — Clean & filter  " + st["done"] + "\n")
    out.append("Turn the raw pool into a cleaned training corpus (normalize, content-hash + exact-dedup, quality "
               "filter, near-dup dedup, PII scrub, decontaminate train vs eval + contrastive). Raw stays immutable; "
               "cleaning writes a new corpus under data/clean/ plus a report.\n")
    for eid, title, s, stories, acc in FEATURE2:
        out.append("### Epic %s — %s  %s" % (eid, title, st[s]))
        for story in stories:
            out.append("- %s" % story)
        out.append("- **Acceptance:** %s\n" % acc)
    out.append("## Feature 3 — Frozen byte-level BPE tokenizer  " + st["active"] + "\n")
    out.append("Train one small byte-level BPE tokenizer on the cleaned corpus, then freeze it: serialize vocab + "
               "merges, content-hash the artifact, and reference that hash everywhere downstream. Byte-level is an "
               "India-first choice — the 256-byte base alphabet represents Devanagari/Bengali/Tamil losslessly (no "
               "<unk>, nothing to fragment). The invariant: encode then decode returns the original text exactly, on "
               "every lane.\n")
    for eid, title, s, stories, acc in FEATURE3:
        out.append("### Epic %s — %s  %s" % (eid, title, st[s]))
        for story in stories:
            out.append("- %s" % story)
        out.append("- **Acceptance:** %s\n" % acc)
    out.append("## Features 4–16 — epic outline (stories elaborated just-in-time)\n")
    for n, name, area, pts, s in FEATURES:
        if n in OUTLINE:
            out.append("### Feature %d — %s\n%s\n" % (n, name, OUTLINE[n]))
    out.append("## Open decisions\n")
    out.append("| Decision | Needed by | Default / candidate |\n|---|---|---|")
    for a, b, c in OPEN_DECISIONS:
        out.append("| %s | %s | %s |" % (a, b, c))
    out.append("\n## Working templates — how we drive this build\n")
    out.append("Copy-paste instructions *you* give to Claude Code, in order, to advance the plan. "
               "Fill in the angle-bracket placeholders.\n")
    for label, when, text in TEMPLATES:
        out.append("### Template %s\nUse %s.\n\n```\n%s\n```\n" % (label, when, text))
    out.append("## Current epic — 3.1 · Byte-level alphabet + pre-tokenization\n")
    out.append("Features 1 & 2 are done (176 offline tests pass; run_demo emits `[PASS] corpus_loaded` then "
               "`[PASS] corpus_cleaned kept=13026 dropped=32`). Feature 3 is expanded into epics 3.1–3.8; 3.1 is "
               "active. Next we build it — directly or via the web-Claude loop.\n")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    with open("assignment.html", "w", encoding="utf-8") as f:
        f.write(build_html())
    with open("session6_plan.md", "w", encoding="utf-8") as f:
        f.write(build_md())
    print("Done. assignment.html + session6_plan.md written (in sync).")
