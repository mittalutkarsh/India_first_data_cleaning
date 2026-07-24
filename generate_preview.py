"""
Generate index.html — interactive normalization preview.
Normalization steps follow Normalization_SKILLS.md (Steps 04-14).
Each step is a checkbox; left panel shows raw with removed content
highlighted in rose; right panel shows the normalized result.

Run:  python3 generate_preview.py
Open: push to GitHub Pages, or python3 -m http.server 8000 locally.
"""

import json
import os
import re
import unicodedata

JSONL_PATH    = os.path.join("data", "wiki_hi", "wiki_hi.jsonl")
OUTPUT_PATH   = "index.html"
N_SAMPLE      = 30
PREVIEW_CHARS = 3000


# ---------------------------------------------------------------------------
# Synthetic "kitchen-sink" demo article
# ---------------------------------------------------------------------------
# Real Hindi Wikipedia is pre-cleaned Parquet, so most filters are no-ops on
# it. This synthetic article deliberately contains every kind of noise so all
# 11 steps fire visibly. Every invisible character is written with a Python
# escape (\uXXXX / \xNN) — no raw control bytes live in this source file.

def build_synthetic_article():
    BOM   = "﻿"          # Step 10
    ZWNJ  = "‌"          # Step 07 (preserved)
    ZWJ   = "‍"          # Step 07 (preserved)
    ZWSP  = "​"          # Step 08
    NBSP  = " "          # Step 13
    FFFD  = "�"          # Step 12
    NUL   = "\x00"          # Step 09
    VT    = "\x0b"          # Step 09
    DEL   = "\x7f"          # Step 09
    C1    = "\x85"          # Step 09 (NEL, a C1 control)
    LRE   = "‪"          # Step 11 (bidi embedding)
    PDF   = "‬"          # Step 11 (pop directional formatting)
    RLI   = "⁦"          # Step 11 (directional isolate)
    PDI   = "⁩"          # Step 11
    # NFC: decomposed forms that will compose on normalize()
    QA_DECOMP = "क़"      # क + ़  -> क़  (U+0958)
    E_ACUTE   = "é"           # e + ◌́  -> é

    lines = [
        BOM + "साफ-सफाई डेमो लेख " + LRE + "(bidi embed)" + PDF,
        "",
        "1. HTML एंटिटीज़: AT&amp;T, 5 &lt; 10 &gt; 3, &quot;नमस्ते&quot;, "
        "&#2360;&#2340;&#2381;&#2351; (सत्य), &#x0939;िंदी &nbsp; समाप्त।",
        "",
        "2. यूनिकोड NFC: " + QA_DECOMP + "िला (क़िला), caf" + E_ACUTE + " — "
        "दोनों संयोजित रूप में सामान्यीकृत होंगे।",
        "",
        "3. इंडिक जॉइनर (सुरक्षित): क्ष में ZWJ -> क्" + ZWJ + "ष, "
        "और ZWNJ -> अ" + ZWNJ + "ब — इन्हें कभी नहीं हटाया जाता।",
        "",
        "4. ज़ीरो-विड्थ स्पेस: शब्द" + ZWSP + "बीच" + ZWSP + "में छिपा है।",
        "",
        "5. C0/C1 कंट्रोल: पंक्ति" + NUL + "शून्य" + VT + "वर्टिकल" + DEL
        + "डेल" + C1 + "नेल — सब हटेंगे।",
        "",
        "6. भ्रष्ट वर्ण: टूटा" + FFFD + "अक्षर यहाँ है।",
        "",
        "7. दिशात्मक आइसोलेट: " + RLI + "العربية" + PDI + " के आसपास।",
        "",
        "8. CRLF लाइन एंडिंग:\r\nदूसरी पंक्ति\rतीसरी पंक्ति (CR/LF मिश्रित)।",
        "",
        "9. फालतू   स्पेस:  बहुत      सारे\t\tटैब और" + NBSP + NBSP
        + "नॉन-ब्रेकिंग स्पेस।",
        "",
        "",
        "",
        "",
        "10. घोस्ट टैग: <|endoftext|> [INST] यह प्रॉम्प्ट रैपर है [/INST] "
        "<|im_start|>assistant साफ हो जाना चाहिए।",
    ]
    text = "\n".join(lines)
    return {
        "id":    "synthetic-demo",
        "title": "\U0001F9EA Synthetic demo — every filter fires",
        "url":   "#",
        "text":  text,
        "kind":  "synthetic",
    }


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

# Patterns used to detect "interesting" real articles (evaluated on the
# preview window only, so whatever we detect is actually visible).
_DETECT = {
    "html":  re.compile(r"&(amp|lt|gt|quot|apos|nbsp|#\d+|#x[0-9a-fA-F]+);"),
    "zwsp":  re.compile("​"),
    "c0c1":  re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]"),
    "bom":   re.compile("﻿"),
    "bidi":  re.compile("[‪-‮⁦-⁩]"),
    "fffd":  re.compile("�"),
    "joiner": re.compile("[‌‍]"),
}


def curate_real(path, n_real):
    """Pick real articles that exercise the rare filters, then fill the rest
    with ordinary articles. Detection runs on the preview window only."""
    rare_keys = ["html", "c0c1", "bom", "bidi", "fffd", "zwsp", "joiner"]
    picked, filler = [], []
    seen = set()

    with open(path, encoding="utf-8") as f:
        for line in f:
            a = json.loads(line)
            window = a["text"][:PREVIEW_CHARS]
            hits = [k for k in rare_keys if _DETECT[k].search(window)]
            # articles with the RAREST features first (html/c0c1/bom/bidi/fffd)
            special = [k for k in ("html", "c0c1", "bom", "bidi", "fffd") if k in hits]
            if special and a["id"] not in seen:
                picked.append((special, a))
                seen.add(a["id"])
            elif len(filler) < n_real * 3 and a["id"] not in seen:
                filler.append(a)
                seen.add(a["id"])
            if len(picked) >= n_real:
                break

    # Sort picked so the most feature-rich come first
    picked.sort(key=lambda pa: -len(pa[0]))
    result = [a for _, a in picked]

    # Add a couple of zwsp/joiner examples if we have room and none picked them
    if len(result) < n_real:
        for a in filler:
            w = a["text"][:PREVIEW_CHARS]
            if _DETECT["zwsp"].search(w) or _DETECT["joiner"].search(w):
                result.append(a)
                if len(result) >= n_real:
                    break

    # Fill remaining slots with plain articles
    for a in filler:
        if len(result) >= n_real:
            break
        if a["id"] not in {r["id"] for r in result}:
            result.append(a)

    return result[:n_real]


def process_articles(articles):
    out = []
    for a in articles:
        out.append({
            "id":       a["id"],
            "title":    a["title"],
            "url":      a["url"],
            "text":     a["text"][:PREVIEW_CHARS],
            "full_len": len(a["text"]),
            "kind":     a.get("kind", "real"),
        })
    return out


def escape_json_controls(s):
    """json.dumps(ensure_ascii=False) escapes C0 (<0x20) but leaves DEL/C1
    (U+007F-U+009F) as raw bytes, which HTML parsers can mangle. Escape those
    to \\uXXXX so JSON.parse restores them intact in the browser."""
    return re.sub(
        "[\x7f-\x9f]",
        lambda m: "\\u%04x" % ord(m.group()),
        s,
    )


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

CSS = """
:root {
  --bg:#FAFBFD; --ink:#16162A; --indigo:#2E357E; --indigo-soft:#6169B8;
  --marigold:#E0982B; --teal:#147D74; --teal-soft:#3aa89c;
  --rose:#B5476B; --line:#E3E4EE; --muted:#656579; --panel:#F1F2F8;
}
*, *::before, *::after { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body {
  margin: 0; background: var(--bg); color: var(--ink);
  font-family: "Inter", system-ui, sans-serif;
  font-size: 15px; line-height: 1.6; -webkit-font-smoothing: antialiased;
}
a { color: var(--indigo); text-decoration: none; }
a:hover { text-decoration: underline; }
.nav {
  position: sticky; top: 0; z-index: 50;
  background: rgba(250,251,253,.96); border-bottom: 1px solid var(--line);
}
.nav-in {
  max-width: 1280px; margin: 0 auto; padding: 10px 24px;
  display: flex; align-items: center; gap: 18px; flex-wrap: wrap;
}
.brand {
  font-family: "Spectral", serif; font-weight: 700;
  color: var(--indigo); font-size: 16px; margin-right: auto;
}
.nav a {
  font-family: "IBM Plex Mono", monospace; font-size: 11px;
  letter-spacing: .03em; color: var(--muted);
  padding: 3px 2px; border-bottom: 2px solid transparent;
}
.nav a:hover { color: var(--ink); text-decoration: none; }
.nav a.active { color: var(--indigo); border-bottom-color: var(--marigold); }
.wrap { max-width: 1280px; margin: 0 auto; padding: 0 24px 80px; }
.phead { padding: 34px 0 12px; border-bottom: 2px solid var(--ink); }
.phead h1 {
  font-family: "Spectral", serif; font-weight: 700;
  font-size: clamp(24px, 3.6vw, 38px); margin: 8px 0 6px;
}
.phead .dek { font-size: 13px; color: #33334a; margin: 0; }
.del-eg {
  background: #fceef2; color: #8a1a3a; border-radius: 3px;
  padding: 1px 5px; font-family: "IBM Plex Mono", monospace; font-size: 11px;
}
.art-controls {
  display: flex; align-items: center; gap: 14px;
  padding: 16px 0 0; flex-wrap: wrap;
}
.ctrl-label {
  font-family: "IBM Plex Mono", monospace; font-size: 10px;
  letter-spacing: .12em; text-transform: uppercase;
  color: var(--muted); font-weight: 600;
}
.art-nav { display: flex; align-items: center; gap: 8px; }
.nav-btn {
  font-family: "IBM Plex Mono", monospace; font-size: 14px;
  border: 1px solid var(--line); border-radius: 7px;
  padding: 5px 13px; background: #fff; color: var(--indigo); cursor: pointer;
}
.nav-btn:hover { background: var(--panel); }
.nav-btn:disabled { color: var(--muted); cursor: default; background: #fff; }
.art-counter {
  font-family: "IBM Plex Mono", monospace; font-size: 12px;
  color: var(--muted); min-width: 68px; text-align: center;
}
.toggle-btn {
  margin-left: auto; font-family: "IBM Plex Mono", monospace; font-size: 11px;
  border: 1px solid var(--line); border-radius: 6px;
  padding: 4px 11px; background: #fff; color: var(--muted); cursor: pointer;
}
.toggle-btn:hover { color: var(--indigo); border-color: var(--indigo-soft); }
.step-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 8px; margin: 12px 0 0;
}
.step-card {
  border: 1px solid var(--line); border-radius: 10px; background: #fff;
  padding: 10px 11px; display: flex; align-items: flex-start; gap: 8px;
  cursor: pointer; user-select: none; transition: border-color .12s;
}
.step-card:hover { border-color: var(--indigo-soft); }
.step-card.on { border-color: var(--indigo); background: #f5f6fd; }
.step-card.preserve:hover { border-color: var(--teal-soft); }
.step-card.preserve.on { border-color: var(--teal); background: #eef6f4; }
.step-cb { margin-top: 2px; accent-color: var(--indigo); cursor: pointer; flex-shrink: 0; }
.step-card.preserve .step-cb { accent-color: var(--teal); }
.step-body { flex: 1; min-width: 0; }
.step-num {
  font-family: "IBM Plex Mono", monospace; font-size: 9px;
  font-weight: 600; letter-spacing: .1em; color: var(--marigold);
  display: block; margin-bottom: 2px;
}
.step-card.preserve .step-num { color: var(--teal); }
.step-name {
  font-weight: 600; font-size: 12px; color: var(--ink);
  display: block; margin-bottom: 2px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.step-desc { font-size: 10.5px; color: var(--muted); line-height: 1.35; display: block; margin-bottom: 5px; }
.step-badge {
  font-family: "IBM Plex Mono", monospace; font-size: 10px;
  font-weight: 600; padding: 1px 6px; border-radius: 4px;
  background: var(--panel); color: var(--muted); display: inline-block;
}
.step-badge.changed { background: #fceef2; color: var(--rose); }
.step-badge.found   { background: #eef6f4; color: var(--teal); }
.title-bar {
  margin: 12px 0 0; padding: 10px 15px; background: #fff;
  border: 1px solid var(--line); border-radius: 10px;
  display: flex; align-items: baseline; gap: 14px; flex-wrap: wrap;
}
.title-bar .t { font-family: "Spectral", serif; font-weight: 600; font-size: 18px; }
.title-bar a { font-family: "IBM Plex Mono", monospace; font-size: 11px; color: var(--muted); }
.stat-strip {
  display: grid; grid-template-columns: repeat(5, 1fr); gap: 1px;
  background: var(--line); border: 1px solid var(--line);
  margin: 11px 0; border-radius: 10px; overflow: hidden;
}
.stat { background: var(--bg); padding: 10px 13px; }
.stat-n {
  font-family: "IBM Plex Mono", monospace; font-weight: 600;
  font-size: clamp(12px, 1.9vw, 18px); color: var(--indigo); line-height: 1;
}
.stat-l { font-size: 10px; color: var(--muted); margin-top: 4px; }
.stat.rose .stat-n { color: var(--rose); }
.stat.teal .stat-n { color: var(--teal); }
.stat.grey .stat-n { color: var(--muted); }
@media (max-width: 600px) { .stat-strip { grid-template-columns: repeat(3, 1fr); } }
.panels { display: grid; grid-template-columns: 1fr 1fr; gap: 13px; }
@media (max-width: 860px) { .panels { grid-template-columns: 1fr; } }
.panel { border: 1px solid var(--line); border-radius: 12px; overflow: hidden; }
.panel-hd {
  padding: 8px 14px; display: flex; align-items: center; gap: 8px;
  border-bottom: 1px solid var(--line); background: var(--panel);
}
.panel-label {
  font-family: "IBM Plex Mono", monospace; font-size: 10px;
  font-weight: 600; letter-spacing: .09em; text-transform: uppercase; flex: 1;
}
.panel-label.raw  { color: var(--muted); }
.panel-label.norm { color: var(--indigo); }
.panel-body {
  padding: 15px; background: #fff; min-height: 260px; max-height: 520px;
  overflow-y: auto; font-size: 13.5px; line-height: 1.8;
  white-space: pre-wrap; word-break: break-word;
}
.del    { background: #fceef2; color: #8a1a3a; border-radius: 3px; }
.del-ws { background: #fceef2; color: #c0718d; border-radius: 3px;
          font-family: "IBM Plex Mono", monospace; font-size: 10px; }
.joiner { background: #eef6f4; color: var(--teal); border-radius: 3px;
          font-family: "IBM Plex Mono", monospace; font-size: 10px; padding: 0 2px; }
.ctrl { background: #fbeada; color: #9a5a12; border-radius: 3px;
        font-family: "IBM Plex Mono", monospace; font-size: 10px; padding: 0 2px; }
.badge-kind {
  font-family: "IBM Plex Mono", monospace; font-size: 10px; font-weight: 600;
  letter-spacing: .04em; padding: 2px 8px; border-radius: 5px; margin-left: 2px;
}
.badge-kind.synthetic { background: #fbeada; color: #9a5a12; }
.badge-kind.real      { background: #eef6f4; color: var(--teal); }
.trunc-note {
  font-family: "IBM Plex Mono", monospace; font-size: 10.5px; color: var(--muted);
  margin-top: 12px; padding-top: 9px; border-top: 1px dashed var(--line);
}
"""


# ---------------------------------------------------------------------------
# JavaScript
# NOTE: This is a raw string. All regex unicode escapes (\uXXXX) are
# written as literal ASCII so the browser's JS engine interprets them,
# NOT Python.  Never embed actual invisible/control characters here.
# ---------------------------------------------------------------------------

JS = r"""
var ARTICLES = JSON.parse(document.getElementById('articles-data').textContent);
var state = { idx: 0 };

/* ---- helpers ---- */
function countRe(text, re) {
  var m = text.match(re);
  return m ? m.length : 0;
}

function esc(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function fmt(n) {
  n = Math.abs(n);
  if (n >= 1e6) return (n / 1e6).toFixed(1) + 'M';
  if (n >= 1e3) return (n / 1e3).toFixed(1) + 'k';
  return String(n);
}

/* ================================================================
   NORMALIZATION STEPS  (Normalization_SKILLS.md Steps 04-14)
   All Unicode ranges use \uXXXX JS escape sequences — safe ASCII.
   ================================================================ */

var STEPS = [
  {
    id: 'step04', num: '04', name: 'HTML Entities',
    desc: 'Decode &amp; &lt; &#8217; and numeric refs',
    preserve: false,
    fn: function(text) {
      var before = text;
      text = text
        .replace(/&amp;/g,    '&')
        .replace(/&lt;/g,     '<')
        .replace(/&gt;/g,     '>')
        .replace(/&quot;/g,   '"')
        .replace(/&apos;/g,   "'")
        .replace(/&nbsp;/g,   ' ')
        .replace(/&#(\d+);/g, function(_, n) {
          var c = parseInt(n, 10);
          try { return c > 0 ? String.fromCodePoint(c) : _; } catch(e) { return _; }
        })
        .replace(/&#x([0-9a-fA-F]+);/g, function(_, h) {
          var c = parseInt(h, 16);
          try { return c > 0 ? String.fromCodePoint(c) : _; } catch(e) { return _; }
        });
      return { text: text, count: Math.max(0, before.length - text.length), label: 'decoded' };
    }
  },

  {
    id: 'step05', num: '05', name: 'Unicode NFC',
    desc: 'Compose diacritics to canonical form',
    preserve: false,
    fn: function(text) {
      var norm = text.normalize('NFC');
      return { text: norm, count: Math.max(0, text.length - norm.length), label: 'changed' };
    }
  },

  {
    id: 'step06', num: '06', name: 'Line Endings',
    desc: 'Convert CRLF and standalone CR to LF',
    preserve: false,
    fn: function(text) {
      var count = countRe(text, /\r/g);
      return { text: text.replace(/\r\n/g, '\n').replace(/\r/g, '\n'), count: count, label: 'converted' };
    }
  },

  {
    id: 'step07', num: '07', name: 'Indic Joiners',
    desc: 'Highlight U+200C ZWNJ and U+200D ZWJ — preserved',
    preserve: true,   // highlight-only, no removal
    fn: function(text) {
      var count = countRe(text, /[‌‍]/g);
      return { text: text, count: count, label: 'found' };
    }
  },

  {
    id: 'step08', num: '08', name: 'Zero Width Space',
    desc: 'Remove U+200B extraction noise',
    preserve: false,
    fn: function(text) {
      var count = countRe(text, /​/g);
      return { text: text.replace(/​/g, ''), count: count, label: 'removed' };
    }
  },

  {
        id: 'step09', num: '09', name: 'C0/C1 Controls',
    desc: 'Remove NUL and controls, keep LF and TAB',
    preserve: false,
    fn: function(text) {
      var re = /[\x00-\x08\x0b\x0c\x0e-\x1f\x7f\x80-\x9f]/g;
      var count = countRe(text, re);
      return { text: text.replace(/[\x00-\x08\x0b\x0c\x0e-\x1f\x7f\x80-\x9f]/g, ''), count: count, label: 'removed' };
    }
  },

  {
id: 'step10', num: '10', name: 'BOM',
    desc: 'Remove U+FEFF byte order marks',
    preserve: false,
    fn: function(text) {
      var count = countRe(text, /﻿/g);
      return { text: text.replace(/﻿/g, ''), count: count, label: 'removed' };
    }
  },

  {
    id: 'step11', num: '11', name: 'Bidi Controls',
    desc: 'Remove U+202A-U+202E and U+2066-U+2069',
    preserve: false,
    fn: function(text) {
      var count = countRe(text, /[‪-‮⁦-⁩]/g);
      return { text: text.replace(/[‪-‮⁦-⁩]/g, ''), count: count, label: 'removed' };
    }
  },

  {
    id: 'step12', num: '12', name: 'U+FFFD Corrupt',
    desc: 'Remove U+FFFD replacement characters',
    preserve: false,
    fn: function(text) {
      var count = countRe(text, /�/g);
      return { text: text.replace(/�/g, ''), count: count, label: 'removed' };
    }
  },

  {
    id: 'step13', num: '13', name: 'Whitespace',
    desc: 'Collapse spaces, trim lines, max 2 newlines',
    preserve: false,
    fn: function(text) {
      var before = text;
      // tabs to spaces
      text = text.replace(/\t/g, ' ');
      // collapse horizontal whitespace: regular space + non-breaking space U+00A0
      text = text.replace(/[  ]+/g, ' ');
      // trim trailing spaces per line
      text = text.replace(/[ ]+$/mg, '');
      // trim leading spaces per line
      text = text.replace(/^[ ]+/mg, '');
      // collapse 3+ newlines to 2
      text = text.replace(/\n{3,}/g, '\n\n');
      text = text.trim();
      return { text: text, count: Math.max(0, before.length - text.length), label: 'removed' };
    }
  },

  {
    id: 'step14', num: '14', name: 'Ghost Tags',
    desc: 'Remove <|endoftext|>, [INST], role wrappers',
    preserve: false,
    fn: function(text) {
      var patterns = [
        /<\|endoftext\|>/g,
        /<\|im_start\|>/g,      /<\|im_end\|>/g,
        /<\|eot_id\|>/g,
        /<\|start_header_id\|>/g, /<\|end_header_id\|>/g,
        /\[INST\]/g,            /\[\/INST\]/g,
        /\[USER\]/g,            /\[ASSISTANT\]/g,
        /<<SYS>>/g,             /<\/SYS>>/g,
        /<s>\s*/g,              /\s*<\/s>/g
      ];
      var count = 0;
      for (var i = 0; i < patterns.length; i++) {
        count += countRe(text, patterns[i]);
        text = text.replace(patterns[i], '');
      }
      return { text: text, count: count, label: 'removed' };
    }
  }
];

/* ---- apply checked steps in order ---- */
function applySteps(rawText, checkedIds) {
  var text = rawText;
  var counts = {};
  for (var i = 0; i < STEPS.length; i++) {
    var step = STEPS[i];
    var result = step.fn(text);           // compute on current accumulated text
    counts[step.id] = { count: result.count, label: result.label };
    if (!step.preserve && checkedIds[step.id]) {
      text = result.text;                 // only advance if checked
    }
  }
  return { normalized: text, counts: counts };
}

/* ---- word+whitespace diff ---- */
function splitTokens(text) {
  var parts = text.split(/(\s+)/);
  var out = [];
  for (var i = 0; i < parts.length; i++) {
    if (parts[i].length > 0) out.push(parts[i]);
  }
  return out;
}

function computeDiff(oldText, newText) {
  if (oldText === newText) return null;
  var a = splitTokens(oldText);
  var b = splitTokens(newText);
  if (a.length > 1200 || b.length > 1200) return null;
  var m = a.length, n = b.length, i, j;
  var dp = [];
  for (i = 0; i <= m; i++) dp[i] = new Int32Array(n + 1);
  for (i = m - 1; i >= 0; i--) {
    for (j = n - 1; j >= 0; j--) {
      dp[i][j] = a[i] === b[j]
        ? dp[i+1][j+1] + 1
        : (dp[i+1][j] >= dp[i][j+1] ? dp[i+1][j] : dp[i][j+1]);
    }
  }
  var ops = [];
  i = 0; j = 0;
  while (i < m || j < n) {
    if (i < m && j < n && a[i] === b[j]) {
      ops.push({ t: 'eq', s: a[i] }); i++; j++;
    } else if (j < n && (i >= m || dp[i][j+1] >= dp[i+1][j])) {
      ops.push({ t: 'ins', s: b[j] }); j++;
    } else {
      ops.push({ t: 'del', s: a[i] }); i++;
    }
  }
  return ops;
}

/* ---- joiner highlight: run on the final HTML string ---- */
function addJoinerHighlights(html) {
  return html
    .replace(/‌/g, '<span class="joiner" title="U+200C ZWNJ">[ZWNJ]</span>')
    .replace(/‍/g, '<span class="joiner" title="U+200D ZWJ">[ZWJ]</span>');
}

/* ---- make invisible / control characters visible as labelled badges ---- */
function hex(c) {
  var h = c.charCodeAt(0).toString(16).toUpperCase();
  while (h.length < 4) h = '0' + h;
  return 'U+' + h;
}
function markInvisibles(html) {
  return html
    .replace(/​/g, '<span class="ctrl" title="U+200B ZERO WIDTH SPACE">[ZWSP]</span>')
    .replace(/﻿/g, '<span class="ctrl" title="U+FEFF BYTE ORDER MARK">[BOM]</span>')
    .replace(/�/g, '<span class="ctrl" title="U+FFFD REPLACEMENT CHARACTER">[FFFD]</span>')
    .replace(/[‪-‮⁦-⁩]/g, function(c) {
      return '<span class="ctrl" title="bidi control ' + hex(c) + '">[BIDI ' + hex(c) + ']</span>';
    })
    .replace(/[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]/g, function(c) {
      return '<span class="ctrl" title="control ' + hex(c) + '">[' + hex(c) + ']</span>';
    });
}

/* ---- build raw panel HTML with diff highlights ---- */
function buildRawHtml(ops, rawText, showJoiners) {
  var html;
  if (!ops) {
    html = esc(rawText);
  } else {
    html = '';
    for (var k = 0; k < ops.length; k++) {
      var op = ops[k];
      if (op.t === 'ins') continue;
      if (op.t === 'del') {
        var isWs = /^\s+$/.test(op.s);
        if (isWs) {
          var vis = op.s
            .replace(/\n/g, '↵\n')
            .replace(/\t/g, '→')
            .replace(/ /g, '⍽')     /* NBSP U+00A0 */
            .replace(/ /g, '·');
          html += '<span class="del-ws">' + esc(vis) + '</span>';
        } else {
          html += '<span class="del">' + esc(op.s) + '</span>';
        }
      } else {
        html += esc(op.s);
      }
    }
  }
  if (showJoiners) html = addJoinerHighlights(html);
  html = markInvisibles(html);
  return html;
}

/* ---- main render ---- */
function getChecked() {
  var ids = {};
  var cbs = document.querySelectorAll('.step-cb');
  for (var i = 0; i < cbs.length; i++) ids[cbs[i].dataset.id] = cbs[i].checked;
  return ids;
}

function render() {
  var art        = ARTICLES[state.idx];
  var rawText    = art.text;
  var checkedIds = getChecked();

  var pipeline   = applySteps(rawText, checkedIds);
  var normText   = pipeline.normalized;
  var counts     = pipeline.counts;
  var showJoiners = checkedIds['step07'];

  /* --- step badge updates --- */
  for (var i = 0; i < STEPS.length; i++) {
    var s  = STEPS[i];
    var sc = counts[s.id];
    var el = document.getElementById('badge-' + s.id);
    if (!el) continue;
    el.textContent = sc.count + ' ' + sc.label;
    el.className   = 'step-badge' + (sc.count > 0 ? (s.preserve ? ' found' : ' changed') : '');
  }

  /* --- article header --- */
  document.getElementById('art-title').textContent          = art.title;
  var kindEl = document.getElementById('art-kind');
  kindEl.textContent = art.kind === 'synthetic' ? 'SYNTHETIC' : 'REAL — Wikipedia';
  kindEl.className   = 'badge-kind ' + (art.kind === 'synthetic' ? 'synthetic' : 'real');
  var urlEl = document.getElementById('art-url');
  urlEl.href         = art.url;
  urlEl.style.display = art.kind === 'synthetic' ? 'none' : '';
  document.getElementById('art-counter').textContent        = (state.idx + 1) + ' of ' + ARTICLES.length;
  document.getElementById('prev-btn').disabled              = state.idx === 0;
  document.getElementById('next-btn').disabled              = state.idx === ARTICLES.length - 1;

  /* --- stats --- */
  var rawTok      = Math.round(rawText.length / 4.5);
  var normTok     = Math.round(normText.length / 4.5);
  var delta       = normTok - rawTok;
  var charsRm     = rawText.length - normText.length;
  var stepsOn     = Object.keys(checkedIds).filter(function(k) { return checkedIds[k]; }).length;

  document.getElementById('s-raw').textContent    = fmt(rawTok);
  document.getElementById('s-norm').textContent   = fmt(normTok);
  document.getElementById('s-chars').textContent  = charsRm > 0 ? '-' + fmt(charsRm) : '0';
  document.getElementById('s-steps').textContent  = stepsOn;

  var dEl   = document.getElementById('s-delta');
  var dCell = dEl.parentElement;
  dEl.textContent  = delta === 0 ? '—' : (delta > 0 ? '+' : '') + fmt(Math.abs(delta));
  dCell.className  = 'stat ' + (delta < 0 ? 'rose' : delta > 0 ? 'teal' : 'grey');

  /* --- panels --- */
  var ops     = computeDiff(rawText, normText);
  var isTrunc = art.full_len > art.text.length;
  var truncNote = isTrunc
    ? '<div class="trunc-note">Showing first ' + fmt(art.text.length) + ' of ' + fmt(art.full_len) + ' chars</div>'
    : '';

  var rawHtml  = buildRawHtml(ops, rawText, showJoiners);
  var normHtml = esc(normText);
  if (showJoiners) normHtml = addJoinerHighlights(normHtml);
  normHtml = markInvisibles(normHtml);

  document.getElementById('panel-raw').innerHTML =
    '<div class="panel-hd"><span class="panel-label raw">Raw</span></div>' +
    '<div class="panel-body">' + rawHtml + truncNote + '</div>';

  document.getElementById('panel-norm').innerHTML =
    '<div class="panel-hd"><span class="panel-label norm">Normalized</span></div>' +
    '<div class="panel-body">' + normHtml + truncNote + '</div>';
}

/* ---- init: build step cards ---- */
var grid = document.getElementById('step-grid');
for (var si = 0; si < STEPS.length; si++) {
  (function(step) {
    var card = document.createElement('label');
    card.className = 'step-card on' + (step.preserve ? ' preserve' : '');
    card.innerHTML =
      '<input type="checkbox" class="step-cb" data-id="' + step.id + '" checked>' +
      '<div class="step-body">' +
        '<span class="step-num">STEP ' + step.num + '</span>' +
        '<span class="step-name">' + esc(step.name) + '</span>' +
        '<span class="step-desc">' + esc(step.desc) + '</span>' +
        '<span class="step-badge" id="badge-' + step.id + '">—</span>' +
      '</div>';
    grid.appendChild(card);
  })(STEPS[si]);
}

/* checkbox toggles */
grid.addEventListener('change', function(e) {
  if (!e.target.classList.contains('step-cb')) return;
  var card = e.target.closest('.step-card');
  if (e.target.checked) { card.classList.add('on'); }
  else                  { card.classList.remove('on'); }
  render();
});

/* select / clear all */
var allOn = true;
document.getElementById('toggle-btn').addEventListener('click', function() {
  allOn = !allOn;
  var cbs = document.querySelectorAll('.step-cb');
  for (var i = 0; i < cbs.length; i++) {
    cbs[i].checked = allOn;
    var card = cbs[i].closest('.step-card');
    if (allOn) { card.classList.add('on'); }
    else       { card.classList.remove('on'); }
  }
  this.textContent = allOn ? 'Clear all' : 'Check all';
  render();
});

/* article nav */
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


# ---------------------------------------------------------------------------
# HTML assembly  (plain string concatenation — no f-string brace issues)
# ---------------------------------------------------------------------------

def build_html(articles):
    data_json = escape_json_controls(json.dumps(articles, ensure_ascii=False))

    return (
        '<!DOCTYPE html>\n'
        '<html lang="en">\n'
        '<head>\n'
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>Data Preview — India-First 40B</title>\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link href="https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,600;0,700;1,600'
        '&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">\n'
        '<style>' + CSS + '</style>\n'
        '</head>\n'
        '<body>\n'
        '<script type="application/json" id="articles-data">' + data_json + '</script>\n'
        '<div class="nav"><div class="nav-in">\n'
        '  <span class="brand">India-First 40B</span>\n'
        '  <a href="#">Overview</a><a href="#">Data</a>\n'
        '  <a href="index.html" class="active">Cleaning</a>\n'
        '  <a href="language.html">Language</a>\n'
        '  <a href="quality.html">Quality</a>\n'
        '  <a href="dedup.html">Dedup</a>\n'
        '  <a href="pii.html">PII</a>\n'
        '  <a href="#">Tokenizer</a>\n'
        '</div></div>\n'
        '<div class="wrap">\n'
        '  <div class="phead">\n'
        '    <h1>Data Cleaning Preview</h1>\n'
        '    <p class="dek">Check/uncheck steps from <em>Normalization_SKILLS.md</em> — '
        '<span class="del-eg">rose highlights</span> show what each step removes from the raw text.</p>\n'
        '  </div>\n'
        '  <div class="art-controls">\n'
        '    <span class="ctrl-label">Article</span>\n'
        '    <div class="art-nav">\n'
        '      <button class="nav-btn" id="prev-btn">&#8592;</button>\n'
        '      <span class="art-counter" id="art-counter">1 of ' + str(N_SAMPLE) + '</span>\n'
        '      <button class="nav-btn" id="next-btn">&#8594;</button>\n'
        '    </div>\n'
        '    <button class="toggle-btn" id="toggle-btn">Clear all</button>\n'
        '  </div>\n'
        '  <div class="step-grid" id="step-grid"></div>\n'
        '  <div class="title-bar">\n'
        '    <span class="t" id="art-title"></span>\n'
        '    <span class="badge-kind" id="art-kind"></span>\n'
        '    <a id="art-url" href="#" target="_blank">&#8599; Wikipedia</a>\n'
        '  </div>\n'
        '  <div class="stat-strip">\n'
        '    <div class="stat"><div class="stat-n" id="s-raw">-</div><div class="stat-l">Raw tokens</div></div>\n'
        '    <div class="stat"><div class="stat-n" id="s-norm">-</div><div class="stat-l">Normalized tokens</div></div>\n'
        '    <div class="stat"><div class="stat-n" id="s-delta">-</div><div class="stat-l">Token delta</div></div>\n'
        '    <div class="stat"><div class="stat-n" id="s-chars">-</div><div class="stat-l">Chars removed</div></div>\n'
        '    <div class="stat"><div class="stat-n" id="s-steps">-</div><div class="stat-l">Steps active</div></div>\n'
        '  </div>\n'
        '  <div class="panels">\n'
        '    <div class="panel" id="panel-raw"></div>\n'
        '    <div class="panel" id="panel-norm"></div>\n'
        '  </div>\n'
        '</div>\n'
        '<script>' + JS + '</script>\n'
        '</body>\n'
        '</html>\n'
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    n_real = N_SAMPLE - 1  # first slot is the synthetic demo

    print("Building synthetic demo article...")
    synthetic = build_synthetic_article()

    print("Curating {} real articles (seeking rare-filter examples)...".format(n_real))
    real = curate_real(JSONL_PATH, n_real)

    print("Processing...")
    processed = [
        {
            "id":       synthetic["id"],
            "title":    synthetic["title"],
            "url":      synthetic["url"],
            "text":     synthetic["text"],
            "full_len": len(synthetic["text"]),
            "kind":     "synthetic",
        }
    ] + process_articles(real)

    print("Generating {}...".format(OUTPUT_PATH))
    html = build_html(processed)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    import re as _re

    # 1) No literal control chars must leak into the executable JS block
    js_start = html.find('<script>') + len('<script>')
    js_end   = html.rfind('</script>')
    js_block = html[js_start:js_end]
    bad_js = _re.findall(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", js_block)
    if bad_js:
        print("WARNING: control chars in JS block:", [hex(ord(c)) for c in bad_js])
    else:
        print("OK: no raw control chars in JS block.")

    # 2) No raw control chars anywhere in the file (data must be \\uXXXX-escaped)
    bad_all = _re.findall(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", html)
    if bad_all:
        print("WARNING: raw control chars in HTML:", sorted({hex(ord(c)) for c in bad_all}))
    else:
        print("OK: no raw control chars anywhere in the HTML.")

    print("\nDone. {} written ({} articles: 1 synthetic + {} real).".format(
        OUTPUT_PATH, len(processed), len(real)))
