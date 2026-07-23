"""
Generate index.html — interactive data cleaning preview tool.
Always shows Raw (left) vs Stage (right) side by side.
Deleted/removed content highlighted in rose on the left panel.

Run : python3 generate_preview.py
Serve: python3 -m http.server 8000  (then open http://localhost:8000)
"""

import json
import os
import re

JSONL_PATH    = os.path.join("data", "wiki_hi", "wiki_hi.jsonl")
OUTPUT_PATH   = "index.html"
N_SAMPLE      = 30
PREVIEW_CHARS = 3000


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_sample(path, n):
    articles = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= n:
                break
            articles.append(json.loads(line))
    return articles


def estimate_tokens(text):
    return round(len(text) / 4.5)


# ---------------------------------------------------------------------------
# Cleaning stages  (each returns new_text, status, reason)
# ---------------------------------------------------------------------------

def stage_raw(text):
    return text, "kept", None


def stage_whitespace(text):
    new = re.sub(r'\n{3,}', '\n\n', text)
    new = re.sub(r'[ \t]+', ' ', new)
    new = new.strip()
    return new, "kept", None


def stage_length_filter(text):
    if len(text) < 400:
        return text, "filtered", f"Too short ({len(text)} chars, min 400)"
    return text, "kept", None


def stage_stub_filter(text):
    patterns = ["may refer to", "disambiguation", "is a stub"]
    lower = text.lower()
    for p in patterns:
        if p in lower:
            return text, "filtered", f'Matched stub pattern: "{p}"'
    return text, "kept", None


STAGES = [
    ("raw",             "Raw",                   stage_raw),
    ("whitespace_norm", "Whitespace Normalized",  stage_whitespace),
    ("length_filter",   "Length Filter",          stage_length_filter),
    ("stub_filter",     "Stub / Disambig Filter", stage_stub_filter),
]


# ---------------------------------------------------------------------------
# Process articles through all stages
# ---------------------------------------------------------------------------

def process_articles(articles):
    result = []
    for art in articles:
        stages_out = {}
        current_text   = art["text"]
        current_status = "kept"

        for stage_id, _, fn in STAGES:
            if current_status == "filtered":
                stages_out[stage_id] = {
                    "text":     current_text[:PREVIEW_CHARS],
                    "full_len": len(current_text),
                    "tokens":   estimate_tokens(current_text),
                    "chars":    len(current_text),
                    "status":   "filtered",
                    "reason":   None,
                }
            else:
                new_text, status, reason = fn(current_text)
                stages_out[stage_id] = {
                    "text":     new_text[:PREVIEW_CHARS],
                    "full_len": len(new_text),
                    "tokens":   estimate_tokens(new_text),
                    "chars":    len(new_text),
                    "status":   status,
                    "reason":   reason,
                }
                current_text   = new_text
                current_status = status

        result.append({
            "id":     art["id"],
            "title":  art["title"],
            "url":    art["url"],
            "stages": stages_out,
        })
    return result


# ---------------------------------------------------------------------------
# HTML generation  (data embedded in <script type="application/json">)
# ---------------------------------------------------------------------------

CSS = """
:root {
  --bg: #FAFBFD; --ink: #16162A; --indigo: #2E357E; --indigo-soft: #6169B8;
  --marigold: #E0982B; --teal: #147D74; --teal-soft: #3aa89c;
  --rose: #B5476B; --line: #E3E4EE; --muted: #656579; --panel: #F1F2F8;
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body {
  margin: 0; background: var(--bg); color: var(--ink);
  font-family: "Inter", system-ui, sans-serif;
  font-size: 16px; line-height: 1.62; -webkit-font-smoothing: antialiased;
}
a { color: var(--indigo); text-decoration: none; }
a:hover { text-decoration: underline; }

/* nav */
.nav {
  position: sticky; top: 0; z-index: 50;
  background: rgba(250,251,253,.95);
  border-bottom: 1px solid var(--line);
}
.nav-in {
  max-width: 1200px; margin: 0 auto; padding: 11px 24px;
  display: flex; align-items: center; gap: 18px; flex-wrap: wrap;
}
.brand {
  font-family: "Spectral", serif; font-weight: 700;
  color: var(--indigo); font-size: 16px; margin-right: auto;
}
.nav a {
  font-family: "IBM Plex Mono", monospace; font-size: 11.5px;
  color: var(--muted); padding: 3px 2px; border-bottom: 2px solid transparent;
}
.nav a:hover { color: var(--ink); text-decoration: none; }
.nav a.active { color: var(--indigo); border-bottom-color: var(--marigold); }

/* layout */
.wrap { max-width: 1200px; margin: 0 auto; padding: 0 24px 80px; }
.phead { padding: 40px 0 16px; border-bottom: 2px solid var(--ink); }
.phead h1 {
  font-family: "Spectral", serif; font-weight: 700;
  font-size: clamp(26px, 4vw, 40px); margin: 8px 0 6px;
}
.phead .dek { font-size: 14px; color: #33334a; margin: 0; }
.del-example {
  background: #fceef2; color: #8a1a3a; border-radius: 3px;
  padding: 1px 5px; font-family: "IBM Plex Mono", monospace; font-size: 12px;
}

/* controls */
.controls {
  display: flex; align-items: flex-end; gap: 20px;
  flex-wrap: wrap; padding: 20px 0 0;
}
.ctrl-label {
  display: block; font-family: "IBM Plex Mono", monospace;
  font-size: 10px; letter-spacing: .12em; text-transform: uppercase;
  color: var(--muted); font-weight: 600; margin-bottom: 5px;
}
select {
  font-family: "IBM Plex Mono", monospace; font-size: 13px;
  border: 1px solid var(--line); border-radius: 8px;
  padding: 8px 14px; background: #fff; color: var(--ink);
  cursor: pointer; outline: none; min-width: 230px;
}
select:focus { border-color: var(--indigo); }
.article-nav { display: flex; align-items: center; gap: 8px; }
.nav-btn {
  font-family: "IBM Plex Mono", monospace; font-size: 14px;
  border: 1px solid var(--line); border-radius: 7px;
  padding: 6px 14px; background: #fff; color: var(--indigo); cursor: pointer;
}
.nav-btn:hover { background: var(--panel); }
.nav-btn:disabled { color: var(--muted); cursor: default; background: #fff; }
.article-counter {
  font-family: "IBM Plex Mono", monospace; font-size: 12px;
  color: var(--muted); min-width: 70px; text-align: center;
}

/* title bar */
.title-bar {
  margin: 16px 0 0; padding: 12px 18px;
  background: #fff; border: 1px solid var(--line); border-radius: 12px;
  display: flex; align-items: baseline; gap: 14px; flex-wrap: wrap;
}
.title-bar .t {
  font-family: "Spectral", serif; font-weight: 600; font-size: 20px;
}
.title-bar a {
  font-family: "IBM Plex Mono", monospace; font-size: 11px; color: var(--muted);
}

/* stats strip */
.stat-strip {
  display: grid; grid-template-columns: repeat(5, 1fr);
  gap: 1px; background: var(--line);
  border: 1px solid var(--line); margin: 14px 0;
  border-radius: 10px; overflow: hidden;
}
.stat { background: var(--bg); padding: 12px 14px; }
.stat-n {
  font-family: "IBM Plex Mono", monospace; font-weight: 600;
  font-size: clamp(14px, 2.2vw, 20px); color: var(--indigo); line-height: 1;
}
.stat-l { font-size: 10.5px; color: var(--muted); margin-top: 5px; }
.rose .stat-n { color: var(--rose); }
.teal .stat-n { color: var(--teal); }
.muted-stat .stat-n { color: var(--muted); }
@media (max-width: 640px) { .stat-strip { grid-template-columns: repeat(3, 1fr); } }

/* panels */
.panels { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
@media (max-width: 820px) { .panels { grid-template-columns: 1fr; } }
.panel { border: 1px solid var(--line); border-radius: 14px; overflow: hidden; }
.panel-hd {
  padding: 10px 16px; display: flex; align-items: center; gap: 10px;
  border-bottom: 1px solid var(--line); background: var(--panel);
}
.panel-label {
  font-family: "IBM Plex Mono", monospace; font-size: 10.5px;
  font-weight: 600; letter-spacing: .09em; text-transform: uppercase; flex: 1;
}
.panel-label.raw   { color: var(--muted); }
.panel-label.stage { color: var(--indigo); }
.pbadge {
  font-family: "IBM Plex Mono", monospace; font-size: 10px;
  padding: 2px 8px; border-radius: 5px; font-weight: 600;
}
.pbadge.kept     { background: #e8f5f3; color: var(--teal); }
.pbadge.filtered { background: #fceef2; color: var(--rose); }
.panel-body {
  padding: 18px; background: #fff;
  min-height: 300px; max-height: 560px; overflow-y: auto;
  position: relative; font-size: 14px; line-height: 1.75;
  white-space: pre-wrap; word-break: break-word;
}

/* diff highlights */
.del    { background: #fceef2; color: #8a1a3a; border-radius: 3px; padding: 0 1px; }
.del-ws { background: #fceef2; color: #c0718d; border-radius: 3px; padding: 0 1px;
           font-family: "IBM Plex Mono", monospace; font-size: 11px; }

/* filtered overlay */
.filtered-overlay {
  position: absolute; inset: 0; background: rgba(181,71,107,.07);
  display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 10px;
}
.filtered-badge {
  font-family: "IBM Plex Mono", monospace; font-size: 13px; font-weight: 600;
  background: var(--rose); color: #fff; padding: 6px 18px;
  border-radius: 8px; letter-spacing: .1em;
}
.filtered-reason {
  font-family: "IBM Plex Mono", monospace; font-size: 11px;
  color: var(--rose); background: #fceef2;
  border: 1px solid #f0c0cc; border-radius: 6px;
  padding: 5px 12px; max-width: 280px; text-align: center;
}
.trunc-note {
  font-family: "IBM Plex Mono", monospace; font-size: 11px; color: var(--muted);
  margin-top: 14px; padding-top: 10px; border-top: 1px dashed var(--line);
}
"""

JS = r"""
const ARTICLES = JSON.parse(document.getElementById('articles-data').textContent);
const STAGES   = JSON.parse(document.getElementById('stages-data').textContent);
let state = { idx: 0, stageIdx: 0 };

function esc(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function fmt(n) {
  if (n >= 1e6) return (n / 1e6).toFixed(1) + 'M';
  if (n >= 1e3) return (n / 1e3).toFixed(1) + 'k';
  return String(n);
}

/* ---- word+whitespace level diff ---- */
function splitTokens(text) {
  return text.split(/(\s+)/).filter(function(t) { return t.length > 0; });
}

function computeDiff(oldText, newText) {
  if (oldText === newText) return null;
  const a = splitTokens(oldText);
  const b = splitTokens(newText);
  if (a.length > 1000 || b.length > 1000) return null;

  const m = a.length, n = b.length;
  const dp = [];
  for (let i = 0; i <= m; i++) {
    dp[i] = new Int32Array(n + 1);
  }
  for (let i = m - 1; i >= 0; i--) {
    for (let j = n - 1; j >= 0; j--) {
      dp[i][j] = a[i] === b[j]
        ? dp[i+1][j+1] + 1
        : Math.max(dp[i+1][j], dp[i][j+1]);
    }
  }

  const ops = [];
  let i = 0, j = 0;
  while (i < m || j < n) {
    if (i < m && j < n && a[i] === b[j]) {
      ops.push({ type: 'eq', text: a[i] }); i++; j++;
    } else if (j < n && (i >= m || dp[i][j+1] >= dp[i+1][j])) {
      ops.push({ type: 'ins', text: b[j] }); j++;
    } else {
      ops.push({ type: 'del', text: a[i] }); i++;
    }
  }
  return ops;
}

/* ---- build HTML for left (raw) panel with diff highlights ---- */
function buildRawHtml(ops, rawText) {
  if (!ops) return esc(rawText);
  var html = '';
  for (var k = 0; k < ops.length; k++) {
    var op = ops[k];
    if (op.type === 'ins') continue;  // insertions don't appear in raw
    if (op.type === 'del') {
      var isWs = /^\s+$/.test(op.text);
      if (isWs) {
        var visible = op.text.replace(/\n/g, '↵\n').replace(/ /g, '·');
        html += '<span class="del-ws">' + esc(visible) + '</span>';
      } else {
        html += '<span class="del">' + esc(op.text) + '</span>';
      }
    } else {
      html += esc(op.text);
    }
  }
  return html;
}

/* ---- render a single panel ---- */
function buildPanel(labelText, labelClass, badgeStatus, bodyHtml, showFilteredOverlay, reason, isTruncated, fullLen, previewLen) {
  var truncNote = isTruncated
    ? '<div class="trunc-note">Showing first ' + fmt(previewLen) + ' of ' + fmt(fullLen) + ' chars</div>'
    : '';
  var overlay = '';
  if (showFilteredOverlay) {
    overlay = '<div class="filtered-overlay">'
            + '<div class="filtered-badge">FILTERED</div>'
            + (reason ? '<div class="filtered-reason">' + esc(reason) + '</div>' : '')
            + '</div>';
  }
  return '<div class="panel-hd">'
       + '<span class="panel-label ' + labelClass + '">' + esc(labelText) + '</span>'
       + '<span class="pbadge ' + badgeStatus + '">' + badgeStatus + '</span>'
       + '</div>'
       + '<div class="panel-body">'
       + bodyHtml
       + truncNote
       + overlay
       + '</div>';
}

/* ---- main render ---- */
function render() {
  var art      = ARTICLES[state.idx];
  var stage    = STAGES[state.stageIdx];
  var rawData  = art.stages[STAGES[0].id];
  var sData    = art.stages[stage.id];

  document.getElementById('article-title').textContent = art.title;
  document.getElementById('article-url').href          = art.url;
  document.getElementById('article-counter').textContent = (state.idx + 1) + ' of ' + ARTICLES.length;
  document.getElementById('prev-btn').disabled = (state.idx === 0);
  document.getElementById('next-btn').disabled = (state.idx === ARTICLES.length - 1);

  document.getElementById('s-raw-tok').textContent   = fmt(rawData.tokens);
  document.getElementById('s-stage-tok').textContent = fmt(sData.tokens);
  document.getElementById('s-raw-chars').textContent = fmt(rawData.chars);

  var delta    = sData.tokens - rawData.tokens;
  var deltaEl  = document.getElementById('s-delta');
  var deltaCell = deltaEl.parentElement;
  deltaEl.textContent = delta === 0 ? '—' : (delta > 0 ? '+' : '') + fmt(delta);
  deltaCell.className = 'stat ' + (delta < 0 ? 'rose' : delta > 0 ? 'teal' : 'muted-stat');

  var statusEl   = document.getElementById('s-status');
  var statusCell = document.getElementById('s-status-cell');
  statusEl.textContent = sData.status.toUpperCase();
  statusCell.className = 'stat ' + (sData.status === 'filtered' ? 'rose' : 'teal');

  // build diff between raw and stage
  var ops = computeDiff(rawData.text, sData.text);

  // left panel — raw with highlights
  var rawHtml = buildPanel(
    'Raw', 'raw', rawData.status,
    buildRawHtml(ops, rawData.text),
    false, null,
    rawData.full_len > rawData.text.length,
    rawData.full_len, rawData.text.length
  );

  // right panel — stage result with filtered overlay if needed
  var stageHtml = buildPanel(
    stage.label, 'stage', sData.status,
    esc(sData.text),
    sData.status === 'filtered', sData.reason,
    sData.full_len > sData.text.length,
    sData.full_len, sData.text.length
  );

  document.getElementById('panel-raw').innerHTML   = rawHtml;
  document.getElementById('panel-stage').innerHTML = stageHtml;
}

// populate stage dropdown
var sel = document.getElementById('stage-select');
STAGES.forEach(function(s, i) {
  var o = document.createElement('option');
  o.value = i; o.textContent = s.label;
  sel.appendChild(o);
});
sel.addEventListener('change', function(e) { state.stageIdx = +e.target.value; render(); });

document.getElementById('prev-btn').addEventListener('click', function() {
  if (state.idx > 0) { state.idx--; render(); }
});
document.getElementById('next-btn').addEventListener('click', function() {
  if (state.idx < ARTICLES.length - 1) { state.idx++; render(); }
});
document.addEventListener('keydown', function(e) {
  if (e.key === 'ArrowLeft'  && state.idx > 0)                   { state.idx--; render(); }
  if (e.key === 'ArrowRight' && state.idx < ARTICLES.length - 1) { state.idx++; render(); }
});

render();
"""


def build_html(articles):
    stages_meta = [{"id": s[0], "label": s[1]} for s in STAGES]

    articles_json = json.dumps(articles,    ensure_ascii=False, indent=None)
    stages_json   = json.dumps(stages_meta, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Data Preview — India-First 40B</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,600;0,700;1,600&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>

<script type="application/json" id="articles-data">{articles_json}</script>
<script type="application/json" id="stages-data">{stages_json}</script>

<div class="nav">
  <div class="nav-in">
    <span class="brand">India-First 40B</span>
    <a href="#">Overview</a>
    <a href="#">Data</a>
    <a href="#">Cleaning</a>
    <a href="#">Tokenizer</a>
    <a href="#" class="active">Preview</a>
  </div>
</div>

<div class="wrap">
  <div class="phead">
    <h1>Data Cleaning Preview</h1>
    <p class="dek">
      Raw (left) vs cleaning stage (right) — 30 sample Hindi Wikipedia articles.
      <span class="del-example">highlighted</span> text on the left shows what each stage removes.
    </p>
  </div>

  <div class="controls">
    <div>
      <span class="ctrl-label">Cleaning stage</span>
      <select id="stage-select"></select>
    </div>
    <div>
      <span class="ctrl-label">Article</span>
      <div class="article-nav">
        <button class="nav-btn" id="prev-btn">&#8592;</button>
        <span class="article-counter" id="article-counter">1 of {N_SAMPLE}</span>
        <button class="nav-btn" id="next-btn">&#8594;</button>
      </div>
    </div>
  </div>

  <div class="title-bar">
    <span class="t" id="article-title"></span>
    <a id="article-url" href="#" target="_blank">&#8599; Wikipedia</a>
  </div>

  <div class="stat-strip">
    <div class="stat"><div class="stat-n" id="s-raw-tok">—</div><div class="stat-l">Raw tokens</div></div>
    <div class="stat"><div class="stat-n" id="s-stage-tok">—</div><div class="stat-l">Stage tokens</div></div>
    <div class="stat"><div class="stat-n" id="s-delta">—</div><div class="stat-l">Token delta</div></div>
    <div class="stat"><div class="stat-n" id="s-raw-chars">—</div><div class="stat-l">Raw chars</div></div>
    <div class="stat" id="s-status-cell"><div class="stat-n" id="s-status">—</div><div class="stat-l">Status</div></div>
  </div>

  <div class="panels">
    <div class="panel" id="panel-raw"></div>
    <div class="panel" id="panel-stage"></div>
  </div>
</div>

<script>{JS}</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print(f"Loading {N_SAMPLE} articles from {JSONL_PATH}...")
    raw = load_sample(JSONL_PATH, N_SAMPLE)

    print("Applying cleaning stages...")
    processed = process_articles(raw)

    print(f"Generating {OUTPUT_PATH}...")
    html = build_html(processed)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    kept = sum(1 for a in processed if a["stages"]["stub_filter"]["status"] == "kept")
    print(f"\nDone. {OUTPUT_PATH} written.")
    print(f"  Articles                 : {len(processed)}")
    print(f"  Kept after all stages    : {kept}/{len(processed)}")
    print(f"\nServe with:")
    print(f"  python3 -m http.server 8000")
    print(f"  then open http://localhost:8000")
