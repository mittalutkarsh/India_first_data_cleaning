"""Generate v5_playbook.html — a step-by-step, layman's how-to for actually
BUILDING the V5 mixture-and-curriculum plan, with the real data explained."""

# Worked example uses a 3T-token budget (within the 2.4-4T the course allows).
BUDGET_B = 3000  # billions of tokens

# lane, share%, "points at", available tokens (approx, billions), note
PANTRY = [
    ("General web", 34, "DCLM / FineWeb", 8000, "Plenty — trillions available"),
    ("Code", 25, "Stack v2", 900, "Enough — will even dedup/downsample"),
    ("STEM", 12, "DCLM-STEM / textbooks", 500, "Enough"),
    ("Agentic / tools", 16, "ToolBench / Bolt + your own traces", 0.08, "STARVED — ~80M trainable tokens only"),
    ("Reasoning", 7, "distilled short↔long chains", 30, "STARVED — must distil more"),
    ("Indic", 4, "Sangraha / IndicCorp / Wikipedia", 270, "Enough overall; verified tier is thin"),
    ("Long-context", 2, "book-length + multi-doc", 40, "Tight — needs long samples"),
]

STEPS = [
    ("1", "Pick the exams you must pass", "coach picks the meets",
     "Before any percentages, list the <b>benchmarks</b> that define the model. That single list <i>is</i> the target — "
     "everything downstream is chosen to win these.",
     "Coding: SWE-bench, SWE-bench-Pro/Live · Agentic: Terminal-bench, τ-bench, BFCL, WebArena, GAIA · "
     "Reasoning/math: AIME, FrontierMath, LiveBench · General knowledge: MMLU · Indic: MILU + Indic evals.",
     "You have a written list of target benchmarks, grouped by capability lane."),

    ("2", "For each exam, get the right textbook", "match each meet to a drill",
     "This is “compose backward”: every benchmark is matched to the <b>dataset</b> that teaches that skill. A lane is only "
     "real if a dataset fills it.",
     "SWE-bench → GitHub-issue+patch data · Terminal-bench → shell-session traces · BFCL/τ-bench → ToolBench/Bolt · "
     "AIME → math-reasoning traces · MMLU → general web (DCLM/FineWeb) · MILU → Sangraha/IndicCorp/Wikipedia.",
     "Every benchmark has at least one dataset mapped to it."),

    ("3", "Take stock of your pantry", "weigh the ingredients you own",
     "Count what you actually have, in <b>two numbers</b>: <b>samples</b> (variety) and <b>tokens</b> (depth). And count "
     "only <b>trainable</b> tokens — because of loss-masking, the model is trained only on its own words, not on user "
     "turns or tool logs. A giant agent log is mostly <i>not</i> trainable.",
     "Stack v2 ≈ 600M samples / ~900B tokens · ToolBench ≈ 120k samples / only ~80M tokens (tiny each) · "
     "DCLM/FineWeb ≈ trillions · Sangraha ≈ 251B · IndicCorp ≈ 20.9B · Wikipedia ≈ 10–90M per language.",
     "You have a table of samples + trainable tokens available for every lane."),

    ("4", "Decide the plate — slice the budget into lanes", "portion the meal",
     "Fix the total <b>budget</b> (the course says 2.4–4T tokens; we’ll use <b>3T</b>). Give each lane a % that sums to "
     "100, then turn % into tokens so it’s concrete: <code>tokens = share × budget</code>.",
     "At a 3T budget: Web 34% → ~1,020B · Code 25% → ~750B · Agentic 16% → ~480B · STEM 12% → ~360B · "
     "Reasoning 7% → ~210B · Indic 4% → ~120B · Long-context 2% → ~60B.",
     "You have a mixture table where the shares add to 100% and each is written in tokens."),

    ("5", "Reality-check: pantry vs plate → find the STARVED lanes", "do you have enough of each?",
     "Put “tokens needed” next to “tokens available”. Where you need more than you have, the lane is <b>starved</b> — that’s "
     "the single most important output of this whole exercise, because it tells the cleaning pipeline what to go get.",
     "Agentic wants ~480B but only ~0.08B is trainable → <b>massively starved</b>. Reasoning wants ~210B, have ~30B → "
     "<b>starved</b>. Code wants ~750B, have ~900B → fine. See the table below.",
     "Every lane is marked ENOUGH or STARVED, with the shortfall in tokens."),

    ("6", "Split the Indic dish into its four qualities", "grade the ingredients",
     "Don’t write one Indic number. Break the 120B into the four <b>tiers</b> by how much you can honestly source of each, "
     "and say when Sanskrit / Urdu / other languages enter.",
     "e.g. Indic 120B → Verified (T0) 45% (54B, Wikipedia/textbooks — thin, so this caps you) · Unverified (T1) 35% "
     "(42B, Sangraha/IndicCorp) · Translated (T3) 12% (14B) · Synthetic (T2) 8% (10B, distilled).",
     "The Indic lane is written as four tier-numbers that add up, with a note on which languages and when."),

    ("7", "Pin the non-negotiables (the floor) — because of OPUS", "the vitamins you never skip",
     "During training an auto-selector called <b>OPUS</b> keeps only data that helps the target benchmarks — but it peeks "
     "at just the first ~512 tokens and its benchmarks are English/coding-heavy, so it would <b>throw away Indic and "
     "agentic</b>. Set minimums it may never cross.",
     "Always-on floor: Indic ≥ 3% · agentic ≥ 8% · safety ≥ 1% · each smallest Indic language ≥ 0.3%.",
     "You have explicit floor percentages the selector is forbidden to go below."),

    ("8", "Save dessert for last — the anneal reserve", "peak nutrition before the race",
     "Hold back a slice of your <b>very best</b> data for the final <b>cooldown</b> (~last 2%, learning-rate→0), where what "
     "the model sees last sticks hardest. Spend it only then.",
     "Reserve ~2% of the budget (~60B): premium verified Indic + PhD-grade LaTeX/math + the cleanest agentic traces.",
     "A named reserve of best data with a % and a rule: “fed only in the cooldown.”"),

    ("9", "Sort by difficulty and thinking-length", "label easy/hard and short/long",
     "Add two more labels so the schedule can be deliberate: how <b>hard</b> each sample is, and how <b>long</b> the reasoning "
     "should be (the model is trained to obey low/medium/high/ultra tags). Long-context is separate: grow the sequence "
     "length in steps.",
     "Difficulty — Easy: “Capital of India?” · Hard: “Prove √2 irrational.” Depth — low ≤256 · medium ≤1k · high ≤4k · "
     "ultra ≤16k+ thinking tokens. Sequence length ladder: 4K → 8K → 16K → 32K.",
     "Every dataset is tagged with a difficulty band and (for reasoning) a depth band, with example boundaries."),

    ("10", "Write the weekly schedule — the curriculum", "plan the training weeks",
     "The <b>order</b> matters as much as the mix. Broad web first (learn language + common sense), then code/STEM/reasoning, "
     "long-context late, premium anneal last. Bands must <b>overlap</b> (~15–20%) or the gradients spike. Show the mix as a "
     "few <b>phase snapshots</b>, not one static table.",
     "Early (nursery): Web 55% / Code 15% / STEM 10% / Indic 8% / rest small. Mid: the 34/25/16/12/7/4/2 plate above. "
     "Anneal: tiny, premium-only. Blend 18% of the next phase into the current one.",
     "You have 3 phase-snapshot mixtures + a stated overlap rule between phases."),

    ("11", "Trial on a junior first — proxy runs", "test the plan on a trainee",
     "Every number is a <b>guess</b> until tested cheaply. Commit to running competing recipes at <b>1B and 3B</b> (V4’s "
     "small sizes) for a small budget, compare on the Step-1 benchmarks, and only promote winners. During the real run, "
     "OPUS gives ~8× token efficiency.",
     "e.g. Recipe A (Indic 4%) vs B (Indic 6%) at 1B for ~20B tokens → if B lifts Indic evals without hurting English, "
     "promote to 3B → then 40B. OPUS keep-fraction ~50%.",
     "You have a written experiment plan: which recipes, which scale, which evals, promotion criteria."),

    ("12", "Send the shopping list back to the kitchen", "restock the starved shelves",
     "Point the 8-stage cleaning pipeline at the lanes Step 5 marked <b>starved</b> — that’s the “cleaning continues, aimed "
     "at the starved slots” line. Then assemble everything into the <b>README</b> you submit.",
     "Priority queue for cleaning: agentic traces (biggest gap) → reasoning traces → long-context docs. README sections: "
     "target benchmarks · mixture (per phase) · Indic tiers · floor · anneal · bands · curriculum · validation plan.",
     "A prioritised cleaning queue + a complete, defended README ready to submit."),
]

CSS = """
:root { --bg:#FAFBFD; --ink:#16162A; --indigo:#2E357E; --indigo-soft:#6169B8; --marigold:#E0982B;
  --teal:#147D74; --rose:#B5476B; --line:#E3E4EE; --muted:#656579; --panel:#F1F2F8; }
*, *::before, *::after { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--ink); font-family:"Inter",system-ui,sans-serif; font-size:15px; line-height:1.6; -webkit-font-smoothing:antialiased; }
a { color:var(--indigo); text-decoration:none; } a:hover { text-decoration:underline; }
.nav { position:sticky; top:0; z-index:50; background:rgba(250,251,253,.96); border-bottom:1px solid var(--line); }
.nav-in { max-width:1280px; margin:0 auto; padding:10px 24px; display:flex; align-items:center; gap:13px; flex-wrap:wrap; }
.brand { font-family:"Spectral",serif; font-weight:700; color:var(--indigo); font-size:16px; margin-right:auto; }
.nav a { font-family:"IBM Plex Mono",monospace; font-size:11px; letter-spacing:.02em; color:var(--muted); padding:3px 2px; border-bottom:2px solid transparent; }
.nav a:hover { color:var(--ink); text-decoration:none; }
.nav a.active { color:var(--indigo); border-bottom-color:var(--marigold); }
.wrap { max-width:1000px; margin:0 auto; padding:0 24px 80px; }
.crumb { font-family:"IBM Plex Mono",monospace; font-size:11px; color:var(--muted); padding:20px 0 0; }
.hero { padding:10px 0 20px; border-bottom:2px solid var(--ink); }
.hero .eyebrow { font-family:"IBM Plex Mono",monospace; font-size:11px; letter-spacing:.15em; text-transform:uppercase; color:var(--marigold); font-weight:600; }
.hero h1 { font-family:"Spectral",serif; font-weight:700; font-size:clamp(27px,4.4vw,44px); margin:8px 0 10px; line-height:1.08; }
.hero p { font-size:15px; color:#33334a; margin:0; max-width:76ch; }
.analogy { margin:20px 0 0; border:1px solid var(--line); border-left:4px solid var(--marigold); border-radius:0 12px 12px 0; background:#fff; padding:14px 18px; font-size:14px; color:#33334a; }
.analogy b { color:var(--ink); }
.step { border:1px solid var(--line); border-radius:14px; background:#fff; padding:18px 20px; margin:13px 0 0; }
.step .top { display:flex; align-items:baseline; gap:12px; flex-wrap:wrap; }
.step .n { font-family:"IBM Plex Mono",monospace; font-weight:700; font-size:14px; color:#fff; background:var(--indigo); border-radius:9px; width:30px; height:30px; display:inline-flex; align-items:center; justify-content:center; }
.step h3 { font-family:"Spectral",serif; font-size:20px; margin:0; }
.step .kite { font-family:"IBM Plex Mono",monospace; font-size:10px; letter-spacing:.06em; text-transform:uppercase; color:var(--teal); }
.step .plain { font-size:14px; color:#33334a; margin:10px 0 0; }
.step .data { margin:12px 0 0; padding:11px 14px; background:var(--panel); border-radius:9px; font-size:13px; }
.step .data .lbl { font-family:"IBM Plex Mono",monospace; font-size:10px; letter-spacing:.08em; text-transform:uppercase; color:var(--indigo); font-weight:600; display:block; margin-bottom:5px; }
.step .done { font-size:12.5px; color:var(--teal); margin:11px 0 0; }
.step .done b { color:#0f5c43; }
.big { margin:32px 0 0; } .big h2 { font-family:"Spectral",serif; font-size:24px; margin:0 0 4px; } .big .lead { font-size:13px; color:var(--muted); margin:0 0 14px; }
.tbl { width:100%; border-collapse:collapse; font-size:13px; background:#fff; border:1px solid var(--line); border-radius:12px; overflow:hidden; }
.tbl th, .tbl td { text-align:left; padding:8px 12px; border-bottom:1px solid var(--line); }
.tbl th { font-family:"IBM Plex Mono",monospace; font-size:10px; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); background:var(--panel); }
.tbl .num { font-family:"IBM Plex Mono",monospace; text-align:right; }
.tbl code { font-family:"IBM Plex Mono",monospace; font-size:11.5px; }
.badge { font-family:"IBM Plex Mono",monospace; font-size:10px; font-weight:600; padding:1px 8px; border-radius:5px; }
.ok { background:#e6f5ef; color:#0f7a54; } .starved { background:#fceef2; color:var(--rose); }
.formula { font-family:"IBM Plex Mono",monospace; font-size:12.5px; background:#16162a; color:#eee; border-radius:8px; padding:10px 14px; margin-top:8px; }
.cta { margin:26px 0 0; border-radius:12px; background:#f2faf8; border:1px solid #cfe6e1; padding:16px 20px; font-size:14px; }
.cta a { font-weight:600; }
"""


def build_html():
    steps = ""
    for n, title, kite, plain, data, done in STEPS:
        steps += (
            '<div class="step"><div class="top"><span class="n">' + n + '</span>'
            '<h3>' + title + '</h3><span class="kite">' + kite + '</span></div>'
            '<div class="plain">' + plain + '</div>'
            '<div class="data"><span class="lbl">The data / the numbers</span>' + data + '</div>'
            '<div class="done">✔ <b>Done when:</b> ' + done + '</div></div>\n'
        )
    pantry = ""
    for lane, share, points, avail, note in PANTRY:
        need = share / 100 * BUDGET_B
        starved = avail < need
        avail_s = ("%.2fB" % avail) if avail < 1 else "{:,}B".format(int(avail))
        pantry += (
            '<tr><td>' + lane + '</td>'
            '<td class="num">' + str(share) + '%</td>'
            '<td class="num">~' + ("%d" % round(need)) + 'B</td>'
            '<td class="num">~' + avail_s + '</td>'
            '<td><span class="badge ' + ('starved' if starved else 'ok') + '">' + ('STARVED' if starved else 'ENOUGH') + '</span></td>'
            '<td style="font-size:12px;color:#656579">' + note + '</td></tr>\n'
        )
    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>V5 Plan — Step-by-Step How-To</title>\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link href="https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,600;0,700;1,600'
        '&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">\n'
        '<style>' + CSS + '</style>\n</head>\n<body>\n'
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
        '  <a href="v5_brief.html" class="active">V5 Plan</a>\n'
        '</div></div>\n'
        '<div class="wrap">\n'
        '  <div class="crumb"><a href="v5_brief.html">V5 Plan</a> › Step-by-step how-to</div>\n'
        '  <div class="hero">\n'
        '    <div class="eyebrow">How to actually build the plan</div>\n'
        '    <h1>12 steps to a defended V5 mixture &amp; curriculum.</h1>\n'
        '    <p>The <a href="v5_brief.html">V5 Plan</a> page explains <em>what</em> is being asked. This page is the '
        '<b>recipe for doing it</b> — each step in plain words, with the real datasets and token maths worked out, ending '
        'in the README you submit.</p>\n'
        '  </div>\n'
        '  <div class="analogy">Running analogy: you are the <b>head chef</b> planning a season’s meal plan for an athlete '
        '(the model). Steps go: pick the events → choose drills → weigh your pantry → portion the plate → spot what you’re '
        'short on → grade ingredients → fix the daily vitamins → save dessert for race week → label easy/hard &amp; '
        'quick/slow → write the weekly schedule → trial on a junior → restock the empty shelves.</div>\n'
        + steps +
        '  <div class="big">\n'
        '    <h2>The one table that matters: pantry vs plate</h2>\n'
        '    <p class="lead">This is Step 4 + 5 made concrete at a <b>3 trillion-token</b> budget. “Needed” = share × budget. '
        'Where <b>available &lt; needed</b>, the lane is <span class="badge starved">STARVED</span> — and that is exactly '
        'what you send back to the cleaning pipeline.</p>\n'
        '    <div class="formula">tokens_needed  =  share%  ×  budget      (e.g.  16% × 3,000B  =  480B for agentic)</div>\n'
        '    <table class="tbl" style="margin-top:10px"><tr><th>Lane</th><th class="num">Share</th><th class="num">Needed</th>'
        '<th class="num">Available</th><th>Status</th><th>Why</th></tr>\n' + pantry + '</table>\n'
        '    <p class="lead" style="margin-top:10px">Read-out: <b>web, code, STEM, Indic</b> are fillable; <b>agentic and '
        'reasoning are badly starved and long-context is tight</b> — so your plan’s honest conclusion is “we must generate/'
        'distil agentic + reasoning data and gather long documents, and protect the scarce lanes with the always-on floor '
        'so OPUS doesn’t bin them.”</p>\n'
        '  </div>\n'
        '  <div class="cta">📄 Next: I can turn these 12 steps into the actual <b>V5_PLAN.md README</b> in the repo — real '
        'per-phase tables, the benchmark→data map, floor/reserve/bands, and the 1B/3B experiment protocol — plus a small '
        '<code>mixture.py</code> that checks shares sum to 100%, respects the floor, and reserves the anneal. '
        '<a href="v5_brief.html">← back to what the ask is</a></div>\n'
        '</div>\n</body>\n</html>\n'
    )


if __name__ == "__main__":
    with open("v5_playbook.html", "w", encoding="utf-8") as f:
        f.write(build_html())
    print("Done. v5_playbook.html written.")
