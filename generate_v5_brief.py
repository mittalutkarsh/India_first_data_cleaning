"""Generate v5_brief.html — the V5 assignment explained, written as an essay
in a plain, intuition-first Substack voice."""

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
  --teal:#147D74; --rose:#B5476B; --line:#E6E6DF; --muted:#7a7a86; }
*, *::before, *::after { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--ink);
  font-family:"Spectral", Georgia, "Times New Roman", serif; font-size:19px; line-height:1.75; -webkit-font-smoothing:antialiased; }
a { color:var(--indigo); } a:hover { color:var(--marigold); }
.nav { position:sticky; top:0; z-index:50; background:rgba(252,252,250,.95); border-bottom:1px solid var(--line); backdrop-filter:saturate(1.2) blur(4px); }
.nav-in { max-width:1180px; margin:0 auto; padding:9px 24px; display:flex; align-items:center; gap:13px; flex-wrap:wrap; }
.brand { font-weight:700; color:var(--indigo); font-size:16px; margin-right:auto; }
.nav a { font-family:"IBM Plex Mono",monospace; font-size:11px; letter-spacing:.02em; color:var(--muted); padding:3px 2px; border-bottom:2px solid transparent; text-decoration:none; }
.nav a:hover { color:var(--ink); } .nav a.active { color:var(--indigo); border-bottom-color:var(--marigold); }
.article { max-width:700px; margin:0 auto; padding:0 24px 90px; }
.kicker { font-family:"IBM Plex Mono",monospace; font-size:12px; letter-spacing:.14em; text-transform:uppercase; color:var(--marigold); font-weight:600; margin-top:44px; }
h1 { font-weight:700; font-size:clamp(30px,5vw,46px); line-height:1.12; margin:12px 0 6px; letter-spacing:-.01em; }
.dek { font-size:20px; color:var(--soft); font-style:italic; margin:0 0 30px; }
h2 { font-weight:700; font-size:26px; margin:40px 0 6px; letter-spacing:-.01em; }
p { margin:18px 0; }
em { font-style:italic; } strong { font-weight:700; }
.lead { font-size:21px; }
.pull { border-left:3px solid var(--marigold); margin:30px 0; padding:4px 0 4px 22px; font-size:23px; line-height:1.4; font-style:italic; color:var(--indigo); }
.snapshot { font-family:"IBM Plex Mono",monospace; font-size:13px; line-height:1.7; background:#16162a; color:#e8e8ef; border-radius:10px; padding:18px 20px; margin:26px 0; white-space:pre; overflow-x:auto; }
.snapshot .h { color:#E0982B; } .snapshot .g { color:#8fd6bf; } .snapshot .r { color:#e79ab3; }
.cta { margin:36px 0 0; padding:18px 22px; background:#fff; border:1px solid var(--line); border-radius:12px; font-size:17px; }
hr { border:none; border-top:1px solid var(--line); margin:40px 0; }
.foot { font-size:15px; color:var(--muted); font-style:italic; }
"""


def build_html():
    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>You’ve been asked to design what the model eats</title>\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link href="https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,400;0,600;0,700;1,400;1,600'
        '&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">\n'
        '<style>' + CSS + '</style>\n</head>\n<body>\n' + NAV +
        '<div class="article">\n'
        '  <div class="kicker">The V5 assignment, in plain words</div>\n'
        '  <h1>You’ve been asked to design what the model eats.</h1>\n'
        '  <p class="dek">Not the architecture. The data — how much of each kind, in what order, with the best saved for last. Here is what that really means, and what your plan has to contain to survive a hard question.</p>\n'

        '  <p class="lead">Everyone wants to talk about the architecture. How many layers, which attention trick, the newest '
        'optimizer. And I get it — that part is fun. But here is the uncomfortable truth the course keeps circling back to: '
        'the architecture is mostly solved. Point a beautiful transformer at a random folder of data and hit train, and you get '
        'garbage.</p>\n'
        '  <p>The thing that actually decides whether your model is brilliant or useless is much less glamorous. It is the data '
        '— <em>what</em> you feed it, in <em>what</em> proportions, in <em>what</em> order. That choice is called the '
        '<strong>mixture</strong> and the <strong>curriculum</strong>, and writing it down, defended number by number, is the '
        'whole assignment.</p>\n'

        '  <div class="pull">A model becomes what it eats. The mixture isn’t a config file — it’s the personality.</div>\n'

        '  <h2>Start with the diet</h2>\n'
        '  <p>You have a fixed budget of tokens, a few trillion. Think of it as your total calories for the season. Now you have '
        'to spend it: how much English, how much code, how much math, how much of the Indian languages you actually care about. '
        'Every slice you give one skill is a slice you take from another, because the budget doesn’t grow.</p>\n'
        '  <p>And this is the part people underestimate. Pour most of your budget into code and starve the general web, and you '
        'get a model that writes flawless programs and has no common sense. Ask it to count the index fingers in a room and it '
        'will happily write a function that asks you how many index fingers each person has. The code runs. It just doesn’t '
        'understand the world. Common sense lives on the messy web, and if you don’t feed it, it won’t be there. That '
        'is why a big slice stays on general web even when it feels unglamorous.</p>\n'

        '  <h2>Be honest about the Indian-language data</h2>\n'
        '  <p>Indic is your differentiator — the reason this model is worth building. So the plan can’t hide behind a '
        'single number like “Indic 8%.” You have to break it open and say how much of it is genuinely verified '
        '(Wikipedia, textbooks), how much is raw web you cleaned, how much is translated from English, and how much you had a '
        'model generate. Those are four very different levels of trust, and a good plan admits exactly how much it is leaning on '
        'the weaker ones. Hiding that is the fastest way to lose the room.</p>\n'

        '  <h2>Name the hard skills out loud</h2>\n'
        '  <p>Three capabilities are easy to forget and painful to source: being <strong>agentic</strong> (planning, calling '
        'tools, recovering when a call fails), <strong>reasoning</strong> (showing its working), and <strong>long context</strong> '
        '(staying coherent over very long inputs). The assignment asks you to name each one and point at the actual dataset that '
        'will fill it. A slot without a dataset behind it is a wish, not a plan.</p>\n'

        '  <h2>Protect the fragile lanes from your own selector</h2>\n'
        '  <p>Here is my favorite trap. During training you often run an automatic selector that keeps whatever data seems to help '
        'the model most. Sounds great. But it usually glances only at the first few hundred tokens of each example, and it judges '
        '“helpful” against mostly English, mostly coding tests. So it looks at your Indian-language data, sees nothing '
        'that moves its English score, and throws it away. It looks at a long agent trace, sees a boring log, and tosses that too.</p>\n'
        '  <p>Left alone, your own selector will quietly starve the exact capabilities you are trying to build. So your plan sets '
        'a <strong>floor</strong> — a hard minimum for those lanes that the selector is never allowed to cross — and, '
        'better still, teaches the selector to care about the right things by scoring it against your target languages and tasks '
        'in the first place.</p>\n'

        '  <h2>Save your best data for last</h2>\n'
        '  <p>Training ends with a short cooldown, where the learning rate winds down to almost nothing. Whatever the model sees '
        'in that window lands with unusual force. It is the young Einstein, finally ready, sitting down to write the good paper. '
        'So you hold back your cleanest, highest-quality material — the PhD-level stuff — and spend it precisely then. '
        'Feed it too early and it just washes over an infant. That held-back slice is the <strong>anneal reserve</strong>, and it '
        'lives inside your budget, not on top of it.</p>\n'

        '  <h2>Order matters as much as amount</h2>\n'
        '  <p>You don’t teach a child quantum mechanics in nursery. You go broad and simple first — let the model learn '
        'language and how the world works — then gradually turn toward code, science, reasoning, and the long, hard problems. '
        'That progression is the curriculum, and it comes with two more labels on your data: how <strong>hard</strong> each piece '
        'is, and how <strong>long</strong> the thinking should be. One warning from painful experience: don’t switch the diet '
        'abruptly. Jump straight from easy web text to hard reasoning and the training destabilizes. You have to blend one phase '
        'into the next, the way school eases you from one grade into the following one rather than dropping you into a PhD seminar '
        'the day after high school.</p>\n'

        '  <h2>Every number is a guess until a cheap experiment proves it</h2>\n'
        '  <p>This is the principle under everything. Each proportion, each ordering, each floor feels like a decision and is '
        'written like one, but until you test it, it is a guess wearing a suit. And you don’t test guesses on the giant, '
        'expensive run. You test them small — a one-billion and a three-billion parameter model, cheap and fast, on competing '
        'recipes — and only the ones that actually win get promoted to full scale.</p>\n'

        '  <div class="pull">A data decision is a hypothesis until a cheap experiment has tested it.</div>\n'

        '  <h2>So what do you actually hand in?</h2>\n'
        '  <p>A written specification — a README — that a skeptic could read and push on. It gives a defended share of the '
        'budget to every capability, splits the Indic slice across those four trust tiers, names the agentic, reasoning and '
        'long-context lanes with the datasets behind them, sets the floors the selector can’t cross, reserves the best data '
        'for the cooldown, lays out the difficulty and reasoning-length bands with examples, and commits to proving all of it with '
        'small proxy runs first. It is graded on the quality of your reasoning, not on hitting some magic number.</p>\n'
        '  <p>Roughly, a mid-training snapshot of such a plan looks like this — illustrative, not gospel:</p>\n'
        '  <div class="snapshot">'
        '<span class="h">V5 mixture — mid-training snapshot (of a 3T-token budget)</span>\n\n'
        'general web   ~37%   common sense, world knowledge\n'
        'code          ~22%   Stack v2\n'
        'agentic       ~13%   tool-use + reasoning + reflection traces\n'
        'STEM          ~12%   textbooks, science\n'
        'reasoning      ~7%   step-by-step, short and long\n'
        'indic          ~8%   verified / unverified / translated / synthetic\n'
        'safety         ~1%\n\n'
        'best data held back for the cooldown · floors keep indic + agentic alive\n'
        'every share above tested at 1B and 3B before anyone trusts it at full scale</div>\n'

        '  <h2>The bottom line</h2>\n'
        '  <p>The architecture gets the headlines, but the mixture and curriculum are what make or break the model. Decide what '
        'you want it to be. Be honest about what you can actually feed it, and treat the gaps as your shopping list. Teach it in '
        'an order that goes from broad to deep, and save your best for last. Protect the fragile lanes from your own optimizer. '
        'And never forget that none of your numbers are true until a small, cheap experiment says they are.</p>\n'
        '  <p>Get this right, and the rest of training is the easy part.</p>\n'

        '  <div class="cta">Ready to actually build it? The <a href="v5_playbook.html"><strong>step-by-step how-to</strong></a> '
        'walks through it in order, with the real datasets and the token arithmetic worked out — including the moment you '
        'discover you’re starving in three places at once.</div>\n'
        '  <p class="foot">Companion files in the repo: <code>V5_PLAN.md</code> (the defended plan) and <code>mixture.py</code> '
        '(a script that checks every number).</p>\n'
        '</div>\n</body>\n</html>\n'
    )


if __name__ == "__main__":
    with open("v5_brief.html", "w", encoding="utf-8") as f:
        f.write(build_html())
    print("Done. v5_brief.html written.")
