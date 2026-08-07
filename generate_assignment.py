"""Generate assignment.html — the living tracker for the Session 6
Training Data Execution System. Reuses the house CSS from the playbook
generator. Updated step by step as each piece is integrated and verified."""
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

# n, title, area, points, status (done | active | pending)
STEPS = [
    (0, "Scaffold — repo layout, config, deterministic RNG + hashing, run.log logger, run_demo.py skeleton", "End-to-end", 150, "active"),
    (1, "Tiny corpus (multiple lanes + eval set + contrastive pairs) + frozen BPE tokenizer with content hash", "Tokenizer integrity", 100, "pending"),
    (2, "Tokenize → immutable shards + manifests (content hash, token count, lane, provenance, chauvinism tag)", "Shards/manifests", 100, "pending"),
    (3, "Evaluation / validation firewall — eval shards can never enter a loss-bearing batch", "Firewall", 50, "pending"),
    (4, "Mixture schedule — curriculum stages, lane weights, protected floors (planned shares)", "Mixture", 150, "pending"),
    (5, "OPUS selector — accept / reject / defer + protected-floor override; ΔS surprisal as a selection signal", "Mixture/OPUS", 150, "pending"),
    (6, "Packer — per-type packing policies (incl. contrastive pairs), loss + attention masks, position ids", "Packing/masks", 150, "pending"),
    (7, "Deterministic batch stream + consumption ledger (batch id, token spans, shard offsets, hashes)", "Ledgers", 150, "pending"),
    (8, "Trainer (tiny MoE transformer) + learning ledger + F1 per-token surprisal + F2 ΔS per contrastive pair", "Ledgers", 150, "pending"),
    (9, "Checkpoints tied to ledger offset + RNG state", "Checkpoint", 150, "pending"),
    (10, "Deliberate crash → resume; prove the next batch is exactly the expected batch (no skip/repeat)", "Checkpoint", 150, "pending"),
    (11, "Replay an earlier interval; prove batch ids / token spans / hashes match the original run", "Checkpoint", 150, "pending"),
    (12, "Fork from an earlier checkpoint (branch)", "Checkpoint", 150, "pending"),
    (13, "Throughput + packing efficiency → performance.json", "Throughput", 50, "pending"),
    (14, "Audit + evidence bundle — evidence.json / evidence.md generated from real artifacts", "Evidence", 50, "pending"),
    (15, "Invariant tests + README + one-command run_demo.py wiring", "Tests/docs", 50, "pending"),
]

DECISIONS = [
    ("Stack", "Python 3.11 + PyTorch on CPU, determinism pinned (fixed seeds, deterministic algorithms, single thread)."),
    ("Model", "Tiny Mixture-of-Experts transformer, built as a pluggable module at Step 8 (after the data plane is proven)."),
    ("Tokenizer", "Self-contained byte-level BPE, trained once on the toy corpus then frozen — vocab + merges committed and content-hashed."),
    ("Method", "Contrastive perspective lane (y+/y−) + F1/F2 surprisal in the learning ledger + ΔS as an OPUS signal. F3–F7 geometry kept as a documented hook (see contrastive_perspective_corpus.md)."),
    ("Repo", "New standalone GitHub repository (the submission), separate from this proposal site. This page is the tracker; the code lives in the submission repo."),
]

PROMPT_STEP0 = r'''CONTEXT
I am building a "Training Data Execution System" — a reproducible, auditable data plane
for LLM pretraining — as a course assignment. It must be correct, reproducible, and
auditable, and run with one command. Stack: Python 3.11, PyTorch on CPU with determinism
pinned, NumPy allowed. It is a new standalone repo. The full pipeline (built over later
steps, NOT now) is:

  corpus -> frozen byte-level BPE tokenizer -> immutable tokenized shards + manifests
  -> evaluation firewall -> mixture/curriculum compiler (lanes, protected floors)
  -> OPUS selector (accept/reject/defer + floor override) -> packer (loss & attention
  masks, position ids) -> deterministic batch stream + consumption ledger
  -> trainer (tiny MoE transformer) + learning ledger (per-token loss / surprisal)
  -> checkpoints tied to ledger offset -> crash -> resume -> replay -> fork -> audit
  -> evidence bundle.

The final demo must deliberately crash, resume with the EXACT next batch (no skip or
repeat), and replay an earlier interval whose batch ids, token spans, and hashes match
the original run. Everything must be reconstructible from a seed + a ledger offset.

SCOPE OF THIS PROMPT — STEP 0 ONLY: the project scaffold and the determinism / hashing /
logging foundation. Do NOT implement tokenization, packing, training, etc. Only the
skeleton the later steps build on.

PRODUCE
1. A repo file tree.
2. Full code for these foundation modules:
   - config.py: a frozen dataclass Config (global seed, artifact-root path, and
     placeholders for budget, lane weights, protected floors). Loadable from a JSON dict.
     Include a method returning a canonical, content-hashable representation.
   - hashing.py: canonical_hash(obj) that serialises any JSON-able object to canonical
     bytes (sorted keys, UTF-8, compact separators) and returns a sha256 hex digest;
     plus hash_bytes and hash_file helpers. A hash must NEVER depend on wall-clock time,
     dict insertion order, or absolute paths.
   - determinism.py: set_global_determinism(seed) that seeds Python random, NumPy and
     torch, sets torch deterministic flags, single thread, CPU. Also a DeterministicRNG
     class that (a) derives named independent sub-streams, e.g. rng.derive("packer"), so
     each subsystem is reproducible in isolation, and (b) can snapshot() and restore(state)
     its full state (needed later for checkpoint/resume).
   - eventlog.py: an EventLog that appends human-readable lines to
     submission_artifacts/run.log AND accumulates structured events in memory for the
     evidence bundle. Support a pass(event_name, **fields) that writes a line like
     "[PASS] tokenizer_hash_verified key=value ..." and an info(msg, **fields). Timestamps
     may appear in the log text but must NOT feed any hash. Provide to_list() returning the
     structured events.
   - artifacts.py: represent and create the submission_artifacts/ layout: run.log,
     evidence.json, evidence.md, manifests/, ledgers/, checkpoints/, performance.json.
     ensure_layout(root) creates the directories.
   - run_demo.py: the one-command entry point. It sets determinism from config, creates
     the artifact layout, opens the EventLog, then calls an ordered list of STAGE STUBS
     (each logs an [INFO] "<stage> started" and a [PASS] placeholder). Stages, in order:
     create_shards, validate_manifests, block_eval, compile_mixture, run_opus,
     pack_batches, train, checkpoint, crash, resume, replay, fork, audit,
     measure_performance, write_evidence. Each stub takes a shared context object.
3. A tiny pytest smoke test proving: determinism (same seed => identical derived
   sub-stream sequence; snapshot/restore round-trips exactly) and hashing (canonical_hash
   is dict-key-order independent and stable across processes).

REQUIREMENTS: deterministic; no wall-clock or randomness in any hash; small and readable;
standard library + numpy + torch only. Return the COMPLETE code for every file plus a
one-line description of each module's role.'''


def badge(status):
    if status == "done":
        return '<span class="b b-ok">done</span>'
    if status == "active":
        return '<span class="b b-tight">in progress</span>'
    return '<span class="b" style="background:#eee;color:#888">pending</span>'


def steps_rows():
    out = ""
    for n, title, area, pts, status in STEPS:
        out += ('<tr><td>%d</td><td>%s</td><td>%s</td><td>%d</td><td>%s</td></tr>\n'
                % (n, title, area, pts, badge(status)))
    return out


def decisions_rows():
    return "".join('<tr><td><b>%s</b></td><td>%s</td></tr>\n' % (k, v) for k, v in DECISIONS)


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
        '    <div class="eyebrow">Session 6 assignment</div>\n'
        '    <h1>Training Data Execution System</h1>\n'
        '    <p class="dek">A small but complete, reproducible and auditable data plane for V5: '
        'documents &rarr; shards &rarr; manifests &rarr; mixture &rarr; packing &rarr; batches &rarr; training '
        '&rarr; ledgers &rarr; checkpoint &rarr; crash &rarr; resume &rarr; replay &rarr; audit. This page is the '
        'living tracker; we build it step by step and record each step&rsquo;s prompt and evidence here.</p>\n'
        '  </div>\n'

        '  <div class="sec"><h2>What it must prove</h2>\n'
        '    <p>The goal is not scale; it is that the data system is correct, reproducible, auditable and '
        'efficient. The governing invariant is that <strong>a seed plus a ledger offset reconstructs any batch '
        'byte-for-byte</strong> &mdash; which is what makes resume, replay and fork provable. The final run must '
        'deliberately crash, resume with the exact next batch, and replay an earlier interval whose batch ids, '
        'token spans and hashes match the original.</p></div>\n'

        '  <div class="sec"><h2>Decisions (locked)</h2>\n'
        '    <div class="tblwrap"><table class="stbl"><tr><th>Area</th><th>Decision</th></tr>\n'
        + decisions_rows() +
        '    </table></div></div>\n'

        '  <div class="sec"><h2>Architecture</h2>\n'
        '    <div class="diagram"><pre>\n'
        'corpus\n'
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
        '</pre></div>\n'
        '    <p>The contrastive perspective lane and the surprisal metrics are specified in '
        '<code>contrastive_perspective_corpus.md</code>; they enter the system as a data type with its own '
        'packing policy (F1/F2), a learning-ledger signal, and an OPUS selection signal.</p></div>\n'

        '  <div class="sec"><h2>Roadmap</h2>\n'
        '    <div class="tblwrap"><table class="stbl"><tr><th>#</th><th>Step</th><th>Area</th>'
        '<th>Pts</th><th>Status</th></tr>\n'
        + steps_rows() +
        '    </table></div>\n'
        '    <p class="cap">Points map to the assignment&rsquo;s 1,000-point rubric. A step advances only once its '
        'invariant is proven by reproducible evidence.</p></div>\n'

        '  <div class="sec"><h2>How each step runs</h2>\n'
        '    <ol>\n'
        '      <li>Paste the step&rsquo;s prompt (below) into Claude on the web; it returns the code.</li>\n'
        '      <li>Bring the code back; we integrate it into the submission repo.</li>\n'
        '      <li>We verify the step&rsquo;s invariant (the part graders check &mdash; evidence produced by the '
        'implementation, never hardcoded) and record the result here.</li>\n'
        '      <li>Only then do we advance to the next step.</li>\n'
        '    </ol></div>\n'

        '  <div class="sec"><h2>Current step — Step 0 · Scaffold</h2>\n'
        '    <p>Foundation the whole system builds on: deterministic RNG with derivable sub-streams and '
        'snapshot/restore, a canonical content-hasher, the <code>run.log</code> event logger, the '
        '<code>submission_artifacts/</code> layout, and a stubbed one-command <code>run_demo.py</code>. Prompt to '
        'paste into web Claude:</p>\n'
        '    <div class="diagram"><pre>' + html.escape(PROMPT_STEP0) + '</pre></div></div>\n'

        '  <div class="foot">Session 6 &middot; tracker for the Training Data Execution System. '
        'Method spec: <code>contrastive_perspective_corpus.md</code>.</div>\n'
        '</div>\n</body>\n</html>\n'
    )


if __name__ == "__main__":
    with open("assignment.html", "w", encoding="utf-8") as f:
        f.write(build_html())
    print("Done. assignment.html written.")
