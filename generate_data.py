"""Generate data.html — the data sources & practice-corpus page."""

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
.phead { padding:34px 0 12px; border-bottom:2px solid var(--ink); }
.phead h1 { font-family:"Spectral",serif; font-weight:700; font-size:clamp(24px,3.6vw,38px); margin:8px 0 6px; }
.phead .dek { font-size:13px; color:#33334a; margin:0; max-width:82ch; }
.sec { margin:30px 0 0; } .sec h2 { font-family:"Spectral",serif; font-size:22px; margin:0 0 4px; }
.sec .lead { font-size:13px; color:var(--muted); margin:0 0 14px; }
.facts { display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:1px; background:var(--line); border:1px solid var(--line); border-radius:12px; overflow:hidden; }
.fact { background:#fff; padding:15px 16px; }
.fact .n { font-family:"IBM Plex Mono",monospace; font-weight:700; font-size:22px; color:var(--indigo); }
.fact .l { font-size:11.5px; color:var(--muted); margin-top:4px; }
.tbl { width:100%; border-collapse:collapse; font-size:13px; background:#fff; border:1px solid var(--line); border-radius:12px; overflow:hidden; }
.tbl th, .tbl td { text-align:left; padding:9px 13px; border-bottom:1px solid var(--line); }
.tbl th { font-family:"IBM Plex Mono",monospace; font-size:10px; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); background:var(--panel); }
.tbl td code { font-family:"IBM Plex Mono",monospace; font-size:11.5px; background:var(--panel); padding:1px 5px; border-radius:4px; }
.tier { font-family:"IBM Plex Mono",monospace; font-size:10px; font-weight:600; padding:1px 7px; border-radius:5px; }
.t0 { background:#eef6f4; color:var(--teal); } .t1 { background:#eef0fb; color:var(--indigo); }
.t2 { background:#fdf3e3; color:#9a5a12; } .t3 { background:#fceef2; color:var(--rose); }
.langs { display:flex; flex-wrap:wrap; gap:8px; }
.lang { border:1px solid var(--line); border-radius:8px; background:#fff; padding:8px 12px; font-size:13px; }
.lang b { font-family:"Spectral",serif; }
.lang .sc { font-family:"IBM Plex Mono",monospace; font-size:10px; color:var(--muted); }
.callout { border-left:3px solid var(--marigold); background:#fdf9f1; border-radius:0 8px 8px 0; padding:12px 15px; font-size:13.5px; color:#5a4520; margin-top:14px; }
.callout b { color:#8a5a12; }
"""


def build_html():
    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>Data — India-First 40B</title>\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link href="https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,600;0,700;1,600'
        '&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">\n'
        '<style>' + CSS + '</style>\n</head>\n<body>\n'
        '<div class="nav"><div class="nav-in">\n'
        '  <span class="brand">India-First 40B</span>\n'
        '  <a href=\"overview.html\">Overview</a>\n'
        '  <a href=\"data.html\" class=\"active\">Data</a>\n'
        '  <a href=\"index.html\">Cleaning</a>\n'
        '  <a href=\"language.html\">Language</a>\n'
        '  <a href=\"quality.html\">Quality</a>\n'
        '  <a href=\"dedup.html\">Dedup</a>\n'
        '  <a href=\"pii.html\">PII</a>\n'
        '  <a href=\"decontam.html\">Decontam</a>\n'
        '  <a href=\"tokenizer.html\">Tokenizer</a>\n'
        '  <a href=\"manifest.html\">Manifest</a>\n'
        '  <a href=\"v5_brief.html\">V5 Plan</a>\n'
        '  <a href=\"v5_playbook.html\">V5 Plan — Proposal</a>\n'
        '</div></div>\n'
        '<div class="wrap">\n'
        '  <div class="phead">\n'
        '    <h1>The Data</h1>\n'
        '    <p class="dek">Where the corpus comes from, how provenance is tiered, and the small practice slice these '
        'interactive pages actually run on.</p>\n'
        '  </div>\n'
        '  <div class="sec">\n'
        '    <h2>Practice slice (what these pages use)</h2>\n'
        '    <p class="lead">A laptop-sized sample so everything runs live in the browser.</p>\n'
        '    <div class="facts">\n'
        '      <div class="fact"><div class="n">40,000</div><div class="l">Hindi Wikipedia articles</div></div>\n'
        '      <div class="fact"><div class="n">~14.5M</div><div class="l">estimated tokens</div></div>\n'
        '      <div class="fact"><div class="n">1,635</div><div class="l">avg characters / article</div></div>\n'
        '      <div class="fact"><div class="n">T0</div><div class="l">tier — native-verified</div></div>\n'
        '    </div>\n'
        '    <div class="callout"><b>Source:</b> <code>wikimedia/wikipedia</code>, config <code>20231101.hi</code>, '
        'streamed to <code>data/wiki_hi/wiki_hi.jsonl</code>. Each interactive page embeds ~10–30 of these real '
        'articles plus hand-made <b>🧪 synthetic</b> examples that tour the tricky cases the real data rarely shows.</div>\n'
        '  </div>\n'
        '  <div class="sec">\n'
        '    <h2>Full-corpus sources</h2>\n'
        '    <p class="lead">The datasets the real 6T-token corpus would draw on (beyond this practice slice).</p>\n'
        '    <table class="tbl">\n'
        '      <tr><th>Source</th><th>Scale</th><th>Role</th></tr>\n'
        '      <tr><td><code>ai4bharat/sangraha</code></td><td>~251B tokens</td><td>Largest verified Indic web + curated corpus</td></tr>\n'
        '      <tr><td><code>ai4bharat/IndicCorpV2</code></td><td>~20.9B tokens</td><td>Cleaned Indic monolingual web text</td></tr>\n'
        '      <tr><td><code>wikimedia/wikipedia</code></td><td>10–90M / language</td><td>High-trust native-verified reference text</td></tr>\n'
        '    </table>\n'
        '  </div>\n'
        '  <div class="sec">\n'
        '    <h2>Provenance tiers</h2>\n'
        '    <p class="lead">Every document is tagged by how trustworthy its origin is — this drives quality and PII policy downstream.</p>\n'
        '    <table class="tbl">\n'
        '      <tr><th>Tier</th><th>Meaning</th><th>Example</th></tr>\n'
        '      <tr><td><span class="tier t0">T0</span></td><td>Native-verified — high-trust, human-curated native text</td><td>Wikipedia, textbooks</td></tr>\n'
        '      <tr><td><span class="tier t1">T1</span></td><td>Native-web — crawled native text, machine-cleaned</td><td>Sangraha, IndicCorp</td></tr>\n'
        '      <tr><td><span class="tier t2">T2</span></td><td>Synthetic — model-generated, lineage-tracked</td><td>Generated Q&amp;A, distillation</td></tr>\n'
        '      <tr><td><span class="tier t3">T3</span></td><td>Translated — content ported from another language</td><td>MT of English corpora</td></tr>\n'
        '    </table>\n'
        '  </div>\n'
        '  <div class="sec">\n'
        '    <h2>Target languages</h2>\n'
        '    <p class="lead">The ten Indian languages the model treats as first-class.</p>\n'
        '    <div class="langs">\n'
        '      <div class="lang"><b>Hindi</b> <span class="sc">hi · Deva</span></div>\n'
        '      <div class="lang"><b>Bengali</b> <span class="sc">bn · Beng</span></div>\n'
        '      <div class="lang"><b>Tamil</b> <span class="sc">ta · Taml</span></div>\n'
        '      <div class="lang"><b>Telugu</b> <span class="sc">te · Telu</span></div>\n'
        '      <div class="lang"><b>Marathi</b> <span class="sc">mr · Deva</span></div>\n'
        '      <div class="lang"><b>Kannada</b> <span class="sc">kn · Knda</span></div>\n'
        '      <div class="lang"><b>Malayalam</b> <span class="sc">ml · Mlym</span></div>\n'
        '      <div class="lang"><b>Gujarati</b> <span class="sc">gu · Gujr</span></div>\n'
        '      <div class="lang"><b>Punjabi</b> <span class="sc">pa · Guru</span></div>\n'
        '      <div class="lang"><b>Odia</b> <span class="sc">or · Orya</span></div>\n'
        '    </div>\n'
        '    <div class="callout">Hindi and Marathi share the <b>Devanagari</b> script; that shared-script ambiguity is '
        'exactly what the <a href="language.html">Language</a> stage has to resolve.</div>\n'
        '  </div>\n'
        '</div>\n</body>\n</html>\n'
    )


if __name__ == "__main__":
    with open("data.html", "w", encoding="utf-8") as f:
        f.write(build_html())
    print("Done. data.html written.")
