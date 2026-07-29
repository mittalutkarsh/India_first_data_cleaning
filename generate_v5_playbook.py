"""Generate v5_playbook.html — how to actually build the V5 plan, written as an
essay in a plain, intuition-first Substack voice, keeping the one table that
earns its place (pantry vs plate, OPUS keep-fraction applied)."""

BUDGET_B = 3000.0

# lane, share%, OPUS keep-fraction, unique-eligible tokens (B), note
PANTRY = [
    ("General web", 37, 0.5, 8000, "plenty after dedup"),
    ("Code", 22, 0.5, 600, "Stack v2, after licences + dedup"),
    ("STEM", 12, 0.5, 350, "textbooks, science"),
    ("Agentic", 13, 1.0, 0.08, "must be generated, not scraped"),
    ("Reasoning", 7, 0.5, 30, "distilled traces, must scale"),
    ("Indic", 8, 1.0, 150, "mostly raw web; verified tier is thin"),
    ("Safety", 1, 1.0, 15, "curated"),
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
    '  <a href="v5_brief.html" class="active">V5 Plan</a>\n'
    '</div></div>\n'
)

CSS = """
:root { --bg:#FCFCFA; --ink:#1a1a22; --soft:#3d3d4a; --indigo:#2E357E; --marigold:#C77d1a;
  --teal:#147D74; --rose:#B5476B; --line:#E6E6DF; --muted:#7a7a86; --panel:#f3f3ee; }
*, *::before, *::after { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--ink);
  font-family:"Spectral", Georgia, "Times New Roman", serif; font-size:19px; line-height:1.75; -webkit-font-smoothing:antialiased; }
a { color:var(--indigo); } a:hover { color:var(--marigold); }
.nav { position:sticky; top:0; z-index:50; background:rgba(252,252,250,.95); border-bottom:1px solid var(--line); backdrop-filter:saturate(1.2) blur(4px); }
.nav-in { max-width:1180px; margin:0 auto; padding:9px 24px; display:flex; align-items:center; gap:13px; flex-wrap:wrap; }
.brand { font-weight:700; color:var(--indigo); font-size:16px; margin-right:auto; }
.nav a { font-family:"IBM Plex Mono",monospace; font-size:11px; letter-spacing:.02em; color:var(--muted); padding:3px 2px; border-bottom:2px solid transparent; text-decoration:none; }
.nav a:hover { color:var(--ink); } .nav a.active { color:var(--indigo); border-bottom-color:var(--marigold); }
.article { max-width:720px; margin:0 auto; padding:0 24px 90px; }
.crumb { font-family:"IBM Plex Mono",monospace; font-size:12px; color:var(--muted); margin-top:26px; }
.kicker { font-family:"IBM Plex Mono",monospace; font-size:12px; letter-spacing:.14em; text-transform:uppercase; color:var(--marigold); font-weight:600; margin-top:14px; }
h1 { font-weight:700; font-size:clamp(30px,5vw,44px); line-height:1.12; margin:10px 0 6px; letter-spacing:-.01em; }
.dek { font-size:20px; color:var(--soft); font-style:italic; margin:0 0 30px; }
h2 { font-weight:700; font-size:25px; margin:40px 0 6px; letter-spacing:-.01em; }
p { margin:18px 0; } .lead { font-size:21px; }
.pull { border-left:3px solid var(--marigold); margin:30px 0; padding:4px 0 4px 22px; font-size:22px; line-height:1.4; font-style:italic; color:var(--indigo); }
.ptable { width:100%; border-collapse:collapse; font-family:"IBM Plex Mono",monospace; font-size:13.5px; margin:24px 0; background:#fff; border:1px solid var(--line); border-radius:10px; overflow:hidden; }
.ptable th, .ptable td { padding:8px 10px; border-bottom:1px solid var(--line); text-align:right; }
.ptable th:first-child, .ptable td:first-child { text-align:left; }
.ptable th { font-size:10.5px; letter-spacing:.05em; text-transform:uppercase; color:var(--muted); background:var(--panel); }
.b { font-weight:600; padding:1px 7px; border-radius:5px; }
.b-ok { background:#e6f5ef; color:#0f7a54; } .b-tight { background:#fbeede; color:#9a5a12; }
.b-starved { background:#fceef2; color:var(--rose); } .b-inf { background:#f7e0e6; color:#8a1a3a; }
.cap { font-size:14px; color:var(--muted); font-style:italic; margin-top:-8px; }
.cta { margin:36px 0 0; padding:18px 22px; background:#fff; border:1px solid var(--line); border-radius:12px; font-size:17px; }
code { font-family:"IBM Plex Mono",monospace; font-size:15px; background:var(--panel); padding:1px 5px; border-radius:4px; }
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
        out += (
            '<tr><td>' + lane + '</td>'
            '<td>' + str(share) + '%</td>'
            '<td>~' + ("%d" % round(trained)) + 'B</td>'
            '<td>~' + ("%d" % round(presented)) + 'B</td>'
            '<td>~' + avail_s + '</td>'
            '<td><span class="b ' + cls + '">' + lab + '</span></td></tr>\n'
        )
    return out


def build_html():
    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>How to actually build the V5 plan</title>\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link href="https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,400;0,600;0,700;1,400;1,600'
        '&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">\n'
        '<style>' + CSS + '</style>\n</head>\n<body>\n' + NAV +
        '<div class="article">\n'
        '  <div class="crumb"><a href="v5_brief.html">V5 Plan</a> › how to build it</div>\n'
        '  <div class="kicker">The hands-on version</div>\n'
        '  <h1>How to actually build the plan.</h1>\n'
        '  <p class="dek">The other page told you what the assignment wants. This one walks through it in the order I’d '
        'actually do it — including the moment the arithmetic turns on you.</p>\n'

        '  <p class="lead">There is a temptation to open a spreadsheet and start typing percentages. Resist it. If you pick '
        'numbers first, you’ll fall in love with a plan you can’t actually cook. Do it in this order instead.</p>\n'

        '  <h2>1. Start from the exams, not the data</h2>\n'
        '  <p>Before any proportions, write down the benchmarks you’re trying to win — the coding ones, the agentic ones, the '
        'math and reasoning ones, the general-knowledge one, the Indic ones. That list <em>is</em> the model. Everything '
        'downstream exists to win it. Then, for each exam, name the dataset that teaches it. People call this “composing '
        'backward,” and it just means you choose the textbook after you know the test.</p>\n'

        '  <h2>2. Weigh your pantry before you plan the menu</h2>\n'
        '  <p>Now go count what you actually own — and be ruthless about it. A published corpus size is an upper bound, not '
        'trainable inventory. The number drops once you strip out bad licences, remove duplicates, filter for quality, take out '
        'anything that overlaps your test sets, and re-tokenize with your own tokenizer. Count two things for every lane: how '
        'many <em>samples</em> you have (that’s variety) and how many <em>tokens</em> (that’s depth). A million examples of '
        'twenty tokens each teaches almost nothing.</p>\n'
        '  <p>One subtlety that trips everyone up. For chat and agent data, you only train on the model’s own words — the user '
        'turns and the raw tool logs are masked out. So a giant agent trace is mostly <em>not</em> trainable, and counting its '
        'full size flatters you. (Plain web pretraining is different — there, every token counts.)</p>\n'

        '  <h2>3. Portion the plate — and brace yourself</h2>\n'
        '  <p>Now you write the mixture: a share of the budget for each lane, adding to a hundred. Say the budget is three '
        'trillion tokens. Multiply the shares out so they’re concrete. This is where most first drafts feel finished.</p>\n'
        '  <p>They aren’t, because of one detail. That automatic selector I mentioned typically keeps only about half of what you '
        'show it. So to <em>train</em> on a billion tokens of code, you have to <em>present</em> two billion. Put “presented” '
        'next to “available” and the picture changes. Watch what happens to code and STEM:</p>\n'
        '  <table class="ptable"><tr><th>lane</th><th>share</th><th>trained</th><th>presented</th><th>you have</th><th>verdict</th></tr>\n'
        + pantry_rows() +
        '  </table>\n'
        '  <p class="cap">Presented = trained ÷ the selector’s keep-rate. Verdict compares what you must present against the unique data you actually own.</p>\n'

        '  <div class="pull">Code and STEM looked fine until the selector doubled the bill. That’s the kind of thing a grader finds in ten seconds — so you find it first.</div>\n'

        '  <h2>4. Stare at the three empty shelves</h2>\n'
        '  <p>The table is doing the most important job in the whole exercise: it shows you where you’re starving. Code and STEM '
        'are merely tight. But <strong>agentic is infeasible</strong> as written — you’d need something like 190 million good '
        'trajectories, and scraping can’t get you there. <strong>Reasoning is starved</strong>. And notice there’s no '
        '“long-context” row at all, because long context isn’t a lane — it’s a property a document already has. A long Hindi '
        'legal filing is Indic <em>and</em> long; counting it twice is cheating. Long context becomes a rule about how you pack '
        'your batches in the later phases, not a slice of the pie.</p>\n'
        '  <p>So your honest conclusion writes itself: you cannot scrape your way to agentic and reasoning data, you have to '
        '<em>generate</em> it. And the cheapest lever isn’t more trajectories — it’s better ones. A trace that includes the '
        'plan, the reasoning, and a reflection at the end yields several times more trainable tokens than a bare tool call. '
        'Design beats scraping.</p>\n'

        '  <h2>5. Grade the Indian-language shelf</h2>\n'
        '  <p>Split Indic into its four trust tiers, and let the honest numbers hurt a little. Genuinely verified material — '
        'Wikipedia, textbooks — across all those languages is only a few billion unique tokens. If your plan quietly wanted ten '
        'times that in the verified tier, you’d be running the same Wikipedia through the model twenty times, which memorizes '
        'rather than teaches. So cap the repeats at a handful, let the verified tier be as small as it truly is, and be explicit '
        'that the rest leans on cleaned web and translation, with the quality risk that implies.</p>\n'
        '  <p>And when you protect a small language, protect it in <em>tokens</em>, not percentages. “Every language gets at '
        'least 0.3% of the budget” sounds fair until you notice twenty-two languages times 0.3% is more than the whole Indic '
        'slice. Say “Hindi at least this many billion, each small language at least that many,” and sample the rest by '
        'temperature.</p>\n'

        '  <h2>6. Keep the vitamins, save the dessert</h2>\n'
        '  <p>Set your floors — the minimums the selector can’t cross — and enforce them <em>constantly</em>, not as a '
        'run-long average. A floor that’s only true on average lets the selector starve a lane for ninety percent of training '
        'and backfill at the end, which is worse than useless. And put safety in the plate as a real lane; a floor for something '
        'that isn’t in your hundred percent is just an inconsistency waiting to be caught.</p>\n'
        '  <p>Then carve out the dessert: a small reserve of your very best data for the cooldown at the end. Keep it '
        '<em>inside</em> the budget, not stacked on top, and remember its value is a claim you’ll test against a run with no '
        'cooldown — not an article of faith.</p>\n'

        '  <h2>7. Write the weekly schedule</h2>\n'
        '  <p>Turn the single mixture into a handful of phases — broad and web-heavy first, then code and science and reasoning, '
        'the scarce lanes concentrated late, the premium data last. Each phase gets its own budget, its own maximum sequence '
        'length, and its own mixture that adds to a hundred; the phases, weighted by size, should average back to your global '
        'mixture. Blend each phase into the next so nothing lurches. And decide difficulty by measurement, not by vibe — a '
        'problem is “hard” if a small reference model fails it most of the time — and let the depth tag be earned by the '
        'shortest correct answer, or you’ll teach the model to ramble whenever you ask it to think hard.</p>\n'

        '  <h2>8. Trial it on a junior</h2>\n'
        '  <p>Everything above is a hypothesis. Test it on a one-billion and a three-billion model before you spend the real '
        'run. Pick evaluations that actually show signal at that size — the giant benchmarks read zero for everyone at one '
        'billion, so they tell you nothing. To see if Indic helps, don’t compare 4% against 5%; compare 4% against 12% so the '
        'effect is visible, then interpolate. And promote a recipe because it <em>ranks</em> above the others across both sizes, '
        'not because of the exact score, since the scores shift as the model grows.</p>\n'

        '  <h2>9. Restock the empty shelves</h2>\n'
        '  <p>Finally, hand the starvation list back to the cleaning pipeline. It now has a priority queue, in order: generate '
        'agentic trajectories, distill reasoning traces, gather genuinely long documents, and hunt down more verified Indic '
        '(textbooks, government records, news — because Wikipedia alone won’t fill the tier). That’s the whole loop. The plan '
        'tells the pipeline what to go get; the pipeline feeds the next version of the plan.</p>\n'

        '  <h2>What you hand in</h2>\n'
        '  <p>A README that a skeptic could read and push on at every number — and, ideally, a small script that '
        're-derives the tables and refuses to run if anything doesn’t add up. That script is the difference between “trust me” '
        'and “here, check it.”</p>\n'

        '  <div class="cta">Both live in the repo now: <code>V5_PLAN.md</code> is the defended write-up, and '
        '<code>mixture.py</code> re-computes this table, applies the selector’s keep-rate, and exits with an error if a phase '
        'doesn’t sum to a hundred or a lane is impossible. Run <code>python3 mixture.py</code> to watch it check itself. '
        '<a href="v5_brief.html">← back to what the ask is</a></div>\n'
        '</div>\n</body>\n</html>\n'
    )


if __name__ == "__main__":
    with open("v5_playbook.html", "w", encoding="utf-8") as f:
        f.write(build_html())
    print("Done. v5_playbook.html written.")
