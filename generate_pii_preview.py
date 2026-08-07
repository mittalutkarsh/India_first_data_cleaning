"""
Generate pii.html — interactive PII detection & redaction preview.

Follows PII.md (detect -> classify by entity + context + source tier ->
typed redaction / pseudonymization -> route the document -> re-scan) and
PII_policy-and-thresholds.md (named context policies + document routing).

Hard rule honored: the detection log NEVER shows a raw identifier — only a
typed placeholder (<EMAIL>) and the risk tier. All identifiers in the demo are
synthetic/fake; the input text is shown only to make detection visible, with a
disclaimer. Full multilingual NER + quasi-identifier linkage is a documented
offline tier. Engine verified in Python and re-checked in Node.

Run: python3 generate_pii_preview.py
"""

import json
import os
import pii_sample

OUTPUT_PATH = "pii.html"


CSS = """
:root {
  --bg:#FAFBFD; --ink:#16162A; --indigo:#2E357E; --indigo-soft:#6169B8;
  --marigold:#E0982B; --teal:#147D74; --rose:#B5476B; --line:#E3E4EE;
  --muted:#656579; --panel:#F1F2F8;
}
*, *::before, *::after { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--ink);
  font-family:"Inter",system-ui,sans-serif; font-size:15px; line-height:1.6; -webkit-font-smoothing:antialiased; }
a { color:var(--indigo); text-decoration:none; } a:hover { text-decoration:underline; }
.nav { position:sticky; top:0; z-index:50; background:rgba(250,251,253,.96); border-bottom:1px solid var(--line); }
.nav-in { max-width:1280px; margin:0 auto; padding:10px 24px; display:flex; align-items:center; gap:16px; flex-wrap:wrap; }
.brand { font-family:"Spectral",serif; font-weight:700; color:var(--indigo); font-size:16px; margin-right:auto; }
.nav a { font-family:"IBM Plex Mono",monospace; font-size:11px; letter-spacing:.03em; color:var(--muted);
  padding:3px 2px; border-bottom:2px solid transparent; }
.nav a:hover { color:var(--ink); text-decoration:none; }
.nav a.active { color:var(--indigo); border-bottom-color:var(--marigold); }
.wrap { max-width:1280px; margin:0 auto; padding:0 24px 80px; }
.phead { padding:34px 0 12px; border-bottom:2px solid var(--ink); }
.phead h1 { font-family:"Spectral",serif; font-weight:700; font-size:clamp(24px,3.6vw,38px); margin:8px 0 6px; }
.phead .dek { font-size:13px; color:#33334a; margin:0; max-width:82ch; }
.note { font-size:12px; color:var(--muted); margin-top:8px; max-width:82ch; }
.warn { margin:12px 0 0; padding:9px 13px; background:#fdf3e3; border:1px solid #f0dcb8; border-radius:9px;
  font-size:12px; color:#7a4d10; }

.explainer { margin:16px 0 0; border:1px solid var(--line); border-radius:12px; background:#fff; overflow:hidden; }
.explainer > summary, .more > summary { cursor:pointer; list-style:none; padding:12px 16px; font-weight:600;
  font-size:13.5px; color:var(--indigo); background:var(--panel); display:flex; align-items:center; gap:8px; }
.explainer > summary::-webkit-details-marker, .more > summary::-webkit-details-marker { display:none; }
.explainer > summary::before, .more > summary::before { content:"\\25B8"; font-size:11px; transition:transform .15s; color:var(--marigold); }
.explainer[open] > summary::before, .more[open] > summary::before { transform:rotate(90deg); }
.explainer-bd { padding:14px 18px; font-size:13.5px; color:#33334a; line-height:1.7; }
.explainer-bd .lead { margin:0 0 12px; } .explainer-bd b { color:var(--ink); }
.verdict-key { display:flex; flex-direction:column; gap:6px; margin:10px 0 4px; }
.vk-row { display:flex; align-items:center; gap:10px; font-size:13px; }
.vk-badge { font-weight:700; font-size:11px; padding:2px 9px; border-radius:6px; min-width:150px; text-align:center; }
.more { margin-top:13px; border:1px solid var(--line); border-radius:12px; background:#fff; overflow:hidden; }
.more > summary { color:var(--muted); background:#fff; }
.more[open] > summary { border-bottom:1px solid var(--line); }
.more-bd { padding:15px; }

.strict { margin:16px 0 0; border:1px solid var(--line); border-radius:12px; background:#fff; padding:16px 18px; }
.strict-top { display:flex; align-items:baseline; gap:12px; flex-wrap:wrap; }
.strict-top .lbl { font-family:"IBM Plex Mono",monospace; font-size:10px; letter-spacing:.12em; text-transform:uppercase; color:var(--muted); font-weight:600; }
.strict-name { font-family:"IBM Plex Mono",monospace; font-weight:700; font-size:13.5px; color:var(--indigo); }
.strict-desc { font-size:12.5px; color:var(--muted); margin-left:auto; }
.strict input[type=range] { width:100%; margin:14px 0 4px; accent-color:var(--indigo); }
.strict-ticks { display:flex; justify-content:space-between; font-family:"IBM Plex Mono",monospace; font-size:9.5px; color:var(--muted); }
.strict-ticks span { flex:1; text-align:center; }
.strict-ticks span:first-child { text-align:left; } .strict-ticks span:last-child { text-align:right; }

.art-controls { display:flex; align-items:center; gap:14px; padding:16px 0 0; flex-wrap:wrap; }
.ctrl-label { font-family:"IBM Plex Mono",monospace; font-size:10px; letter-spacing:.12em; text-transform:uppercase; color:var(--muted); font-weight:600; }
.art-nav { display:flex; align-items:center; gap:8px; }
.nav-btn { font-family:"IBM Plex Mono",monospace; font-size:14px; border:1px solid var(--line); border-radius:7px; padding:5px 13px; background:#fff; color:var(--indigo); cursor:pointer; }
.nav-btn:hover { background:var(--panel); } .nav-btn:disabled { color:var(--muted); cursor:default; }
.art-counter { font-family:"IBM Plex Mono",monospace; font-size:12px; color:var(--muted); min-width:68px; text-align:center; }
.art-select { font-family:"Inter",sans-serif; font-size:13px; padding:5px 10px; border:1px solid var(--line); border-radius:7px; background:#fff; max-width:360px; }

.title-bar { margin:16px 0 0; padding:12px 15px; background:#fff; border:1px solid var(--line); border-radius:10px; display:flex; align-items:baseline; gap:12px; flex-wrap:wrap; }
.title-bar .t { font-family:"Spectral",serif; font-weight:600; font-size:19px; }
.title-bar a { font-family:"IBM Plex Mono",monospace; font-size:11px; color:var(--muted); }
.chip { font-family:"IBM Plex Mono",monospace; font-size:10px; font-weight:600; letter-spacing:.04em; padding:2px 8px; border-radius:5px; }
.chip.synthetic { background:#fbeada; color:#9a5a12; } .chip.real { background:#eef6f4; color:var(--teal); }
.chip.tier { background:#eef0fb; color:var(--indigo); }
.caption { margin:12px 0 0; padding:10px 14px; border-left:3px solid var(--marigold); background:#fdf9f1; border-radius:0 8px 8px 0; font-size:13.5px; color:#5a4520; } .caption b { color:#8a5a12; }

.verdict { margin:14px 0; border:1px solid var(--line); border-radius:12px; overflow:hidden; }
.verdict-hd { padding:14px 18px 6px; display:flex; align-items:center; gap:12px; flex-wrap:wrap; }
.verdict-badge { font-weight:700; font-size:17px; padding:7px 15px; border-radius:9px; }
.v-keep { background:#eef6f4; color:var(--teal); }
.v-quar { background:#fceef2; color:var(--rose); }
.v-excl { background:var(--panel); color:var(--muted); }
.verdict-code { font-family:"IBM Plex Mono",monospace; font-size:10.5px; color:var(--muted); }
.verdict-why { padding:2px 18px 14px; font-size:14px; color:#26263c; line-height:1.55; }
.gloss { border-bottom:1px dotted currentColor; cursor:help; }

.card { border:1px solid var(--line); border-radius:12px; background:#fff; overflow:hidden; }
.card-hd { padding:9px 15px; border-bottom:1px solid var(--line); background:var(--panel); font-family:"IBM Plex Mono",monospace; font-size:10px; font-weight:600; letter-spacing:.09em; text-transform:uppercase; color:var(--indigo); }
.card-bd { padding:14px 15px; }

.tbl { width:100%; border-collapse:collapse; font-size:12.5px; }
.tbl th, .tbl td { text-align:left; padding:6px 8px; border-bottom:1px solid var(--line); }
.tbl th { font-family:"IBM Plex Mono",monospace; font-size:10px; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); }
.tbl code { background:var(--panel); padding:1px 6px; border-radius:4px; font-size:11px; }
.pill { font-family:"IBM Plex Mono",monospace; font-size:10px; font-weight:600; padding:1px 7px; border-radius:5px; }
.act-mask { background:#fdf3e3; color:#9a5a12; } .act-remove { background:#fceef2; color:var(--rose); }
.act-pseudo { background:#eef0fb; color:var(--indigo); } .act-keep { background:#eef6f4; color:var(--teal); }
.empty { font-size:13px; color:var(--teal); }

.panels { display:grid; grid-template-columns:1fr 1fr; gap:13px; margin-top:13px; }
@media (max-width:860px){ .panels { grid-template-columns:1fr; } }
.panel-body { padding:14px; background:#fff; min-height:150px; max-height:320px; overflow-y:auto; font-size:13px;
  line-height:1.85; white-space:pre-wrap; word-break:break-word; }
.ph { padding:8px 14px; border-bottom:1px solid var(--line); background:var(--panel); font-family:"IBM Plex Mono",monospace; font-size:10px; font-weight:600; letter-spacing:.09em; text-transform:uppercase; }
.ph.raw { color:var(--muted); } .ph.out { color:var(--indigo); }
.hl { border-radius:3px; padding:0 2px; }
.t-secret,.t-strong_id,.t-sensitive { background:#fceef2; color:#8a1a3a; }
.t-contact { background:#fdf3e3; color:#8a5a12; }
.t-online_id,.t-person_private { background:#eef0fb; color:var(--indigo); }
.t-person_public,.t-org_loc { background:#eef6f4; color:var(--teal); }
.ph-out { background:#eef0fb; color:var(--indigo); border-radius:3px; padding:0 3px; font-family:"IBM Plex Mono",monospace; font-size:11px; }
.blocked { padding:20px; text-align:center; color:var(--rose); font-size:13.5px; }

.acct-grid { display:grid; grid-template-columns:1fr 1fr; gap:13px; }
@media (max-width:860px){ .acct-grid { grid-template-columns:1fr; } }
.acct-row { display:flex; align-items:center; gap:10px; font-size:13px; padding:5px 0; border-bottom:1px dashed var(--line); }
.acct-row:last-child { border-bottom:none; }
.acct-k { flex:1; } .acct-v { font-family:"IBM Plex Mono",monospace; font-weight:600; color:var(--indigo); }
.acct-bar { height:10px; border-radius:5px; }
.sweep { width:100%; border-collapse:collapse; font-size:12px; margin-top:6px; }
.sweep th, .sweep td { padding:5px 6px; text-align:center; border-bottom:1px solid var(--line); font-family:"IBM Plex Mono",monospace; }
.sweep th:first-child, .sweep td:first-child { text-align:left; }
.sweep tr.here { background:#f5f6fd; }
.trunc-note { font-family:"IBM Plex Mono",monospace; font-size:10.5px; color:var(--muted); margin-top:12px; padding-top:9px; border-top:1px dashed var(--line); }
"""


JS = r"""
var RAW = JSON.parse(document.getElementById('articles-data').textContent);
var state = { idx:0, policy:2 };

var HI_NAMES = ['राहुल','प्रिया','अमित','सुनीता','रवि','वर्मा','शर्मा'];
var PUBLIC_MARKERS = ['प्रधानमंत्री','राष्ट्रपति','मुख्यमंत्री','मंत्री','नेता','सांसद','अभिनेता','डॉ','President','Minister'];
var SENSITIVE = ['कैंसर','एचआईवी','एड्स','बीमारी','गर्भवती','cancer','HIV','AIDS'];
var ORG_LOC = ['गूगल','Google','भारत','दिल्ली','मुंबई','बेंगलुरु','कंपनी','कार्यालय'];

function esc(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function escAttr(s){ return esc(s).replace(/"/g,'&quot;'); }
function reEsc(s){ return s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'); }

function luhn(num){ var s=0, alt=false; for (var i=num.length-1;i>=0;i--){ var n=+num[i];
  if (isNaN(n)) return false; if (alt){ n*=2; if (n>9) n-=9; } s+=n; alt=!alt; } return s%10===0; }

/* ---------- offset-based detection (mirror of the verified Python) ---------- */
function detect(text){
  var spans=[], occ=new Array(text.length).fill(false);
  function free(a,b){ for (var i=a;i<b;i++) if (occ[i]) return false; return true; }
  function claim(a,b){ for (var i=a;i<b;i++) occ[i]=true; }
  function run(re, tier, ph, validator){
    var m; re.lastIndex=0;
    while ((m=re.exec(text))!==null){ var a=m.index, b=a+m[0].length;
      if (b===a){ re.lastIndex++; continue; }
      if (free(a,b) && (!validator || validator(m[0]))){ claim(a,b); spans.push({start:a,end:b,tier:tier,ph:ph}); } }
  }
  run(/-----BEGIN[ A-Z]*PRIVATE KEY-----/g,'secret','<SECRET>');
  run(/\bAKIA[0-9A-Z]{16}\b/g,'secret','<SECRET>');
  run(/(?:password|passwd|pwd|api[_-]?key|secret|token)\s*[=:]\s*['"]?[^\s'"]{6,}/gi,'secret','<SECRET>');
  run(/(?:\d[ -]?){13,19}/g,'strong_id','<CARD>', function(v){ var d=v.replace(/\D/g,''); return d.length>=13 && d.length<=19 && luhn(d); });
  run(/\b\d{4}[ -]?\d{4}[ -]?\d{4}\b/g,'strong_id','<AADHAAR>');
  run(/\b[A-Z]{5}\d{4}[A-Z]\b/g,'strong_id','<PAN>');
  run(/[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g,'contact','<EMAIL>');
  run(/[A-Za-z0-9._%+-]+\s*\[?\(?at\)?\]?\s*[A-Za-z0-9.-]+\s*\[?\(?dot\)?\]?\s*[A-Za-z]{2,}/gi,'contact','<EMAIL>');
  run(/\b(?:\d{1,3}\.){3}\d{1,3}\b/g,'contact','<IP_ADDRESS>', function(v){ return v.split('.').every(function(x){ return +x<=255; }); });
  run(/(?:\+91[ -]?)?[6-9]\d{4}[ -]?\d{5}\b/g,'contact','<PHONE>');
  run(/github\.com\/[A-Za-z0-9_-]+/g,'online_id','<USERNAME>');
  run(/(?:^|\s)u\/[A-Za-z0-9_-]+/g,'online_id','<USERNAME>');
  run(/(?:^|\s)@[A-Za-z0-9_]{2,}/g,'online_id','<USERNAME>');
  for (var n=0;n<HI_NAMES.length;n++){ var reN=new RegExp(reEsc(HI_NAMES[n]),'g'), m;
    while ((m=reN.exec(text))!==null){ var a=m.index,b=a+m[0].length; if (!free(a,b)) continue;
      var before=text.slice(Math.max(0,a-20),a);
      var pub=PUBLIC_MARKERS.some(function(mk){ return before.indexOf(mk)!==-1; });
      claim(a,b); spans.push({start:a,end:b,tier:pub?'person_public':'person_private',ph:'<PERSON>'}); } }
  [['sensitive',SENSITIVE,'<SENSITIVE>'],['org_loc',ORG_LOC,'<ORG_LOC>']].forEach(function(pair){
    pair[1].forEach(function(w){ var reW=new RegExp(reEsc(w),'g'), m;
      while ((m=reW.exec(text))!==null){ var a=m.index,b=a+m[0].length; if (!free(a,b)) continue;
        claim(a,b); spans.push({start:a,end:b,tier:pair[0],ph:pair[2]}); } }); });
  spans.sort(function(x,y){ return x.start-y.start; });
  return spans;
}

function flagsOf(spans){
  var t={}; spans.forEach(function(s){ t[s.tier]=(t[s.tier]||0)+1; });
  return { secret:!!t.secret, contact:t.contact||0, strong:t.strong_id||0,
           direct:(t.contact||0)+(t.strong_id||0),
           sensitiveLinked:!!t.sensitive && !!t.person_private, t:t };
}
function routeDoc(spans, policy){
  var f=flagsOf(spans);
  if (f.secret) return 'QUARANTINE_DOCUMENT';
  if (policy>=1 && f.direct>=6) return 'EXCLUDE_DOCUMENT';
  if (policy===2 && (f.sensitiveLinked || f.strong>=2)) return 'QUARANTINE_DOCUMENT';
  if (policy===3 && (f.sensitiveLinked || f.strong>=1 || f.direct>=3)) return 'QUARANTINE_DOCUMENT';
  if (policy===4 && (f.sensitiveLinked || f.strong>=1 || f.contact>=1)) return 'QUARANTINE_DOCUMENT';
  return 'KEEP_SCRUBBED';
}
function actionFor(tier, policy){
  if (tier==='secret') return 'REMOVE';
  if (tier==='strong_id'||tier==='contact') return 'MASK';
  if (tier==='online_id') return policy===0?'KEEP':'PSEUDONYMIZE';
  if (tier==='person_private') return policy===0?'KEEP':'MASK';
  if (tier==='person_public') return policy<=2?'KEEP':'MASK';
  if (tier==='sensitive') return policy<=1?'KEEP':'REMOVE';
  return 'KEEP';   /* org_loc */
}

var POLICIES = {
  0:{name:'STRUCTURED_ONLY', desc:'Redact only structured identifiers & secrets; leave all names.'},
  1:{name:'PUBLIC_ATTRIBUTION_PRESERVING', desc:'Keep public figures, mask private names; exclude personal-record dumps.'},
  2:{name:'MULTILINGUAL_BALANCED', desc:'The balanced default: also quarantine strong-ID and sensitive-attribute docs.'},
  3:{name:'PRIVATE_SOURCE_AGGRESSIVE', desc:'Treat sources as private: pseudonymize even public names; quarantine sooner.'},
  4:{name:'HIGH_RISK_QUARANTINE', desc:'Quarantine any document with a strong ID, contact detail or sensitive attribute.'}
};
var TIER_LABEL = { secret:'Critical secret', strong_id:'Strong identifier', contact:'Direct contact',
  online_id:'Online handle', person_private:'Private person', person_public:'Public figure',
  sensitive:'Sensitive attribute', org_loc:'Org / place' };
var GLOSS = {
  secret:'API key, password or private key — account/system compromise. Quarantines the whole document.',
  strong_id:'Card / Aadhaar / PAN — a single valid one can identify a person, so it is redacted.',
  contact:'Email, phone or IP — direct contact info, masked with a typed placeholder.',
  online_id:'A username/handle — pseudonymized to break cross-site linkage.',
  person_private:'An ordinary private individual’s name.',
  person_public:'A public / attributed figure — kept for provenance in curated/news sources.',
  sensitive:'A sensitive attribute (e.g. health) tied to a person — quarantined.',
  org_loc:'A company or place — not a natural person, so it is kept (avoids over-redaction).',
  KEEP_SCRUBBED:'The document is kept after replacing PII spans with typed placeholders.',
  QUARANTINE_DOCUMENT:'Set aside for governed handling — a secret, sensitive attribute, or too many strong IDs.',
  EXCLUDE_DOCUMENT:'Dropped — it is primarily a personal-record dump (many contact identifiers).',
  masked:'The raw value is never shown. This is the typed placeholder that replaces it.'
};
function glossOf(c){ return GLOSS[c]||c; }
function pct(x){ return Math.round(x*100)+'%'; }

var VBADGE = { KEEP_SCRUBBED:{e:'✅',w:'KEEP (scrubbed)',c:'v-keep'},
  QUARANTINE_DOCUMENT:{e:'🔴',w:'QUARANTINE',c:'v-quar'},
  EXCLUDE_DOCUMENT:{e:'⬜',w:'EXCLUDE',c:'v-excl'} };

/* build the redacted output (only meaningful when KEEP_SCRUBBED) */
function redact(text, spans, policy){
  var out='', pos=0, pcount=0, ucount=0, persons={}, users={};
  spans.forEach(function(s){
    out += esc(text.slice(pos, s.start));
    var act = actionFor(s.tier, policy);
    if (act==='KEEP'){ out += esc(text.slice(s.start, s.end)); }
    else {
      var ph = s.ph;
      if (s.tier==='person_private'||s.tier==='person_public'){ var key=text.slice(s.start,s.end);
        if (!persons[key]) persons[key]='<PERSON_'+(++pcount)+'>'; ph=persons[key]; }
      else if (s.tier==='online_id'){ var k2=text.slice(s.start,s.end);
        if (!users[k2]) users[k2]='<USERNAME_'+(++ucount)+'>'; ph=users[k2]; }
      out += '<span class="ph-out">'+esc(ph)+'</span>';
    }
    pos = s.end;
  });
  out += esc(text.slice(pos));
  return out;
}
function highlightInput(text, spans){
  var out='', pos=0;
  spans.forEach(function(s){ out += esc(text.slice(pos,s.start));
    out += '<span class="hl t-'+s.tier+'" title="'+escAttr(TIER_LABEL[s.tier]||s.tier)+'">'+esc(text.slice(s.start,s.end))+'</span>';
    pos=s.end; });
  out += esc(text.slice(pos)); return out;
}

/* ---------- render ---------- */
function render(){
  var art=RAW[state.idx], spans=detect(art.text), disp=routeDoc(spans, state.policy);

  document.getElementById('art-title').textContent=art.title;
  var kindEl=document.getElementById('art-kind'); kindEl.textContent=art.kind==='synthetic'?'SYNTHETIC':'REAL — Wikipedia';
  kindEl.className='chip '+(art.kind==='synthetic'?'synthetic':'real');
  var tierEl=document.getElementById('art-tier'); tierEl.textContent='source: '+art.source_tier; tierEl.className='chip tier';
  var urlEl=document.getElementById('art-url'); urlEl.href=art.url; urlEl.style.display=art.kind==='synthetic'?'none':'';
  document.getElementById('art-counter').textContent=(state.idx+1)+' of '+RAW.length;
  document.getElementById('prev-btn').disabled=state.idx===0;
  document.getElementById('next-btn').disabled=state.idx===RAW.length-1;
  document.getElementById('art-select').value=state.idx;
  var capEl=document.getElementById('caption');
  if (art.caption){ capEl.innerHTML='<b>What this example shows:</b> '+esc(art.caption); capEl.style.display=''; }
  else capEl.style.display='none';

  var vb=VBADGE[disp]; var badge=document.getElementById('verdict-badge');
  badge.className='verdict-badge '+vb.c; badge.textContent=vb.e+' '+vb.w;
  var codeEl=document.getElementById('verdict-code'); codeEl.textContent=disp; codeEl.title=glossOf(disp);
  document.getElementById('verdict-sub').textContent = whyText(disp, spans, art);

  /* detection table (NEVER raw values) */
  var host=document.getElementById('pii-table');
  if (!spans.length){ host.innerHTML='<div class="empty">✓ No PII detected — nothing to redact.</div>'; }
  else {
    var rows='<table class="tbl"><tr><th>entity</th><th>risk tier</th><th>action</th><th>replaced with</th></tr>';
    for (var i=0;i<spans.length;i++){ var s=spans[i], act=actionFor(s.tier, state.policy);
      var actCls={MASK:'act-mask',REMOVE:'act-remove',PSEUDONYMIZE:'act-pseudo',KEEP:'act-keep'}[act];
      rows += '<tr><td><span class="gloss" title="'+escAttr(glossOf(s.tier))+'">'+(TIER_LABEL[s.tier]||s.tier)+'</span></td>'+
        '<td>'+s.tier+'</td>'+
        '<td><span class="pill '+actCls+'">'+act+'</span></td>'+
        '<td>'+(act==='KEEP'?'<span style="color:#999">kept</span>':'<code>'+esc(s.ph)+'</code>')+'</td></tr>'; }
    rows += '</table>';
    host.innerHTML=rows;
  }

  /* before / after */
  document.getElementById('panel-raw').innerHTML=highlightInput(art.text, spans);
  var outHost=document.getElementById('panel-out');
  if (disp==='KEEP_SCRUBBED'){ outHost.innerHTML=redact(art.text, spans, state.policy); }
  else { var msg=disp==='QUARANTINE_DOCUMENT'
      ? 'Document QUARANTINED — held for governed handling; not emitted to training as-is.'
      : 'Document EXCLUDED — primarily a personal record; dropped from the corpus.';
    outHost.innerHTML='<div class="blocked">'+msg+'</div>'; }

  /* residual re-scan of the output */
  var residual=0;
  if (disp==='KEEP_SCRUBBED'){ var tmp=document.createElement('div'); tmp.innerHTML=redact(art.text,spans,state.policy);
    residual=detect(tmp.textContent).filter(function(s){ return s.tier!=='org_loc' && actionFor(s.tier,state.policy)!=='KEEP'; }).length; }
  var f=flagsOf(spans);
  document.getElementById('mech').innerHTML =
    '<div class="acct-row"><span class="acct-k">PII spans detected</span><span class="acct-v">'+spans.length+'</span></div>'+
    '<div class="acct-row"><span class="acct-k">Direct identifiers (contact + strong)</span><span class="acct-v">'+f.direct+'</span></div>'+
    '<div class="acct-row"><span class="acct-k">Critical secrets</span><span class="acct-v">'+(f.t.secret||0)+'</span></div>'+
    '<div class="acct-row"><span class="acct-k">Residual PII after redaction (independent re-scan)</span><span class="acct-v">'+(disp==='KEEP_SCRUBBED'?residual+(residual===0?' ✓':''):'n/a')+'</span></div>';

  accounting();
}

function whyText(disp, spans, art){
  var f=flagsOf(spans);
  if (disp==='QUARANTINE_DOCUMENT'){
    if (f.secret) return 'Contains a critical secret (API key / password) — the whole document is quarantined; the value is never emitted.';
    if (f.sensitiveLinked) return 'A sensitive attribute (e.g. health) is tied to a private person — quarantined for governed handling.';
    return 'Carries strong government/financial identifiers — quarantined at this policy rather than lightly masked.';
  }
  if (disp==='EXCLUDE_DOCUMENT') return 'Mostly a list of people with their contact details ('+f.direct+' direct identifiers) — a personal-record dump, so it is dropped entirely.';
  if (!spans.length) return 'No personal data found — kept unchanged.';
  var acted=spans.filter(function(s){ return actionFor(s.tier,state.policy)!=='KEEP'; }).length;
  if (!acted) return 'The only entities here are public figures / organisations / places — kept as-is, nothing to redact at this policy.';
  return acted+' PII span(s) replaced with typed placeholders; the document keeps its meaning and is accepted.';
}

/* ---------- corpus accounting ---------- */
var DCOLOR={ KEEP_SCRUBBED:'#147D74', QUARANTINE_DOCUMENT:'#B5476B', EXCLUDE_DOCUMENT:'#656579' };
function countsAt(p){ var c={}; for (var i=0;i<RAW.length;i++){ var d=routeDoc(detect(RAW[i].text),p); c[d]=(c[d]||0)+1; } return c; }
function entityCounts(){ var c={}; for (var i=0;i<RAW.length;i++){ detect(RAW[i].text).forEach(function(s){ c[s.tier]=(c[s.tier]||0)+1; }); } return c; }

function accounting(){
  var total=RAW.length, c=countsAt(state.policy);
  var order=Object.keys(c).sort(function(a,b){ return c[b]-c[a]; }), rows='';
  for (var i=0;i<order.length;i++){ var k=order[i], n=c[k], w=(n/total)*100, vb=VBADGE[k]||{e:'',w:k};
    rows+='<div class="acct-row"><span class="acct-k">'+vb.e+' '+vb.w+' <span style="color:#999;font-size:11px">'+k+'</span></span>'+
      '<span style="width:120px"><span class="acct-bar" style="display:block;width:'+w+'%;background:'+(DCOLOR[k]||'#6169B8')+'"></span></span>'+
      '<span class="acct-v">'+n+'</span></div>'; }
  document.getElementById('acct-disp').innerHTML=rows;

  var ec=entityCounts(), ek=Object.keys(ec).sort(function(a,b){ return ec[b]-ec[a]; }), erows='';
  for (var j=0;j<ek.length;j++){ erows+='<div class="acct-row"><span class="acct-k">'+(TIER_LABEL[ek[j]]||ek[j])+'</span><span class="acct-v">'+ec[ek[j]]+'</span></div>'; }
  document.getElementById('acct-entities').innerHTML=erows;

  var sw='<table class="sweep"><tr><th>policy</th><th>keep</th><th>quar</th><th>excl</th></tr>';
  for (var p=0;p<5;p++){ var cc=countsAt(p);
    sw+='<tr'+(p===state.policy?' class="here"':'')+'><td>'+p+' '+POLICIES[p].name+'</td><td>'+(cc.KEEP_SCRUBBED||0)+'</td><td>'+(cc.QUARANTINE_DOCUMENT||0)+'</td><td>'+(cc.EXCLUDE_DOCUMENT||0)+'</td></tr>'; }
  sw+='</table>'; document.getElementById('sweep').innerHTML=sw;
}

/* ---------- wiring ---------- */
var sel=document.getElementById('art-select');
for (var i=0;i<RAW.length;i++){ var o=document.createElement('option'); o.value=i; o.textContent=(i+1)+'. '+RAW[i].title; sel.appendChild(o); }
sel.addEventListener('change', function(){ state.idx=parseInt(this.value,10); render(); });
document.getElementById('prev-btn').addEventListener('click', function(){ if (state.idx>0){ state.idx--; render(); } });
document.getElementById('next-btn').addEventListener('click', function(){ if (state.idx<RAW.length-1){ state.idx++; render(); } });
document.addEventListener('keydown', function(e){ if (e.key==='ArrowLeft'&&state.idx>0){ state.idx--; render(); } if (e.key==='ArrowRight'&&state.idx<RAW.length-1){ state.idx++; render(); } });
var slider=document.getElementById('strict-slider');
function updatePolicy(){ state.policy=parseInt(slider.value,10);
  document.getElementById('strict-name').textContent=state.policy+' · '+POLICIES[state.policy].name;
  document.getElementById('strict-desc').textContent=POLICIES[state.policy].desc; render(); }
slider.addEventListener('input', updatePolicy);
updatePolicy();
"""


def build_html(articles):
    data_json = json.dumps(articles, ensure_ascii=False)
    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>PII &amp; Redaction — India-First 40B</title>\n'
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
        '  <a href=\"pii.html\" class=\"active\">PII</a>\n'
        '  <a href=\"decontam.html\">Decontam</a>\n'
        '  <a href=\"tokenizer.html\">Tokenizer</a>\n'
        '  <a href=\"manifest.html\">Manifest</a>\n'
        '  <a href=\"v5_brief.html\">V5 Plan</a>\n'
        '  <a href=\"v5_playbook.html\">V5 Plan — Proposal</a>\n'
        '  <a href=\"assignment.html\">Assignment</a>\n'
        '</div></div>\n'
        '<div class="wrap">\n'
        '  <div class="phead">\n'
        '    <h1>PII &amp; Redaction</h1>\n'
        '    <p class="dek">Per <em>PII.md</em>: find personal data, decide from <b>entity type + context + source</b>, '
        'replace only the necessary spans with typed placeholders, and route the document — without erasing public '
        'attribution, organisations or places.</p>\n'
        '    <div class="warn">⚠️ Every identifier on this page is <b>synthetic / fake</b> (example.com, standard test '
        'card, invented Aadhaar/PAN/keys). A real run <b>never displays raw PII</b> — note the detection table below '
        'shows only typed placeholders, never the value.</div>\n'
        '  </div>\n'
        '  <details class="explainer" open>\n'
        '    <summary>How to read this page</summary>\n'
        '    <div class="explainer-bd">\n'
        '      <p class="lead">Each document is scanned for personal data. Every hit gets a <b>risk tier</b> and an '
        '<b>action</b> (mask / pseudonymize / keep), then the whole document is routed:</p>\n'
        '      <div class="verdict-key">\n'
        '        <div class="vk-row"><span class="vk-badge v-keep">✅ KEEP (scrubbed)</span><span>PII replaced with placeholders; the text is kept.</span></div>\n'
        '        <div class="vk-row"><span class="vk-badge v-quar">🔴 QUARANTINE</span><span>A secret, a sensitive attribute, or strong IDs — held for governed handling.</span></div>\n'
        '        <div class="vk-row"><span class="vk-badge v-excl">⬜ EXCLUDE</span><span>Primarily a personal-record dump — dropped entirely.</span></div>\n'
        '      </div>\n'
        '      <p class="note" style="margin-top:12px">The decision depends on the <b>source</b> (a public figure is kept '
        'in the news but pseudonymized on a forum) and on the <b>policy</b>. The slider selects a named policy bundle '
        '(from <em>policy-and-thresholds.md</em>) from least to most aggressive. Full multilingual NER and quasi-'
        'identifier linkage are a documented offline tier. Hover any underlined term.</p>\n'
        '    </div>\n'
        '  </details>\n'
        '  <div class="strict">\n'
        '    <div class="strict-top">\n'
        '      <span class="lbl">Policy</span>\n'
        '      <span class="strict-name" id="strict-name"></span>\n'
        '      <span class="strict-desc" id="strict-desc"></span>\n'
        '    </div>\n'
        '    <input type="range" min="0" max="4" step="1" value="2" id="strict-slider">\n'
        '    <div class="strict-ticks"><span>0 structured</span><span>1 attribution</span><span>2 balanced</span>'
        '<span>3 aggressive</span><span>4 high-risk</span></div>\n'
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
        '    <span class="chip tier" id="art-tier"></span>\n'
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
        '    <div class="card-hd">Detected PII — typed placeholders only, never the raw value</div>\n'
        '    <div class="card-bd"><div id="pii-table"></div></div>\n'
        '  </div>\n'
        '  <div class="panels">\n'
        '    <div class="card"><div class="ph raw">Input (synthetic) — detected spans highlighted</div><div class="panel-body" id="panel-raw"></div></div>\n'
        '    <div class="card"><div class="ph out">Output — redacted / routed</div><div class="panel-body" id="panel-out"></div></div>\n'
        '  </div>\n'
        '  <details class="more">\n'
        '    <summary>Show metrics &amp; independent re-scan</summary>\n'
        '    <div class="more-bd"><div id="mech"></div></div>\n'
        '  </details>\n'
        '  <details class="more">\n'
        '    <summary>Show corpus accounting across all ' + str(len(articles)) + ' documents</summary>\n'
        '    <div class="more-bd">\n'
        '      <div class="acct-grid">\n'
        '        <div class="card"><div class="card-hd">Document routing at current policy</div><div class="card-bd" id="acct-disp"></div></div>\n'
        '        <div class="card"><div class="card-hd">Entities detected (whole corpus)</div><div class="card-bd" id="acct-entities"></div></div>\n'
        '      </div>\n'
        '      <div class="card" style="margin-top:13px"><div class="card-hd">Routing across every policy</div><div class="card-bd" id="sweep"></div></div>\n'
        '    </div>\n'
        '  </details>\n'
        '</div>\n'
        '<script>' + JS + '</script>\n'
        '</body>\n</html>\n'
    )


if __name__ == "__main__":
    print("Building PII corpus (synthetic identifiers only)...")
    articles = pii_sample.build_sample()
    print("Generating {}...".format(OUTPUT_PATH))
    html = build_html(articles)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    n_syn = sum(1 for a in articles if a["kind"] == "synthetic")
    print("\nDone. {} written ({} docs: {} synthetic + {} real).".format(
        OUTPUT_PATH, len(articles), n_syn, len(articles) - n_syn))
