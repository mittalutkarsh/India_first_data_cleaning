"""
Generate quality.html — interactive Quality Filter preview.

Follows Quality_Filter.md (9-metric heuristic cascade, Layer 1) and
Quality_Filter_threshold-selection.md (named strictness bundles). The browser
runs the full Layer-1 cascade live; a strictness slider (0-5) selects a named
policy bundle and re-decides every document. Layer 2 (a learned 0-5 quality
classifier) needs a teacher model and is a documented offline tier, not faked.

The metric + decision logic here is a 1:1 mirror of the verified reference in
the scratchpad verifier. Run:  python3 generate_quality_preview.py
"""

import json
import os

import quality_sample

OUTPUT_PATH = "quality.html"


CSS = """
:root {
  --bg:#FAFBFD; --ink:#16162A; --indigo:#2E357E; --indigo-soft:#6169B8;
  --marigold:#E0982B; --teal:#147D74; --teal-soft:#3aa89c;
  --rose:#B5476B; --line:#E3E4EE; --muted:#656579; --panel:#F1F2F8;
  --pass:#1f9d76; --passbg:#e6f5ef; --failbg:#fceef2;
}
*, *::before, *::after { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--ink);
  font-family:"Inter",system-ui,sans-serif; font-size:15px; line-height:1.6;
  -webkit-font-smoothing:antialiased; }
a { color:var(--indigo); text-decoration:none; } a:hover { text-decoration:underline; }
.nav { position:sticky; top:0; z-index:50; background:rgba(250,251,253,.96);
       border-bottom:1px solid var(--line); }
.nav-in { max-width:1280px; margin:0 auto; padding:10px 24px; display:flex;
          align-items:center; gap:18px; flex-wrap:wrap; }
.brand { font-family:"Spectral",serif; font-weight:700; color:var(--indigo);
         font-size:16px; margin-right:auto; }
.nav a { font-family:"IBM Plex Mono",monospace; font-size:11px; letter-spacing:.03em;
         color:var(--muted); padding:3px 2px; border-bottom:2px solid transparent; }
.nav a:hover { color:var(--ink); text-decoration:none; }
.nav a.active { color:var(--indigo); border-bottom-color:var(--marigold); }
.wrap { max-width:1280px; margin:0 auto; padding:0 24px 80px; }
.phead { padding:34px 0 12px; border-bottom:2px solid var(--ink); }
.phead h1 { font-family:"Spectral",serif; font-weight:700;
            font-size:clamp(24px,3.6vw,38px); margin:8px 0 6px; }
.phead .dek { font-size:13px; color:#33334a; margin:0; max-width:82ch; }
.note { font-size:12px; color:var(--muted); margin-top:8px; max-width:82ch; }

.explainer { margin:16px 0 0; border:1px solid var(--line); border-radius:12px; background:#fff; overflow:hidden; }
.explainer > summary, .more > summary { cursor:pointer; list-style:none; padding:12px 16px;
  font-weight:600; font-size:13.5px; color:var(--indigo); background:var(--panel);
  display:flex; align-items:center; gap:8px; }
.explainer > summary::-webkit-details-marker, .more > summary::-webkit-details-marker { display:none; }
.explainer > summary::before, .more > summary::before { content:"\\25B8"; font-size:11px;
  transition:transform .15s; color:var(--marigold); }
.explainer[open] > summary::before, .more[open] > summary::before { transform:rotate(90deg); }
.explainer-bd { padding:14px 18px; font-size:13.5px; color:#33334a; line-height:1.7; }
.explainer-bd .lead { margin:0 0 12px; } .explainer-bd b { color:var(--ink); }
.verdict-key { display:flex; flex-direction:column; gap:6px; margin:10px 0 4px; }
.vk-row { display:flex; align-items:center; gap:10px; font-size:13px; }
.vk-badge { font-weight:700; font-size:11px; padding:2px 9px; border-radius:6px;
            min-width:150px; text-align:center; }
.more { margin-top:13px; border:1px solid var(--line); border-radius:12px; background:#fff; overflow:hidden; }
.more > summary { color:var(--muted); background:#fff; }
.more[open] > summary { border-bottom:1px solid var(--line); }
.more-bd { padding:15px; }

/* strictness slider */
.strict { margin:16px 0 0; border:1px solid var(--line); border-radius:12px; background:#fff; padding:16px 18px; }
.strict-top { display:flex; align-items:baseline; gap:12px; flex-wrap:wrap; }
.strict-top .lbl { font-family:"IBM Plex Mono",monospace; font-size:10px; letter-spacing:.12em;
  text-transform:uppercase; color:var(--muted); font-weight:600; }
.strict-name { font-family:"IBM Plex Mono",monospace; font-weight:700; font-size:14px; color:var(--indigo); }
.strict-desc { font-size:12.5px; color:var(--muted); margin-left:auto; }
.strict input[type=range] { width:100%; margin:14px 0 4px; accent-color:var(--indigo); }
.strict-ticks { display:flex; justify-content:space-between; font-family:"IBM Plex Mono",monospace;
  font-size:10px; color:var(--muted); }
.strict-ticks span { flex:1; text-align:center; }
.strict-ticks span:first-child { text-align:left; } .strict-ticks span:last-child { text-align:right; }

.art-controls { display:flex; align-items:center; gap:14px; padding:16px 0 0; flex-wrap:wrap; }
.ctrl-label { font-family:"IBM Plex Mono",monospace; font-size:10px; letter-spacing:.12em;
  text-transform:uppercase; color:var(--muted); font-weight:600; }
.art-nav { display:flex; align-items:center; gap:8px; }
.nav-btn { font-family:"IBM Plex Mono",monospace; font-size:14px; border:1px solid var(--line);
  border-radius:7px; padding:5px 13px; background:#fff; color:var(--indigo); cursor:pointer; }
.nav-btn:hover { background:var(--panel); } .nav-btn:disabled { color:var(--muted); cursor:default; }
.art-counter { font-family:"IBM Plex Mono",monospace; font-size:12px; color:var(--muted);
  min-width:68px; text-align:center; }
.art-select { font-family:"Inter",sans-serif; font-size:13px; padding:5px 10px; border:1px solid var(--line);
  border-radius:7px; background:#fff; max-width:340px; }

.title-bar { margin:16px 0 0; padding:12px 15px; background:#fff; border:1px solid var(--line);
  border-radius:10px; display:flex; align-items:baseline; gap:12px; flex-wrap:wrap; }
.title-bar .t { font-family:"Spectral",serif; font-weight:600; font-size:19px; }
.title-bar a { font-family:"IBM Plex Mono",monospace; font-size:11px; color:var(--muted); }
.chip { font-family:"IBM Plex Mono",monospace; font-size:10px; font-weight:600; letter-spacing:.04em;
  padding:2px 8px; border-radius:5px; }
.chip.synthetic { background:#fbeada; color:#9a5a12; } .chip.real { background:#eef6f4; color:var(--teal); }
.chip.profile { background:#eef0fb; color:var(--indigo); }
.caption { margin:12px 0 0; padding:10px 14px; border-left:3px solid var(--marigold);
  background:#fdf9f1; border-radius:0 8px 8px 0; font-size:13.5px; color:#5a4520; }
.caption b { color:#8a5a12; }

.verdict { margin:14px 0; border:1px solid var(--line); border-radius:12px; overflow:hidden; }
.verdict-hd { padding:14px 18px 6px; display:flex; align-items:center; gap:12px; flex-wrap:wrap; }
.verdict-badge { font-weight:700; font-size:17px; padding:7px 15px; border-radius:9px; }
.v-accept { background:#eef6f4; color:var(--teal); }
.v-special { background:#eef0fb; color:var(--indigo); }
.v-review { background:#fdf3e3; color:#9a5a12; }
.v-exclude { background:#fceef2; color:var(--rose); }
.verdict-code { font-family:"IBM Plex Mono",monospace; font-size:10.5px; color:var(--muted); }
.verdict-why { padding:2px 18px 14px; font-size:14px; color:#26263c; line-height:1.55; }

.gloss { border-bottom:1px dotted currentColor; cursor:help; }

.card { border:1px solid var(--line); border-radius:12px; background:#fff; overflow:hidden; }
.card-hd { padding:9px 15px; border-bottom:1px solid var(--line); background:var(--panel);
  font-family:"IBM Plex Mono",monospace; font-size:10px; font-weight:600; letter-spacing:.09em;
  text-transform:uppercase; color:var(--indigo); }
.card-bd { padding:14px 15px; }

/* metric gauges */
.gauge { display:grid; grid-template-columns:190px 1fr 132px; gap:10px; align-items:center;
  padding:7px 0; border-bottom:1px dashed var(--line); }
.gauge:last-child { border-bottom:none; }
.g-name { font-size:12.5px; }
.g-track { position:relative; height:16px; background:var(--panel); border-radius:8px; overflow:hidden; }
.g-band { position:absolute; top:0; height:100%; background:var(--passbg);
  border-left:1px dashed var(--pass); border-right:1px dashed var(--pass); }
.g-mark { position:absolute; top:-2px; width:2px; height:20px; background:var(--ink); }
.g-mark.ok { background:var(--pass); } .g-mark.bad { background:var(--rose); }
.g-val { font-family:"IBM Plex Mono",monospace; font-size:11.5px; text-align:right; }
.g-tag { font-family:"IBM Plex Mono",monospace; font-size:10px; font-weight:600; padding:1px 6px;
  border-radius:4px; margin-left:6px; }
.g-tag.ok { background:var(--passbg); color:var(--pass); }
.g-tag.bad { background:var(--failbg); color:var(--rose); }
.g-tag.exempt { background:var(--panel); color:var(--muted); }

.text-view { border:1px solid var(--line); border-radius:12px; background:#fff; margin-top:13px; }
.text-body { padding:15px; max-height:280px; overflow-y:auto; font-size:13.5px; line-height:1.75;
  white-space:pre-wrap; word-break:break-word; font-family:"IBM Plex Mono",monospace; }

.acct-grid { display:grid; grid-template-columns:1fr 1fr; gap:13px; }
@media (max-width:860px){ .acct-grid { grid-template-columns:1fr; } }
.acct-row { display:flex; align-items:center; gap:10px; font-size:13px; padding:5px 0;
  border-bottom:1px dashed var(--line); } .acct-row:last-child { border-bottom:none; }
.acct-k { flex:1; } .acct-v { font-family:"IBM Plex Mono",monospace; font-weight:600; color:var(--indigo); }
.acct-bar { height:10px; border-radius:5px; }
.sweep { width:100%; border-collapse:collapse; font-size:12.5px; margin-top:6px; }
.sweep th, .sweep td { padding:5px 8px; text-align:right; border-bottom:1px solid var(--line);
  font-family:"IBM Plex Mono",monospace; }
.sweep th:first-child, .sweep td:first-child { text-align:left; }
.sweep tr.here { background:#f5f6fd; }
.trunc-note { font-family:"IBM Plex Mono",monospace; font-size:10.5px; color:var(--muted);
  margin-top:12px; padding-top:9px; border-top:1px dashed var(--line); }
"""


JS = r"""
var ARTICLES = JSON.parse(document.getElementById('articles-data').textContent);
var state = { idx: 0, strictness: 3 };

/* ---------- stop-word lists ---------- */
var HI_STOP = 'है और में की के को से का यह कि हैं पर ने एक भी हो था थे थी कर जो तो ही इस उस अपने होता करने गया लिए रहा साथ'.split(' ');
var EN_STOP = 'the be to of and that have with'.split(' ');
var BULLETS = ['-','*','•','–','‣','●','·'];
var TERM = ['.','!','?','।','॥','؟'];

function hasAlnum(t){ return /[\p{L}\p{N}]/u.test(t); }
function esc(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function escAttr(s){ return esc(s).replace(/"/g,'&quot;'); }
function pct(x){ return (x*100).toFixed(1)+'%'; }
function fx(x){ return (Math.round(x*100)/100).toString(); }

/* ---------- the 9 metrics (mirror of the verified Python) ---------- */
function analyse(text){
  var tokens = text.split(/\s+/).filter(function(t){ return t.length; });
  var words = tokens.filter(hasAlnum);
  var wc = words.length;
  var lines = text.split('\n').map(function(l){ return l.trim(); }).filter(function(l){ return l.length; });
  var nlines = lines.length;

  var deva=0, latn=0;
  for (var i=0;i<text.length;i++){ var c=text.charCodeAt(i);
    if (c>=0x900 && c<=0x97F) deva++;
    else if (c<128 && /[a-zA-Z]/.test(text[i])) latn++; }

  var stoplist = deva>=latn ? HI_STOP : EN_STOP;
  var mwl = wc ? words.reduce(function(s,w){ return s+w.length; },0)/wc : 0;
  var hashr = ((text.match(/#/g)||[]).length)/(wc||1);
  var ellr  = (((text.match(/\.\.\./g)||[]).length)+((text.match(/…/g)||[]).length))/(wc||1);

  function endsTerm(l){ for (var i=0;i<TERM.length;i++){ if (l.slice(-TERM[i].length)===TERM[i]) return true; } return false; }
  var termOk=0; for (var j=0;j<lines.length;j++){ if (endsTerm(lines[j])) termOk++; }
  var term = nlines ? termOk/nlines : 0;

  var freq={}; for (var k=0;k<lines.length;k++){ var key=lines[k].toLowerCase(); freq[key]=(freq[key]||0)+1; }
  var dupsum=0; for (var f in freq){ dupsum += Math.max(freq[f]-1,0); }
  var dup = nlines ? dupsum/nlines : 0;

  var bg={}, topBg=null, topCnt=0;
  for (var w=0; w<words.length-1; w++){ var kk=words[w]+''+words[w+1];
    bg[kk]=(bg[kk]||0)+1; if (bg[kk]>topCnt){ topCnt=bg[kk]; topBg=[words[w],words[w+1]]; } }
  var bg2=0;
  if (topBg && text.length){ var covered=topCnt*(topBg[0].length+1+topBg[1].length); bg2=covered/text.length; }

  var wset={}; for (var q=0;q<words.length;q++) wset[words[q].toLowerCase()]=1;
  var stops=0; for (var s=0;s<stoplist.length;s++){ if (wset[stoplist[s]]) stops++; }

  function isBullet(l){ var c=l.replace(/^\s+/,'').charAt(0); return BULLETS.indexOf(c)!==-1; }
  var bl=0; for (var b=0;b<lines.length;b++){ if (isBullet(lines[b])) bl++; }
  var bullet = nlines ? bl/nlines : 0;
  var el=0; for (var e=0;e<lines.length;e++){ if (lines[e].slice(-3)==='...' || lines[e].slice(-1)==='…') el++; }
  var ellip = nlines ? el/nlines : 0;

  return { wc:wc, nlines:nlines, mwl:mwl, hashr:hashr, ellr:ellr, term:term, dup:dup,
           bg2:bg2, stops:stops, bullet:bullet, ellip:ellip, topBg:topBg, deva:deva, latn:latn };
}

function profileOf(a, text){
  var lines = text.split('\n').filter(function(l){ return l.trim().length; });
  var n = lines.length||1, code=0;
  var re = /\b(def|return|import|class|function|var|const|for|while|if|else)\b|[{}=;]|\):|print\(/;
  for (var i=0;i<lines.length;i++){ if (re.test(lines[i])) code++; }
  if (a.latn>a.deva && code/n>=0.4 && code>=3) return 'code';
  if (a.bullet>=0.6) return 'list-recipe';
  if (a.ellip>=0.3) return 'conversation';
  return 'web-prose';
}

/* ---------- strictness bundles ---------- */
var BUNDLES = {
  0:{name:'OFF', desc:'Keep everything — no filtering. A baseline to compare against.'},
  1:{name:'LOOSE', desc:'Only drop obvious spam/junk; maximise how much data survives.',
     mwl:[2,12], sym:0.20, term:0.10, dup:0.50, bg2:0.30, stop:0, bullet:0.95, ellip:0.50, wc_min:20, wc_max:100000},
  2:{name:'BALANCED · high recall', desc:'Lean toward keeping data; still catch clear junk.',
     mwl:[2.5,11], sym:0.15, term:0.20, dup:0.40, bg2:0.25, stop:1, bullet:0.92, ellip:0.40, wc_min:30, wc_max:100000},
  3:{name:'BALANCED · high quality', desc:'The user-baseline-v1 thresholds from the skill.',
     mwl:[3,10], sym:0.10, term:0.30, dup:0.30, bg2:0.20, stop:2, bullet:0.90, ellip:0.30, wc_min:50, wc_max:100000},
  4:{name:'STRICT · educational', desc:'Tight thresholds; keep only clean, substantial prose.',
     mwl:[3.5,9], sym:0.05, term:0.50, dup:0.20, bg2:0.15, stop:3, bullet:0.75, ellip:0.10, wc_min:100, wc_max:100000},
  5:{name:'KEEP NONE', desc:'Drop everything — a sanity check that the pipeline actually runs.'}
};
var SOFT_LIMIT = {1:99, 2:3, 3:2, 4:1};
var HARD = {sym:1, dup:1, bg2:1};

function bundleFor(s){ return (s===0||s===5) ? BUNDLES[3] : BUNDLES[s]; }

function metricStatus(a, b, prof){
  var exempt={};
  if (prof==='code'){ ['sym','stop','term','mwl','bullet','ellip'].forEach(function(k){ exempt[k]=1; }); }
  else if (prof==='list-recipe'){ exempt.bullet=1; exempt.term=1; }
  else if (prof==='conversation'){ exempt.ellip=1; exempt.term=1; }
  if (a.wc<30){ exempt.dup=1; exempt.bg2=1; }   /* repetition stats unreliable on tiny docs */
  var symVal = prof==='conversation' ? a.hashr : Math.max(a.hashr, a.ellr);
  var m = {
    mwl:   {value:a.mwl,    ok:(a.mwl>=b.mwl[0] && a.mwl<=b.mwl[1]), hard:false},
    sym:   {value:symVal,   ok:(symVal<b.sym),   hard:true},
    term:  {value:a.term,   ok:(a.term>=b.term), hard:false},
    dup:   {value:a.dup,    ok:(a.dup<b.dup),    hard:true},
    bg2:   {value:a.bg2,    ok:(a.bg2<b.bg2),    hard:true},
    stop:  {value:a.stops,  ok:(a.stops>=b.stop),hard:false},
    bullet:{value:a.bullet, ok:(a.bullet<b.bullet), hard:false},
    ellip: {value:a.ellip,  ok:(a.ellip<b.ellip),   hard:false},
    wc:    {value:a.wc,     ok:(a.wc>=b.wc_min && a.wc<=b.wc_max), hard:false}
  };
  for (var k in m){ m[k].exempt = !!exempt[k]; }
  return m;
}

function decide(a, prof, strictness){
  if (strictness===0) return { disp:'ACCEPT_STANDARD', hard:[], soft:[] };
  if (strictness===5) return { disp:'EXCLUDE_HEURISTIC', hard:[], soft:[] };
  var b = BUNDLES[strictness];
  var m = metricStatus(a, b, prof);
  var hard=[], soft=[];
  for (var k in m){ if (!m[k].ok && !m[k].exempt){ if (m[k].hard) hard.push(k); else if (k!=='wc') soft.push(k); } }
  if (hard.length) return { disp:'EXCLUDE_HEURISTIC', hard:hard, soft:soft };
  if (prof==='code'||prof==='list-recipe'||prof==='conversation') return { disp:'ACCEPT_SPECIAL_FORMAT', hard:hard, soft:soft };
  if (!m.wc.ok) return { disp:'REVIEW', hard:hard, soft:soft };
  if (soft.length >= SOFT_LIMIT[strictness]) return { disp:'REVIEW', hard:hard, soft:soft };
  return { disp:'ACCEPT_STANDARD', hard:hard, soft:soft };
}

/* ---------- plain-language labels + tooltips ---------- */
var PLAIN = {
  ACCEPT_STANDARD:      { emoji:'✅', word:'KEEP', cls:'v-accept' },
  ACCEPT_HIGH:          { emoji:'✅', word:'KEEP', cls:'v-accept' },
  ACCEPT_SPECIAL_FORMAT:{ emoji:'📄', word:'KEEP (special format)', cls:'v-special' },
  REVIEW:               { emoji:'🟠', word:'REVIEW', cls:'v-review' },
  EXCLUDE_HEURISTIC:    { emoji:'⬜', word:'DROP', cls:'v-exclude' }
};
var GLOSS = {
  ACCEPT_STANDARD:'KEEP — clears the quality checks, clean enough to train on.',
  ACCEPT_SPECIAL_FORMAT:'KEEP but routed to a special bucket (code / list / chat) where normal prose rules do not apply.',
  REVIEW:'Hold for a human or a stronger check — not clearly good, not clearly junk.',
  EXCLUDE_HEURISTIC:'DROP — failed a hard quality check (spam, repetition or symbol-soup).',
  'web-prose':'Ordinary article/prose — all nine prose checks apply.',
  'list-recipe':'A list or recipe — the bullet and sentence-ending rules are relaxed.',
  'conversation':'Chat/dialogue — the ellipsis and sentence-ending rules are relaxed.',
  'code':'Source code — prose rules (symbols, stop-words, sentences) do not apply.'
};
function glossOf(c){ return GLOSS[c]||c; }

/* metric display specs: label, tooltip, scaleMax, direction (lo/hi/range) */
var METRICS = [
  {k:'wc',    label:'Word count',            max:600, dir:'range', tip:'Number of real words. Too few to judge, or implausibly many, gets special handling.'},
  {k:'mwl',   label:'Mean word length',      max:15,  dir:'range', tip:'Average characters per word. Very low or very high suggests broken tokenization or gibberish.'},
  {k:'sym',   label:'Symbol-to-word ratio',  max:0.5, dir:'lo',    tip:"How many '#'/'…' symbols relative to words. High = symbol soup, not prose."},
  {k:'term',  label:'Sentence-ending lines', max:1,   dir:'hi',    tip:'Fraction of lines ending in . ! ? । ॥ . Low = fragments, not sentences.'},
  {k:'dup',   label:'Duplicate lines',       max:1,   dir:'lo',    tip:'Fraction of lines that repeat another line. High = boilerplate or spam.'},
  {k:'bg2',   label:'Top word-pair repeat',  max:1,   dir:'lo',    tip:'Share of the text taken up by its single most-repeated word pair. High = keyword stuffing.'},
  {k:'stop',  label:'Common stop words',     max:8,   dir:'hi',    tip:'How many everyday function words appear (है, और … / the, of, and …). Real prose has several.'},
  {k:'bullet',label:'Bullet lines',          max:1,   dir:'lo',    tip:'Fraction of lines that are bullet points. Near 100% = a list, not an article.'},
  {k:'ellip', label:'Ellipsis lines',        max:1,   dir:'lo',    tip:"Fraction of lines ending in '…'. High = chat/dramatic style or scraped snippets."}
];
function bandFor(spec, b){
  /* returns [start,end] of pass zone in [0,max] coords */
  if (spec.dir==='range'){
    if (spec.k==='wc') return [b.wc_min, Math.min(b.wc_max, spec.max)];
    return [b.mwl[0], b.mwl[1]];
  }
  var cut = b[spec.k];
  if (spec.dir==='lo') return [0, cut];
  return [cut, spec.max];   /* hi */
}
function metricVal(a, k){
  if (k==='sym') return Math.max(a.hashr, a.ellr);
  if (k==='stop') return a.stops;
  return a[k];
}
function fmtVal(k, v){
  if (k==='wc'||k==='stop') return String(Math.round(v));
  if (k==='mwl') return fx(v);
  return v.toFixed(2);
}

/* ---------- render one document ---------- */
function render(){
  var art = ARTICLES[state.idx];
  var a = analyse(art.text);
  var prof = profileOf(a, art.text);
  var b = bundleFor(state.strictness);
  var m = metricStatus(a, b, prof);
  var d = decide(a, prof, state.strictness);

  /* header */
  document.getElementById('art-title').textContent = art.title;
  var kindEl = document.getElementById('art-kind');
  kindEl.textContent = art.kind==='synthetic' ? 'SYNTHETIC' : 'REAL — Wikipedia';
  kindEl.className = 'chip gloss '+(art.kind==='synthetic'?'synthetic':'real');
  kindEl.title = art.kind==='synthetic' ? 'A made-up example to demonstrate a case.' : 'A genuine Hindi Wikipedia article.';
  var profEl = document.getElementById('art-profile');
  profEl.textContent = 'profile: '+prof; profEl.className='chip profile gloss'; profEl.title=glossOf(prof);
  var urlEl = document.getElementById('art-url'); urlEl.href=art.url; urlEl.style.display = art.kind==='synthetic'?'none':'';
  document.getElementById('art-counter').textContent = (state.idx+1)+' of '+ARTICLES.length;
  document.getElementById('prev-btn').disabled = state.idx===0;
  document.getElementById('next-btn').disabled = state.idx===ARTICLES.length-1;
  document.getElementById('art-select').value = state.idx;

  var capEl = document.getElementById('caption');
  if (art.caption){ capEl.innerHTML='<b>What this example shows:</b> '+esc(art.caption); capEl.style.display=''; }
  else capEl.style.display='none';

  /* verdict */
  var pv = PLAIN[d.disp] || {emoji:'',word:d.disp,cls:''};
  var badge = document.getElementById('verdict-badge');
  badge.className='verdict-badge '+pv.cls; badge.textContent = pv.emoji+' '+pv.word;
  var codeEl=document.getElementById('verdict-code'); codeEl.textContent=d.disp; codeEl.title=glossOf(d.disp);
  document.getElementById('verdict-sub').textContent = whyText(d, prof, m, a, b);

  /* gauges */
  var g='';
  for (var i=0;i<METRICS.length;i++){
    var spec=METRICS[i], st=m[spec.k], v=metricVal(a,spec.k);
    var band=bandFor(spec,b);
    var bs=Math.max(0,Math.min(1,band[0]/spec.max))*100;
    var be=Math.max(0,Math.min(1,band[1]/spec.max))*100;
    var mk=Math.max(0,Math.min(1,v/spec.max))*100;
    var tag = st.exempt ? '<span class="g-tag exempt">exempt</span>'
              : (st.ok ? '<span class="g-tag ok">✓ pass</span>' : '<span class="g-tag bad">✗ fail</span>');
    var mkcls = st.exempt ? '' : (st.ok?'ok':'bad');
    g += '<div class="gauge">'+
      '<div class="g-name"><span class="gloss" title="'+escAttr(spec.tip)+'">'+spec.label+'</span></div>'+
      '<div class="g-track"><div class="g-band" style="left:'+bs+'%;width:'+Math.max(0,be-bs)+'%"></div>'+
        '<div class="g-mark '+mkcls+'" style="left:'+mk+'%"></div></div>'+
      '<div class="g-val">'+fmtVal(spec.k,v)+tag+'</div></div>';
  }
  document.getElementById('gauges').innerHTML = g;

  /* text */
  var isTrunc = art.full_len > art.text.length;
  document.getElementById('text-body').innerHTML = esc(art.text) +
    (isTrunc ? '<div class="trunc-note">Showing first '+art.text.length+' of '+art.full_len+' chars</div>' : '');

  accounting();
}

function whyText(d, prof, m, a, b){
  if (state.strictness===0) return 'Strictness is OFF — every document is kept, so you can see the raw metrics before any filtering.';
  if (state.strictness===5) return 'Strictness is KEEP-NONE — everything is dropped. A sanity check, not a real setting.';
  if (d.disp==='EXCLUDE_HEURISTIC'){
    var names={sym:'symbol soup',dup:'duplicate lines',bg2:'a repeated word-pair'};
    var reasons = d.hard.map(function(k){ return names[k]||k; }).join(' and ');
    return 'Failed a hard quality check ('+reasons+') — this is the kind of spam/junk the filter is built to drop.';
  }
  if (d.disp==='ACCEPT_SPECIAL_FORMAT')
    return 'Detected as '+prof+'. Normal prose rules don’t fit it, so it is kept and routed to the '+prof+' bucket instead of being wrongly failed.';
  if (d.disp==='REVIEW'){
    if (!m.wc.ok) return 'Too short to judge confidently ('+a.wc+' words) — routed to review rather than dropped, in case it is a useful caption or definition.';
    return d.soft.length+' quality checks fell short at this strictness — sent to review instead of being dropped outright.';
  }
  return 'Passes the quality checks at this strictness — clean enough to accept into the training data.';
}

/* ---------- corpus accounting + strictness sweep ---------- */
function decideAll(strictness){
  var counts={};
  for (var i=0;i<ARTICLES.length;i++){
    var a=analyse(ARTICLES[i].text), prof=profileOf(a,ARTICLES[i].text);
    var dec=decide(a,prof,strictness).disp;
    counts[dec]=(counts[dec]||0)+1;
  }
  return counts;
}
function keptOf(c){ return (c.ACCEPT_STANDARD||0)+(c.ACCEPT_SPECIAL_FORMAT||0)+(c.ACCEPT_HIGH||0); }

var DISP_COLOR = { ACCEPT_STANDARD:'#147D74', ACCEPT_SPECIAL_FORMAT:'#6169B8',
  REVIEW:'#E0982B', EXCLUDE_HEURISTIC:'#B5476B' };

function accounting(){
  var total=ARTICLES.length, c=decideAll(state.strictness);
  var keys=Object.keys(c).sort(function(x,y){ return c[y]-c[x]; }), rows='';
  for (var i=0;i<keys.length;i++){ var k=keys[i], n=c[k], w=(n/total)*100;
    var pv=PLAIN[k]||{word:k}; var col=DISP_COLOR[k]||'#6169B8';
    rows += '<div class="acct-row"><span class="acct-k">'+pv.emoji+' '+pv.word+' <span style="color:#999;font-size:11px">'+k+'</span></span>'+
      '<span style="width:120px"><span class="acct-bar" style="display:block;width:'+w+'%;background:'+col+'"></span></span>'+
      '<span class="acct-v">'+n+'</span></div>'; }
  document.getElementById('acct-disp').innerHTML = rows;

  var kept=keptOf(c);
  document.getElementById('acct-summary').innerHTML =
    '<div class="acct-row"><span class="acct-k">Documents kept (accepted)</span><span class="acct-v">'+kept+' / '+total+'  ('+pct(kept/total)+')</span></div>'+
    '<div class="acct-row"><span class="acct-k">Sent to review</span><span class="acct-v">'+(c.REVIEW||0)+'</span></div>'+
    '<div class="acct-row"><span class="acct-k">Dropped</span><span class="acct-v">'+(c.EXCLUDE_HEURISTIC||0)+'</span></div>'+
    '<div class="acct-row"><span class="acct-k">Active policy</span><span class="acct-v">'+BUNDLES[state.strictness].name+'</span></div>';

  var sw='<table class="sweep"><tr><th>strictness</th><th>kept</th><th>review</th><th>dropped</th></tr>';
  for (var s=0;s<6;s++){ var cc=decideAll(s);
    sw += '<tr'+(s===state.strictness?' class="here"':'')+'><td>'+s+' '+BUNDLES[s].name+'</td>'+
      '<td>'+keptOf(cc)+'</td><td>'+(cc.REVIEW||0)+'</td><td>'+(cc.EXCLUDE_HEURISTIC||0)+'</td></tr>'; }
  sw+='</table>';
  document.getElementById('sweep').innerHTML = sw;
}

/* ---------- wiring ---------- */
var sel=document.getElementById('art-select');
for (var i=0;i<ARTICLES.length;i++){ var o=document.createElement('option');
  o.value=i; o.textContent=(i+1)+'. '+ARTICLES[i].title; sel.appendChild(o); }
sel.addEventListener('change', function(){ state.idx=parseInt(this.value,10); render(); });
document.getElementById('prev-btn').addEventListener('click', function(){ if (state.idx>0){ state.idx--; render(); } });
document.getElementById('next-btn').addEventListener('click', function(){ if (state.idx<ARTICLES.length-1){ state.idx++; render(); } });
document.addEventListener('keydown', function(e){
  if (e.key==='ArrowLeft' && state.idx>0){ state.idx--; render(); }
  if (e.key==='ArrowRight' && state.idx<ARTICLES.length-1){ state.idx++; render(); } });

var slider=document.getElementById('strict-slider');
function updateStrict(){
  state.strictness=parseInt(slider.value,10);
  document.getElementById('strict-name').textContent = state.strictness+' · '+BUNDLES[state.strictness].name;
  document.getElementById('strict-desc').textContent = BUNDLES[state.strictness].desc;
  render();
}
slider.addEventListener('input', updateStrict);

updateStrict();
"""


def build_html(articles):
    data_json = json.dumps(articles, ensure_ascii=False)
    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>Quality Filter — India-First 40B</title>\n'
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
        '  <a href=\"quality.html\" class=\"active\">Quality</a>\n'
        '  <a href=\"dedup.html\">Dedup</a>\n'
        '  <a href=\"pii.html\">PII</a>\n'
        '  <a href=\"decontam.html\">Decontam</a>\n'
        '  <a href=\"tokenizer.html\">Tokenizer</a>\n'
        '  <a href=\"manifest.html\">Manifest</a>\n'
        '  <a href=\"v5_brief.html\">V5 Plan</a>\n'
        '  <a href=\"v5_playbook.html\">V5 Plan — Proposal</a>\n'
        '  <a href=\"assignment.html\">Assignment</a>\n'
        '</div></div>\n'
        '<div class="wrap">\n'
        '  <div class="phead">\n'
        '    <h1>Quality Filter</h1>\n'
        '    <p class="dek">Per <em>Quality_Filter.md</em>: decide whether each document is good enough to train on. '
        'Nine cheap checks score it, a content <b>profile</b> protects legitimate lists/code/chat, and every document '
        'is <b>routed</b> — not silently deleted.</p>\n'
        '  </div>\n'
        '  <details class="explainer" open>\n'
        '    <summary>How to read this page</summary>\n'
        '    <div class="explainer-bd">\n'
        '      <p class="lead">Each document gets nine quick quality measurements. Each has a <b>pass zone</b> '
        '(shaded green on its gauge); a marker shows where this document lands. The document is then routed:</p>\n'
        '      <div class="verdict-key">\n'
        '        <div class="vk-row"><span class="vk-badge v-accept">✅ KEEP</span><span>Clears the checks — goes into training.</span></div>\n'
        '        <div class="vk-row"><span class="vk-badge v-special">📄 KEEP (special)</span><span>A list, code or chat — kept, but normal prose rules don’t apply.</span></div>\n'
        '        <div class="vk-row"><span class="vk-badge v-review">🟠 REVIEW</span><span>Borderline or too short — held for a closer look.</span></div>\n'
        '        <div class="vk-row"><span class="vk-badge v-exclude">⬜ DROP</span><span>Spam, repetition or symbol-soup — excluded.</span></div>\n'
        '      </div>\n'
        '      <p class="note" style="margin-top:12px">There is no single right cut-off. The <b>strictness slider</b> '
        'below selects a named policy bundle (from <em>threshold-selection.md</em>): drag it and watch the pass zones and '
        'every verdict move. This is Layer 1 (fast heuristics); a learned quality classifier (Layer 2) is a documented '
        'offline tier, not run here. Hover any underlined term for its meaning.</p>\n'
        '    </div>\n'
        '  </details>\n'
        '  <div class="strict">\n'
        '    <div class="strict-top">\n'
        '      <span class="lbl">Strictness</span>\n'
        '      <span class="strict-name" id="strict-name"></span>\n'
        '      <span class="strict-desc" id="strict-desc"></span>\n'
        '    </div>\n'
        '    <input type="range" min="0" max="5" step="1" value="3" id="strict-slider">\n'
        '    <div class="strict-ticks"><span>0 off</span><span>1 loose</span><span>2 recall</span>'
        '<span>3 quality</span><span>4 strict</span><span>5 none</span></div>\n'
        '  </div>\n'
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
        '    <span class="chip profile" id="art-profile"></span>\n'
        '    <a id="art-url" href="#" target="_blank">&#8599; Wikipedia</a>\n'
        '  </div>\n'
        '  <div class="caption" id="caption"></div>\n'
        '  <div class="verdict" id="verdict">\n'
        '    <div class="verdict-hd">\n'
        '      <span class="verdict-badge" id="verdict-badge"></span>\n'
        '      <span class="verdict-code gloss" id="verdict-code"></span>\n'
        '    </div>\n'
        '    <div class="verdict-why" id="verdict-sub"></div>\n'
        '  </div>\n'
        '  <div class="card">\n'
        '    <div class="card-hd">The nine quality checks — green is the pass zone at this strictness</div>\n'
        '    <div class="card-bd"><div id="gauges"></div></div>\n'
        '  </div>\n'
        '  <div class="text-view">\n'
        '    <div class="card-hd" style="border-bottom:1px solid var(--line)">The document</div>\n'
        '    <div class="text-body" id="text-body"></div>\n'
        '  </div>\n'
        '  <details class="more">\n'
        '    <summary>Show corpus accounting — the big picture across all ' + str(len(articles)) + ' documents</summary>\n'
        '    <div class="more-bd">\n'
        '      <p class="note" style="margin-top:0">Where every document lands at the current strictness, and how the '
        'keep / review / drop split changes as you move the slider.</p>\n'
        '      <div class="acct-grid">\n'
        '        <div class="card"><div class="card-hd">Decisions at current strictness</div><div class="card-bd" id="acct-disp"></div></div>\n'
        '        <div class="card"><div class="card-hd">Summary</div><div class="card-bd" id="acct-summary"></div></div>\n'
        '      </div>\n'
        '      <div class="card" style="margin-top:13px"><div class="card-hd">Retention across every strictness bundle</div>'
        '<div class="card-bd" id="sweep"></div></div>\n'
        '    </div>\n'
        '  </details>\n'
        '</div>\n'
        '<script>' + JS + '</script>\n'
        '</body>\n</html>\n'
    )


if __name__ == "__main__":
    print("Building quality sample...")
    articles = quality_sample.build_sample()
    print("Generating {}...".format(OUTPUT_PATH))
    html = build_html(articles)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    n_syn = sum(1 for a in articles if a["kind"] == "synthetic")
    print("\nDone. {} written ({} articles: {} synthetic + {} real).".format(
        OUTPUT_PATH, len(articles), n_syn, len(articles) - n_syn))
