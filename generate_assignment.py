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
# Data-first ordering: each step is one small artifact. The reproducibility
# utilities are introduced where first needed (hasher at the tokenizer/shards;
# deterministic RNG at the batch stream) rather than as an upfront scaffold.
# run_demo.py and run.log are born at Step 1 and grow one stage per step.
STEPS = [
    (1, "Corpus — tiny multi-lane docs (web/code/math/indic) + eval split + contrastive pairs; minimal run_demo + run.log", "Tokenizer integrity", 100, "active"),
    (2, "Normalize + per-document content hash (light clean; the content-hasher is introduced here)", "Shards/manifests", 100, "pending"),
    (3, "Frozen byte-level BPE tokenizer + content hash", "Tokenizer integrity", 100, "pending"),
    (4, "Immutable tokenized shards + manifests (hash, token count, lane, provenance, chauvinism tag)", "Shards/manifests", 100, "pending"),
    (5, "Evaluation / validation firewall — eval shards can never enter a loss-bearing batch", "Firewall", 50, "pending"),
    (6, "Mixture schedule — curriculum stages, lane weights, protected floors (planned shares)", "Mixture", 150, "pending"),
    (7, "OPUS selector — accept / reject / defer + protected-floor override; ΔS surprisal as a selection signal", "Mixture/OPUS", 150, "pending"),
    (8, "Packer — per-type packing policies (incl. contrastive pairs), loss + attention masks, position ids", "Packing/masks", 150, "pending"),
    (9, "Deterministic batch stream + consumption ledger (RNG introduced here; batch id, token spans, offsets, hashes)", "Ledgers", 150, "pending"),
    (10, "Trainer (tiny MoE transformer) + learning ledger + F1 per-token surprisal + F2 ΔS per contrastive pair", "Ledgers", 150, "pending"),
    (11, "Checkpoints tied to ledger offset + RNG state", "Checkpoint", 150, "pending"),
    (12, "Deliberate crash → resume; prove the next batch is exactly the expected batch (no skip/repeat)", "Checkpoint", 150, "pending"),
    (13, "Replay an earlier interval; prove batch ids / token spans / hashes match the original run", "Checkpoint", 150, "pending"),
    (14, "Fork from an earlier checkpoint (branch)", "Checkpoint", 150, "pending"),
    (15, "Throughput + packing efficiency → performance.json", "Throughput", 50, "pending"),
    (16, "Audit + evidence bundle (evidence.json / .md from real artifacts) + one-command run_demo.py + tests + README", "Evidence/tests/docs", 50, "pending"),
]

DECISIONS = [
    ("Stack", "Python 3.11 + PyTorch on CPU, determinism pinned (fixed seeds, deterministic algorithms, single thread)."),
    ("Model", "Tiny Mixture-of-Experts transformer, built as a pluggable module at Step 8 (after the data plane is proven)."),
    ("Tokenizer", "Self-contained byte-level BPE, trained once on the toy corpus then frozen — vocab + merges committed and content-hashed."),
    ("Method", "Contrastive perspective lane (y+/y−) + F1/F2 surprisal in the learning ledger + ΔS as an OPUS signal. F3–F7 geometry kept as a documented hook (see contrastive_perspective_corpus.md)."),
    ("Repo", "New standalone GitHub repository (the submission), separate from this proposal site. This page is the tracker; the code lives in the submission repo."),
]

PROMPT_CURRENT = r'''CONTEXT: I am building a small, reproducible "Training Data Execution System" for LLM
pretraining (a course assignment), Python 3.11, built in small steps. THIS IS STEP 1 ONLY
— just the toy corpus and a minimal runner. No tokenization yet.

TASK
1. A tiny in-repo corpus organised by lane. A module corpus.py returning documents, each a
   dict {id, lane, provenance_tier, split, text}. Include: 2-3 short "web", "code" and
   "math" docs; one or two "indic" docs; an "eval" split (a couple of docs marked
   split="eval") that must never be trained on; and 3-4 "contrastive" pairs on contested
   topics — each a shared prefix plus two continuations y_plus (Indian-vantage) and y_minus
   (Western-default) differing only in a framing span, tagged {vantage, chauvinism:"none"}.
   Represent a contrastive pair as its own document type. Keep every text 1-3 sentences,
   fixed/authored, no randomness.
2. A minimal run_demo.py that creates a submission_artifacts/ folder with a run.log, calls
   one stage load_corpus(), logs one line per lane like "[INFO] corpus_loaded lane=web
   docs=3", and a final "[PASS] corpus_loaded total=N eval=M contrastive=K".
3. A tiny pytest test asserting: the corpus loads; the eval split is non-empty and flagged;
   every contrastive pair has a prefix, y_plus, y_minus, and a vantage tag.

REQUIREMENTS: standard library only for now; deterministic (no randomness); small and
readable. Return the full code for corpus.py, run_demo.py and the test, plus a one-line
note on the data model.'''


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

        '  <div class="sec"><h2>Current step — Step 1 · Corpus</h2>\n'
        '    <p>The first concrete artifact: a tiny multi-lane corpus (web / code / math / indic), an eval split '
        'quarantined from training, and a handful of contrastive perspective pairs (prefix + y+ / y&minus;). Plus a '
        'minimal one-command <code>run_demo.py</code> and <code>run.log</code>, which grow one stage per step. The '
        'reproducibility utilities (content-hasher, deterministic RNG) are introduced later, at the step where each is '
        'first needed. Prompt to paste into web Claude:</p>\n'
        '    <div class="diagram"><pre>' + html.escape(PROMPT_CURRENT) + '</pre></div></div>\n'

        '  <div class="foot">Session 6 &middot; tracker for the Training Data Execution System. '
        'Method spec: <code>contrastive_perspective_corpus.md</code>.</div>\n'
        '</div>\n</body>\n</html>\n'
    )


if __name__ == "__main__":
    with open("assignment.html", "w", encoding="utf-8") as f:
        f.write(build_html())
    print("Done. assignment.html written.")
