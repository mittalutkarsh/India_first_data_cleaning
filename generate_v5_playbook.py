"""Generate v5_playbook.html — the procedure for constructing the V5 plan,
in a formal research-proposal register on the shared house style."""

BUDGET_B = 3000.0

# lane, share%, selector keep-fraction, unique-eligible tokens (B), note
PANTRY = [
    ("General web", 37, 0.5, 8000, "ample after deduplication"),
    ("Code", 22, 0.5, 600, "Stack v2, after licensing and deduplication"),
    ("STEM", 12, 0.5, 350, "textbooks and scientific text"),
    ("Agentic", 13, 1.0, 0.08, "must be generated; scraping is insufficient"),
    ("Reasoning", 7, 0.5, 30, "distilled traces; requires scaling"),
    ("Indic", 8, 1.0, 150, "predominantly unverified web; verified tier is limited"),
    ("Safety", 1, 1.0, 15, "curated"),
]

# Surveyed July 2026 (see Sources in Section 1). name, lane, size, metric, best score (date)
BENCHMARKS = [
    ("SWE-bench Verified", "code", "500 verified GitHub issues", "resolved rate (hidden tests pass)", "~76% pass@1, ~81% pass@3 (Jan 2026); frontier 71–77%"),
    ("Terminal-Bench v2", "agentic", "89 terminal tasks", "sandbox task success", "hard; frontier well below human"),
    ("&tau;-bench", "agentic", "165 (115 retail, 50 airline)", "pass^k (all k runs pass)", "frontier pass^1 &lt; 70%; GPT-4o retail 60% &rarr; 25% (pass^1&rarr;pass^8)"),
    ("BFCL v4", "agentic", "function-calling suite", "weighted acc. (agentic 40%, multi-turn 30%)", "continuous leaderboard"),
    ("GAIA", "agentic", "466 questions, 3 levels", "exact-match (tools + web allowed)", "humans ~92%; public agents trail"),
    ("AIME", "reasoning", "30 problems / year", "accuracy", "year-rotated; strong reasoning models high"),
    ("FrontierMath", "reasoning", "338 (295 Tiers 1–3 + 43 Tier 4)", "accuracy", "&gt;50% Tiers 1–3, 25–40% Tier 4 (mid-2026); ~0–6% in 2025"),
    ("MMLU", "general web", "15,908 Q, 57 subjects", "accuracy", "saturated at the top; kept for regression"),
    ("MMLU-Pro", "general web", "12,000+ Q, 14 domains", "accuracy", "harder than MMLU; still has headroom"),
    ("MILU", "indic", "~85,000 MCQs, 11 languages", "accuracy", "Indic understanding; below English MMLU"),
    ("IndicGenBench", "indic", "generation, 29 languages", "chrF / ROUGE / EM", "reference-based; generative"),
]

PROXIES = [
    ("code", "SWE-bench Verified", "HumanEval, MBPP", "164 / ~974 problems"),
    ("reasoning", "AIME, FrontierMath", "GSM8K, MATH-500", "1,319 test / 500 problems"),
    ("general web", "MMLU-Pro", "MMLU", "15,908 questions"),
    ("indic", "MILU, IndicGenBench", "MILU (subset)", "subset of ~85k"),
    ("agentic", "Terminal-Bench, &tau;-bench", "scripted tool-call success rate", "in-house set"),
]

# Benchmark / lane, why selected, capability targeted, how (data lever),
# current industry best (dated), V5 target (illustrative; locked after validation)
STRATEGY = [
    ("SWE-bench Verified", "code",
     "Execution-graded on real repository bugs; contamination-resistant via the temporal Live variant.",
     "Autonomous repository-level bug fixing.",
     "Stack v2 plus generated issue&#8594;patch&#8594;test trajectories.",
     "~76% pass@1 (Jan 2026)", "&#8805; 50% resolved at 40B"),
    ("Terminal-Bench v2", "agentic",
     "Scores multi-step tool use in a real sandbox, not isolated API calls.",
     "Planning and acting across a terminal session.",
     "Generated plan&#8594;act&#8594;reflect trajectories, loss-masked on model turns.",
     "frontier well below human", "~30% task success at 40B"),
    ("&tau;-bench", "agentic",
     "Grades whole multi-turn dialogues under pass^k, penalising unreliable behaviour.",
     "Reliable tool-using assistants.",
     "Synthetic tool-use dialogues paired with programmatic verifiers.",
     "retail ~60% &#8594; 25% (pass^1&#8594;pass^8)", "~45% pass^1 at 40B"),
    ("AIME", "reasoning",
     "Integer-answer competition mathematics, exact-match and year-rotated (fresh each year).",
     "Multi-step mathematical reasoning.",
     "Distilled step-by-step solution traces, banded by reasoning depth.",
     "high for reasoning models; year-rotated", "~40% on the held-out year"),
    ("FrontierMath", "reasoning",
     "Research-level mathematics with large headroom; solutions withheld from training.",
     "Deep, original reasoning.",
     "Distilled expert traces plus tool-augmented reasoning.",
     "25&#8211;40% Tier 4 (mid-2026)", "~15% Tiers 1&#8211;3"),
    ("MMLU-Pro", "general web",
     "Broad knowledge that still has headroom, unlike the saturated original MMLU.",
     "General knowledge and a regression guard for unlisted capabilities.",
     "High-quality deduplicated web (DCLM / FineWeb).",
     "harder than MMLU; headroom remains", "&#8805; 65%, no regression vs baseline"),
    ("MILU", "indic",
     "Native Indic-language examinations across 11 languages, not translated English.",
     "Indic knowledge and comprehension.",
     "Sangraha / IndicCorp / Wikipedia plus verified Indic textbooks.",
     "below English MMLU", "best open-weight Indic; ~60% macro-avg"),
    ("IndicGenBench", "indic",
     "Measures generation across 29 languages, not only recognition.",
     "Fluent Indic generation and translation.",
     "Verified and translated Indic tiers, with a per-language worst-case floor.",
     "reference-based (chrF / ROUGE)", "macro-avg + worst-language reported; chrF above baseline"),
]

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
    '  <a href="v5_playbook.html" class="active">V5 Plan — Procedure</a>\n'
    '</div></div>\n'
)

CSS = """
:root { --bg:#FAFBFD; --ink:#16162A; --indigo:#2E357E; --indigo-soft:#6169B8; --marigold:#E0982B;
  --teal:#147D74; --rose:#B5476B; --line:#E3E4EE; --muted:#656579; --panel:#F1F2F8; }
*, *::before, *::after { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--ink); font-family:"Inter",system-ui,sans-serif; font-size:15px; line-height:1.65; -webkit-font-smoothing:antialiased; }
a { color:var(--indigo); text-decoration:none; } a:hover { text-decoration:underline; }
.nav { position:sticky; top:0; z-index:50; background:rgba(250,251,253,.96); border-bottom:1px solid var(--line); }
.nav-in { max-width:1280px; margin:0 auto; padding:10px 24px; display:flex; align-items:center; gap:13px; flex-wrap:wrap; }
.brand { font-family:"Spectral",serif; font-weight:700; color:var(--indigo); font-size:16px; margin-right:auto; }
.nav a { font-family:"IBM Plex Mono",monospace; font-size:11px; letter-spacing:.02em; color:var(--muted); padding:3px 2px; border-bottom:2px solid transparent; }
.nav a:hover { color:var(--ink); text-decoration:none; } .nav a.active { color:var(--indigo); border-bottom-color:var(--marigold); }
.wrap { max-width:820px; margin:0 auto; padding:0 24px 80px; }
.crumb { font-family:"IBM Plex Mono",monospace; font-size:11px; color:var(--muted); padding:18px 0 0; }
.phead { padding:8px 0 14px; border-bottom:2px solid var(--ink); }
.eyebrow { font-family:"IBM Plex Mono",monospace; font-size:11px; letter-spacing:.13em; text-transform:uppercase; color:var(--marigold); font-weight:600; }
.phead h1 { font-family:"Spectral",serif; font-weight:700; font-size:clamp(26px,3.6vw,38px); margin:8px 0 8px; }
.phead .dek { font-size:15px; color:#33334a; margin:0; }
.sec { margin:28px 0 0; } .sec h2 { font-family:"Spectral",serif; font-size:20px; margin:0 0 6px; }
h3 { font-size:15px; margin:22px 0 4px; color:var(--indigo); }
p { margin:13px 0; } strong { font-weight:600; }
ol, ul { margin:12px 0; padding-left:22px; } li { margin:6px 0; }
.diagram { background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:14px 16px; overflow-x:auto; margin:16px 0; }
.diagram pre { margin:0; font-family:"IBM Plex Mono",monospace; font-size:12px; line-height:1.55; color:#26263c; white-space:pre; }
.tblwrap { overflow-x:auto; }
.egbox { border:1px solid var(--line); border-left:3px solid var(--indigo-soft); border-radius:0 8px 8px 0; background:#fff; padding:11px 14px; margin:10px 0; font-size:13.5px; line-height:1.55; }
.yes { color:var(--teal); font-weight:600; } .no { color:var(--rose); font-weight:600; }
.q { font-family:"IBM Plex Mono",monospace; font-size:12.5px; }
.tbl { width:100%; border-collapse:collapse; font-family:"IBM Plex Mono",monospace; font-size:13px; background:#fff; border:1px solid var(--line); border-radius:12px; overflow:hidden; margin:16px 0; }
.tbl th, .tbl td { padding:8px 11px; border-bottom:1px solid var(--line); text-align:right; }
.tbl th:first-child, .tbl td:first-child { text-align:left; }
.tbl th { font-size:10px; letter-spacing:.05em; text-transform:uppercase; color:var(--muted); background:var(--panel); }
.b { font-weight:600; padding:1px 7px; border-radius:5px; }
.b-ok { background:#e6f5ef; color:#0f7a54; } .b-tight { background:#fbeede; color:#9a5a12; }
.b-starved { background:#fceef2; color:var(--rose); } .b-inf { background:#f7e0e6; color:#8a1a3a; }
.cap { font-size:13px; color:var(--muted); margin-top:-6px; font-style:italic; }
.callout { margin:16px 0; border-left:3px solid var(--marigold); background:#fdf9f1; border-radius:0 8px 8px 0; padding:12px 16px; font-size:14px; color:#4a3a1e; }
.foot { margin-top:30px; padding-top:16px; border-top:1px solid var(--line); font-size:13.5px; color:var(--muted); }
code { font-family:"IBM Plex Mono",monospace; font-size:12.5px; background:var(--panel); padding:1px 5px; border-radius:4px; }
.fig { margin:20px 0; padding:16px 16px 6px; background:#fff; border:1px solid var(--line); border-radius:12px; }
.fig svg { display:block; }
.fig figcaption { font-size:12.5px; color:var(--muted); margin-top:10px; padding-top:8px; border-top:1px solid var(--line); line-height:1.5; }
.fig figcaption b { color:var(--ink); }
.eq { margin:14px 0; overflow-x:auto; }
mjx-container { color:var(--ink); }
.stbl { width:100%; border-collapse:collapse; font-family:"Inter",sans-serif; font-size:12.5px; line-height:1.45; background:#fff; border:1px solid var(--line); border-radius:12px; overflow:hidden; margin:16px 0; }
.stbl th, .stbl td { text-align:left; vertical-align:top; padding:9px 11px; border-bottom:1px solid var(--line); }
.stbl th { font-family:"IBM Plex Mono",monospace; font-size:9.5px; letter-spacing:.05em; text-transform:uppercase; color:var(--muted); background:var(--panel); font-weight:600; }
.stbl td:first-child { white-space:nowrap; }
.stbl .lanetag { font-family:"IBM Plex Mono",monospace; font-size:10px; }
.stbl .tgt { font-weight:600; color:var(--indigo); }
"""


def pantry_rows():
    out = ""
    for lane, share, keep, avail, note in PANTRY:
        trained = share / 100 * BUDGET_B
        presented = trained / keep
        executable = min(trained, avail * 4)
        if executable < trained * 0.5:
            cls, lab = "b-inf", "INFEASIBLE"
        elif executable < trained * 0.999:
            cls, lab = "b-starved", "STARVED"
        elif presented > avail * 1.5:
            cls, lab = "b-tight", "TIGHT"
        else:
            cls, lab = "b-ok", "ENOUGH"
        avail_s = ("%.2fB" % avail) if avail < 1 else "{:,}B".format(int(avail))
        out += ("<tr><td>%s</td><td>%d%%</td><td>~%dB</td><td>~%dB</td><td>~%s</td>"
                "<td><span class=\"b %s\">%s</span></td></tr>\n"
                % (lane, share, round(trained), round(presented), avail_s, cls, lab))
    return out


def bench_rows():
    return "".join(
        "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>\n" % b
        for b in BENCHMARKS)


def proxy_rows():
    return "".join(
        "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>\n" % p
        for p in PROXIES)


def strategy_rows():
    out = ""
    for bench, lane, why, what, how, best, target in STRATEGY:
        acc = LANE_COLOR.get(lane, ("#656579", ""))[0]
        out += ('<tr><td><b>%s</b><br><span class="lanetag" style="color:%s">%s</span></td>'
                '<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td class="tgt">%s</td></tr>\n'
                % (bench, acc, lane, why, what, how, best, target))
    return out


# ---------------------------------------------------------------------------
# Diagrams. Real SVG in the economist style of the ml-pipeline-diagram skill:
# light tinted regions, cylinders for data sources, rounded process boxes,
# orthogonal labelled arrows, a caption. Palette matches the page CSS.
# ---------------------------------------------------------------------------

# lane -> accent colour, light fill (kept consistent across every figure)
LANE_COLOR = {
    "code":        ("#2E357E", "#ECEEF8"),
    "agentic":     ("#B5476B", "#FBEEF3"),
    "reasoning":   ("#E0982B", "#FBF1E0"),
    "general web": ("#656579", "#F1F2F8"),
    "indic":       ("#147D74", "#E6F3F0"),
}


def _rr(x, y, w, h, fill, stroke, label, sub="", fs=12, rx=8, tcolor="#16162A"):
    """A rounded-rect process/label box with an optional grey subtitle line."""
    t = ('<text x="%d" y="%d" text-anchor="middle" font-family="Inter,sans-serif" '
         'font-size="%d" font-weight="600" fill="%s">%s</text>'
         % (x + w // 2, y + (h // 2 - 2 if sub else h // 2 + 4), fs, tcolor, label))
    if sub:
        t += ('<text x="%d" y="%d" text-anchor="middle" font-family="IBM Plex Mono,monospace" '
              'font-size="10" fill="#6B6B7B">%s</text>' % (x + w // 2, y + h // 2 + 13, sub))
    return ('<rect x="%d" y="%d" width="%d" height="%d" rx="%d" fill="%s" stroke="%s" '
            'stroke-width="1.4"/>%s' % (x, y, w, h, rx, fill, stroke, t))


def _cyl(x, y, w, h, stroke, label, sub=""):
    """A 3D data cylinder (source/output dataset)."""
    ry = 9
    body = ('<path d="M%d %d a%d %d 0 0 0 %d 0 v%d a%d %d 0 0 1 -%d 0 z" '
            'fill="#FFFFFF" stroke="%s" stroke-width="1.5"/>'
            % (x, y + ry, w // 2, ry, w, h - 2 * ry, w // 2, ry, w, stroke))
    top = ('<ellipse cx="%d" cy="%d" rx="%d" ry="%d" fill="#FFFFFF" stroke="%s" '
           'stroke-width="1.5"/>' % (x + w // 2, y + ry, w // 2, ry, stroke))
    t = ('<text x="%d" y="%d" text-anchor="middle" font-family="Inter,sans-serif" '
         'font-size="11" font-weight="600" fill="#16162A">%s</text>'
         % (x + w // 2, y + h // 2 + 2, label))
    if sub:
        t += ('<text x="%d" y="%d" text-anchor="middle" font-family="IBM Plex Mono,monospace" '
              'font-size="9" fill="#6B6B7B">%s</text>' % (x + w // 2, y + h // 2 + 15, sub))
    return body + top + t


def _arrow(x1, y1, x2, y2, label="", dash=False, color="#5A5A6E"):
    d = ' stroke-dasharray="5 4"' if dash else ""
    line = ('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1.5"%s '
            'marker-end="url(#ah)"/>' % (x1, y1, x2, y2, color, d))
    if label:
        mx, my = (x1 + x2) // 2, (y1 + y2) // 2
        line += ('<rect x="%d" y="%d" width="%d" height="15" rx="3" fill="#FAFBFD"/>'
                 '<text x="%d" y="%d" text-anchor="middle" font-family="IBM Plex Mono,monospace" '
                 'font-size="9" fill="#656579">%s</text>'
                 % (mx - len(label) * 3 - 3, my - 8, len(label) * 6 + 6, mx, my + 3, label))
    return line


def _svg_open(w, h):
    return ('<svg viewBox="0 0 %d %d" width="100%%" role="img" '
            'xmlns="http://www.w3.org/2000/svg" font-family="Inter,sans-serif">'
            '<defs><marker id="ah" markerWidth="9" markerHeight="9" refX="7" refY="3" '
            'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L7,3 L0,6 z" '
            'fill="#5A5A6E"/></marker></defs>' % (w, h))


def _col_header(x, w, y, text):
    return ('<text x="%d" y="%d" text-anchor="middle" font-family="IBM Plex Mono,monospace" '
            'font-size="10" letter-spacing="0.06em" fill="#656579">%s</text>'
            % (x + w // 2, y, text.upper()))


COMPOSE = [
    # lane, benchmark(s), supplying dataset, dataset sub
    ("code", "SWE-bench Verified", "Stack v2 + repo-fix traces", "generated"),
    ("agentic", "Terminal-Bench · &#964;-bench · GAIA", "tool-use trajectories", "generated"),
    ("reasoning", "AIME · FrontierMath", "distilled step-by-step traces", "distilled"),
    ("general web", "MMLU · MMLU-Pro", "DCLM / FineWeb", "web"),
    ("indic", "MILU · IndicGenBench", "Sangraha / IndicCorp / Wiki", "mixed tiers"),
]


def svg_compose_backward():
    W, top, rh, gap = 820, 58, 46, 12
    H = top + len(COMPOSE) * (rh + gap) + 6
    s = _svg_open(W, H)
    s += _col_header(8, 168, 34, "capability lane")
    s += _col_header(250, 300, 34, "target benchmark")
    s += _col_header(600, 212, 34, "supplying dataset")
    y = top
    for lane, bench, ds, sub in COMPOSE:
        acc, fill = LANE_COLOR[lane]
        s += _rr(8, y, 168, rh, fill, acc, lane, fs=13, tcolor=acc)
        s += _rr(250, y, 300, rh, "#FFFFFF", "#6169B8", bench, fs=11.5)
        s += _cyl(600, y - 2, 212, rh + 4, acc, ds, sub)
        s += _arrow(176, y + rh // 2, 249, y + rh // 2)              # lane -> benchmark
        s += _arrow(599, y + rh // 2, 551, y + rh // 2)              # dataset -> benchmark
        y += rh + gap
    s += "</svg>"
    return s


def svg_instance_trace():
    W, H = 820, 250
    s = _svg_open(W, H)
    acc = "#2E357E"
    # context inputs (read, no loss) -> model -> supervised target -> sandbox -> bit
    s += ('<rect x="8" y="30" width="230" height="150" rx="10" fill="#F1F2F8" '
          'stroke="#C9CBDD" stroke-width="1.2"/>'
          '<text x="123" y="50" text-anchor="middle" font-family="IBM Plex Mono,monospace" '
          'font-size="9" letter-spacing="0.05em" fill="#656579">CONTEXT &#8212; READ, NO LOSS</text>')
    s += _cyl(30, 66, 186, 60, acc, "repository @ commit", "~600,000 lines")
    s += _rr(30, 138, 186, 34, "#FFFFFF", acc, "issue text", "~180 words", fs=11)
    s += _rr(300, 78, 150, 54, "#ECEEF8", acc, "model", "produces a patch", fs=12, tcolor=acc)
    s += ('<rect x="512" y="30" width="300" height="150" rx="10" fill="#E6F3F0" '
          'stroke="#8FC4BC" stroke-width="1.2"/>'
          '<text x="662" y="50" text-anchor="middle" font-family="IBM Plex Mono,monospace" '
          'font-size="9" letter-spacing="0.05em" fill="#147D74">SANDBOX &#8212; EXECUTED GRADING</text>')
    s += _rr(300, 150, 150, 34, "#FFFFFF", "#B5476B", "gold patch", "+14 / &#8722;3, target", fs=11, tcolor="#B5476B")
    s += _rr(532, 66, 260, 30, "#FFFFFF", "#147D74", "3 fail&#8594;pass tests must flip", fs=10.5)
    s += _rr(532, 104, 260, 30, "#FFFFFF", "#147D74", "41 pass&#8594;pass tests must hold", fs=10.5)
    s += _rr(532, 142, 260, 34, "#E6F3F0", "#147D74", "resolved = 1 iff all 44 pass", fs=11.5, tcolor="#147D74")
    s += _arrow(217, 105, 299, 105)                     # inputs -> model
    s += _arrow(300, 167, 250, 167)                     # gold patch -> (target, leftward marker) decorative
    s += _arrow(451, 105, 531, 105, "run tests")        # model -> sandbox
    s += "</svg>"
    return s


PHASES = [
    ("Foundation", 45, "general web, early code", "up to 8k"),
    ("Expansion", 30, "code, STEM, reasoning", "up to 32k"),
    ("Reasoning + LC", 23, "scarce lanes, long docs", "up to 128k"),
    ("Anneal", 2, "premium, verified Indic", "held in-budget"),
]


def svg_curriculum():
    W, H = 820, 170
    x0, y0, bar_w, bar_h = 8, 62, 804, 60
    s = _svg_open(W, H)
    s += ('<text x="8" y="30" font-family="IBM Plex Mono,monospace" font-size="10" '
          'letter-spacing="0.05em" fill="#656579">BUDGET (3T UPDATE TOKENS), LEFT &#8594; RIGHT IN TRAINING ORDER</text>')
    accents = ["#2E357E", "#147D74", "#E0982B", "#B5476B"]
    fills = ["#ECEEF8", "#E6F3F0", "#FBF1E0", "#FBEEF3"]
    x = x0
    for i, (name, pct, dom, seq) in enumerate(PHASES):
        w = round(bar_w * pct / 100)
        s += ('<rect x="%d" y="%d" width="%d" height="%d" rx="6" fill="%s" stroke="%s" '
              'stroke-width="1.4"/>' % (x, y0, w, bar_h, fills[i], accents[i]))
        cx = x + w // 2
        s += ('<text x="%d" y="%d" text-anchor="middle" font-family="Inter,sans-serif" '
              'font-size="12" font-weight="600" fill="%s">%s</text>' % (cx, y0 + 22, accents[i], name))
        s += ('<text x="%d" y="%d" text-anchor="middle" font-family="IBM Plex Mono,monospace" '
              'font-size="13" fill="%s">%d%%</text>' % (cx, y0 + 40, accents[i], pct))
        if w > 90:
            s += ('<text x="%d" y="%d" text-anchor="middle" font-family="Inter,sans-serif" '
                  'font-size="9.5" fill="#4a4a5e">%s</text>' % (cx, y0 + 54, dom))
        s += ('<text x="%d" y="%d" text-anchor="middle" font-family="IBM Plex Mono,monospace" '
              'font-size="9" fill="#656579">%s</text>' % (cx, y0 + bar_h + 16, seq))
        x += w
    s += ('<text x="8" y="%d" font-family="Inter,sans-serif" font-size="10" font-style="italic" '
          'fill="#656579">Max sequence length rises left to right; transitions are gradual (overlapping bands), '
          'not step changes.</text>' % (y0 + bar_h + 40))
    s += "</svg>"
    return s


def figure(svg, caption, n):
    return ('  <figure class="fig">' + svg +
            '<figcaption><b>Figure %s.</b> %s</figcaption></figure>\n' % (n, caption))


def build_html():
    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>Constructing the V5 Plan — Procedure</title>\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link href="https://fonts.googleapis.com/css2?family=Spectral:wght@600;700'
        '&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">\n'
        '<script>window.MathJax={tex:{inlineMath:[["\\\\(","\\\\)"]],displayMath:[["\\\\[","\\\\]"]]},'
        'svg:{fontCache:"global"}};</script>\n'
        '<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js" id="MathJax-script" async></script>\n'
        '<style>' + CSS + '</style>\n</head>\n<body>\n' + NAV +
        '<div class="wrap">\n'
        '  <div class="crumb"><a href="v5_brief.html">V5 Plan</a> / Construction procedure</div>\n'
        '  <div class="phead">\n'
        '    <div class="eyebrow">V5 mixture &amp; curriculum</div>\n'
        '    <h1>Construction Procedure</h1>\n'
        '    <p class="dek">The recommended order of construction, and the supply analysis that constrains the '
        'allocation. Quantities use an illustrative 3-trillion update-token budget.</p>\n'
        '  </div>\n'

        '  <div class="sec"><h2>1. Define the target benchmarks</h2>\n'
        '    <p>Large-scale pretraining is ordinarily evaluated after the fact. A corpus is assembled from whatever data '
        'is available, a model is trained on it, and its capabilities are measured only once training is complete. Under '
        'this ordering, evaluation is a diagnosis rather than a design target, and the composition of the corpus &mdash; '
        'which datasets to acquire, how many tokens to allocate to each, and in what order to present them &mdash; is '
        'left unconstrained by the capabilities the model is ultimately meant to have. Two data recipes that produce very '
        'different models are, at the point of the design decision, indistinguishable.</p>\n'
        '    <p>We invert this ordering. Before any data is assembled, we fix a closed set of benchmarks that defines the '
        'model&rsquo;s intended capabilities, and we treat every subsequent decision about the corpus as a choice to be '
        'justified by its measurable effect on that set. A benchmark, throughout, is an executable test: SWE-bench '
        'presents a model with a real repository bug and grades the patch it returns by running hidden unit tests, so a '
        'score reflects behaviour rather than recognition. Composing the corpus backward from such tests makes the '
        'capability the fixed quantity and the data the free variable, and it renders a capability that no benchmark '
        'measures explicitly out of scope: the plan cannot claim to develop what it does not measure.</p>\n'
        '    <p>The inversion is only useful if the benchmark set is chosen well. A benchmark that a multiple-choice '
        'format lets a model pass by recognition, that a human rater must score, that already sits in the training '
        'crawl, or that the frontier has already saturated, provides no usable gradient for corpus design. Section&nbsp;'
        '1.2 therefore states an explicit admission rule, and the remainder of the section applies it: &sect;1.3 and '
        '&sect;1.4 record the qualifying benchmarks with their sizes, grading metrics, and current best scores; '
        '&sect;1.5 traces a single graded instance end to end, so that the loss-bearing token accounting used in later '
        'sections rests on an observed example rather than an assumption; &sect;1.6 names the small-scale proxies used '
        'during validation; and &sect;1.7 states the limits of the method. Figures were collected in July&nbsp;2026 and '
        'are cited at the end of the section; where a state-of-the-art score is moving quickly, its date is attached to '
        'the number so that the claim remains checkable.</p>\n'

        '    <h3>1.1 Target benchmarks and performance commitments</h3>\n'
        '    <p>Table&nbsp;1 fixes the targets of the programme. For each benchmark it records the property that '
        'qualifies it as a target, the capability that a strong score certifies, the data lever by which the plan '
        'intends to move the score, the current best public result, and the result this programme commits to. The '
        'columns are the argument of the section in compressed form: &sect;1.2 justifies the second column, '
        '&sect;1.3&ndash;1.5 substantiate the fifth, and the remaining sections of the plan are the means of reaching '
        'the sixth.</p>\n'
        '    <div class="tblwrap"><table class="stbl"><tr>'
        '<th>Benchmark / lane</th><th>Why selected</th><th>Capability achieved</th><th>How (data lever)</th>'
        '<th>Industry best (dated)</th><th>V5 target</th></tr>\n'
        + strategy_rows() +
        '    </table></div>\n'
        '    <p class="cap"><b>Table 1.</b> Target benchmarks, the capability each certifies, the data lever intended '
        'to move it, and the committed target. Industry-best figures are the July&nbsp;2026 public state of the art '
        '(inventory in &sect;1.4; sources at the end of the section). The committed targets are stated for the 40B '
        'flagship; their direction is validated at 1B and 3B before full-scale commitment (&sect;10), and they remain '
        'provisional until that validation.</p>\n'

        '    <h3>1.2 Selection procedure</h3>\n'
        '    <p>A benchmark qualifies as a target only if it passes five tests. The tests exist because the usual '
        'failure of a backward-composed plan is not a missing benchmark but an unsuitable one &mdash; a test that a '
        'model can pass without holding the capability, or one whose score cannot be trusted or improved. Each test '
        'below is stated once and then applied to a benchmark it admits and one it rejects.</p>\n'

        '    <p><strong>1. Direct measurement.</strong> The benchmark must exercise the capability itself, not a proxy '
        'for it.</p>\n'
        '    <div class="egbox"><span class="yes">Admitted &mdash; SWE-bench.</span> The model receives a real bug '
        'report and the full repository, must return a code patch, and 44 unit tests are executed on that patch. Fixing '
        'the bug is the capability; running the tests measures it directly.<br>\n'
        '    <span class="no">Rejected &mdash; a Python quiz.</span> <span class="q">&ldquo;Which keyword defines a '
        'function? (a) def &nbsp;(b) func &nbsp;(c) function &nbsp;(d) lambda&rdquo;</span> A model can pick (a) from '
        'memory while being unable to write a function that runs. The quiz measures recognition, which only correlates '
        'with the skill we want.</div>\n'

        '    <p><strong>2. Machine-checkable metric.</strong> The score must come from execution or a verifier, not a '
        'human or model rating.</p>\n'
        '    <div class="egbox"><span class="yes">Admitted &mdash; GSM8K.</span> The gold answer is a number, for '
        'example <span class="q">18</span>. The harness reads the model&rsquo;s final number and checks it equals 18 &mdash; '
        'same input, same score, every time, in milliseconds.<br>\n'
        '    <span class="no">Rejected &mdash; &ldquo;rate this answer 1&ndash;5&rdquo;.</span> Two graders, or two runs '
        'of an LLM judge, return 3 and 4 for the same answer. The score is not reproducible, so it cannot be trusted '
        'inside a cheap proxy run.</div>\n'

        '    <p><strong>3. Contamination resistance.</strong> There must be a held-out, temporal, or private variant, so '
        'the score cannot be obtained by training on the test.</p>\n'
        '    <div class="egbox"><span class="yes">Admitted &mdash; SWE-bench Live.</span> It draws GitHub issues created '
        '<em>after</em> the model&rsquo;s data cutoff, so the model could not have seen them during training.<br>\n'
        '    <span class="no">Rejected &mdash; a fixed public quiz already in the crawl.</span> If the 500 questions sit '
        'in Common Crawl, a model can memorise the answer key and report 95% while having learned nothing. The number '
        'describes recall of the test, not capability.</div>\n'

        '    <p><strong>4. Public and reproducible.</strong> The items, harness, and metric must be published, so a '
        'reported number can be rerun.</p>\n'
        '    <div class="egbox"><span class="yes">Admitted &mdash; HumanEval.</span> 164 problems and the grading '
        'harness are on GitHub; anyone reruns them and gets the same figure.<br>\n'
        '    <span class="no">Rejected &mdash; a vendor eval reported only as &ldquo;92%&rdquo;.</span> With no items and '
        'no harness, the 92% cannot be checked or compared against our own model.</div>\n'

        '    <p><strong>5. Headroom.</strong> The frontier score must sit below about 90%, or there is no gradient left '
        'to optimise against.</p>\n'
        '    <div class="egbox"><span class="yes">Admitted &mdash; FrontierMath Tier 4.</span> The best systems score '
        '25&ndash;40% (mid-2026), so an improvement from 30% to 40% is real signal.<br>\n'
        '    <span class="no">Rejected as a primary target &mdash; original GSM8K.</span> Frontier models already reach '
        '~97%; moving 97.0 to 97.3 tells us almost nothing. It is still useful as a small-scale proxy (see &sect;1.6).</div>\n'

        '    <p>Each admitted benchmark is recorded with six fields. Filled in for SWE-bench Verified:</p>\n'
        '    <div class="diagram"><pre>\n'
        'version .......... SWE-bench Verified (500), snapshot 2024-08\n'
        'size ............. 500 issues\n'
        'metric ........... resolved rate (all hidden tests pass)\n'
        'best score (date)  ~76% pass@1 (Jan 2026)\n'
        'decontamination .. repository-disjoint; prefer the Live / temporal variant\n'
        '1B/3B proxy ...... HumanEval, MBPP\n'
        '</pre></div>\n'

        '    <p>Each benchmark, and later each training document, is filed under exactly one primary lane. Take a '
        'concrete document: a 12,000-token Hindi tutorial that walks through fixing a Python sorting bug with '
        'step-by-step reasoning. It touches four capabilities at once &mdash; Indic, code, reasoning, and long-context. '
        'The rule files it under one primary lane (code, its core task) and stores the rest as tags '
        '<span class="q">{language: hi, reasoning: yes, length: long}</span>.</p>\n'
        '    <div class="egbox"><span class="no">Without the rule:</span> the same 12,000 tokens are counted in code '
        '<em>and</em> Indic <em>and</em> reasoning <em>and</em> long-context = 48,000 counted tokens, and the budget in '
        '§5 is inflated 4&times;.<br>\n'
        '    <span class="yes">With the rule:</span> 12,000 tokens counted once, under code; the tags still let the plan '
        'report how much code data is also Indic or long.</div>\n'
        '    <p>Writing \\(L(d)\\) for the set of capabilities a document \\(d\\) touches and \\(|d|\\) for its token '
        'count, the naive count sums the document once per capability, while the one-lane rule counts it once:</p>\n'
        '    <div class="eq">\\[ C_{\\text{naive}}(d)=\\sum_{\\ell\\in L(d)}|d| = 4\\times 12{,}000 = 48{,}000, '
        '\\qquad C_{\\text{one\\text{-}lane}}(d)=|d| = 12{,}000. \\]</div>\n'

        '    <h3>1.3 The benchmark set</h3>\n'
        + figure(svg_compose_backward(),
                 'Composing backward. Each target benchmark (centre) fixes a capability lane (left); the supplying '
                 'dataset (right) is then chosen so that training on it moves that benchmark. Arrows point into the '
                 'benchmark from both sides: the lane it measures and the data selected to satisfy it. Section 2 '
                 'formalises the right-hand column.', "1") +

        '    <h3>1.4 Benchmark inventory</h3>\n'
        '    <div class="tblwrap"><table class="tbl"><tr><th>Benchmark</th><th>Lane</th><th>Size</th><th>Metric</th>'
        '<th>Best score (date)</th></tr>\n' + bench_rows() + '</table></div>\n'
        '    <p>Two design consequences follow. First, the code and agentic lanes are graded by execution and the '
        'reasoning lanes by exact answers; the model is scored on what it produces, not on the tool logs it reads, which '
        'is why §3 counts loss-bearing tokens rather than raw trace size. Second, the Indic lane is measured by MILU '
        '(understanding) and IndicGenBench (generation) together, because a high MILU score with weak generation would '
        'describe a model that recognises Hindi but cannot write it; Indic results are therefore reported as a '
        'macro-average across languages and a worst-language figure, not a single average.</p>\n'

        '    <h3>1.5 One instance, traced end to end</h3>\n'
        '    <p>The phrase &ldquo;resolved rate on 500 issues&rdquo; hides what a single graded item is. One '
        'representative SWE-bench Verified instance:</p>\n'
        + figure(svg_instance_trace(),
                 'A single graded item. The repository and issue text are read as context (no loss is taken on them); '
                 'the gold patch is the supervised target; grading executes 44 tests in a sandbox and returns one bit. '
                 'A code sample therefore contributes far fewer loss-bearing tokens than its raw size suggests.', "2") +
        '    <p>The item score is an indicator, and the benchmark score is its mean over the 500 instances:</p>\n'
        '    <div class="eq">\\[ \\text{resolved}_i=\\mathbb{1}\\!\\left[\\textstyle\\bigwedge_{t=1}^{44}'
        '\\text{test}_t\\text{ passes}\\right],\\qquad \\text{resolved rate}=\\frac{1}{500}\\sum_{i=1}^{500}'
        '\\text{resolved}_i=\\frac{380}{500}=0.76. \\]</div>\n'
        '    <p>This fixes three quantities the plan depends on. The trainable content per item is small: the 600,000-line '
        'repository is read as context, and the supervised target is a 17-line diff, so a code sample contributes far '
        'fewer loss-bearing tokens than its raw size implies (§3). The reward is verifiable, computed by executing 44 '
        'tests, so the same item can be scored inside a cheap proxy run. And the supplying dataset is defined by the '
        'target: Stack v2 provides raw code but not the issue-to-patch structure, so the code lane also requires '
        'generated repository-fix trajectories, recorded as a supply gap in §6.</p>\n'

        '    <h3>1.6 Proxy benchmarks for the 1B and 3B runs</h3>\n'
        '    <p>The headline benchmarks return near-zero at 1B and cannot decide anything during validation (§10). '
        'Concretely, at 1B a model resolves 0 of 500 SWE-bench issues &mdash; it cannot yet produce a working patch &mdash; '
        'so the score is 0 for every recipe and cannot separate them. On HumanEval the same 1B model solves roughly '
        '15&ndash;20 of 164 problems, and that number does move between recipes, so it can rank them. Each lane therefore '
        'names a proxy with signal at small scale.</p>\n'
        '    <div class="tblwrap"><table class="tbl"><tr><th>Lane</th><th>Headline benchmark</th><th>1B/3B proxy</th>'
        '<th>Proxy size</th></tr>\n' + proxy_rows() + '</table></div>\n'
        '    <p>The proxy establishes the direction of an effect and the rank of two recipes, never the absolute number, '
        'because rankings shift with scale.</p>\n'

        '    <h3>1.7 What this method does not do</h3>\n'
        '    <ul>\n'
        '      <li><strong>A benchmark set can be over-fit.</strong> Composing data backward from a fixed set risks '
        'teaching the test format. For example, train on 5,000 paraphrased copies of the SWE-bench issue texts and the '
        'reported resolved rate can rise ten points while the model is no better at unseen bugs. §11 pairs this method '
        'with a decontamination policy and a private, temporally held-out set; without that pairing, a reported gain is '
        'not trustworthy.</li>\n'
        '      <li><strong>It measures only listed capabilities.</strong> Anything absent from the set is invisible to '
        'the plan. For example, nothing here measures legal drafting or Hindi poetry, so the plan cannot tell whether '
        'the model can do them. General-web coverage (MMLU, MMLU-Pro) is retained partly to guard against regressing '
        'capabilities no targeted benchmark names.</li>\n'
        '      <li><strong>Generative Indic quality is only partly machine-checkable.</strong> IndicGenBench uses '
        'reference-based metrics (chrF, ROUGE) that correlate imperfectly with human judgement. For example, two correct '
        'Hindi translations of one English sentence can score chrF 0.55 and 0.72 purely from word choice, so a lower '
        'score need not mean a worse translation. The Indic result therefore carries more uncertainty than the '
        'execution-graded lanes and is flagged as such.</li>\n'
        '    </ul>\n'

        '    <p class="cap">Sources: SWE-bench Verified (<a href="https://epoch.ai/benchmarks/swe-bench-verified">Epoch AI</a>, '
        '<a href="https://arxiv.org/abs/2310.06770">Jimenez et&nbsp;al.</a>); Terminal-Bench '
        '(<a href="https://arxiv.org/abs/2601.11868">arXiv</a>); &tau;-bench '
        '(<a href="https://github.com/sierra-research/tau2-bench">Sierra</a>); BFCL '
        '(<a href="https://gorilla.cs.berkeley.edu/leaderboard.html">Gorilla</a>); GAIA '
        '(<a href="https://arxiv.org/abs/2311.12983">arXiv</a>); FrontierMath '
        '(<a href="https://epoch.ai/frontiermath/the-benchmark">Epoch AI</a>); MMLU-Pro '
        '(<a href="https://arxiv.org/abs/2406.01574">arXiv</a>); MILU '
        '(<a href="https://arxiv.org/abs/2411.02538">arXiv</a>); IndicGenBench '
        '(<a href="https://arxiv.org/abs/2404.16816">arXiv</a>).</p>\n'
        '  </div>\n'

        '  <div class="sec"><h2>2. Map each benchmark to a dataset</h2>\n'
        '    <p>Each target is associated with the dataset that develops the corresponding capability — a procedure '
        'sometimes termed composing backward. A capability lane without an identified source dataset is not a plan but an '
        'aspiration, and is recorded as such.</p></div>\n'

        '  <div class="sec"><h2>3. Establish the trainable inventory</h2>\n'
        '    <p>Effective inventory is measured, not assumed. Published corpus sizes are upper bounds; the usable quantity '
        'is reduced by licensing, deduplication, quality filtering, contamination removal, and re-tokenisation. Two '
        'measures are recorded per lane: the number of samples (variety) and the number of tokens (depth). For chat and '
        'agent data, only the model-generated positions are supervised — user turns and tool outputs are loss-masked — so '
        'the loss-bearing token count is materially smaller than the raw trace size. In ordinary causal pre-training, by '
        'contrast, every position is a training target.</p>\n'
        '    <div class="eq">\\[ T_{\\text{loss}}=\\sum_{i=1}^{T_{\\text{raw}}}\\mathbb{1}\\big[\\text{position }i'
        '\\text{ is model-generated}\\big]\\ \\ll\\ T_{\\text{raw}}\\ \\ (\\text{chat/agent SFT}),\\qquad '
        'T_{\\text{loss}}=T_{\\text{raw}}\\ \\ (\\text{plain pre-training}). \\]</div></div>\n'

        '  <div class="sec"><h2>4. Specify the allocation</h2>\n'
        '    <p>A share of the budget is assigned to each lane, summing to 100%, and each share is expressed in tokens '
        'so that it can be reconciled against inventory:</p>\n'
        '    <div class="eq">\\[ t_\\ell = s_\\ell\\, B,\\qquad \\sum_{\\ell} s_\\ell = 1,\\qquad '
        'B = 3\\times 10^{12}\\ \\text{update tokens}. \\]</div></div>\n'

        '  <div class="sec"><h2>5. Apply the selector keep-fraction and reconcile against supply</h2>\n'
        '    <p>The online selector retains only a fraction of the data it screens; consequently the quantity that must be '
        '<em>presented</em> exceeds the quantity <em>trained</em> on. Reconciling presented tokens against unique '
        'available supply is the decisive check, and it materially changes the assessment of the code and STEM '
        'lanes:</p>\n'
        '    <div class="eq">\\[ \\text{presented}_\\ell=\\frac{\\text{trained}_\\ell}{k_\\ell}\\ '
        '\\xrightarrow{\\,k_\\ell=0.5\\,}\\ 2\\,\\text{trained}_\\ell,\\qquad '
        '\\text{epochs}_\\ell=\\frac{\\text{presented}_\\ell}{U_\\ell}\\le 4, \\]</div>\n'
        '    <p>where \\(k_\\ell\\) is the selector keep-fraction and \\(U_\\ell\\) the unique eligible supply; a lane '
        'is feasible only if it clears the four-epoch repetition limit.</p>\n'
        '    <table class="tbl"><tr><th>Lane</th><th>Share</th><th>Trained</th><th>Presented</th><th>Unique avail.</th><th>Status</th></tr>\n'
        + pantry_rows() +
        '    </table>\n'
        '    <p class="cap">Presented = trained &divide; selector keep-fraction. Status compares presented tokens against '
        'unique eligible supply and the permitted repetition limit (≤4 epochs).</p></div>\n'

        '  <div class="sec"><h2>6. Classify lane feasibility</h2>\n'
        '    <p>The reconciliation identifies which lanes are supply-constrained. The <strong>agentic</strong> lane is '
        'infeasible under current inventory: at approximately 2,000 trainable tokens per trajectory \\(\\tau\\), the '
        'requirement is on the order of \\(10^{8}\\) trajectories, which cannot be obtained by scraping.</p>\n'
        '    <div class="eq">\\[ N_{\\text{traj}}=\\frac{t_{\\text{agentic}}}{\\tau}'
        '=\\frac{0.13\\times 3\\times 10^{12}}{2{,}000}\\approx 1.95\\times 10^{8}. \\]</div>\n'
        '    <p>The <strong>reasoning</strong> lane is starved. <strong>Long context</strong> is not represented as a lane at all: '
        'sequence length is a property that data in other lanes already possesses (a long legal document in Indic is both '
        'Indic and long), and treating it as an independent lane double-counts tokens. It is instead specified as a '
        'per-phase packing constraint. The principal remedy for the constrained lanes is generation and distillation; the '
        'most efficient lever is trace design, since trajectories that include planning, reasoning, and reflection yield '
        'several times more trainable tokens per trajectory than bare tool calls.</p></div>\n'

        '  <div class="sec"><h2>7. Decompose the Indic allocation</h2>\n'
        '    <p>The Indic allocation is reported across four provenance tiers. The verified tier binds hardest: genuinely '
        'verified material across the target languages amounts to only a few billion unique tokens, so at a repetition '
        'limit of four epochs the maximum trainable verified quantity is small, and any larger verified figure would imply '
        'excessive repetition. The verified tier is therefore capped at its supported level and the remainder is carried '
        'by the unverified and translated tiers, with the associated quality risk stated. Per-language protection is '
        'expressed as minimum token counts, not as a per-language percentage of the total budget, since the latter would '
        'exceed the entire Indic allocation once summed across all languages.</p>\n'
        '    <div class="eq">\\[ T^{\\text{ver}}_{\\max}=4\\,U^{\\text{ver}},\\qquad '
        '\\sum_{j=1}^{22} m_j \\le t_{\\text{indic}} = 0.08\\,B, \\]</div>\n'
        '    <p>where \\(U^{\\text{ver}}\\) is unique verified supply and \\(m_j\\) the token floor for language '
        '\\(j\\). A flat per-language floor of \\(p\\%\\) of the total budget fails as soon as \\(22p \\ge 8\\) '
        '(i.e. \\(p \\gtrsim 0.36\\%\\)), because the floors alone would then consume the whole Indic allocation.</p></div>\n'

        '  <div class="sec"><h2>8. Specify floors and the annealing reserve</h2>\n'
        '    <p>Protected minima are enforced at batch granularity rather than as run-level averages; a run-level floor '
        'permits the selector to suppress a lane throughout training and satisfy the constraint only in aggregate. Safety '
        'is represented as an explicit lane so that its floor is consistent with a mixture summing to 100%. The annealing '
        'reserve is held within the budget, not added to it, and its contribution is validated against a control run '
        'without annealing.</p></div>\n'

        '  <div class="sec"><h2>9. Define the curriculum phases</h2>\n'
        + figure(svg_curriculum(),
                 'The four curriculum phases across the budget, in training order. Widths are proportional to each '
                 'phase&#8217;s share of the 3T tokens; maximum sequence length rises left to right, and the scarce and '
                 'premium lanes are concentrated in the later phases. The budget-weighted average of the phase mixtures '
                 'reproduces the global mixture.', "3") +
        '    <p>The single mixture is expanded into a small number of phases — broad, general-web-dominant data first, '
        'followed by code, science, and reasoning, with the scarce lanes concentrated later and the premium data reserved '
        'for the final phase. Each phase specifies its own budget, maximum sequence length, and mixture summing to 100%; '
        'the budget-weighted average of the phase mixtures reproduces the global mixture. Transitions between phases are '
        'gradual, to avoid the gradient instability associated with abrupt distribution shifts. Difficulty is assigned by '
        'measurement — for example, the failure rate of a reference model, or pass@k on verifiable items — rather than by '
        'inspection, and the reasoning-depth label is defined by the shortest correct trace to avoid inducing length '
        'inflation.</p>\n'
        '    <div class="eq">\\[ s_\\ell = \\frac{\\sum_{p} B_p\\, s_{\\ell,p}}{\\sum_{p} B_p},\\qquad '
        '\\sum_{\\ell} s_{\\ell,p} = 1\\ \\ \\forall p, \\]</div>\n'
        '    <p>where \\(B_p\\) is the budget of phase \\(p\\) and \\(s_{\\ell,p}\\) the share of lane \\(\\ell\\) '
        'within it; this identity is what <code>mixture.py</code> checks.</p></div>\n'

        '  <div class="sec"><h2>10. Define the validation protocol</h2>\n'
        '    <p>Every quantity is treated as a hypothesis and tested at the 1B and 3B scales before full-scale commitment. '
        'Evaluations are chosen to exhibit signal at those scales; the most demanding benchmarks return near-zero at 1B '
        'and are uninformative there. Capability contrasts are amplified (for example, 4% versus 12% Indic) to establish '
        'the direction of an effect, and recipes are promoted on rank stability across scales rather than on absolute '
        'scores, which shift with scale.</p></div>\n'

        '  <div class="sec"><h2>11. Prioritise data acquisition</h2>\n'
        '    <p>The supply-constrained lanes define the acquisition queue for the cleaning pipeline, in order: agentic '
        'trajectory generation, reasoning-trace distillation, long-document collection, and additional verified Indic '
        'material (textbooks, government records, and news, since encyclopaedic text alone is insufficient). The mixture '
        'plan thereby determines the priorities of the upstream pipeline.</p></div>\n'

        '  <div class="callout">The complete plan is provided as <code>V5_PLAN.md</code>, and the arithmetic above is '
        'reproduced and validated by <code>mixture.py</code>, which derives the global mixture from the phase mixtures, '
        'applies the selector keep-fraction, and exits with an error if any phase mixture does not sum to 100% or any lane '
        'is infeasible.</div>\n'

        '  <div class="foot"><a href="v5_brief.html">&larr; Specification brief</a></div>\n'
        '</div>\n</body>\n</html>\n'
    )


if __name__ == "__main__":
    with open("v5_playbook.html", "w", encoding="utf-8") as f:
        f.write(build_html())
    print("Done. v5_playbook.html written.")
