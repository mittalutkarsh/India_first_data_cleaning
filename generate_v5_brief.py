"""Generate v5_brief.html — a plain-English explainer of the V5
mixture-and-curriculum assignment (what is being asked, with examples)."""

DELIVERABLES = [
    ("01", "A share of the budget for every capability",
     "The model trains on a fixed pile of tokens — the <b>budget</b> (say ~6 trillion). "
     "You slice that pie, one slice per <b>capability slot</b> (a skill the model needs). The slices must add to 100%.",
     "English 35% · Indic 22% · Code 18% · Math/Science 10% · Reasoning 6% · Agentic 4% · Long-context 3% · Safety/Other 2%",
     "These slice sizes are the <b>targets</b> the whole cleaning pipeline is trying to fill. The Manifest stage admits each shard into one of these slots."),

    ("02", "The Indic slot, split by tier — not one number",
     "Don’t hide behind “Indic 22%”. Break that 22% into the four <b>provenance tiers</b> you already built, so the plan is honest "
     "about how much of your Indian-language data is high-trust vs. lower-trust.",
     "Inside the 22% Indic → Verified (T0) 40% · Unverified web (T1) 35% · Translated (T3) 15% · Synthetic (T2) 10%",
     "The tiers are exactly the T0–T3 from the <a href='data.html'>Data</a> page. You’d love it to be all verified, but there isn’t enough — so you say clearly how much you’re leaning on weaker tiers."),

    ("03", "Name the agentic, reasoning &amp; long-context slots — and point each at a dataset",
     "Three modern capabilities are easy to forget and hard to source, so the plan must call them out <b>by name</b> and say "
     "which dataset from the inventory fills each one.",
     "Reasoning → a step-by-step math/logic set · Agentic → a tool-use / function-call set · Long-context → book-length &amp; multi-document set",
     "“Agentic” = using tools and taking multi-step actions. “Reasoning” = showing its working. “Long-context” = handling very long inputs. Each needs its own data, not general web text."),

    ("04", "The protected always-on floor",
     "A <b>selector</b> (an automatic system that keeps re-tuning the data mix to lower the loss fastest) will happily starve anything "
     "that doesn’t pay off immediately. The <b>floor</b> is a set of minimums it is <i>forbidden</i> to cross.",
     "Odia ≥ 0.5% at all times · Safety data ≥ 1% · smallest Indic languages ≥ 0.3% each — no matter what the optimizer prefers",
     "This protects fragile, low-resource things (small Indian languages, safety) from quietly vanishing because they’re “inefficient”."),

    ("05", "The anneal reserve (held back for the cooldown)",
     "Training ends with a <b>cooldown / anneal</b> phase where the learning rate ramps to zero. What the model sees in that window "
     "sticks disproportionately. So you <b>hold back</b> a reserve of your very best data and spend it only then.",
     "Reserve 5% of the budget — premium verified Indic + textbook-grade reasoning — fed only in the final ~10% of training",
     "It’s the “peak-nutrition week before the race”. If you burn your best data early, the cooldown has nothing special to lock in."),

    ("06", "Difficulty bands &amp; reasoning-length bands (with an example each)",
     "Group your data two more ways so the schedule (the <b>curriculum</b>) can be deliberate: by how <b>hard</b> it is, and by how "
     "<b>long the reasoning</b> is. Give a concrete example for every band.",
     "Difficulty — Easy: “Capital of India? → New Delhi.” · Medium: a 4-step profit-percent word problem · Hard: “Prove √2 is irrational.”<br>"
     "Reasoning-length — Short: “2+3=5.” · Medium: a 4–6 step solution · Long: a multi-page proof or multi-hop research answer",
     "Too much easy/short data and the model never learns to think slowly; too much hard/long and early training destabilises. Bands let you schedule easy→hard."),

    ("07", "Prove the numbers with cheap 1B &amp; 3B proxy runs first",
     "Every number above is a <b>guess</b> until tested. So you commit to trialling recipes on tiny 1-billion and 3-billion models "
     "(cheap) and only scaling up the ones that actually win — before spending the full 40B run.",
     "Run Recipe A (22% Indic) vs Recipe B (28% Indic) at 1B for 20B tokens → compare Indic &amp; English evals → promote the winner to 3B → only then 40B",
     "The rule that runs through the whole course: <b>a data decision is a hypothesis until a cheap experiment has tested it.</b>"),

    ("08", "Keep cleaning — now aimed at the starved slots",
     "The 8-stage cleaning pipeline keeps running toward the cumulative token target, but <b>prioritised</b>: pointed at whichever "
     "slot the mixture shows is <b>starved</b> (you want more of it than you have cleaned).",
     "Plan wants 6% reasoning but only 2% is cleaned so far → point Cleaning → Language → Quality → … at reasoning sources next",
     "The mixture plan is the <i>why</i> behind all the cleaning you built: it tells the pipeline what to go get next."),
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
.analogy p { margin:0; font-size:14px; color:#33334a; }
.analogy b { color:var(--ink); }
.sec { margin:30px 0 0; } .sec h2 { font-family:"Spectral",serif; font-size:24px; margin:0 0 4px; }
.sec .lead { font-size:13px; color:var(--muted); margin:0 0 16px; }
.card { border:1px solid var(--line); border-radius:14px; background:#fff; padding:18px 20px; margin-bottom:13px; }
.card .top { display:flex; align-items:baseline; gap:12px; }
.card .num { font-family:"IBM Plex Mono",monospace; font-weight:700; font-size:13px; color:#fff; background:var(--indigo); border-radius:8px; padding:3px 9px; }
.card h3 { font-family:"Spectral",serif; font-size:19px; margin:0; }
.card .plain { font-size:14px; color:#33334a; margin:10px 0 0; }
.card .eg { margin:12px 0 0; padding:11px 14px; background:var(--panel); border-radius:9px; font-size:13.5px; }
.card .eg .lbl { font-family:"IBM Plex Mono",monospace; font-size:10px; letter-spacing:.08em; text-transform:uppercase; color:var(--teal); font-weight:600; display:block; margin-bottom:5px; }
.card .conn { font-size:12.5px; color:var(--muted); margin:11px 0 0; }
.card .conn .lbl { font-family:"IBM Plex Mono",monospace; font-size:10px; letter-spacing:.06em; text-transform:uppercase; color:var(--marigold); font-weight:600; }
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
"""


def build_html():
    cards = ""
    for num, title, plain, eg, conn in DELIVERABLES:
        cards += (
            '<div class="card"><div class="top"><span class="num">' + num + '</span>'
            '<h3>' + title + '</h3></div>'
            '<div class="plain">' + plain + '</div>'
            '<div class="eg"><span class="lbl">Concrete example</span>' + eg + '</div>'
            '<div class="conn"><span class="lbl">How it connects</span> ' + conn + '</div></div>\n'
        )
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
        '  <a href=\"overview.html\">Overview</a>\n'
        '  <a href=\"data.html\">Data</a>\n'
        '  <a href=\"index.html\">Cleaning</a>\n'
        '  <a href=\"language.html\">Language</a>\n'
        '  <a href=\"quality.html\">Quality</a>\n'
        '  <a href=\"dedup.html\">Dedup</a>\n'
        '  <a href=\"pii.html\">PII</a>\n'
        '  <a href=\"decontam.html\">Decontam</a>\n'
        '  <a href=\"tokenizer.html\">Tokenizer</a>\n'
        '  <a href=\"manifest.html\">Manifest</a>\n'
        '  <a href=\"v5_brief.html\" class=\"active\">V5 Plan</a>\n'
        '</div></div>\n'
        '<div class="wrap">\n'
        '  <div class="hero">\n'
        '    <div class="eyebrow">The assignment, in plain words</div>\n'
        '    <h1>Write the model’s training diet &amp; study schedule — and prove it works.</h1>\n'
        '    <p>The task is to draft the <b>mixture-and-curriculum plan</b> for the next model version (V5): a written '
        'specification, specific enough to defend, that says exactly what data the model trains on, in what proportions, '
        'in what order, with the best data saved for last — plus a promise to test the recipe cheaply before trusting '
        'it at full scale. This page explains every part of that ask, with an example for each.</p>\n'
        '  </div>\n'
        '  <div class="analogy">\n'
        '    <h3>The whole thing in one analogy</h3>\n'
        '    <p>You are a <b>coach planning a season</b> for an athlete (the model). The <b>mixture</b> is the meal plan '
        '(how much of each food); the <b>curriculum</b> is the practice schedule (what to drill, in what order). You '
        'protect a few non-negotiables (the <b>floor</b>), you save peak nutrition for the week before the event (the '
        '<b>anneal reserve</b>), and you trial the whole plan on a junior athlete first (the <b>1B/3B proxy runs</b>) '
        'before committing your star.</p>\n'
        '  </div>\n'
        '  <div class="sec">\n'
        '    <h2>The 8 things your plan must contain</h2>\n'
        '    <p class="lead">Each is a required part of the written spec. Plain meaning, a concrete example, and how it ties back to the pipeline you built.</p>\n'
        + cards +
        '  </div>\n'
        '  <div class="sec">\n'
        '    <h2>What a finished (toy) plan looks like</h2>\n'
        '    <p class="lead">A miniature, illustrative version — so you can see the <em>shape</em> of the deliverable. These numbers are made up to show the format, not a real recommendation.</p>\n'
        '    <div class="toy"><div class="toy-hd">V5 MIXTURE &amp; CURRICULUM — TOY EXAMPLE</div><div class="toy-bd">\n'
        '      <table>\n'
        '        <tr><th>Capability slot</th><th>Budget share</th><th>Notes</th></tr>\n'
        '        <tr><td>English (general)</td><td class="pct">35%</td><td>web-prose, high quality</td></tr>\n'
        '        <tr><td>Indic</td><td class="pct">22%</td><td>split below ↓</td></tr>\n'
        '        <tr><td>Code</td><td class="pct">18%</td><td>permissively-licensed repos</td></tr>\n'
        '        <tr><td>Math / Science</td><td class="pct">10%</td><td>textbooks + problem sets</td></tr>\n'
        '        <tr><td>Reasoning</td><td class="pct">6%</td><td>→ chain-of-thought set</td></tr>\n'
        '        <tr><td>Agentic</td><td class="pct">4%</td><td>→ tool-use / function-call set</td></tr>\n'
        '        <tr><td>Long-context</td><td class="pct">3%</td><td>→ book-length + multi-doc set</td></tr>\n'
        '        <tr><td>Safety / Other</td><td class="pct">2%</td><td>protected (see floor)</td></tr>\n'
        '      </table>\n'
        '      <div style="margin-top:14px"><b>Indic 22%, by tier:</b></div>\n'
        '      <table style="margin-top:4px">\n'
        '        <tr><td>Verified (T0)</td><td class="pct">40%</td><td>Wikipedia, textbooks</td></tr>\n'
        '        <tr><td>Unverified web (T1)</td><td class="pct">35%</td><td>Sangraha, IndicCorp</td></tr>\n'
        '        <tr><td>Translated (T3)</td><td class="pct">15%</td><td>MT from English</td></tr>\n'
        '        <tr><td>Synthetic (T2)</td><td class="pct">10%</td><td>model-generated, lineage-tracked</td></tr>\n'
        '      </table>\n'
        '      <div style="margin-top:14px; font-size:13px">\n'
        '        <div><b>Protected floor:</b> Odia ≥ 0.5% · Safety ≥ 1% · each small Indic language ≥ 0.3% — the selector may never cross these.</div>\n'
        '        <div style="margin-top:4px"><b>Anneal reserve:</b> 5% of the budget (premium verified Indic + textbook reasoning), spent only in the final ~10% of training.</div>\n'
        '        <div style="margin-top:4px"><b>Curriculum:</b> difficulty easy→hard; keep short and long reasoning chains mixed throughout, long chains weighted up near the end.</div>\n'
        '        <div style="margin-top:4px"><b>Validation:</b> every share above is tested at 1B and 3B before the 40B run; only recipes that win on the evals are promoted.</div>\n'
        '      </div>\n'
        '      <div class="disc">Illustrative only — the real assignment is to justify numbers like these and defend them.</div>\n'
        '    </div></div>\n'
        '  </div>\n'
        '  <div class="rule">\n'
        '    <div class="k">The rule behind the whole assignment</div>\n'
        '    <div class="q">“A data decision is a hypothesis until a cheap experiment has tested it.”</div>\n'
        '  </div>\n'
        '  <div class="sec">\n'
        '    <h2>Mini-glossary</h2>\n'
        '    <p class="lead">Every bit of jargon from the assignment, in one line.</p>\n'
        '    <dl class="gloss">\n'
        '      <dt>Mixture</dt><dd>The recipe: what fraction of training data is each type.</dd>\n'
        '      <dt>Curriculum</dt><dd>The schedule: which data the model sees when (e.g. easy→hard, best saved for last).</dd>\n'
        '      <dt>Budget</dt><dd>The total number of training tokens you get to spend — the pie you’re slicing.</dd>\n'
        '      <dt>Capability slot</dt><dd>A skill bucket you allocate budget to (English, Indic, Code, Reasoning, Agentic, …).</dd>\n'
        '      <dt>Tier (T0–T3)</dt><dd>Provenance/quality grade: verified · unverified web · synthetic · translated.</dd>\n'
        '      <dt>Selector</dt><dd>An automatic system that keeps re-tuning the mix during training to lower loss fastest.</dd>\n'
        '      <dt>Protected floor</dt><dd>Minimum shares the selector is forbidden to go below, so fragile data isn’t starved.</dd>\n'
        '      <dt>Anneal / cooldown</dt><dd>The final training phase (learning rate → 0) where the last data seen sticks hardest.</dd>\n'
        '      <dt>Anneal reserve</dt><dd>Your best data, held back to spend in that cooldown window.</dd>\n'
        '      <dt>Difficulty band</dt><dd>Grouping data by how hard it is (easy / medium / hard).</dd>\n'
        '      <dt>Reasoning-length band</dt><dd>Grouping by how long the chain of reasoning is (short / medium / long).</dd>\n'
        '      <dt>Proxy run</dt><dd>A cheap small-model (1B / 3B) experiment that tests a recipe before the full run.</dd>\n'
        '      <dt>Starved slot</dt><dd>A capability you want more of than you’ve managed to clean — where the pipeline aims next.</dd>\n'
        '    </dl>\n'
        '  </div>\n'
        '</div>\n</body>\n</html>\n'
    )


if __name__ == "__main__":
    with open("v5_brief.html", "w", encoding="utf-8") as f:
        f.write(build_html())
    print("Done. v5_brief.html written.")
