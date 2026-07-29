"""Generate overview.html — the landing page that frames the whole pipeline."""

STAGES = [
    ("Cleaning", "index.html", "01", "Normalize", "Fix Unicode, strip control chars & boilerplate, decode entities — without touching Indic joiners."),
    ("Language", "language.html", "02", "Identify", "Which language is this really? Script analysis + a model, routing keep / review / quarantine."),
    ("Quality", "quality.html", "03", "Judge", "Nine cheap checks + a strictness slider decide if a document is good enough to train on."),
    ("Dedup", "dedup.html", "04", "De-duplicate", "MinHash / Jaccard find exact & near copies; keep one representative, drop the rest — keep translations."),
    ("PII", "pii.html", "05", "Redact", "Detect emails, IDs, secrets & names; mask or quarantine — never expose raw personal data."),
    ("Decontam", "decontam.html", "06", "Protect eval", "Remove training copies of benchmark items so scores measure ability, not memorization."),
    ("Tokenizer", "tokenizer.html", "07", "Measure fertility", "Why Indic scripts cost 2–4× the tokens under an English tokenizer — and how to fix it."),
    ("Manifest", "manifest.html", "08", "Admit", "The system-of-record: hashes, imported stage results, admission gates → admit / block a shard."),
]

CSS = """
:root { --bg:#FAFBFD; --ink:#16162A; --indigo:#2E357E; --indigo-soft:#6169B8; --marigold:#E0982B;
  --teal:#147D74; --rose:#B5476B; --line:#E3E4EE; --muted:#656579; --panel:#F1F2F8; }
*, *::before, *::after { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--ink); font-family:"Inter",system-ui,sans-serif; font-size:15px; line-height:1.6; -webkit-font-smoothing:antialiased; }
a { color:var(--indigo); text-decoration:none; } a:hover { text-decoration:underline; }
.nav { position:sticky; top:0; z-index:50; background:rgba(250,251,253,.96); border-bottom:1px solid var(--line); }
.nav-in { max-width:1280px; margin:0 auto; padding:10px 24px; display:flex; align-items:center; gap:14px; flex-wrap:wrap; }
.brand { font-family:"Spectral",serif; font-weight:700; color:var(--indigo); font-size:16px; margin-right:auto; }
.nav a { font-family:"IBM Plex Mono",monospace; font-size:11px; letter-spacing:.02em; color:var(--muted); padding:3px 2px; border-bottom:2px solid transparent; }
.nav a:hover { color:var(--ink); text-decoration:none; }
.nav a.active { color:var(--indigo); border-bottom-color:var(--marigold); }
.wrap { max-width:1280px; margin:0 auto; padding:0 24px 80px; }
.hero { padding:48px 0 20px; border-bottom:2px solid var(--ink); }
.hero .eyebrow { font-family:"IBM Plex Mono",monospace; font-size:11px; letter-spacing:.15em; text-transform:uppercase; color:var(--marigold); font-weight:600; }
.hero h1 { font-family:"Spectral",serif; font-weight:700; font-size:clamp(30px,5vw,52px); margin:10px 0 10px; line-height:1.05; }
.hero p { font-size:15px; color:#33334a; margin:0; max-width:70ch; }
.sec { margin:32px 0 0; } .sec h2 { font-family:"Spectral",serif; font-size:22px; margin:0 0 4px; }
.sec .lead { font-size:13px; color:var(--muted); margin:0 0 16px; }
.stages { display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:12px; }
.stage { display:block; border:1px solid var(--line); border-radius:12px; background:#fff; padding:16px 17px; transition:border-color .12s, transform .12s; }
.stage:hover { border-color:var(--indigo-soft); transform:translateY(-2px); text-decoration:none; }
.stage .num { font-family:"IBM Plex Mono",monospace; font-size:11px; font-weight:600; color:var(--marigold); }
.stage .nm { font-family:"Spectral",serif; font-weight:700; font-size:19px; color:var(--ink); margin:2px 0; }
.stage .verb { font-family:"IBM Plex Mono",monospace; font-size:10px; letter-spacing:.08em; text-transform:uppercase; color:var(--teal); }
.stage .d { font-size:13px; color:#44445a; margin-top:8px; }
.stage .go { font-family:"IBM Plex Mono",monospace; font-size:11px; color:var(--indigo); margin-top:10px; }
.facts { display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:1px; background:var(--line); border:1px solid var(--line); border-radius:12px; overflow:hidden; }
.fact { background:#fff; padding:15px 16px; }
.fact .n { font-family:"IBM Plex Mono",monospace; font-weight:700; font-size:22px; color:var(--indigo); }
.fact .l { font-size:11.5px; color:var(--muted); margin-top:4px; }
.mix { display:flex; height:26px; border-radius:7px; overflow:hidden; border:1px solid var(--line); margin-top:6px; }
.mix span { display:flex; align-items:center; justify-content:center; font-size:10px; color:#fff; font-family:"IBM Plex Mono",monospace; }
.mixleg { font-size:12px; color:var(--muted); margin-top:8px; }
.conv { border:1px solid var(--line); border-radius:12px; background:#fff; padding:16px 18px; font-size:13.5px; color:#33334a; }
.conv b { color:var(--ink); }
.conv ul { margin:8px 0 0; padding-left:20px; } .conv li { margin:4px 0; }
"""


def build_html():
    stage_cards = ""
    for name, href, num, verb, desc in STAGES:
        stage_cards += (
            '<a class="stage" href="' + href + '">'
            '<div class="num">STAGE ' + num + '</div>'
            '<div class="nm">' + name + '</div>'
            '<div class="verb">' + verb + '</div>'
            '<div class="d">' + desc + '</div>'
            '<div class="go">Open &#8594;</div></a>\n'
        )
    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>India-First 40B — Data Pipeline</title>\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link href="https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,600;0,700;1,600'
        '&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">\n'
        '<style>' + CSS + '</style>\n</head>\n<body>\n'
        '<div class="nav"><div class="nav-in">\n'
        '  <span class="brand">India-First 40B</span>\n'
        '  <a href=\"overview.html\" class=\"active\">Overview</a>\n'
        '  <a href=\"data.html\">Data</a>\n'
        '  <a href=\"index.html\">Cleaning</a>\n'
        '  <a href=\"language.html\">Language</a>\n'
        '  <a href=\"quality.html\">Quality</a>\n'
        '  <a href=\"dedup.html\">Dedup</a>\n'
        '  <a href=\"pii.html\">PII</a>\n'
        '  <a href=\"decontam.html\">Decontam</a>\n'
        '  <a href=\"tokenizer.html\">Tokenizer</a>\n'
        '  <a href=\"manifest.html\">Manifest</a>\n'
        '  <a href=\"v5_brief.html\">V5 Plan</a>\n'
        '</div></div>\n'
        '<div class="wrap">\n'
        '  <div class="hero">\n'
        '    <div class="eyebrow">A 40-billion-parameter model, built India-first</div>\n'
        '    <h1>Turning raw Indian-language text into training-ready data.</h1>\n'
        '    <p>These pages are an interactive tour of the data pipeline behind India-First 40B — a model meant to '
        'match frontier models on general tasks while being genuinely fluent in the top-10 Indian languages. Each '
        'stage below is a live, self-explaining tool you can click through.</p>\n'
        '  </div>\n'
        '  <div class="sec">\n'
        '    <h2>The pipeline</h2>\n'
        '    <p class="lead">Eight stages take a raw web/Wikipedia document and decide, with evidence, whether it '
        'earns a place in the corpus. Click any stage.</p>\n'
        '    <div class="stages">\n' + stage_cards + '    </div>\n'
        '  </div>\n'
        '  <div class="sec">\n'
        '    <h2>What we are building</h2>\n'
        '    <p class="lead">The corpus target the pipeline feeds.</p>\n'
        '    <div class="facts">\n'
        '      <div class="fact"><div class="n">40B</div><div class="l">parameters, trained from scratch</div></div>\n'
        '      <div class="fact"><div class="n">6T</div><div class="l">token corpus target</div></div>\n'
        '      <div class="fact"><div class="n">10</div><div class="l">Indian languages, first-class</div></div>\n'
        '      <div class="fact"><div class="n">4</div><div class="l">provenance tiers (T0–T3)</div></div>\n'
        '    </div>\n'
        '    <div style="margin-top:16px">\n'
        '      <div style="font-size:12px;color:#888;font-family:\'IBM Plex Mono\',monospace">TARGET CORPUS MIX</div>\n'
        '      <div class="mix">\n'
        '        <span style="width:40%;background:#2E357E">English 40%</span>\n'
        '        <span style="width:22%;background:#147D74">Indic 22%</span>\n'
        '        <span style="width:20%;background:#6169B8">Code 20%</span>\n'
        '        <span style="width:12%;background:#E0982B">Math/Sci 12%</span>\n'
        '        <span style="width:6%;background:#B5476B">Other 6%</span>\n'
        '      </div>\n'
        '      <div class="mixleg">Indic gets a deliberately large share so the model is fluent, not just capable of translation.</div>\n'
        '    </div>\n'
        '  </div>\n'
        '  <div class="sec">\n'
        '    <h2>How to read these pages</h2>\n'
        '    <div class="conv">\n'
        '      A few conventions run through every stage:\n'
        '      <ul>\n'
        '        <li><b>Plain verdicts</b> — a colour-coded badge (KEEP / REVIEW / DROP / …) with a one-sentence reason.</li>\n'
        '        <li><b>A strictness slider</b> — most stages have named policy bundles; drag it and every verdict re-computes live.</li>\n'
        '        <li><b>Hover-to-learn</b> — any dotted-underlined term shows a plain-English tooltip.</li>\n'
        '        <li><b>🧪 synthetic vs real</b> — hand-made examples tour the tricky cases; the rest are real Hindi Wikipedia.</li>\n'
        '        <li><b>Offline tiers</b> — heavy models (fastText, embeddings, a real tokenizer) are noted where a browser can’t run them.</li>\n'
        '      </ul>\n'
        '    </div>\n'
        '  </div>\n'
        '</div>\n</body>\n</html>\n'
    )


if __name__ == "__main__":
    with open("overview.html", "w", encoding="utf-8") as f:
        f.write(build_html())
    print("Done. overview.html written.")
