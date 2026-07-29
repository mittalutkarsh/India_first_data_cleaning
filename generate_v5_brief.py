"""Generate v5_brief.html — a plain-English, transcript-faithful explainer of
the V5 mixture-and-curriculum assignment (Era V5 session)."""

DELIVERABLES = [
    ("01", "A defended share of the budget for every capability lane",
     "The budget is a fixed pile of tokens (the course says <b>2.4–4 trillion</b>). Slice it, one slice per "
     "<b>capability lane</b>, and be ready to <b>defend every number</b> to a skeptical reviewer.",
     "General web 34% · Code 25% · STEM 12% · Agentic/tool-calls 16% · Reasoning traces · Long-context · Indic — summing to 100%",
     "Web stays big because <b>common sense lives on the web</b>. A code-only model writes code that runs but makes no sense (“ask the user how many index fingers each human has”)."),

    ("02", "The Indic lane split across all four tiers — not one number",
     "The instructor asked explicitly for a “full end-to-end verifiable / unverified / translated / synthetic” breakdown of Indic. "
     "Don’t hide behind one headline % — say how much leans on weaker tiers.",
     "Inside Indic → Verified (T0) · Unverified web (T1, Sangraha/IndicCorp) · Translated (T3) · Synthetic (T2, distilled). State when Sanskrit / Urdu / other languages enter, if ever.",
     "Tiers are the T0–T3 from the <a href='data.html'>Data</a> page. Indic is <b>the differentiator</b> — “an intelligent Indian who speaks an Indian language.”"),

    ("03", "Name the agentic, reasoning &amp; long-context lanes — and point each at a dataset",
     "These three are the newest, scarcest lanes. Name them and map each to a concrete dataset from the inventory that fills it.",
     "Agentic/function-call → ToolBench / Bolt · Reasoning → distilled chain-of-thought + math sets · Long-context → book-length &amp; multi-doc traces (e.g. long cloud-code sessions)",
     "Agentic = plan → call tools → read results → recover on failure → continue. This is exactly the cloud-code / cursor traces you all generate."),

    ("04", "The protected always-on floor (because OPUS would starve these)",
     "During training an online selector called <b>OPUS</b> keeps only samples that move the “benchmark-weak” weights — but it "
     "peeks at just the <b>first ~512 tokens</b> and its benchmarks are mostly English/coding. So it <b>throws away Indic and "
     "agentic</b> (agentic traces look like logs early). The floor is the minimum it may never cross.",
     "Indic ≥ X% and agentic ≥ Y% <b>always on</b>, regardless of what OPUS prefers — plus safety and the smallest Indic languages.",
     "This is the real, specific reason the floor exists — not a vague “protect fragile data”. It’s to survive OPUS."),

    ("05", "The anneal reserve — best data held back for the cooldown",
     "Training ends with a short <b>anneal / cooldown</b> (~last 2%, learning rate → 0) where the highest-quality “anti-matter” "
     "data has outsized effect — “the young Einstein ready to write the relativity paper.” Hold your best data back for it.",
     "Reserve premium verified Indic + PhD-grade LaTeX/math + clean agentic traces, fed only in the final cooldown — never spent early.",
     "Feed PhD data too early and the model “consumes without learning.” The labs guard exactly this data; if we collect it, we win."),

    ("06", "Difficulty bands &amp; reasoning-depth bands, each with an example",
     "Two more groupings drive the schedule: how <b>hard</b> a sample is, and how <b>long the reasoning</b> should be. The depth "
     "is <b>controllable</b> via low/medium/high/ultra <b>thinking tags</b> — so you need paired short- and long-answer traces and "
     "must define each band’s token boundary.",
     "Difficulty — Easy: “Capital of India? → New Delhi.” · Hard: “Prove √2 is irrational.”<br>"
     "Depth — Low: “43÷17 ≈ 2.5” in ~20 tokens · Ultra: a multi-hour proof in tens of thousands of tokens (same question, tagged)",
     "You can’t fake depth by truncating tokens — the model must be <i>trained</i> to think more when told to. That needs tagged data."),

    ("07", "A curriculum: ordered stages, a difficulty ladder, and smooth band overlap",
     "The <b>order</b> matters as much as the mix. Nursery → school → undergrad → PhD: broad web first (learn language &amp; common "
     "sense), then code/STEM/reasoning, with long sequences introduced late. And bands must <b>overlap</b>, not switch sharply — "
     "in V4 a sudden band change spiked the gradients.",
     "Long-context = grow the sequence length in stages (4K → 8K → 16K → …; one length per batch). Blend ~15–20% of the next band into the current one so the transition is smooth (gradient norm stays ~0.2).",
     "A sharp jump “shocks” the model — like being dropped into a PhD course straight after 12th grade."),

    ("08", "Prove every number with cheap 1B &amp; 3B proxy runs — then keep cleaning the starved lanes",
     "Every share above is a <b>hypothesis</b>. Commit to testing recipes at <b>1B and 3B</b> (V4’s small sizes) before the full run, "
     "and keep the cleaning pipeline aimed at whichever lane is <b>starved</b>.",
     "Recipe A vs B at 1B for ~20B tokens → compare Indic &amp; English evals → promote the winner to 3B → only then full scale. OPUS then gives ~8× token efficiency during the run.",
     "The rule behind the whole course: <b>a data decision is a hypothesis until a cheap experiment has tested it.</b>"),
]

BENCH_MAP = [
    ("SWE-bench (+ Pro / Live)", "Coding", "Real GitHub issues + repos; write a patch that passes hidden tests"),
    ("Terminal-bench", "Agentic", "Tasks solved inside a real shell — install, configure, run"),
    ("τ-bench / BFCL", "Agentic", "Tool-use &amp; function-calling across many turns (retail, airline, APIs)"),
    ("WebArena / GAIA / BrowseComp", "Agentic", "Browse real sites, gather &amp; distill an answer"),
    ("AIME / FrontierMath", "Reasoning", "Olympiad → research-level math; long derivations"),
    ("MMLU", "General web", "UPSC-style general knowledge — needs broad web/common sense"),
    ("MILU / Indic evals", "Indic", "Indian-language understanding &amp; generation"),
]

INVENTORY = [
    ("Stack v2", "code", "~600M samples", "~900B tok (~25%)", "Permissive source across 100 languages"),
    ("ToolBench", "agentic", "~120k samples", "~80M tok", "Multi-tool instructions over real REST APIs — tiny per-sample"),
    ("DCLM / FineWeb", "web + STEM", "very large", "trillions", "High-quality general web &amp; science"),
    ("Reasoning traces", "reasoning", "to build / distil", "—", "Short↔long tagged chains; not freely available"),
    ("Sangraha / IndicCorp / Wikipedia", "indic", "251B / 20.9B / 10–90M", "—", "The Indic tiers T0–T1"),
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
.wrap { max-width:1080px; margin:0 auto; padding:0 24px 80px; }
.hero { padding:44px 0 20px; border-bottom:2px solid var(--ink); }
.hero .eyebrow { font-family:"IBM Plex Mono",monospace; font-size:11px; letter-spacing:.15em; text-transform:uppercase; color:var(--marigold); font-weight:600; }
.hero h1 { font-family:"Spectral",serif; font-weight:700; font-size:clamp(28px,4.5vw,46px); margin:10px 0 10px; line-height:1.08; }
.hero p { font-size:15px; color:#33334a; margin:0; max-width:74ch; }
.analogy { margin:22px 0 0; border:1px solid var(--line); border-left:4px solid var(--marigold); border-radius:0 12px 12px 0; background:#fff; padding:16px 20px; }
.analogy h3 { margin:0 0 6px; font-family:"Spectral",serif; font-size:18px; }
.analogy p { margin:0; font-size:14px; color:#33334a; } .analogy b { color:var(--ink); }
.sec { margin:32px 0 0; } .sec h2 { font-family:"Spectral",serif; font-size:24px; margin:0 0 4px; }
.sec .lead { font-size:13px; color:var(--muted); margin:0 0 16px; max-width:80ch; }
.card { border:1px solid var(--line); border-radius:14px; background:#fff; padding:18px 20px; margin-bottom:13px; }
.card .top { display:flex; align-items:baseline; gap:12px; }
.card .num { font-family:"IBM Plex Mono",monospace; font-weight:700; font-size:13px; color:#fff; background:var(--indigo); border-radius:8px; padding:3px 9px; }
.card h3 { font-family:"Spectral",serif; font-size:19px; margin:0; }
.card .plain { font-size:14px; color:#33334a; margin:10px 0 0; }
.card .eg { margin:12px 0 0; padding:11px 14px; background:var(--panel); border-radius:9px; font-size:13.5px; }
.card .eg .lbl { font-family:"IBM Plex Mono",monospace; font-size:10px; letter-spacing:.08em; text-transform:uppercase; color:var(--teal); font-weight:600; display:block; margin-bottom:5px; }
.card .conn { font-size:12.5px; color:var(--muted); margin:11px 0 0; }
.card .conn .lbl { font-family:"IBM Plex Mono",monospace; font-size:10px; letter-spacing:.06em; text-transform:uppercase; color:var(--marigold); font-weight:600; }
.tbl { width:100%; border-collapse:collapse; font-size:13px; background:#fff; border:1px solid var(--line); border-radius:12px; overflow:hidden; }
.tbl th, .tbl td { text-align:left; padding:8px 12px; border-bottom:1px solid var(--line); vertical-align:top; }
.tbl th { font-family:"IBM Plex Mono",monospace; font-size:10px; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); background:var(--panel); }
.tbl code { font-family:"IBM Plex Mono",monospace; font-size:11.5px; }
.tag { font-family:"IBM Plex Mono",monospace; font-size:10px; font-weight:600; padding:1px 7px; border-radius:5px; background:#eef0fb; color:var(--indigo); }
.mask { display:flex; gap:8px; flex-wrap:wrap; margin-top:10px; }
.mtok { font-family:"IBM Plex Mono",monospace; font-size:12px; padding:4px 9px; border-radius:6px; }
.m-green { background:#e6f5ef; color:#0f7a54; border:1px solid #b9e2d1; }
.m-gray { background:var(--panel); color:var(--muted); border:1px solid var(--line); }
.m-violet { background:#f3edfa; color:#7A3FB0; border:1px solid #ddc9ee; }
.stages { display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:1px; background:var(--line); border:1px solid var(--line); border-radius:12px; overflow:hidden; }
.stg { background:#fff; padding:12px 13px; }
.stg .s { font-family:"IBM Plex Mono",monospace; font-size:10px; color:var(--marigold); font-weight:600; }
.stg .t { font-weight:600; font-size:13.5px; margin:2px 0; }
.stg .d { font-size:11.5px; color:var(--muted); }
.toy { border:2px solid var(--indigo); border-radius:14px; background:#fff; overflow:hidden; }
.toy-hd { background:var(--indigo); color:#fff; padding:10px 16px; font-family:"IBM Plex Mono",monospace; font-size:12px; font-weight:600; letter-spacing:.06em; }
.toy-bd { padding:16px 18px; }
.toy table { width:100%; border-collapse:collapse; font-size:13px; }
.toy td, .toy th { padding:5px 8px; border-bottom:1px solid var(--line); text-align:left; }
.toy th { font-family:"IBM Plex Mono",monospace; font-size:10px; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); }
.toy .pct { font-family:"IBM Plex Mono",monospace; font-weight:600; color:var(--indigo); text-align:right; }
.toy .disc { font-size:11.5px; color:var(--muted); font-style:italic; margin-top:10px; }
.gloss { border:1px solid var(--line); border-radius:12px; background:#fff; padding:6px 18px; }
.gloss dt { font-family:"IBM Plex Mono",monospace; font-size:12.5px; font-weight:600; color:var(--indigo); margin-top:12px; }
.gloss dd { margin:2px 0 0; font-size:13.5px; color:#33334a; }
.rule { margin:26px 0 0; border-radius:14px; background:#16162a; color:#fff; padding:22px 24px; }
.rule .k { font-family:"IBM Plex Mono",monospace; font-size:11px; letter-spacing:.14em; text-transform:uppercase; color:var(--marigold); }
.rule .q { font-family:"Spectral",serif; font-size:clamp(19px,2.6vw,26px); margin:8px 0 0; line-height:1.3; }
.submit { border:1px solid var(--line); border-left:4px solid var(--teal); border-radius:0 12px 12px 0; background:#f2faf8; padding:16px 20px; font-size:14px; color:#22483d; }
.submit b { color:#0f5c43; }
"""


def build_html():
    cards = ""
    for num, title, plain, eg, conn in DELIVERABLES:
        cards += (
            '<div class="card"><div class="top"><span class="num">' + num + '</span><h3>' + title + '</h3></div>'
            '<div class="plain">' + plain + '</div>'
            '<div class="eg"><span class="lbl">Concrete example</span>' + eg + '</div>'
            '<div class="conn"><span class="lbl">Why it matters</span> ' + conn + '</div></div>\n'
        )
    bench = ""
    for name, lane, why in BENCH_MAP:
        bench += '<tr><td><code>' + name + '</code></td><td><span class="tag">' + lane + '</span></td><td>' + why + '</td></tr>\n'
    inv = ""
    for name, lane, samples, toks, note in INVENTORY:
        inv += ('<tr><td><code>' + name + '</code></td><td><span class="tag">' + lane + '</span></td>'
                '<td>' + samples + '</td><td>' + toks + '</td><td>' + note + '</td></tr>\n')
    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>V5 Mixture &amp; Curriculum — The Assignment, Explained</title>\n'
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
        '  <div class="hero">\n'
        '    <div class="eyebrow">The Era-V5 assignment, in plain words</div>\n'
        '    <h1>Write the model’s training diet &amp; study schedule — and defend every number.</h1>\n'
        '    <p>Draft the <b>mixture-and-curriculum plan for V5</b> as a written spec: exactly what data the model trains '
        'on, in what proportions, <b>in what order</b>, with the best data saved for last — plus a promise to test the '
        'recipe cheaply first. It’s graded <b>subjectively</b>: a reviewer will push on every number, so the marks are in '
        'your reasoning and evidence. Submit it as a <b>GitHub README</b>, not a widget.</p>\n'
        '  </div>\n'
        '  <div class="submit" style="margin:18px 0 0">👉 Want the hands-on version? The '
        '<a href="v5_playbook.html"><b>step-by-step how-to</b></a> walks through actually building the plan in 12 steps, '
        'with the real datasets and token maths worked out.</div>\n'
        '  <div class="analogy">\n'
        '    <h3>The whole thing in one analogy</h3>\n'
        '    <p>You’re a <b>coach planning a season</b> for an athlete (the model). The <b>mixture</b> is the meal plan; '
        'the <b>curriculum</b> is the practice schedule (nursery → PhD). You pin a few non-negotiables (the <b>floor</b>), '
        'save peak nutrition for the week before the event (the <b>anneal reserve</b>), ease between training blocks so the '
        'body isn’t shocked (<b>band overlap</b>), and trial the plan on a junior first (the <b>1B/3B proxy runs</b>).</p>\n'
        '  </div>\n'
        '  <div class="sec">\n'
        '    <h2>The core method: compose <em>backward</em> from the benchmarks</h2>\n'
        '    <p class="lead">You don’t pick percentages by taste. First decide which <b>benchmarks</b> you’re trying to win '
        '(that defines the model). Then map each benchmark to the dataset that fills it. The mixture is the deliberate '
        'answer to “what are we trying to win?” The target here is clear: <b>coding &amp; agentic first</b>, then '
        'controllable-depth reasoning, long-context, and <b>Indic as the differentiator</b>.</p>\n'
        '    <table class="tbl"><tr><th>Benchmark</th><th>Lane</th><th>What it tests → what data fills it</th></tr>\n' + bench + '</table>\n'
        '    <p class="note" style="font-size:12px;color:#656579;margin-top:8px">Why is web still ~34%? Because <b>common '
        'sense and world knowledge live on the web</b>. Strip it out and the code runs but doesn’t make sense.</p>\n'
        '  </div>\n'
        '  <div class="sec">\n'
        '    <h2>The 8 things your plan must contain</h2>\n'
        '    <p class="lead">Each is required. Plain meaning → a concrete example → why it matters.</p>\n' + cards +
        '  </div>\n'
        '  <div class="sec">\n'
        '    <h2>Two things that trip everyone up</h2>\n'
        '    <p class="lead">Miss these and your plan won’t survive review.</p>\n'
        '    <div class="card"><div class="top"><h3>① You only train on the model’s own tokens (loss masking)</h3></div>\n'
        '      <div class="plain">In an agent trace, the loss is computed <b>only on what the model generates</b>. The user’s '
        'turns and the <b>tool outputs/logs are masked</b> (the model reads them but is never punished for them) — training '
        'on a raw error log would just teach it to imitate a compiler. Verifier results become <b>reward</b>. '
        '(Pre-training is different: there, every token is in the loss.)</div>\n'
        '      <div class="mask">'
        '<span class="mtok m-green">assistant text = trained</span>'
        '<span class="mtok m-gray">user turn = masked</span>'
        '<span class="mtok m-gray">tool output / log = masked</span>'
        '<span class="mtok m-violet">verifier = reward</span></div>\n'
        '      <div class="conn" style="margin-top:11px"><span class="lbl" style="font-family:\'IBM Plex Mono\',monospace;font-size:10px;color:var(--marigold);font-weight:600">Consequence</span> '
        'A huge agentic trace is <i>mostly not trainable</i> — so size lanes by <b>trainable</b> tokens, not raw tokens.</div>\n'
        '    </div>\n'
        '    <div class="card"><div class="top"><h3>② Size in two dimensions: samples <span style="color:#999">(variety)</span> and tokens <span style="color:#999">(depth)</span></h3></div>\n'
        '      <div class="plain">“400k examples” means nothing if each is 20k tokens of low quality. <b>Number of samples</b> '
        'buys variety; <b>number of tokens</b> buys depth. A plan states both per lane. Example: ToolBench is 120k samples '
        'but only ~80M tokens (tiny each); Stack v2 is 600M samples and ~900B tokens.</div>\n'
        '    </div>\n'
        '  </div>\n'
        '  <div class="sec">\n'
        '    <h2>The curriculum — ordered stages, nursery → PhD</h2>\n'
        '    <p class="lead">The order is a real design decision. Broad web first to learn language &amp; common sense, then '
        'harder/narrower data, long sequences last, and the premium anneal at the very end. Bands must <b>overlap</b> — a '
        'sharp switch spikes the gradients (a real V4 lesson).</p>\n'
        '    <div class="stages">\n'
        '      <div class="stg"><div class="s">STAGE 1 · ~95%</div><div class="t">Pre-training</div><div class="d">General web heavy; loss on every token. Web → STEM → code as it matures.</div></div>\n'
        '      <div class="stg"><div class="s">STAGE 2 · ~2%</div><div class="t">Mid / anneal</div><div class="d">Short cooldown, LR→0; PhD-grade documents locked in.</div></div>\n'
        '      <div class="stg"><div class="s">STAGE 3</div><div class="t">SFT</div><div class="d">Agent traces, chat, code-fix — loss only on model outputs.</div></div>\n'
        '      <div class="stg"><div class="s">STAGE 4</div><div class="t">Reasoning</div><div class="d">Short↔long tagged traces; teaches controllable depth.</div></div>\n'
        '      <div class="stg"><div class="s">STAGE 5</div><div class="t">Preference / RL</div><div class="d">Alignment (GRPO etc.) — a later session, not this plan.</div></div>\n'
        '    </div>\n'
        '    <p class="note" style="font-size:12.5px;color:#33334a;margin-top:12px">This assignment centres on the '
        '<b>pre-training curriculum + Stage 2/3</b>. Long-context = <b>growing the sequence length</b> in steps '
        '(4K → 8K → 16K → …), one length per batch. Blend ~15–20% of the next band into the current one so the transition '
        'is smooth.</p>\n'
        '  </div>\n'
        '  <div class="sec">\n'
        '    <h2>The data inventory your lanes point at</h2>\n'
        '    <p class="lead">A slot is only real if a dataset fills it. Sizes from the session’s inventory widget.</p>\n'
        '    <table class="tbl"><tr><th>Dataset</th><th>Lane</th><th>Samples</th><th>Tokens</th><th>Note</th></tr>\n' + inv + '</table>\n'
        '  </div>\n'
        '  <div class="sec">\n'
        '    <h2>What a finished (toy) plan looks like</h2>\n'
        '    <p class="lead">A miniature, illustrative version — the <em>shape</em> of the deliverable, not a recommendation. Remember the real mix <b>shifts by phase</b>; this is roughly a mid/late-training snapshot.</p>\n'
        '    <div class="toy"><div class="toy-hd">V5 MIXTURE &amp; CURRICULUM — TOY SNAPSHOT (mid-training)</div><div class="toy-bd">\n'
        '      <table>\n'
        '        <tr><th>Capability lane</th><th>Share</th><th>Points at</th></tr>\n'
        '        <tr><td>General web</td><td class="pct">34%</td><td>DCLM / FineWeb — common sense, MMLU</td></tr>\n'
        '        <tr><td>Code</td><td class="pct">25%</td><td>Stack v2</td></tr>\n'
        '        <tr><td>Agentic / tool-calls</td><td class="pct">16%</td><td>ToolBench / Bolt (always-on floor)</td></tr>\n'
        '        <tr><td>STEM</td><td class="pct">12%</td><td>DCLM-STEM / textbooks</td></tr>\n'
        '        <tr><td>Reasoning traces</td><td class="pct">7%</td><td>tagged short↔long chains</td></tr>\n'
        '        <tr><td>Indic</td><td class="pct">4%</td><td>split below (always-on floor)</td></tr>\n'
        '        <tr><td>Long-context</td><td class="pct">2%</td><td>book-length + multi-doc</td></tr>\n'
        '      </table>\n'
        '      <div style="margin-top:14px"><b>Indic 4%, by tier:</b> Verified (T0) 45% · Unverified (T1) 35% · Translated (T3) 12% · Synthetic (T2) 8%.</div>\n'
        '      <div style="margin-top:6px;font-size:13px">\n'
        '        <div><b>Always-on floor:</b> Indic ≥ 3% · agentic ≥ 8% · safety ≥ 1% — OPUS may never cross these.</div>\n'
        '        <div style="margin-top:3px"><b>Anneal reserve:</b> 2% of budget — premium verified Indic + PhD LaTeX + clean agentic — spent only in the cooldown.</div>\n'
        '        <div style="margin-top:3px"><b>Curriculum:</b> web-heavy → code/STEM/reasoning → long-context; seq-len 4K→8K→16K; ~18% band overlap.</div>\n'
        '        <div style="margin-top:3px"><b>Depth bands:</b> low ≤256 · medium ≤1k · high ≤4k · ultra ≤16k+ thinking tokens.</div>\n'
        '        <div style="margin-top:3px"><b>Validation:</b> tested at 1B &amp; 3B on the benchmarks above before 40B; OPUS keep-fraction ~50% during the run.</div>\n'
        '      </div>\n'
        '      <div class="disc">Illustrative only — the assignment is to justify and defend numbers like these.</div>\n'
        '    </div></div>\n'
        '  </div>\n'
        '  <div class="rule">\n'
        '    <div class="k">The rule behind the whole assignment</div>\n'
        '    <div class="q">“A data decision is a hypothesis until a cheap experiment has tested it.”</div>\n'
        '  </div>\n'
        '  <div class="sec">\n'
        '    <h2>How you submit &amp; how it’s graded</h2>\n'
        '    <div class="submit">Submit a <b>GitHub README</b> (may include scripts you ran to compute shares) — not a Netlify '
        'app or widget. Grading is <b>subjective</b>: imagine a data-and-curriculum reviewer from a top lab sitting across '
        'from you, pushing on every number. Marks come from the <b>quality of your reasoning and the evidence</b> behind each '
        'choice — especially <i>why</i> the data you train on <b>last</b> is what it is. A strong submission gives a defended '
        'share to every lane and states the Indic split across verified / unverified / translated / synthetic.</div>\n'
        '  </div>\n'
        '  <div class="sec">\n'
        '    <h2>Mini-glossary</h2>\n'
        '    <dl class="gloss">\n'
        '      <dt>Mixture</dt><dd>What fraction of training data is each type — and it shifts by phase.</dd>\n'
        '      <dt>Curriculum</dt><dd>The order the model sees data: broad → hard, long &amp; premium last.</dd>\n'
        '      <dt>Capability lane / slot</dt><dd>A skill bucket you allocate budget to (web, code, agentic, reasoning, Indic…).</dd>\n'
        '      <dt>Compose backward</dt><dd>Pick target benchmarks first, then choose data that wins them.</dd>\n'
        '      <dt>Loss masking</dt><dd>Train only on the model’s tokens; mask user turns &amp; tool outputs.</dd>\n'
        '      <dt>Trainable tokens</dt><dd>The green (supervised) tokens only — what you actually size a lane by.</dd>\n'
        '      <dt>Tier (T0–T3)</dt><dd>verified · unverified web · synthetic · translated.</dd>\n'
        '      <dt>OPUS / golden proxy</dt><dd>Online selector: keeps samples that move “benchmark-weak” weights; peeks at first ~512 tokens.</dd>\n'
        '      <dt>Always-on floor</dt><dd>Minimums OPUS can’t cut — protects Indic &amp; agentic from being thrown away.</dd>\n'
        '      <dt>Anneal / cooldown</dt><dd>Final short phase (LR→0) where the best data is locked in.</dd>\n'
        '      <dt>Band overlap</dt><dd>Diffusing one data band into the next so gradients don’t spike.</dd>\n'
        '      <dt>Depth bands</dt><dd>low / medium / high / ultra thinking-token budgets, set by tags.</dd>\n'
        '      <dt>Proxy run</dt><dd>Cheap 1B / 3B experiment that tests a recipe before the full run.</dd>\n'
        '      <dt>Starved lane</dt><dd>A capability you want more of than you’ve cleaned — where the pipeline aims next.</dd>\n'
        '    </dl>\n'
        '  </div>\n'
        '</div>\n</body>\n</html>\n'
    )


if __name__ == "__main__":
    with open("v5_brief.html", "w", encoding="utf-8") as f:
        f.write(build_html())
    print("Done. v5_brief.html written.")
