"""
Generate tokenizer.html — Indic tokenizer-fertility preview.

The India-First point: an English-centric byte tokenizer taxes Indic scripts.
Each Devanagari/Tamil character is 3 UTF-8 bytes, so a byte tokenizer with no
Indic merges emits ~3 tokens per character — Hindi costs ~3x the tokens of
English for the same idea. All counts here are EXACT (code points, UTF-8 bytes
via TextEncoder, Unicode grapheme clusters via Intl.Segmenter). A real learned
tokenizer (tiktoken / SentencePiece) is a documented offline tier.

Run: python3 generate_tokenizer_preview.py
"""

import json
import os
import tokenizer_sample as T

OUTPUT_PATH = "tokenizer.html"


CSS = """
:root { --bg:#FAFBFD; --ink:#16162A; --indigo:#2E357E; --indigo-soft:#6169B8; --marigold:#E0982B;
  --teal:#147D74; --rose:#B5476B; --line:#E3E4EE; --muted:#656579; --panel:#F1F2F8; }
*, *::before, *::after { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--ink); font-family:"Inter",system-ui,sans-serif; font-size:15px; line-height:1.6; -webkit-font-smoothing:antialiased; }
a { color:var(--indigo); text-decoration:none; } a:hover { text-decoration:underline; }
.nav { position:sticky; top:0; z-index:50; background:rgba(250,251,253,.96); border-bottom:1px solid var(--line); }
.nav-in { max-width:1280px; margin:0 auto; padding:10px 24px; display:flex; align-items:center; gap:15px; flex-wrap:wrap; }
.brand { font-family:"Spectral",serif; font-weight:700; color:var(--indigo); font-size:16px; margin-right:auto; }
.nav a { font-family:"IBM Plex Mono",monospace; font-size:11px; letter-spacing:.02em; color:var(--muted); padding:3px 2px; border-bottom:2px solid transparent; }
.nav a:hover { color:var(--ink); text-decoration:none; }
.nav a.active { color:var(--indigo); border-bottom-color:var(--marigold); }
.wrap { max-width:1280px; margin:0 auto; padding:0 24px 80px; }
.phead { padding:34px 0 12px; border-bottom:2px solid var(--ink); }
.phead h1 { font-family:"Spectral",serif; font-weight:700; font-size:clamp(24px,3.6vw,38px); margin:8px 0 6px; }
.phead .dek { font-size:13px; color:#33334a; margin:0; max-width:82ch; }
.note { font-size:12px; color:var(--muted); margin-top:8px; max-width:82ch; }
.explainer { margin:16px 0 0; border:1px solid var(--line); border-radius:12px; background:#fff; overflow:hidden; }
.explainer > summary, .more > summary { cursor:pointer; list-style:none; padding:12px 16px; font-weight:600; font-size:13.5px; color:var(--indigo); background:var(--panel); display:flex; align-items:center; gap:8px; }
.explainer > summary::-webkit-details-marker, .more > summary::-webkit-details-marker { display:none; }
.explainer > summary::before, .more > summary::before { content:"\\25B8"; font-size:11px; transition:transform .15s; color:var(--marigold); }
.explainer[open] > summary::before, .more[open] > summary::before { transform:rotate(90deg); }
.explainer-bd { padding:14px 18px; font-size:13.5px; color:#33334a; line-height:1.7; }
.explainer-bd .lead { margin:0 0 10px; } .explainer-bd b { color:var(--ink); }
.more { margin-top:13px; border:1px solid var(--line); border-radius:12px; background:#fff; overflow:hidden; }
.more > summary { color:var(--muted); background:#fff; } .more[open] > summary { border-bottom:1px solid var(--line); }
.more-bd { padding:15px; }
.strict { margin:16px 0 0; border:1px solid var(--line); border-radius:12px; background:#fff; padding:16px 18px; }
.strict-top { display:flex; align-items:baseline; gap:12px; flex-wrap:wrap; }
.strict-top .lbl { font-family:"IBM Plex Mono",monospace; font-size:10px; letter-spacing:.12em; text-transform:uppercase; color:var(--muted); font-weight:600; }
.strict-name { font-family:"IBM Plex Mono",monospace; font-weight:700; font-size:13.5px; color:var(--indigo); }
.strict-desc { font-size:12.5px; color:var(--muted); margin-left:auto; }
.strict input[type=range] { width:100%; margin:14px 0 4px; accent-color:var(--indigo); }
.strict-ticks { display:flex; justify-content:space-between; font-family:"IBM Plex Mono",monospace; font-size:10px; color:var(--muted); }
.strict-ticks span { flex:1; text-align:center; } .strict-ticks span:first-child { text-align:left; } .strict-ticks span:last-child { text-align:right; }
.art-controls { display:flex; align-items:center; gap:14px; padding:16px 0 0; flex-wrap:wrap; }
.ctrl-label { font-family:"IBM Plex Mono",monospace; font-size:10px; letter-spacing:.12em; text-transform:uppercase; color:var(--muted); font-weight:600; }
.art-nav { display:flex; align-items:center; gap:8px; }
.nav-btn { font-family:"IBM Plex Mono",monospace; font-size:14px; border:1px solid var(--line); border-radius:7px; padding:5px 13px; background:#fff; color:var(--indigo); cursor:pointer; }
.nav-btn:hover { background:var(--panel); } .nav-btn:disabled { color:var(--muted); cursor:default; }
.art-counter { font-family:"IBM Plex Mono",monospace; font-size:12px; color:var(--muted); min-width:68px; text-align:center; }
.art-select { font-family:"Inter",sans-serif; font-size:13px; padding:5px 10px; border:1px solid var(--line); border-radius:7px; background:#fff; max-width:360px; }
.title-bar { margin:16px 0 0; padding:12px 15px; background:#fff; border:1px solid var(--line); border-radius:10px; display:flex; align-items:baseline; gap:12px; flex-wrap:wrap; }
.title-bar .t { font-family:"Spectral",serif; font-weight:600; font-size:19px; }
.chip { font-family:"IBM Plex Mono",monospace; font-size:10px; font-weight:600; letter-spacing:.04em; padding:2px 8px; border-radius:5px; }
.chip.synthetic { background:#fbeada; color:#9a5a12; } .chip.real { background:#eef6f4; color:var(--teal); }
.chip.lang { background:#eef0fb; color:var(--indigo); }
.caption { margin:12px 0 0; padding:10px 14px; border-left:3px solid var(--marigold); background:#fdf9f1; border-radius:0 8px 8px 0; font-size:13.5px; color:#5a4520; } .caption b { color:#8a5a12; }
.gloss { border-bottom:1px dotted currentColor; cursor:help; }

.fert { margin:14px 0; display:grid; grid-template-columns:repeat(4,1fr); gap:1px; background:var(--line); border:1px solid var(--line); border-radius:12px; overflow:hidden; }
@media (max-width:640px){ .fert { grid-template-columns:repeat(2,1fr); } }
.fcell { background:#fff; padding:13px 14px; }
.fn { font-family:"IBM Plex Mono",monospace; font-weight:700; font-size:clamp(16px,2.4vw,24px); color:var(--indigo); line-height:1; }
.fl { font-size:11px; color:var(--muted); margin-top:5px; }
.fcell.hot .fn { color:var(--rose); }

.card { border:1px solid var(--line); border-radius:12px; background:#fff; overflow:hidden; margin-top:13px; }
.card-hd { padding:9px 15px; border-bottom:1px solid var(--line); background:var(--panel); font-family:"IBM Plex Mono",monospace; font-size:10px; font-weight:600; letter-spacing:.09em; text-transform:uppercase; color:var(--indigo); }
.card-bd { padding:14px 15px; }
.toks { display:flex; flex-wrap:wrap; gap:3px; line-height:2.4; }
.tok { display:inline-block; padding:1px 5px; border-radius:4px; font-size:13px; border:1px solid var(--line); background:#fff; }
.tok.byte { font-family:"IBM Plex Mono",monospace; font-size:10.5px; background:#fceef2; color:#8a1a3a; border-color:#f0cdd8; }
.tok.ascii { background:#eef6f4; color:var(--teal); border-color:#cfe6e1; }
.tok.deva { background:#eef0fb; color:var(--indigo); border-color:#d3d8f2; }
.tok.ws { background:transparent; border-color:transparent; color:#bbb; }
.legend { font-size:11.5px; color:var(--muted); margin-top:10px; }

.acct-row { display:flex; align-items:center; gap:10px; font-size:13px; padding:5px 0; border-bottom:1px dashed var(--line); }
.acct-row:last-child { border-bottom:none; }
.acct-k { flex:1; } .acct-v { font-family:"IBM Plex Mono",monospace; font-weight:600; color:var(--indigo); }
.bar { height:12px; border-radius:6px; background:var(--indigo-soft); }
.trunc-note { font-family:"IBM Plex Mono",monospace; font-size:10.5px; color:var(--muted); margin-top:12px; padding-top:9px; border-top:1px dashed var(--line); }
"""


JS = r"""
var RAW = JSON.parse(document.getElementById('articles-data').textContent);
var state = { idx:0, profile:1 };

var PROFILES = {
  0:{name:'CHARACTER', desc:'One token per Unicode character — a tokenizer that never merges. Script-neutral.'},
  1:{name:'BYTE-LEVEL (no merges)', desc:'One token per UTF-8 byte — the floor for any script the tokenizer never learned to merge. English escapes it; Indic is stuck here.'},
  2:{name:'INDIC-AWARE', desc:'One token per Unicode grapheme cluster — what an Indic-tuned vocabulary targets.'}
};

function esc(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function escAttr(s){ return esc(s).replace(/"/g,'&quot;'); }
function words(t){ return t.split(/\s+/).filter(function(w){ return w.length; }); }
function codepoints(t){ return Array.from(t); }
var ENC = (typeof TextEncoder!=='undefined') ? new TextEncoder() : null;
function utf8len(s){ return ENC ? ENC.encode(s).length : s.length; }
function graphemeList(t){
  try { var seg=new Intl.Segmenter('und',{granularity:'grapheme'}); var out=[];
    var it=seg.segment(t); for (var s of it) out.push(s.segment); return out; }
  catch(e){ return codepoints(t); }
}

/* exact counts */
function metrics(text){
  var w=words(text).length;
  var cp=codepoints(text).length;
  var by=utf8len(text);
  var gr=graphemeList(text).length;
  return { words:w, cp:cp, by:by, gr:gr,
           tok:{0:cp, 1:by, 2:gr},                         /* tokens per profile */
           fert:{0:cp/(w||1), 1:by/(w||1), 2:gr/(w||1)} }; /* tokens per word     */
}

/* tokenization for the visual, per profile */
function tokerize(text, profile){
  var toks=[];
  if (profile===0){ codepoints(text).forEach(function(c){ toks.push(cell(c)); }); return toks; }
  if (profile===2){ graphemeList(text).forEach(function(g){ toks.push(cell(g)); }); return toks; }
  /* byte profile: one token per UTF-8 byte; ASCII shows the char, multibyte shows hex */
  codepoints(text).forEach(function(ch){
    if (/\s/.test(ch)){ toks.push({t:'·',c:'ws'}); return; }
    var b = ENC ? ENC.encode(ch) : [ch.charCodeAt(0)];
    if (b.length===1){ toks.push({t:ch,c:'ascii'}); }
    else { for (var i=0;i<b.length;i++){ toks.push({t:b[i].toString(16).padStart(2,'0'),c:'byte'}); } }
  });
  return toks;
}
function cell(ch){ if (/\s/.test(ch)) return {t:'·',c:'ws'};
  var by=ENC?ENC.encode(ch).length:1; return {t:ch, c:(by>1?'deva':'ascii')}; }

function pctish(x){ return (Math.round(x*10)/10); }

/* ---------- render ---------- */
function render(){
  var art=RAW[state.idx], m=metrics(art.text), p=state.profile;

  document.getElementById('art-title').textContent=art.title;
  var kindEl=document.getElementById('art-kind'); kindEl.textContent=art.kind==='synthetic'?'SYNTHETIC':'REAL — Wikipedia';
  kindEl.className='chip '+(art.kind==='synthetic'?'synthetic':'real');
  var langEl=document.getElementById('art-lang'); langEl.textContent='lang: '+art.lang; langEl.className='chip lang';
  document.getElementById('art-counter').textContent=(state.idx+1)+' of '+RAW.length;
  document.getElementById('prev-btn').disabled=state.idx===0;
  document.getElementById('next-btn').disabled=state.idx===RAW.length-1;
  document.getElementById('art-select').value=state.idx;
  var capEl=document.getElementById('caption');
  if (art.caption){ capEl.innerHTML='<b>What this example shows:</b> '+esc(art.caption); capEl.style.display=''; }
  else capEl.style.display='none';

  /* fertility cells */
  var fert=m.fert[p], bpc=m.by/(m.cp||1);
  document.getElementById('fert').innerHTML =
    '<div class="fcell"><div class="fn">'+m.words+'</div><div class="fl">words</div></div>'+
    '<div class="fcell"><div class="fn">'+m.tok[p]+'</div><div class="fl">tokens ('+PROFILES[p].name.toLowerCase()+')</div></div>'+
    '<div class="fcell '+(fert>=2.5?'hot':'')+'"><div class="fn">'+pctish(fert)+'×</div><div class="fl">'+
      '<span class="gloss" title="Tokens divided by words. Higher = the tokenizer is more expensive for this text.">fertility (tokens/word)</span></div></div>'+
    '<div class="fcell '+(bpc>=2?'hot':'')+'"><div class="fn">'+pctish(bpc)+'</div><div class="fl">'+
      '<span class="gloss" title="UTF-8 bytes per character. 1.0 for ASCII, ~3.0 for Devanagari/Tamil — the physical root of the tax.">bytes / character</span></div></div>';

  /* token visualisation */
  var toks=tokerize(art.text, p), html='';
  for (var i=0;i<toks.length;i++){ html += '<span class="tok '+toks[i].c+'">'+esc(toks[i].t)+'</span>'; }
  document.getElementById('toks').innerHTML=html;
  document.getElementById('tok-legend').innerHTML = p===1
    ? 'Each box is one token. <span class="tok ascii" style="line-height:1">green</span> = a 1-byte ASCII character (an English tokenizer merges these into words). '+
      '<span class="tok byte" style="line-height:1">rose</span> = a raw UTF-8 byte of an Indic character — the tokenizer never learned to merge these, so one letter becomes 3 tokens.'
    : (p===0 ? 'Each box is one Unicode character.' : 'Each box is one grapheme cluster (a letter with its vowel signs) — an Indic-aware tokenizer aims for roughly this.');

  accounting();
}

/* ---------- corpus rollup ---------- */
function accounting(){
  var byLang={}, order=['en','code','other','hi','ta'];
  for (var i=0;i<RAW.length;i++){ var a=RAW[i], m=metrics(a.text), L=a.lang;
    (byLang[L]=byLang[L]||{w:0,by:0,cp:0,gr:0}); byLang[L].w+=m.words; byLang[L].by+=m.by; byLang[L].cp+=m.cp; byLang[L].gr+=m.gr; }
  var langs=Object.keys(byLang).sort(function(a,b){ return (byLang[a].by/byLang[a].w)-(byLang[b].by/byLang[b].w); });
  var maxF=0; langs.forEach(function(L){ maxF=Math.max(maxF, byLang[L].by/(byLang[L].w||1)); });
  var rows='';
  langs.forEach(function(L){ var d=byLang[L], f=d.by/(d.w||1);
    rows += '<div class="acct-row"><span class="acct-k">'+L+'</span>'+
      '<span style="width:200px"><span class="bar" style="display:block;width:'+(f/maxF*100)+'%;background:'+(f>=2.5?'#B5476B':'#6169B8')+'"></span></span>'+
      '<span class="acct-v">'+pctish(f)+'×</span></div>'; });
  document.getElementById('acct-lang').innerHTML=rows;

  var hi=byLang['hi'], en=byLang['en'];
  var tax = (hi&&en) ? (hi.by/hi.w)/(en.by/en.w) : 0;
  document.getElementById('acct-summary').innerHTML =
    '<div class="acct-row"><span class="acct-k">Bytes per character — English</span><span class="acct-v">'+(en?pctish(en.by/en.cp):'—')+'</span></div>'+
    '<div class="acct-row"><span class="acct-k">Bytes per character — Hindi</span><span class="acct-v" style="color:#B5476B">'+(hi?pctish(hi.by/hi.cp):'—')+'</span></div>'+
    '<div class="acct-row"><span class="acct-k">The Indic tax at the byte floor (Hindi ÷ English, per word)</span><span class="acct-v" style="color:#B5476B">'+(tax?pctish(tax)+'×':'—')+' more tokens</span></div>'+
    '<div class="acct-row"><span class="acct-k">Hindi with an Indic-aware vocab</span><span class="acct-v" style="color:#147D74">'+(hi?pctish(hi.gr/hi.w):'—')+' tokens/word</span></div>';
}

/* ---------- wiring ---------- */
var sel=document.getElementById('art-select');
for (var i=0;i<RAW.length;i++){ var o=document.createElement('option'); o.value=i; o.textContent=(i+1)+'. '+RAW[i].title; sel.appendChild(o); }
sel.addEventListener('change', function(){ state.idx=parseInt(this.value,10); render(); });
document.getElementById('prev-btn').addEventListener('click', function(){ if (state.idx>0){ state.idx--; render(); } });
document.getElementById('next-btn').addEventListener('click', function(){ if (state.idx<RAW.length-1){ state.idx++; render(); } });
document.addEventListener('keydown', function(e){ if (e.key==='ArrowLeft'&&state.idx>0){ state.idx--; render(); } if (e.key==='ArrowRight'&&state.idx<RAW.length-1){ state.idx++; render(); } });
var slider=document.getElementById('prof-slider');
function updateProfile(){ state.profile=parseInt(slider.value,10);
  document.getElementById('strict-name').textContent=state.profile+' · '+PROFILES[state.profile].name;
  document.getElementById('strict-desc').textContent=PROFILES[state.profile].desc; render(); }
slider.addEventListener('input', updateProfile);
updateProfile();
"""


def build_html(articles):
    data_json = json.dumps(articles, ensure_ascii=False)
    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>Tokenizer &amp; Fertility — India-First 40B</title>\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link href="https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,600;0,700;1,600'
        '&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">\n'
        '<style>' + CSS + '</style>\n</head>\n<body>\n'
        '<script type="application/json" id="articles-data">' + data_json + '</script>\n'
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
        '  <a href=\"tokenizer.html\" class=\"active\">Tokenizer</a>\n'
        '  <a href=\"manifest.html\">Manifest</a>\n'
        '  <a href=\"v5_brief.html\">V5 Plan</a>\n'
        '  <a href=\"v5_playbook.html\">V5 Plan — Proposal</a>\n'
        '  <a href=\"assignment.html\">Assignment</a>\n'
        '</div></div>\n'
        '<div class="wrap">\n'
        '  <div class="phead">\n'
        '    <h1>Tokenizer &amp; Fertility</h1>\n'
        '    <p class="dek">Why an India-first model needs its <b>own tokenizer</b>: an English-centric one charges '
        'Indic scripts 2–4× more tokens for the same text — wasting training and inference budget on Hindi.</p>\n'
        '  </div>\n'
        '  <details class="explainer" open>\n'
        '    <summary>How to read this page</summary>\n'
        '    <div class="explainer-bd">\n'
        '      <p class="lead">A tokenizer chops text into <b>tokens</b>; the model pays per token. <b>Fertility</b> = '
        'tokens per word — lower is cheaper. The root cause of the Indic tax is physical: an ASCII letter is <b>1 UTF-8 '
        'byte</b>, but a Devanagari or Tamil letter is <b>3 bytes</b>. A byte tokenizer that learned English merges but '
        'no Indic merges falls back to raw bytes for Indic, so one Hindi letter becomes ~3 tokens.</p>\n'
        '      <p class="note">Switch the <b>tokenizer profile</b> below and watch the token boxes: <b>character</b> '
        '(1 per letter), <b>English byte-BPE</b> (Indic letters explode into their raw bytes), and <b>Indic-aware</b> '
        '(1 per grapheme cluster — the fix). Every count here is exact (UTF-8 bytes, code points, Unicode grapheme '
        'clusters). A real learned tokenizer (tiktoken / SentencePiece) is a documented offline tier. Note: real '
        'English tokenizers <em>do</em> merge English into words — the point is Indic gets no such benefit.</p>\n'
        '    </div>\n'
        '  </details>\n'
        '  <div class="strict">\n'
        '    <div class="strict-top"><span class="lbl">Tokenizer profile</span><span class="strict-name" id="strict-name"></span><span class="strict-desc" id="strict-desc"></span></div>\n'
        '    <input type="range" min="0" max="2" step="1" value="1" id="prof-slider">\n'
        '    <div class="strict-ticks"><span>0 character</span><span>1 byte-level</span><span>2 Indic-aware</span></div>\n'
        '  </div>\n'
        '  <div class="art-controls">\n'
        '    <span class="ctrl-label">Sample</span>\n'
        '    <div class="art-nav">\n'
        '      <button class="nav-btn" id="prev-btn">&#8592;</button>\n'
        '      <span class="art-counter" id="art-counter"></span>\n'
        '      <button class="nav-btn" id="next-btn">&#8594;</button>\n'
        '    </div>\n'
        '    <select class="art-select" id="art-select"></select>\n'
        '  </div>\n'
        '  <div class="title-bar"><span class="t" id="art-title"></span><span class="chip" id="art-kind"></span><span class="chip lang" id="art-lang"></span></div>\n'
        '  <div class="caption" id="caption"></div>\n'
        '  <div class="fert" id="fert"></div>\n'
        '  <div class="card"><div class="card-hd">Tokens for this text at the selected profile</div><div class="card-bd">'
        '<div class="toks" id="toks"></div><div class="legend" id="tok-legend"></div></div></div>\n'
        '  <details class="more">\n'
        '    <summary>Show fertility across the whole sample (the Indic tax)</summary>\n'
        '    <div class="more-bd">\n'
        '      <div class="card" style="margin-top:0"><div class="card-hd">English byte-BPE fertility by language (tokens/word)</div><div class="card-bd" id="acct-lang"></div></div>\n'
        '      <div class="card"><div class="card-hd">The bottom line</div><div class="card-bd" id="acct-summary"></div></div>\n'
        '    </div>\n'
        '  </details>\n'
        '</div>\n'
        '<script>' + JS + '</script>\n'
        '</body>\n</html>\n'
    )


if __name__ == "__main__":
    print("Building tokenizer sample...")
    articles = T.build_sample()
    print("Generating {}...".format(OUTPUT_PATH))
    html = build_html(articles)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    n_syn = sum(1 for a in articles if a["kind"] == "synthetic")
    print("\nDone. {} written ({} samples: {} synthetic + {} real).".format(
        OUTPUT_PATH, len(articles), n_syn, len(articles) - n_syn))
