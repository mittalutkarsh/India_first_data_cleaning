"""Generate a deep-dive HTML page per feature (4-16) of the Training Data
Execution System, plus a features.html index. Each page shows, per module, the
real docstring (what the epic does) and its public signatures (the code) pulled
straight from the v5-execution-system source, plus the feature's actual [PASS]
line(s) from the real run.log as the worked example. Reuses the house CSS."""

import ast
import html
import os
from pathlib import Path

import generate_v5_playbook as P

CSS = P.CSS
REPO = Path("/Users/umittal/Desktop/v5-execution-system")
RUN_LOG = REPO / "submission_artifacts" / "run.log"

# N -> (title, blurb, [package dirs], [pass event prefixes])
FEATURES = {
    4: ("Immutable shards + manifests",
        "Tokenize the cleaned corpus into fixed-size, content-addressed uint16 shards "
        "(whole documents, never split), each with a manifest (hash, tokens, lane, tiers, "
        "source doc ids) and a shard index; re-hashing proves immutability.",
        ["feature4_shards"], ["shards_written"]),
    5: ("Evaluation firewall",
        "Quarantine eval shards so their ids can never enter a training batch — a single hard "
        "gate every shard id passes through, with a disjointness audit.",
        ["feature5_firewall"], ["eval_shard_blocked"]),
    6: ("Mixture / curriculum compiler",
        "Compile an India-first curriculum (phases, lane weights, protected floors) into exact "
        "per-lane token targets; floors are reserved first so indic/multilingual are never starved.",
        ["feature6_mixture"], ["mixture_compiled"]),
    7: ("OPUS selector",
        "Accept / reject / defer each candidate by a pluggable score, with a protected-floor "
        "override and a ΔS surprisal hook, writing an append-only decision ledger.",
        ["feature7_opus"], ["opus_selected"]),
    8: ("The packer",
        "Pack whole docs into fixed seq_len sequences with per-doc position ids, a same-segment "
        "causal attention mask (no cross-doc attention), loss masks, and a contrastive "
        "framing-span policy.",
        ["feature8_packer"], ["sequences_packed"]),
    9: ("Batch stream + consumption ledger",
        "The reproducibility core: batch(i) is a pure function of (seed, i), so any batch rebuilds "
        "from seed + a ledger offset without replaying the stream. Each batch carries a content hash.",
        ["feature9_batches"], ["batch_stream_ready"]),
    10: ("Tiny MoE transformer + learning ledger",
         "A small deterministic PyTorch Mixture-of-Experts model. Per-token cross-entropy is F1 "
         "surprisal (learning ledger, keyed by batch id); ΔS = S(y-)-S(y+) is the F2 signal per "
         "contrastive pair.",
         ["feature10_trainer"], ["trained", "contrastive_delta_s"]),
    11: ("Checkpoints",
         "Snapshot model + optimizer + RNG + ledger offset with a canonical model hash; restore "
         "rebuilds an identical trainer, verified on load.",
         ["feature11_checkpoint"], ["checkpoint_saved"]),
    12: ("Crash + resume",
         "Deliberately crash at a set batch, then resume from the checkpoint offset — proving no "
         "batch is skipped or repeated and the resumed loss trajectory matches a clean run.",
         ["feature12_resume"], ["resume_next_batch_matched"]),
    13: ("Replay",
         "Replay any interval from seed + ledger; rebuilt batch ids, sequence indices and content "
         "hashes must match the recorded ledger exactly.",
         ["feature13_replay"], ["replay_hash_matched"]),
    14: ("Fork",
         "Fork from an earlier checkpoint onto a new-seed branch: shared history, divergent "
         "continuation, lineage recorded back to the parent.",
         ["feature14_fork"], ["fork_lineage_recorded"]),
    15: ("Throughput / packing efficiency",
         "Deterministic packing utilization + loss-bearing token counts (logged), kept apart from "
         "wall-clock throughput (written to performance.json, never to the byte-identical run.log).",
         ["feature15_throughput"], ["throughput_measured"]),
    16: ("Audit + evidence bundle",
         "Cross-check the whole run against its own artifacts and assemble evidence.json + "
         "evidence.md entirely from written files — nothing hardcoded.",
         ["feature16_audit"], ["audit_complete"]),
}


def _arg_names(args: ast.arguments) -> str:
    parts = []
    for a in args.posonlyargs:
        parts.append(a.arg)
    if args.posonlyargs:
        parts.append("/")
    for a in args.args:
        parts.append(a.arg)
    if args.vararg:
        parts.append("*" + args.vararg.arg)
    elif args.kwonlyargs:
        parts.append("*")
    for a in args.kwonlyargs:
        parts.append(a.arg)
    if args.kwarg:
        parts.append("**" + args.kwarg.arg)
    return ", ".join(parts)


def _module_view(path: Path) -> tuple[str, str]:
    """Return (docstring, signatures-block) for one module."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    doc = ast.get_docstring(tree) or ""
    sigs = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
            sigs.append(f"def {node.name}({_arg_names(node.args)})")
        elif isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
            sigs.append(f"class {node.name}:")
            for m in node.body:
                if isinstance(m, ast.FunctionDef) and not m.name.startswith("_"):
                    sigs.append(f"    def {m.name}({_arg_names(m.args)})")
    return doc, "\n".join(sigs)


def _pass_lines(prefixes: list[str]) -> list[str]:
    if not RUN_LOG.exists():
        return []
    out = []
    for line in RUN_LOG.read_text(encoding="utf-8").splitlines():
        for pre in prefixes:
            if line.startswith(f"[PASS] {pre}"):
                out.append(line)
    return out


def _nav(active: str) -> str:
    cls = ' class="active"' if active == "index" else ""
    return (
        '<div class="nav"><div class="nav-in">\n'
        '  <span class="brand">India-First 40B</span>\n'
        '  <a href="assignment.html">Assignment</a>\n'
        '  <a href="feature3.html">Feature 3</a>\n'
        '  <a href="features.html"' + cls + '>Features 4&ndash;16</a>\n'
        '</div></div>\n'
    )


def _code(src: str) -> str:
    return '    <div class="diagram"><pre>%s</pre></div>\n' % html.escape(src.strip("\n"))


def build_feature_page(n: int) -> str:
    title, blurb, dirs, prefixes = FEATURES[n]
    body = ""
    for d in dirs:
        for py in sorted((REPO / d).glob("*.py")):
            if py.name == "__init__.py":
                continue
            doc, sigs = _module_view(py)
            body += '  <div class="sec"><h2>%s</h2>\n' % html.escape(f"{d}/{py.name}")
            if doc:
                first = doc.strip().split("\n\n")[0].replace("\n", " ")
                body += '    <p>%s</p>\n' % html.escape(first)
            if sigs:
                body += '    <p class="cap">Public interface</p>\n' + _code(sigs)
            body += '  </div>\n'
    ev = _pass_lines(prefixes)
    ev_block = ""
    if ev:
        ev_block = ('  <div class="sec"><h2>Evidence — from the real run</h2>\n'
                    '    <p class="cap">Emitted by <code>python run_demo.py</code> on the full 10M corpus.</p>\n'
                    + _code("\n".join(ev)) + '  </div>\n')
    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        f'<title>Feature {n} — {html.escape(title)}</title>\n'
        '<link href="https://fonts.googleapis.com/css2?family=Spectral:wght@600;700'
        '&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">\n'
        '<style>' + CSS + '</style>\n</head>\n<body>\n' + _nav("") +
        '<div class="wrap">\n'
        f'  <div class="crumb">Session 6 / Feature {n}</div>\n'
        '  <div class="phead">\n'
        f'    <div class="eyebrow">Feature {n} · implementation</div>\n'
        f'    <h1>{html.escape(title)}</h1>\n'
        f'    <p class="dek">{blurb}</p>\n'
        '  </div>\n'
        + ev_block + body +
        '  <div class="foot">Code in the <code>v5-execution-system</code> repo · '
        '<a href="features.html">all features</a> · <a href="assignment.html">tracker</a></div>\n'
        '</div>\n</body>\n</html>\n'
    )


def build_index() -> str:
    rows = ""
    for n in sorted(FEATURES):
        title = FEATURES[n][0]
        rows += ('<tr><td><b>%d</b></td><td><a href="feature%d.html">%s</a></td></tr>\n'
                 % (n, n, html.escape(title)))
    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>Features 4–16 — implementation</title>\n'
        '<link href="https://fonts.googleapis.com/css2?family=Spectral:wght@600;700'
        '&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">\n'
        '<style>' + CSS + '</style>\n</head>\n<body>\n' + _nav("index") +
        '<div class="wrap">\n'
        '  <div class="crumb">Session 6 / Features 4–16</div>\n'
        '  <div class="phead">\n'
        '    <div class="eyebrow">Implementation deep-dives</div>\n'
        '    <h1>Features 4–16</h1>\n'
        '    <p class="dek">Every pipeline feature after the tokenizer, each with its modules '
        '(what &amp; code) and the real <code>[PASS]</code> evidence from a full run. Feature 3 '
        'has its own page; Features 1–2 are covered on the tracker.</p>\n'
        '  </div>\n'
        '  <div class="sec"><h2>The pipeline</h2>\n'
        '    <div class="diagram"><pre>\n'
        'corpus -> clean -> [tokenizer] -> shards(4) -> firewall(5) -> mixture(6) -> OPUS(7)\n'
        '  -> packer(8) -> batch stream + ledger(9) -> MoE trainer + learning ledger(10)\n'
        '  -> checkpoint(11) -> crash+resume(12) -> replay(13) -> fork(14) -> throughput(15) -> audit(16)\n'
        '</pre></div></div>\n'
        '  <div class="sec"><h2>Pages</h2>\n'
        '    <div class="tblwrap"><table class="stbl"><tr><th>#</th><th>Feature</th></tr>\n'
        + rows + '</table></div></div>\n'
        '  <div class="foot"><a href="assignment.html">tracker</a> · '
        '<a href="feature3.html">Feature 3</a></div>\n'
        '</div>\n</body>\n</html>\n'
    )


if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    for n in FEATURES:
        Path(f"feature{n}.html").write_text(build_feature_page(n), encoding="utf-8")
    Path("features.html").write_text(build_index(), encoding="utf-8")
    print(f"Wrote feature{{{min(FEATURES)}..{max(FEATURES)}}}.html + features.html")
