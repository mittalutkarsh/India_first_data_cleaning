"""
Generate language.html — interactive language-identification preview.

Follows Language_Skill.md: treats LID as a corpus-admission + accounting
system, not a single classifier call. The browser runs the *observable*,
dependency-free tier — Unicode-block script analysis, code-mix detection,
claimed-vs-detected, decision routing with reason codes, and corpus
accounting. Real model-based LID (fastText) is produced offline by
run_lid.py and baked in as lid_results.json when present.

Run:  python3 generate_language_preview.py
"""

import json
import os

import lang_sample

OUTPUT_PATH = "language.html"
LID_RESULTS = "lid_results.json"


# ---------------------------------------------------------------------------
# CSS  (shares the India-First 40B palette)
# ---------------------------------------------------------------------------

CSS = """
:root {
  --bg:#FAFBFD; --ink:#16162A; --indigo:#2E357E; --indigo-soft:#6169B8;
  --marigold:#E0982B; --teal:#147D74; --teal-soft:#3aa89c;
  --rose:#B5476B; --line:#E3E4EE; --muted:#656579; --panel:#F1F2F8;
  --sc-latn:#C7761B; --sc-arab:#B5476B; --sc-drav:#147D74;
  --sc-beng:#7A3FB0; --sc-other:#8a1a3a;
}
*, *::before, *::after { box-sizing: border-box; }
body {
  margin:0; background:var(--bg); color:var(--ink);
  font-family:"Inter",system-ui,sans-serif; font-size:15px; line-height:1.6;
  -webkit-font-smoothing:antialiased;
}
a { color:var(--indigo); text-decoration:none; }
a:hover { text-decoration:underline; }
.nav { position:sticky; top:0; z-index:50; background:rgba(250,251,253,.96);
       border-bottom:1px solid var(--line); }
.nav-in { max-width:1280px; margin:0 auto; padding:10px 24px; display:flex;
          align-items:center; gap:18px; flex-wrap:wrap; }
.brand { font-family:"Spectral",serif; font-weight:700; color:var(--indigo);
         font-size:16px; margin-right:auto; }
.nav a { font-family:"IBM Plex Mono",monospace; font-size:11px;
         letter-spacing:.03em; color:var(--muted); padding:3px 2px;
         border-bottom:2px solid transparent; }
.nav a:hover { color:var(--ink); text-decoration:none; }
.nav a.active { color:var(--indigo); border-bottom-color:var(--marigold); }
.wrap { max-width:1280px; margin:0 auto; padding:0 24px 80px; }
.phead { padding:34px 0 12px; border-bottom:2px solid var(--ink); }
.phead h1 { font-family:"Spectral",serif; font-weight:700;
            font-size:clamp(24px,3.6vw,38px); margin:8px 0 6px; }
.phead .dek { font-size:13px; color:#33334a; margin:0; max-width:80ch; }
.note { font-size:12px; color:var(--muted); margin-top:8px; max-width:80ch; }

/* explainer + collapsible sections */
.explainer { margin:16px 0 0; border:1px solid var(--line); border-radius:12px;
             background:#fff; overflow:hidden; }
.explainer > summary, .more > summary {
  cursor:pointer; list-style:none; padding:12px 16px; font-weight:600;
  font-size:13.5px; color:var(--indigo); background:var(--panel);
  display:flex; align-items:center; gap:8px; }
.explainer > summary::-webkit-details-marker,
.more > summary::-webkit-details-marker { display:none; }
.explainer > summary::before, .more > summary::before {
  content:"\25B8"; font-size:11px; transition:transform .15s; color:var(--marigold); }
.explainer[open] > summary::before, .more[open] > summary::before { transform:rotate(90deg); }
.explainer-bd { padding:14px 18px; font-size:13.5px; color:#33334a; line-height:1.7; }
.explainer-bd b { color:var(--ink); }
.explainer-bd .lead { margin:0 0 12px; }
.verdict-key { display:flex; flex-direction:column; gap:6px; margin:10px 0 4px; }
.vk-row { display:flex; align-items:center; gap:10px; font-size:13px; }
.vk-badge { font-family:"IBM Plex Mono",monospace; font-weight:700; font-size:11px;
            padding:2px 9px; border-radius:6px; min-width:104px; text-align:center; }
.more { margin-top:13px; border:1px solid var(--line); border-radius:12px;
        background:#fff; overflow:hidden; }
.more > summary { color:var(--muted); background:#fff; border-bottom:1px solid transparent; }
.more[open] > summary { border-bottom:1px solid var(--line); }
.more-bd { padding:15px; }

.caption { margin:12px 0 0; padding:10px 14px; border-left:3px solid var(--marigold);
           background:#fdf9f1; border-radius:0 8px 8px 0; font-size:13.5px; color:#5a4520; }
.caption b { color:#8a5a12; }
.why { font-size:14px; color:#26263c; line-height:1.55; }
.art-controls { display:flex; align-items:center; gap:14px; padding:16px 0 0;
                flex-wrap:wrap; }
.ctrl-label { font-family:"IBM Plex Mono",monospace; font-size:10px;
              letter-spacing:.12em; text-transform:uppercase; color:var(--muted);
              font-weight:600; }
.art-nav { display:flex; align-items:center; gap:8px; }
.nav-btn { font-family:"IBM Plex Mono",monospace; font-size:14px;
           border:1px solid var(--line); border-radius:7px; padding:5px 13px;
           background:#fff; color:var(--indigo); cursor:pointer; }
.nav-btn:hover { background:var(--panel); }
.nav-btn:disabled { color:var(--muted); cursor:default; }
.art-counter { font-family:"IBM Plex Mono",monospace; font-size:12px;
               color:var(--muted); min-width:68px; text-align:center; }
.art-select { font-family:"Inter",sans-serif; font-size:13px; padding:5px 10px;
              border:1px solid var(--line); border-radius:7px; background:#fff;
              max-width:340px; }
.title-bar { margin:16px 0 0; padding:12px 15px; background:#fff;
             border:1px solid var(--line); border-radius:10px; display:flex;
             align-items:baseline; gap:12px; flex-wrap:wrap; }
.title-bar .t { font-family:"Spectral",serif; font-weight:600; font-size:19px; }
.title-bar a { font-family:"IBM Plex Mono",monospace; font-size:11px; color:var(--muted); }
.chip { font-family:"IBM Plex Mono",monospace; font-size:10px; font-weight:600;
        letter-spacing:.04em; padding:2px 8px; border-radius:5px; }
.chip.claim { background:var(--panel); color:var(--muted); }
.chip.synthetic { background:#fbeada; color:#9a5a12; }
.chip.real { background:#eef6f4; color:var(--teal); }

.verdict { margin:14px 0; border:1px solid var(--line); border-radius:12px;
           overflow:hidden; }
.verdict-hd { padding:14px 18px; display:flex; align-items:center; gap:14px;
              flex-wrap:wrap; }
.verdict-badge { font-family:"IBM Plex Mono",monospace; font-weight:700;
                 font-size:15px; letter-spacing:.02em; padding:6px 14px;
                 border-radius:8px; }
.v-accept   { background:#eef6f4; color:var(--teal); }
.v-review   { background:#fdf3e3; color:#9a5a12; }
.v-exclude  { background:var(--panel); color:var(--muted); }
.v-quarantine { background:#fceef2; color:var(--rose); }
.verdict-sub { font-size:13px; color:#33334a; }
.reason-row { padding:0 18px 14px; display:flex; gap:6px; flex-wrap:wrap; }
.reason { font-family:"IBM Plex Mono",monospace; font-size:10.5px; font-weight:600;
          padding:2px 8px; border-radius:5px; background:#fff5f7; color:var(--rose);
          border:1px solid #f3d3dd; }
.reason.ok { background:#eef6f4; color:var(--teal); border-color:#cfe6e1; }
.reason.warn { background:#fdf3e3; color:#9a5a12; border-color:#f0dcb8; }

.grid2 { display:grid; grid-template-columns:1fr 1fr; gap:13px; }
@media (max-width:860px){ .grid2 { grid-template-columns:1fr; } }
.card { border:1px solid var(--line); border-radius:12px; background:#fff;
        overflow:hidden; }
.card-hd { padding:9px 15px; border-bottom:1px solid var(--line);
           background:var(--panel); font-family:"IBM Plex Mono",monospace;
           font-size:10px; font-weight:600; letter-spacing:.09em;
           text-transform:uppercase; color:var(--indigo); }
.card-bd { padding:14px 15px; }

.dist-bar { display:flex; height:22px; border-radius:6px; overflow:hidden;
            border:1px solid var(--line); margin-bottom:10px; }
.dist-seg { height:100%; }
.legend { display:flex; flex-direction:column; gap:5px; }
.legend-row { display:flex; align-items:center; gap:8px; font-size:12.5px; }
.legend-sw { width:12px; height:12px; border-radius:3px; flex-shrink:0; }
.legend-pct { font-family:"IBM Plex Mono",monospace; font-size:11px;
              color:var(--muted); margin-left:auto; }
.cand { font-family:"IBM Plex Mono",monospace; font-size:12px; }
.cand b { color:var(--indigo); }
.amb { font-size:12px; color:#9a5a12; background:#fdf3e3; border-radius:6px;
       padding:6px 9px; margin-top:8px; }

.spans { display:flex; flex-direction:column; gap:6px; }
.span-row { display:flex; align-items:center; gap:10px; font-size:12px; }
.span-idx { font-family:"IBM Plex Mono",monospace; font-size:10px; color:var(--muted);
            width:26px; flex-shrink:0; }
.span-txt { flex:1; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
            color:#33334a; }
.span-tag { font-family:"IBM Plex Mono",monospace; font-size:10px; font-weight:600;
            padding:1px 7px; border-radius:4px; flex-shrink:0; }

.model-row { display:flex; align-items:center; gap:10px; margin-bottom:7px; }
.model-lang { font-family:"IBM Plex Mono",monospace; font-size:13px; font-weight:600;
              color:var(--indigo); width:56px; }
.model-track { flex:1; height:12px; background:var(--panel); border-radius:6px; overflow:hidden; }
.model-fill { height:100%; background:var(--indigo-soft); }
.model-score { font-family:"IBM Plex Mono",monospace; font-size:11px; color:var(--muted);
               width:52px; text-align:right; }
.model-none { font-size:12.5px; color:var(--muted); }
.model-none code { background:var(--panel); padding:1px 5px; border-radius:4px;
                   font-size:11px; }

.text-view { border:1px solid var(--line); border-radius:12px; background:#fff;
             margin-top:13px; }
.text-body { padding:15px; max-height:300px; overflow-y:auto; font-size:14px;
             line-height:1.85; white-space:pre-wrap; word-break:break-word; }
.sc-latn { color:var(--sc-latn); background:#fbf1e3; border-radius:2px; }
.sc-arab { color:var(--sc-arab); background:#fceef2; border-radius:2px; }
.sc-drav { color:var(--sc-drav); background:#eef6f4; border-radius:2px; }
.sc-beng { color:var(--sc-beng); background:#f3edfa; border-radius:2px; }
.sc-other{ color:var(--sc-other); background:#fceef2; border-radius:2px; }

.acct { margin-top:18px; }
.acct h2 { font-family:"Spectral",serif; font-size:22px; margin:0 0 4px;
           border-bottom:2px solid var(--ink); padding-bottom:8px; }
.acct-grid { display:grid; grid-template-columns:1fr 1fr; gap:13px; margin-top:14px; }
@media (max-width:860px){ .acct-grid { grid-template-columns:1fr; } }
.acct-row { display:flex; align-items:center; gap:10px; font-size:13px;
            padding:5px 0; border-bottom:1px dashed var(--line); }
.acct-row:last-child { border-bottom:none; }
.acct-k { flex:1; }
.acct-v { font-family:"IBM Plex Mono",monospace; font-weight:600; color:var(--indigo); }
.acct-bar { height:10px; border-radius:5px; background:var(--indigo-soft); }
.trunc-note { font-family:"IBM Plex Mono",monospace; font-size:10.5px;
              color:var(--muted); margin-top:12px; padding-top:9px;
              border-top:1px dashed var(--line); }
"""


# ---------------------------------------------------------------------------
# JavaScript  (raw string — \\uXXXX escapes are for the JS engine, not Python)
# ---------------------------------------------------------------------------

JS = r"""
var ARTICLES = JSON.parse(document.getElementById('articles-data').textContent);
var state = { idx: 0 };

/* ---------- script classification (Language_Skill Step 04) ---------- */
/* Returns a script family key for a code point, or a non-linguistic class. */
function scriptOf(cp) {
  if (cp >= 0x0900 && cp <= 0x097F) return 'Deva';
  if (cp >= 0xA8E0 && cp <= 0xA8FF) return 'Deva';   /* Devanagari Extended */
  if (cp >= 0x1CD0 && cp <= 0x1CFF) return 'Deva';   /* Vedic Extensions   */
  if (cp >= 0x0980 && cp <= 0x09FF) return 'Beng';
  if (cp >= 0x0A00 && cp <= 0x0A7F) return 'Guru';
  if (cp >= 0x0A80 && cp <= 0x0AFF) return 'Gujr';
  if (cp >= 0x0B00 && cp <= 0x0B7F) return 'Orya';
  if (cp >= 0x0B80 && cp <= 0x0BFF) return 'Taml';
  if (cp >= 0x0C00 && cp <= 0x0C7F) return 'Telu';
  if (cp >= 0x0C80 && cp <= 0x0CFF) return 'Knda';
  if (cp >= 0x0D00 && cp <= 0x0D7F) return 'Mlym';
  if ((cp >= 0x0600 && cp <= 0x06FF) || (cp >= 0x0750 && cp <= 0x077F) ||
      (cp >= 0x08A0 && cp <= 0x08FF) || (cp >= 0xFB50 && cp <= 0xFDFF) ||
      (cp >= 0xFE70 && cp <= 0xFEFF)) return 'Arab';
  if ((cp >= 0x0041 && cp <= 0x005A) || (cp >= 0x0061 && cp <= 0x007A) ||
      (cp >= 0x00C0 && cp <= 0x024F)) return 'Latn';
  /* non-linguistic classes */
  if (cp >= 0x0030 && cp <= 0x0039) return 'digit';
  if (cp === 0x20 || cp === 0x09 || cp === 0x0A || cp === 0x0D) return 'space';
  return 'other';   /* punctuation, symbols, digits of other scripts, emoji */
}

/* script family -> colour class + candidate languages (shared-script aware) */
var SCRIPT_META = {
  Deva: { css:'',        cands:['hi','mr','sa','ne'], name:'Devanagari' },
  Beng: { css:'sc-beng', cands:['bn','as'],           name:'Bengali'    },
  Guru: { css:'sc-beng', cands:['pa'],                name:'Gurmukhi'   },
  Gujr: { css:'sc-beng', cands:['gu'],                name:'Gujarati'   },
  Orya: { css:'sc-beng', cands:['or'],                name:'Odia'       },
  Taml: { css:'sc-drav', cands:['ta'],                name:'Tamil'      },
  Telu: { css:'sc-drav', cands:['te'],                name:'Telugu'     },
  Knda: { css:'sc-drav', cands:['kn'],                name:'Kannada'    },
  Mlym: { css:'sc-drav', cands:['ml'],                name:'Malayalam'  },
  Arab: { css:'sc-arab', cands:['ur','fa','ar'],      name:'Perso-Arabic' },
  Latn: { css:'sc-latn', cands:['en','(romanized)'],  name:'Latin'      }
};
var SCRIPT_COLOR = {
  Deva:'#2E357E', Beng:'#7A3FB0', Guru:'#7A3FB0', Gujr:'#7A3FB0', Orya:'#7A3FB0',
  Taml:'#147D74', Telu:'#147D74', Knda:'#147D74', Mlym:'#147D74',
  Arab:'#B5476B', Latn:'#C7761B'
};

/* weak signal: romanized-Hindi function words (Latin != English) */
var ROMAN_HI = ['aap','hai','hain','kya','nahi','nahin','mein','hum','kaise',
  'kaisa','kyun','kyon','aaj','doston','dhanyavaad','karein','karenge','raha',
  'rahe','rahi','yeh','woh','apni','apna','bahut','accha','achha','theek',
  'namaste','bhai','zaroor','pasand','seekh','sakta','sakte','sakti','ke','ki',
  'ko','hum','baat','naya'];

function esc(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
function pct(x) { return (x * 100).toFixed(1) + '%'; }

/* ---------- analyse one text: script distribution + spans ---------- */
function analyse(text) {
  var counts = {}, linguistic = 0, nonling = 0, total = 0;
  for (var i = 0; i < text.length; i++) {
    var s = scriptOf(text.charCodeAt(i));
    total++;
    if (s === 'space' || s === 'digit' || s === 'other') { nonling++; }
    else { linguistic++; counts[s] = (counts[s] || 0) + 1; }
  }
  var shares = {};
  var keys = Object.keys(counts);
  for (var k = 0; k < keys.length; k++) shares[keys[k]] = counts[keys[k]] / linguistic;

  var ordered = keys.slice().sort(function(a,b){ return counts[b]-counts[a]; });
  var dom = ordered.length ? ordered[0] : null;

  var lingRatio = total ? linguistic / total : 0;

  /* romanized-Hindi weak signal */
  var romanHits = 0, words = text.toLowerCase().split(/[^a-z]+/);
  for (var w = 0; w < words.length; w++) {
    if (words[w] && ROMAN_HI.indexOf(words[w]) !== -1) romanHits++;
  }

  return {
    counts: counts, shares: shares, ordered: ordered, dom: dom,
    linguistic: linguistic, nonling: nonling, total: total,
    lingRatio: lingRatio, romanHits: romanHits
  };
}

/* ---------- per-paragraph script breakdown (Step 06) ---------- */
function paragraphs(text) {
  var raw = text.split(/\n+/), out = [];
  for (var i = 0; i < raw.length; i++) {
    var p = raw[i].trim();
    if (p.length < 2) continue;
    var a = analyse(p);
    out.push({ text: p, dom: a.dom, shares: a.shares, lingRatio: a.lingRatio });
  }
  return out;
}

/* ---------- decision engine: script tier (Steps 09/11/13) ---------- */
function scriptDecision(a, claimedScript) {
  var reasons = [], disp, langNote = '';
  var latn = a.shares['Latn'] || 0;
  var deva = a.shares['Deva'] || 0;

  if (a.linguistic < 20 || a.lingRatio < 0.20) {
    return { disp:'EXCLUDE_NON_LINGUISTIC',
             reasons:[{c:'NO_LINGUISTIC_CONTENT', t:'warn'}],
             langNote:'Mostly digits/punctuation/symbols — route to zxx.' };
  }
  if (!a.dom) {
    return { disp:'QUARANTINE_UNKNOWN', reasons:[{c:'INSUFFICIENT_EVIDENCE',t:'warn'}],
             langNote:'' };
  }

  /* code-mix: Devanagari + Latin both significant, regardless of which leads */
  if (deva >= 0.15 && latn >= 0.15) {
    reasons.push({c:'CODE_MIXED_HI_EN', t:'ok'});
    reasons.push({c:'MIXED_SCRIPT', t:'warn'});
    return { disp:'ACCEPT_CODE_MIXED', reasons:reasons,
             langNote:'Devanagari ' + pct(deva) + ' + Latin ' + pct(latn) +
                      ' — Hindi+English code-mix (allowed mixture).' };
  }

  if (a.dom === 'Deva') {
    disp = 'ACCEPT_MONOLINGUAL';
    reasons.push({c:'SCRIPT_MATCHES_CLAIM', t:'ok'});
    reasons.push({c:'SHARED_SCRIPT_AMBIGUITY', t:'warn'});
    langNote = 'Devanagari is shared by hi/mr/sa/ne — script alone cannot confirm Hindi. Needs model LID.';
  } else if (a.dom === 'Latn') {
    disp = 'REVIEW';
    if (a.romanHits >= 2) {
      reasons.push({c:'ROMANIZED_CANDIDATE', t:'warn'});
      langNote = 'Latin script with ' + a.romanHits + ' romanized-Hindi cue word(s) — likely romanized Indic, NOT English. Needs romanized-capable LID.';
    } else {
      reasons.push({c:'FOREIGN_LATIN', t:'warn'});
      langNote = 'Latin script, no romanized-Hindi cues — likely English (non-target). Needs model LID to confirm.';
    }
    reasons.push({c:'SCRIPT_LANGUAGE_CONFLICT', t:'warn'});
  } else {
    /* a non-Devanagari, non-Latin Indic/Arabic script under a hi/Deva claim */
    disp = 'QUARANTINE_MISMATCH';
    reasons.push({c:'SCRIPT_LANGUAGE_CONFLICT', t:'bad'});
    reasons.push({c:'CLAIM_PREDICTION_MISMATCH', t:'bad'});
    var meta = SCRIPT_META[a.dom];
    langNote = 'Claimed ' + claimedScript + ' but detected ' + (meta ? meta.name : a.dom) +
               ' (' + (meta ? meta.cands.join('/') : '?') + ') — script/claim conflict.';
  }
  return { disp: disp, reasons: reasons, langNote: langNote };
}

/* ---------- reconcile script tier with baked-in model LID ---------- */
function combine(scriptDisp, lid) {
  if (!lid || !lid.top1) return { disp: scriptDisp.disp, note: 'Model LID not run — script-tier verdict only.' };
  var TARGET = 'hi', LOW = 0.50;   /* below LOW, the model abstains (Step 12) */
  var top = lid.top1, conf = lid.candidates && lid.candidates[0] ? lid.candidates[0].score : 0;

  /* Deva monolingual: model disambiguates hi vs mr/sa/ne */
  if (scriptDisp.disp === 'ACCEPT_MONOLINGUAL') {
    if (top === TARGET) return { disp:'ACCEPT_MONOLINGUAL', note:'Model confirms Hindi ('+pct(conf)+').' };
    if (conf < LOW)     return { disp:'ACCEPT_MONOLINGUAL', note:'Model top-1 "'+top+'" but low confidence ('+pct(conf)+') — script ACCEPT stands, flagged.' };
    return { disp:'REVIEW', note:'Model says "'+top+'" ('+pct(conf)+'), not Hindi — shared-script (hi/mr/sa) disambiguation needed.' };
  }
  /* Latin: model separates romanized-Hindi from English — if it is confident */
  if (scriptDisp.disp === 'REVIEW') {
    if (top === TARGET && conf >= LOW) return { disp:'ACCEPT_MONOLINGUAL', note:'Model recovers Hindi ('+pct(conf)+') from Latin — romanized Hindi.' };
    if (conf < LOW)                    return { disp:'REVIEW', note:'Model top-1 "'+top+'" at low confidence ('+pct(conf)+') — abstain; needs a romanized-capable detector (e.g. IndicLID).' };
    return { disp:'EXCLUDE_NON_TARGET', note:'Model says "'+top+'" ('+pct(conf)+') with confidence — treated as non-target.' };
  }
  return { disp: scriptDisp.disp, note: 'Model top-1 "'+top+'" ('+pct(conf)+').' };
}

/* ---------- plain-English explanation of the verdict ---------- */
function plainWhy(fin, sd, a) {
  var d = fin.disp, latn = a.shares['Latn'] || 0;
  if (d === 'ACCEPT_MONOLINGUAL')
    return 'Reads as clean Hindi in Devanagari script, and the model agrees. It goes straight into the Hindi training data.';
  if (d === 'ACCEPT_CODE_MIXED')
    return 'Mostly Hindi with English mixed in (' + pct(latn) + ' Latin) — a normal, allowed mixture. Kept, and tagged as code-mixed so the training recipe knows.';
  if (d === 'EXCLUDE_NON_LINGUISTIC')
    return 'Almost no real words — mostly numbers, punctuation and symbols. There is no language here to train on, so it is excluded.';
  if (d === 'EXCLUDE_NON_TARGET')
    return 'The model is confident this is another language, not Hindi. It is dropped from the Hindi training mixture.';
  if (d === 'QUARANTINE_MISMATCH')
    return 'The script/language does not match the "Hindi" label this document was filed under — a labeling problem. Quarantine it and audit where it came from.';
  if (d === 'REVIEW') {
    if (a.dom === 'Latn')
      return (a.romanHits >= 2
        ? 'Written in English letters, but it carries Hindi cue-words — likely romanized Hindi, not English. The model is not sure, so we do not guess: send it for review.'
        : 'Written in Latin letters — could be English or romanized Hindi, and the model is not confident either way. Send it for review rather than guessing.');
    return 'Script alone cannot pin down the language (Devanagari is shared by Hindi / Marathi / Sanskrit), and the model leans away from Hindi. Flag it for a closer look.';
  }
  return fin.note || '';
}

/* ---------- render text coloured by script run ---------- */
function colourText(text) {
  var html = '', run = '', runScript = null;
  function flush() {
    if (!run) return;
    var meta = SCRIPT_META[runScript];
    if (meta && meta.css) html += '<span class="' + meta.css + '">' + esc(run) + '</span>';
    else html += esc(run);
    run = '';
  }
  for (var i = 0; i < text.length; i++) {
    var s = scriptOf(text.charCodeAt(i));
    var grp = (s === 'space' || s === 'digit' || s === 'other') ? 'plain' : s;
    if (grp !== runScript) { flush(); runScript = grp; }
    run += text[i];
  }
  flush();
  return html;
}

/* ---------- verdict styling ---------- */
function vClass(disp) {
  if (disp.indexOf('ACCEPT') === 0)      return 'v-accept';
  if (disp === 'REVIEW')                 return 'v-review';
  if (disp.indexOf('EXCLUDE') === 0)     return 'v-exclude';
  return 'v-quarantine';
}

/* ================= MAIN RENDER ================= */
function render() {
  var art = ARTICLES[state.idx];
  var a   = analyse(art.text);
  var sd  = scriptDecision(a, art.claimed_script);
  var fin = combine(sd, art.lid);

  /* header */
  document.getElementById('art-title').textContent = art.title;
  var kindEl = document.getElementById('art-kind');
  kindEl.textContent = art.kind === 'synthetic' ? 'SYNTHETIC' : 'REAL — Wikipedia';
  kindEl.className = 'chip ' + (art.kind === 'synthetic' ? 'synthetic' : 'real');
  document.getElementById('art-claim').textContent =
    'claimed: ' + art.claimed_lang + ' / ' + art.claimed_script;
  var urlEl = document.getElementById('art-url');
  urlEl.href = art.url; urlEl.style.display = art.kind === 'synthetic' ? 'none' : '';
  document.getElementById('art-counter').textContent = (state.idx+1) + ' of ' + ARTICLES.length;
  document.getElementById('prev-btn').disabled = state.idx === 0;
  document.getElementById('next-btn').disabled = state.idx === ARTICLES.length-1;
  document.getElementById('art-select').value = state.idx;

  /* teaching caption */
  var capEl = document.getElementById('caption');
  if (art.caption) {
    capEl.innerHTML = '<b>What this example shows:</b> ' + esc(art.caption);
    capEl.style.display = '';
  } else { capEl.style.display = 'none'; }

  /* verdict */
  document.getElementById('verdict').className = 'verdict';
  document.getElementById('verdict-badge').className = 'verdict-badge ' + vClass(fin.disp);
  document.getElementById('verdict-badge').textContent = fin.disp;
  document.getElementById('verdict-sub').className = 'why';
  document.getElementById('verdict-sub').textContent = plainWhy(fin, sd, a);
  var rr = document.getElementById('reason-row'); rr.innerHTML = '';
  for (var i = 0; i < sd.reasons.length; i++) {
    var r = sd.reasons[i];
    var cls = r.t === 'ok' ? 'reason ok' : r.t === 'warn' ? 'reason warn' : 'reason';
    rr.innerHTML += '<span class="' + cls + '">' + r.c + '</span>';
  }

  /* script distribution bar + legend */
  var bar = '', leg = '';
  for (var j = 0; j < a.ordered.length; j++) {
    var k = a.ordered[j], sh = a.shares[k], col = SCRIPT_COLOR[k] || '#999';
    bar += '<div class="dist-seg" style="width:' + (sh*100) + '%;background:' + col + '"></div>';
    var meta = SCRIPT_META[k];
    leg += '<div class="legend-row"><span class="legend-sw" style="background:' + col + '"></span>' +
           '<span>' + (meta?meta.name:k) + ' <span style="color:#999">(' + k + ')</span></span>' +
           '<span class="legend-pct">' + pct(sh) + '</span></div>';
  }
  document.getElementById('dist-bar').innerHTML = bar || '<div class="dist-seg" style="width:100%;background:#ddd"></div>';
  document.getElementById('legend').innerHTML = leg || '<div class="legend-row"><span>no linguistic characters</span></div>';
  document.getElementById('nonling').textContent =
    'Linguistic ' + pct(a.lingRatio) + '  ·  non-linguistic ' + pct(a.total ? a.nonling/a.total : 0) +
    ' (' + a.nonling + ' of ' + a.total + ' chars)';

  /* candidate languages */
  var candHtml = '';
  if (a.dom && SCRIPT_META[a.dom]) {
    candHtml = 'Dominant script <b>' + SCRIPT_META[a.dom].name + '</b> → candidate languages: <b>' +
               SCRIPT_META[a.dom].cands.join(', ') + '</b>';
  } else candHtml = 'No dominant linguistic script.';
  document.getElementById('cands').innerHTML = candHtml;
  document.getElementById('amb').textContent = sd.langNote;
  document.getElementById('amb').style.display = sd.langNote ? '' : 'none';

  /* paragraph spans */
  var ps = paragraphs(art.text), sp = '';
  for (var p = 0; p < ps.length && p < 12; p++) {
    var pr = ps[p], col2 = SCRIPT_COLOR[pr.dom] || '#999';
    sp += '<div class="span-row"><span class="span-idx">#' + (p+1) + '</span>' +
          '<span class="span-txt">' + esc(pr.text.slice(0,80)) + '</span>' +
          '<span class="span-tag" style="background:' + col2 + '22;color:' + col2 + '">' +
          (pr.dom || 'zxx') + '</span></div>';
  }
  document.getElementById('spans').innerHTML = sp || '<div class="model-none">No paragraph-level spans.</div>';

  /* model LID panel */
  var mp = document.getElementById('model-panel');
  if (art.lid && art.lid.candidates && art.lid.candidates.length) {
    var mh = '<div class="model-none" style="margin-bottom:10px;color:#33334a">' + esc(fin.note) + '</div>';
    for (var m = 0; m < art.lid.candidates.length && m < 4; m++) {
      var c = art.lid.candidates[m];
      mh += '<div class="model-row"><span class="model-lang">' + esc(c.lang) + '</span>' +
            '<span class="model-track"><span class="model-fill" style="width:' + (c.score*100) + '%"></span></span>' +
            '<span class="model-score">' + pct(c.score) + '</span></div>';
    }
    var margin = art.lid.margin != null ? '  ·  top-1/top-2 margin ' + pct(art.lid.margin) : '';
    mh += '<div class="model-none" style="margin-top:8px">model: <code>' + esc(art.lid.model || 'unknown') + '</code>' + margin + '</div>';
    mp.innerHTML = mh;
  } else {
    mp.innerHTML = '<div class="model-none">Model LID not run for this article. ' +
      'Run <code>python3 run_lid.py</code> to score with fastText and regenerate.</div>';
  }

  /* coloured text */
  var isTrunc = art.full_len > art.text.length;
  document.getElementById('text-body').innerHTML = colourText(art.text) +
    (isTrunc ? '<div class="trunc-note">Showing first ' + art.text.length + ' of ' + art.full_len + ' chars</div>' : '');
}

/* ================= CORPUS ACCOUNTING (Step 14) ================= */
function accounting() {
  var byDisp = {}, byScript = {}, mismatch = 0, codemix = 0, total = ARTICLES.length;
  for (var i = 0; i < ARTICLES.length; i++) {
    var art = ARTICLES[i], a = analyse(art.text);
    var sd = scriptDecision(a, art.claimed_script), fin = combine(sd, art.lid);
    byDisp[fin.disp] = (byDisp[fin.disp] || 0) + 1;
    var dom = a.dom || 'zxx';
    byScript[dom] = (byScript[dom] || 0) + 1;
    if (fin.disp.indexOf('QUARANTINE') === 0 || fin.disp === 'EXCLUDE_NON_TARGET') mismatch++;
    if (fin.disp === 'ACCEPT_CODE_MIXED') codemix++;
  }
  function rows(obj, colorMap) {
    var keys = Object.keys(obj).sort(function(a,b){ return obj[b]-obj[a]; }), html = '';
    for (var k = 0; k < keys.length; k++) {
      var key = keys[k], n = obj[key], w = (n/total)*100;
      var col = colorMap ? (colorMap[key] || '#6169B8') : '#6169B8';
      html += '<div class="acct-row"><span class="acct-k">' + key + '</span>' +
              '<span style="width:120px"><span class="acct-bar" style="display:block;width:' + w + '%;background:' + col + '"></span></span>' +
              '<span class="acct-v">' + n + '</span></div>';
    }
    return html;
  }
  document.getElementById('acct-disp').innerHTML = rows(byDisp, null);
  document.getElementById('acct-script').innerHTML = rows(byScript, SCRIPT_COLOR);
  document.getElementById('acct-summary').innerHTML =
    '<div class="acct-row"><span class="acct-k">Total documents</span><span class="acct-v">' + total + '</span></div>' +
    '<div class="acct-row"><span class="acct-k">Claimed-vs-detected mismatches (quarantine + non-target)</span><span class="acct-v">' + mismatch + '</span></div>' +
    '<div class="acct-row"><span class="acct-k">Code-mixed documents</span><span class="acct-v">' + codemix + '</span></div>' +
    '<div class="acct-row"><span class="acct-k">All claimed</span><span class="acct-v">hi / Deva</span></div>';
}

/* ================= WIRING ================= */
var sel = document.getElementById('art-select');
for (var i = 0; i < ARTICLES.length; i++) {
  var o = document.createElement('option');
  o.value = i; o.textContent = (i+1) + '. ' + ARTICLES[i].title;
  sel.appendChild(o);
}
sel.addEventListener('change', function(){ state.idx = parseInt(this.value,10); render(); });
document.getElementById('prev-btn').addEventListener('click', function(){ if (state.idx>0){state.idx--;render();} });
document.getElementById('next-btn').addEventListener('click', function(){ if (state.idx<ARTICLES.length-1){state.idx++;render();} });
document.addEventListener('keydown', function(e){
  if (e.key==='ArrowLeft' && state.idx>0){ state.idx--; render(); }
  if (e.key==='ArrowRight' && state.idx<ARTICLES.length-1){ state.idx++; render(); }
});

render();
accounting();
"""


# ---------------------------------------------------------------------------
# HTML assembly
# ---------------------------------------------------------------------------

def build_html(articles):
    data_json = json.dumps(articles, ensure_ascii=False)
    lid_note = ("Model tier: <b>fastText</b> verdicts baked in."
                if any(a.get("lid") for a in articles)
                else "Model tier: <b>not run</b> — run <code>python3 run_lid.py</code> to bake in fastText verdicts.")
    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n'
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>Language ID — India-First 40B</title>\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link href="https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,600;0,700;1,600'
        '&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">\n'
        '<style>' + CSS + '</style>\n</head>\n<body>\n'
        '<script type="application/json" id="articles-data">' + data_json + '</script>\n'
        '<div class="nav"><div class="nav-in">\n'
        '  <span class="brand">India-First 40B</span>\n'
        '  <a href="#">Overview</a><a href="#">Data</a>\n'
        '  <a href="index.html">Cleaning</a>\n'
        '  <a href="language.html" class="active">Language</a>\n'
        '  <a href="#">Tokenizer</a>\n'
        '</div></div>\n'
        '<div class="wrap">\n'
        '  <div class="phead">\n'
        '    <h1>Language Identification</h1>\n'
        '    <p class="dek">This page does not clean text — it <b>judges</b> it. Each document was filed as '
        '<code>hi / Deva</code>; the audit tests whether that is true and decides what to do with it.</p>\n'
        '  </div>\n'
        '  <details class="explainer" open>\n'
        '    <summary>How to read this page</summary>\n'
        '    <div class="explainer-bd">\n'
        '      <p class="lead">Everything here came from a folder <b>labelled "Hindi"</b> — but labels lie. Real '
        'corpora hide English, mislabelled languages, code-mixing and junk. Before spending training compute, every '
        'document must be checked and <b>routed</b> to one of four outcomes:</p>\n'
        '      <div class="verdict-key">\n'
        '        <div class="vk-row"><span class="vk-badge v-accept">ACCEPT</span>'
        '<span>Real target-language text → goes into training.</span></div>\n'
        '        <div class="vk-row"><span class="vk-badge v-review">REVIEW</span>'
        '<span>Evidence is unclear → hold for a human or a stronger detector.</span></div>\n'
        '        <div class="vk-row"><span class="vk-badge v-exclude">EXCLUDE</span>'
        '<span>Another language, or no language at all → dropped.</span></div>\n'
        '        <div class="vk-row"><span class="vk-badge v-quarantine">QUARANTINE</span>'
        '<span>Content conflicts with its label → set aside and audit the source.</span></div>\n'
        '      </div>\n'
        '      <p class="note" style="margin-top:12px">Pick a document below. The <b>🧪 examples</b> are a guided tour '
        'of the situations an auditor hits; the rest are real Hindi Wikipedia. The verdict is decided in two tiers — a '
        'dependency-free <b>script check</b> (which alphabet?) plus a <b>fastText model</b> (which language?). Script '
        'alone cannot tell Hindi from Sanskrit, nor romanized Hindi from English — which is exactly why both exist. '
        + lid_note + '</p>\n'
        '    </div>\n'
        '  </details>\n'
        '  <div class="art-controls">\n'
        '    <span class="ctrl-label">Document</span>\n'
        '    <div class="art-nav">\n'
        '      <button class="nav-btn" id="prev-btn">&#8592;</button>\n'
        '      <span class="art-counter" id="art-counter"></span>\n'
        '      <button class="nav-btn" id="next-btn">&#8594;</button>\n'
        '    </div>\n'
        '    <select class="art-select" id="art-select"></select>\n'
        '  </div>\n'
        '  <div class="title-bar">\n'
        '    <span class="t" id="art-title"></span>\n'
        '    <span class="chip" id="art-kind"></span>\n'
        '    <span class="chip claim" id="art-claim"></span>\n'
        '    <a id="art-url" href="#" target="_blank">&#8599; Wikipedia</a>\n'
        '  </div>\n'
        '  <div class="caption" id="caption"></div>\n'
        '  <div class="verdict" id="verdict">\n'
        '    <div class="verdict-hd">\n'
        '      <span class="verdict-badge" id="verdict-badge"></span>\n'
        '      <span class="verdict-sub" id="verdict-sub"></span>\n'
        '    </div>\n'
        '    <div class="reason-row" id="reason-row"></div>\n'
        '  </div>\n'
        '  <div class="card">\n'
        '    <div class="card-hd">Which alphabet is this? — script distribution</div>\n'
        '    <div class="card-bd">\n'
        '      <div class="dist-bar" id="dist-bar"></div>\n'
        '      <div class="legend" id="legend"></div>\n'
        '      <div class="note" id="nonling" style="margin-top:10px"></div>\n'
        '      <div class="cand" id="cands" style="margin-top:12px"></div>\n'
        '      <div class="amb" id="amb"></div>\n'
        '    </div>\n'
        '  </div>\n'
        '  <div class="text-view">\n'
        '    <div class="card-hd" style="border-bottom:1px solid var(--line)">The document — coloured by script</div>\n'
        '    <div class="text-body" id="text-body"></div>\n'
        '  </div>\n'
        '  <details class="more">\n'
        '    <summary>Show analysis details — model scores &amp; paragraph breakdown</summary>\n'
        '    <div class="more-bd">\n'
        '      <div class="grid2">\n'
        '        <div class="card">\n'
        '          <div class="card-hd">Which language? — fastText model</div>\n'
        '          <div class="card-bd"><div id="model-panel"></div></div>\n'
        '        </div>\n'
        '        <div class="card">\n'
        '          <div class="card-hd">Paragraph-by-paragraph script</div>\n'
        '          <div class="card-bd"><div class="spans" id="spans"></div></div>\n'
        '        </div>\n'
        '      </div>\n'
        '    </div>\n'
        '  </details>\n'
        '  <details class="more">\n'
        '    <summary>Show corpus accounting — the big picture across all ' + str(len(articles)) + ' documents</summary>\n'
        '    <div class="more-bd">\n'
        '      <p class="note" style="margin-top:0">Where every document in this sample ended up — the kind of '
        'roll-up you would run over the whole corpus before training.</p>\n'
        '      <div class="acct-grid">\n'
        '        <div class="card"><div class="card-hd">By final disposition</div><div class="card-bd" id="acct-disp"></div></div>\n'
        '        <div class="card"><div class="card-hd">By dominant script</div><div class="card-bd" id="acct-script"></div></div>\n'
        '      </div>\n'
        '      <div class="card" style="margin-top:13px"><div class="card-hd">Summary</div><div class="card-bd" id="acct-summary"></div></div>\n'
        '    </div>\n'
        '  </details>\n'
        '</div>\n'
        '<script>' + JS + '</script>\n'
        '</body>\n</html>\n'
    )


if __name__ == "__main__":
    print("Building language sample...")
    articles = lang_sample.build_sample()

    # Merge in model LID results if run_lid.py has produced them.
    lid = {}
    if os.path.exists(LID_RESULTS):
        with open(LID_RESULTS, encoding="utf-8") as f:
            lid = json.load(f)
        print("Loaded {} model LID results from {}".format(len(lid), LID_RESULTS))
    else:
        print("No {} found — page will show 'model not run'.".format(LID_RESULTS))

    for a in articles:
        a["lid"] = lid.get(a["id"])

    print("Generating {}...".format(OUTPUT_PATH))
    html = build_html(articles)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    n_syn = sum(1 for a in articles if a["kind"] == "synthetic")
    print("\nDone. {} written ({} articles: {} synthetic + {} real, {} with model LID).".format(
        OUTPUT_PATH, len(articles), n_syn, len(articles) - n_syn,
        sum(1 for a in articles if a.get("lid"))))
