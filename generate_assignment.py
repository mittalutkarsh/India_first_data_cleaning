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
    (1, "Collecting data", "Tokenizer integrity / data", 100, "active"),
    (2, "Clean & filter", "Shards/manifests", 100, "pending"),
    (3, "Frozen BPE tokenizer", "Tokenizer integrity", 100, "pending"),
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
    ("1.4–1.7", "Fetch code / math / indic / multilingual", "active", [
        "Same shape as 1.3, one lane per epic.",
    ], "per-lane caps respected; file hashes recorded."),
    ("1.8", "Author contrastive pairs", "pending", [
        "~30–50 hand-authored ContrastivePairs on contested topics; factual y_plus; chauvinism none.",
    ], "all validate; committed as source, not downloaded."),
    ("1.9", "Eval held-out split", "pending", [
        "Carve a ~1–2% quarantined slice, mark split=eval, keep provenance.",
    ], "eval docs disjoint from train; recorded separately."),
    ("1.10", "Corpus loader", "pending", [
        "Iterate all raw files → Documents in the schema; attach a byte→token estimate.",
    ], "loads deterministically; counts stable across runs."),
    ("1.11", "Corpus summary report", "pending", [
        "Write data/corpus_summary.json (docs + est. tokens per lane/split, contrastive count).",
    ], "report regenerates identically; totals ≈ 10M."),
    ("1.12", "Wire load_corpus into run_demo.py", "pending", [
        "Minimal run_demo.py creates submission_artifacts/run.log, runs load_corpus, logs per-lane [INFO] lines and a final [PASS] corpus_loaded total=N eval=M contrastive=K; end-to-end test.",
    ], "python run_demo.py runs clean; test asserts the PASS event."),
]

# feature num -> provisional epic outline
OUTLINE = {
    2: "2.1 canonical normalization (Unicode NFC, whitespace, strip control chars) · 2.2 content-hasher (sha256 over canonical bytes) — born here — + exact-duplicate removal · 2.3 quality filter (min length, symbol/word ratio, repetition heuristics) · 2.4 near-duplicate dedup (MinHash / LSH) · 2.5 PII scrub (emails, phone numbers → redact) · 2.6 decontamination (n-gram overlap of train vs eval + contrastive; drop leaked docs) · 2.7 cleaning report (per-stage drop counts) + test",
    3: "3.1 BPE trainer on a pool sample · 3.2 freeze (serialize vocab+merges) + tokenizer content hash · 3.3 encode/decode with round-trip test · 3.4 tokenizer manifest (hash, vocab size, special tokens) + test",
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

PROMPT_CURRENT = r'''CONTEXT: I am building a small, reproducible "Training Data Execution System" for LLM
pretraining (a course assignment), Python 3.11, built in very small steps. Two modules
already exist in the repo:
  * corpus_schema.py — defines Document (fields: id, lane, provenance_tier, split, source,
    text) and validate_document(doc).
  * sources_manifest.py — defines LaneSource, SOURCES, and validate_sources(sources). One
    entry has source_id="web-fineweb", lane="web", dataset="HuggingFaceFW/fineweb",
    config="sample-10BT", revision="", provenance_tier="T2", target_tokens=4_000_000.
THIS IS EPIC 1.3 ONLY — the first REAL fetch, for a SINGLE source (web-fineweb). Later
epics repeat this for the other lanes; do NOT fetch them now.

DESIGN FOR OFFLINE TESTABILITY (important): the core write/cap/hash/log logic must run
with NO network, by injecting a document iterator. Only the real run touches HuggingFace.

TASK: Create fetch.py.
 - estimate_tokens(text: str) -> int: max(1, len(text.encode("utf-8")) // 4). A
   pre-tokenizer, byte-based token estimate (no tokenizer exists yet).
 - fetch_source(source, *, out_root="data/raw", doc_iter=None, force=False) -> dict.
   Behaviour, in order:
   1. Caching: if force is False AND out_root/<source_id>/documents.jsonl already exists
      AND fetch_log.jsonl already has a record for this source_id, then SKIP entirely
      (no download, no consuming doc_iter) and return the existing summary with
      cached=True.
   2. Resolve revision: if source.revision != "" use it as-is; else (only when doc_iter is
      None) resolve the dataset's current commit sha via huggingface_hub
      (HfApi().dataset_info(source.dataset).sha) and use that. Record the resolved value.
   3. Obtain documents: if doc_iter is not None, iterate it (each item is a dict with a
      "text" key, or a plain str) — this is how tests inject data offline. Otherwise build
      a streaming iterator with the datasets library:
      load_dataset(source.dataset, name=(source.config or None), split="train",
      streaming=True, revision=<resolved>), yielding each record's "text".
   4. For each text, in order, with running index i: build a Document(
      id=f"{source.source_id}-{i:07d}", lane=source.lane,
      provenance_tier=source.provenance_tier, split="train",
      source=f"{source.dataset}@{revision}#{source.config}", text=text); call
      validate_document on it; write its dict as ONE json line to
      out_root/<source_id>/documents.jsonl. Accumulate estimate_tokens(text); STOP as soon
      as the cumulative estimate >= source.target_tokens.
   5. Compute sha256 of the finished documents.jsonl. Append one json line to
      out_root/fetch_log.jsonl: {source_id, dataset, config, revision, path, bytes,
      sha256, doc_count, est_tokens, target_tokens}.
   6. Return {source_id, revision, path, bytes, sha256, doc_count, est_tokens,
      cached: False}.
 - main() under if __name__ == "__main__": load SOURCES, validate_sources(SOURCES), pick
   the source_id="web-fineweb" entry, and call fetch_source on it (the real download).

REPRODUCIBILITY: a pinned revision + the deterministic take-order + the token cap make
documents.jsonl byte-identical across runs, so its sha256 is stable; a second run is a
cached no-op.

TESTS — test_fetch.py, MUST run offline (no network, no datasets/huggingface_hub import at
test time). Use pytest tmp_path for out_root, a fake doc_iter (a fixed list of ~50 short
dicts like {"text": "..."}), and pass a web-fineweb-like LaneSource via
dataclasses.replace(...) with a small target_tokens (e.g. 200) and revision="pinned-test".
Assert:
   * estimate_tokens matches the bytes//4 formula on a known string and is monotonic.
   * fetch_source caps correctly (stops at/just past target; not all 50 docs consumed).
   * documents.jsonl exists and every line parses to a dict that constructs a Document
     which validate_document accepts.
   * fetch_log.jsonl has one record whose sha256 and byte size match the file when
     recomputed.
   * calling fetch_source a second time with force=False returns cached=True and leaves
     the file unchanged.

REQUIREMENTS: import Document, validate_document from corpus_schema and SOURCES,
validate_sources from sources_manifest. Use hashlib (sha256), json, pathlib. The datasets
and huggingface_hub libraries are used ONLY on the real path (import them lazily inside the
doc_iter-is-None branch so tests need neither). Deterministic JSON: sort_keys=True,
ensure_ascii=False, separators=(",",":"), one object per line. Add datasets and
huggingface_hub to requirements.txt. Return fetch.py, test_fetch.py, the requirements.txt
additions, and a one-line note on how reproducibility is achieved.'''


def badge(status):
    if status == "done":
        return '<span class="b b-ok">done</span>'
    if status == "active":
        return '<span class="b b-tight">in progress</span>'
    return '<span class="b" style="background:#eee;color:#888">pending</span>'


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


def h_feature1():
    out = ""
    for eid, title, st, stories, acc in FEATURE1:
        out += '    <h3>Epic %s — %s &nbsp; %s</h3>\n' % (eid, title, badge(st))
        out += '    <ul>\n' + "".join('      <li>%s</li>\n' % s for s in stories) + '    </ul>\n'
        out += '    <p class="cap">Acceptance: %s</p>\n' % acc
    return out


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

        '  <div class="sec"><h2>Feature 1 — Collecting data (epics &amp; stories)</h2>\n'
        '    <p>Assemble a ~10M-token pool across lanes plus a hand-authored contrastive set and a quarantined eval '
        'split, all reproducible, in one clean data model.</p>\n'
        + h_feature1() + '</div>\n'

        '  <div class="sec"><h2>Features 2–16 — epic outline</h2>\n'
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

        '  <div class="sec"><h2>Current epic — 1.4–1.7 · Fetch the remaining lanes</h2>\n'
        '    <p><strong>Epics 1.1–1.3 done and pushed</strong> &mdash; 46 offline tests pass, and the live FineWeb '
        'fetch is verified (revision pinned, sha256 recorded). The fetch pattern is now proven on one lane; 1.4–1.7 '
        'reuse <code>fetch_source</code> for code, math, indic, and multilingual &mdash; likely no new code, just '
        'fetching each remaining source from the manifest (and confirming the code lane&rsquo;s permissive+ungated '
        'source resolves). The next prompt is prepared on request.</p>\n'
        '    <p class="cap">Reference &mdash; the completed Epic 1.3 prompt:</p>\n'
        '    <div class="diagram"><pre>' + html.escape(PROMPT_CURRENT) + '</pre></div></div>\n'

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
    out.append("\n## Feature 1 — Collecting data  " + st["active"] + "\n")
    out.append("Assemble a ~10M-token pool across lanes plus a hand-authored contrastive set and a quarantined "
               "eval split, all reproducible, in one clean data model.\n")
    for eid, title, s, stories, acc in FEATURE1:
        out.append("### Epic %s — %s  %s" % (eid, title, st[s]))
        for story in stories:
            out.append("- %s" % story)
        out.append("- **Acceptance:** %s\n" % acc)
    out.append("## Features 2–16 — epic outline (stories elaborated just-in-time)\n")
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
    out.append("## Current epic — 1.1 · Corpus data model\n")
    out.append("Prompt (paste into web Claude) is on the Assignment page and returns `corpus_schema.py` + its test.\n")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    with open("assignment.html", "w", encoding="utf-8") as f:
        f.write(build_html())
    with open("session6_plan.md", "w", encoding="utf-8") as f:
        f.write(build_md())
    print("Done. assignment.html + session6_plan.md written (in sync).")
