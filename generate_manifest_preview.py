"""
Generate manifest.html — the Build-Manifest capstone.

Follows Open-Build-Manifest.md: a per-shard system-of-record that imports the
seven pipeline stages' results, records real SHA-256 content/recipe/manifest
digests, checks admission gates, and routes ADMIT / REVIEW / QUARANTINE /
BLOCK. Gate policy (how strictly to treat unverified / unknown evidence) is a
slider. SHA-256 is a genuine implementation, verified byte-for-byte against
Python hashlib and re-checked in Node.

Run: python3 generate_manifest_preview.py
"""

import json
import manifest_sample as M

OUTPUT_PATH = "manifest.html"


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
.note { font-size:12px; color:var(--muted); margin-top:8px; max-width:82ch; }
.explainer { margin:16px 0 0; border:1px solid var(--line); border-radius:12px; background:#fff; overflow:hidden; }
.explainer > summary, .more > summary { cursor:pointer; list-style:none; padding:12px 16px; font-weight:600; font-size:13.5px; color:var(--indigo); background:var(--panel); display:flex; align-items:center; gap:8px; }
.explainer > summary::-webkit-details-marker, .more > summary::-webkit-details-marker { display:none; }
.explainer > summary::before, .more > summary::before { content:"\\25B8"; font-size:11px; transition:transform .15s; color:var(--marigold); }
.explainer[open] > summary::before, .more[open] > summary::before { transform:rotate(90deg); }
.explainer-bd { padding:14px 18px; font-size:13.5px; color:#33334a; line-height:1.7; }
.explainer-bd .lead { margin:0 0 10px; } .explainer-bd b { color:var(--ink); }
.verdict-key { display:flex; flex-direction:column; gap:6px; margin:10px 0 4px; }
.vk-row { display:flex; align-items:center; gap:10px; font-size:13px; }
.vk-badge { font-weight:700; font-size:11px; padding:2px 9px; border-radius:6px; min-width:130px; text-align:center; }
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
.title-bar .t { font-family:"IBM Plex Mono",monospace; font-weight:600; font-size:16px; }
.chip { font-family:"IBM Plex Mono",monospace; font-size:10px; font-weight:600; letter-spacing:.04em; padding:2px 8px; border-radius:5px; background:#eef0fb; color:var(--indigo); }
.caption { margin:12px 0 0; padding:10px 14px; border-left:3px solid var(--marigold); background:#fdf9f1; border-radius:0 8px 8px 0; font-size:13.5px; color:#5a4520; } .caption b { color:#8a5a12; }

.verdict { margin:14px 0; border:1px solid var(--line); border-radius:12px; overflow:hidden; }
.verdict-hd { padding:14px 18px 14px; display:flex; align-items:center; gap:12px; flex-wrap:wrap; }
.verdict-badge { font-weight:700; font-size:17px; padding:7px 15px; border-radius:9px; }
.v-admit { background:#eef6f4; color:var(--teal); }
.v-review { background:#fdf3e3; color:#9a5a12; }
.v-quar { background:#fceef2; color:var(--rose); }
.v-block { background:#f7e9ec; color:#8a1a3a; }
.v-report { background:var(--panel); color:var(--muted); }
.verdict-why { font-size:13.5px; color:#26263c; }
.gloss { border-bottom:1px dotted currentColor; cursor:help; }

.grid2 { display:grid; grid-template-columns:1fr 1fr; gap:13px; }
@media (max-width:860px){ .grid2 { grid-template-columns:1fr; } }
.card { border:1px solid var(--line); border-radius:12px; background:#fff; overflow:hidden; }
.card-hd { padding:9px 15px; border-bottom:1px solid var(--line); background:var(--panel); font-family:"IBM Plex Mono",monospace; font-size:10px; font-weight:600; letter-spacing:.09em; text-transform:uppercase; color:var(--indigo); }
.card-bd { padding:14px 15px; }
.kv { font-size:12.5px; margin:4px 0; display:flex; gap:8px; }
.kv .k { color:var(--muted); min-width:120px; } .kv .v { font-family:"IBM Plex Mono",monospace; word-break:break-all; }
.tbl { width:100%; border-collapse:collapse; font-size:12.5px; }
.tbl th, .tbl td { text-align:left; padding:5px 8px; border-bottom:1px solid var(--line); }
.tbl th { font-family:"IBM Plex Mono",monospace; font-size:10px; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); }
.tbl td code { font-family:"IBM Plex Mono",monospace; font-size:11px; color:var(--muted); }
.st { font-family:"IBM Plex Mono",monospace; font-size:10px; font-weight:600; padding:1px 6px; border-radius:4px; }
.st-pass { background:#eef6f4; color:var(--teal); } .st-notrun { background:var(--panel); color:var(--muted); }
.st-ver { background:#eef6f4; color:var(--teal); } .st-unver { background:#fdf3e3; color:#9a5a12; } .st-na { color:#bbb; }
.gate { display:flex; align-items:center; gap:9px; font-size:13px; padding:5px 0; border-bottom:1px dashed var(--line); }
.gate:last-child { border-bottom:none; }
.gate .ic { width:18px; text-align:center; } .gate .ok { color:var(--teal); } .gate .bad { color:var(--rose); }
.langbar { display:flex; height:16px; border-radius:5px; overflow:hidden; border:1px solid var(--line); margin-top:4px; }
.acct-row { display:flex; align-items:center; gap:10px; font-size:13px; padding:5px 0; border-bottom:1px dashed var(--line); }
.acct-row:last-child { border-bottom:none; }
.acct-k { flex:1; } .acct-v { font-family:"IBM Plex Mono",monospace; font-weight:600; color:var(--indigo); }
.acct-bar { height:10px; border-radius:5px; }
.sweep { width:100%; border-collapse:collapse; font-size:12px; margin-top:6px; }
.sweep th, .sweep td { padding:5px 6px; text-align:center; border-bottom:1px solid var(--line); font-family:"IBM Plex Mono",monospace; }
.sweep th:first-child, .sweep td:first-child { text-align:left; } .sweep tr.here { background:#f5f6fd; }
"""


JS = r"""
var RAW = JSON.parse(document.getElementById('articles-data').textContent);
var STAGES = ['normalization','language','quality','dedup','pii','decontam','tokenizer'];
var REQUIRED = ['normalization','language','quality','dedup','pii','decontam'];
var state = { idx:0, policy:2 };

/* ---------- real SHA-256 (verified against Python hashlib) ---------- */
var K256=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
function sha256hex(str){
  var enc=(typeof TextEncoder!=='undefined')?new TextEncoder():null;
  var bytes = enc ? Array.prototype.slice.call(enc.encode(str)) : (function(){var b=[];for(var i=0;i<str.length;i++)b.push(str.charCodeAt(i)&0xff);return b;})();
  var l=bytes.length, bl=l*8;
  bytes.push(0x80); while(bytes.length%64!==56) bytes.push(0);
  for(var i=7;i>=0;i--) bytes.push(Math.floor(bl/Math.pow(2,8*i))&0xff);
  var H=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
  function rotr(x,n){ return (x>>>n)|(x<<(32-n)); }
  for(var off=0;off<bytes.length;off+=64){
    var w=new Array(64);
    for(var t=0;t<16;t++) w[t]=((bytes[off+t*4]<<24)|(bytes[off+t*4+1]<<16)|(bytes[off+t*4+2]<<8)|(bytes[off+t*4+3]))|0;
    for(var t=16;t<64;t++){ var s0=rotr(w[t-15],7)^rotr(w[t-15],18)^(w[t-15]>>>3); var s1=rotr(w[t-2],17)^rotr(w[t-2],19)^(w[t-2]>>>10); w[t]=(w[t-16]+s0+w[t-7]+s1)|0; }
    var a=H[0],b=H[1],c=H[2],d=H[3],e=H[4],f=H[5],g=H[6],h=H[7];
    for(var t=0;t<64;t++){ var S1=rotr(e,6)^rotr(e,11)^rotr(e,25); var ch=(e&f)^((~e)&g); var t1=(h+S1+ch+K256[t]+w[t])|0;
      var S0=rotr(a,2)^rotr(a,13)^rotr(a,22); var maj=(a&b)^(a&c)^(b&c); var t2=(S0+maj)|0;
      h=g;g=f;f=e;e=(d+t1)|0;d=c;c=b;b=a;a=(t1+t2)|0; }
    H[0]=(H[0]+a)|0;H[1]=(H[1]+b)|0;H[2]=(H[2]+c)|0;H[3]=(H[3]+d)|0;H[4]=(H[4]+e)|0;H[5]=(H[5]+f)|0;H[6]=(H[6]+g)|0;H[7]=(H[7]+h)|0;
  }
  return H.map(function(x){ return (x>>>0).toString(16).padStart(8,'0'); }).join('');
}

function esc(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function escAttr(s){ return esc(s).replace(/"/g,'&quot;'); }

var POLICIES = {
  0:{name:'REPORT ONLY', desc:'No gate — just show the manifest and evidence, no admission decision.'},
  1:{name:'LENIENT', desc:'Block only on hard failures; trust reported passes even without versioned evidence.'},
  2:{name:'STANDARD', desc:'Hard failures block; unknown license, not-run or unverified required stages go to review.'},
  3:{name:'STRICT', desc:'Fail closed: unknown license, any not-run or unverified required stage also blocks.'}
};

function recipeStr(sh){ return JSON.stringify(STAGES.map(function(s){ return [s, sh.stages[s].status]; })); }
function coreStr(sh){ return sha256hex(sh.content)+'|'+sha256hex(recipeStr(sh))+'|'+sh.license.spdx+'|'+sh.records+'|'+sh.tokens; }

function gates(sh){
  var notrun = REQUIRED.some(function(s){ return sh.stages[s].status==='NOT_RUN'; });
  var unver = REQUIRED.some(function(s){ return sh.stages[s].verify==='UNVERIFIED'; });
  return {
    license:   { ok: sh.license.decision==='ALLOWED', label:'License resolved &amp; permits training use' },
    pii:       { ok: sh.pii_residual===0, label:'No residual critical PII' },
    eval:      { ok: !sh.eval_leak, label:'No unresolved evaluation leakage' },
    poison:    { ok: !sh.poison, label:'No suspected poisoning' },
    repro:     { ok: sh.repro==='REPRODUCED', label:'Deterministic rerun reproduced the bytes' },
    ran:       { ok: !notrun, label:'All required stages ran' },
    verified:  { ok: !unver, label:'All required stages carry versioned evidence' }
  };
}
function verdict(sh, policy){
  var g=gates(sh);
  var hardBlock = !g.pii.ok || !g.eval.ok || !g.repro.ok || sh.license.decision==='RESTRICTED';
  if (policy===0) return 'REPORT_ONLY';
  if (hardBlock) return 'BLOCK';
  if (!g.poison.ok) return 'QUARANTINE';
  var unknownLic = sh.license.decision==='UNKNOWN';
  if (policy===1){ return (unknownLic || !g.ran.ok) ? 'REVIEW' : 'ADMIT'; }
  if (policy===2){ return (unknownLic || !g.ran.ok || !g.verified.ok) ? 'REVIEW' : 'ADMIT'; }
  return (unknownLic || !g.ran.ok || !g.verified.ok) ? 'BLOCK' : 'ADMIT';   /* strict */
}

var VB = { ADMIT:{e:'✅',w:'ADMIT',c:'v-admit'}, REVIEW:{e:'🟠',w:'REVIEW',c:'v-review'},
  QUARANTINE:{e:'🔴',w:'QUARANTINE',c:'v-quar'}, BLOCK:{e:'⛔',w:'BLOCK',c:'v-block'},
  REPORT_ONLY:{e:'▫️',w:'REPORT ONLY',c:'v-report'} };
var GLOSS = {
  content:'SHA-256 of the exact emitted shard bytes. Same bytes always produce this digest; it is the shard identity.',
  recipe:'SHA-256 of the ordered processing recipe. A deterministic rerun of the same recipe must reproduce it.',
  manifest:'SHA-256 of the immutable manifest core. Any change to lineage or decisions produces a new digest.',
  verified:'The upstream stage supplied versioned evidence that was checked — not just a claimed pass.',
  spdx:'A standard machine-readable license identifier. LicenseRef-* marks custom / unknown terms.'
};
function glossOf(c){ return GLOSS[c]||c; }
function gloss(term,key){ return '<span class="gloss" title="'+escAttr(glossOf(key))+'">'+term+'</span>'; }
function fmt(n){ if(n>=1e6) return (n/1e6).toFixed(1)+'M'; if(n>=1e3) return (n/1e3).toFixed(1)+'k'; return ''+n; }

var LANG_COLOR={ hi:'#2E357E', en:'#C7761B', ta:'#147D74', und:'#B5476B', code:'#6169B8', other:'#999' };

function render(){
  var sh=RAW[state.idx], v=verdict(sh, state.policy), g=gates(sh);
  document.getElementById('art-title').textContent=sh.name;
  document.getElementById('art-id').textContent=sh.id;
  document.getElementById('art-counter').textContent=(state.idx+1)+' of '+RAW.length;
  document.getElementById('prev-btn').disabled=state.idx===0;
  document.getElementById('next-btn').disabled=state.idx===RAW.length-1;
  document.getElementById('art-select').value=state.idx;
  var capEl=document.getElementById('caption');
  capEl.innerHTML='<b>What this shard shows:</b> '+esc(sh.caption);

  var vb=VB[v]; var badge=document.getElementById('verdict-badge'); badge.className='verdict-badge '+vb.c; badge.textContent=vb.e+' '+vb.w;
  document.getElementById('verdict-sub').textContent=whyText(v, sh, g);

  /* identity */
  var cH=sha256hex(sh.content), rH=sha256hex(recipeStr(sh)), mH=sha256hex(coreStr(sh));
  document.getElementById('identity').innerHTML =
    '<div class="kv"><span class="k">shard_id</span><span class="v">'+gloss('sha256','content')+':'+cH.slice(0,32)+'…</span></div>'+
    '<div class="kv"><span class="k">recipe_sha256</span><span class="v">'+gloss(rH.slice(0,32),'recipe')+'…</span></div>'+
    '<div class="kv"><span class="k">manifest_digest</span><span class="v">'+gloss(mH.slice(0,32),'manifest')+'…</span></div>'+
    '<div class="kv"><span class="k">source</span><span class="v">'+esc(sh.snapshot)+'</span></div>'+
    '<div class="kv"><span class="k">locator</span><span class="v">'+esc(sh.locator)+'</span></div>'+
    '<div class="kv"><span class="k">license</span><span class="v">'+gloss(esc(sh.license.spdx),'spdx')+' · '+sh.license.access+' · '+sh.license.decision+'</span></div>';

  /* transformation table */
  var rows='<table class="tbl"><tr><th>#</th><th>stage</th><th>status</th><th>evidence</th><th>code/config</th></tr>';
  for (var i=0;i<STAGES.length;i++){ var s=STAGES[i], st=sh.stages[s];
    var sc = st.status==='PASS' ? 'st-pass' : 'st-notrun';
    var vc = st.verify==='VERIFIED'?'st-ver':(st.verify==='UNVERIFIED'?'st-unver':'st-na');
    rows += '<tr><td>'+(i+1)+'</td><td>'+s+'</td><td><span class="st '+sc+'">'+st.status+'</span></td>'+
      '<td><span class="st '+vc+'">'+st.verify+'</span></td><td><code>'+sha256hex(sh.id+s).slice(0,10)+'</code></td></tr>'; }
  rows+='</table>';
  document.getElementById('transforms').innerHTML=rows;

  /* composition */
  var ld=sh.langdist, bar='', leg='';
  Object.keys(ld).forEach(function(L){ var col=LANG_COLOR[L]||'#999';
    bar += '<div style="width:'+(ld[L]*100)+'%;background:'+col+'"></div>';
    leg += '<span style="font-size:11.5px;margin-right:10px"><span style="display:inline-block;width:9px;height:9px;background:'+col+';border-radius:2px"></span> '+L+' '+Math.round(ld[L]*100)+'%</span>'; });
  document.getElementById('composition').innerHTML =
    '<div class="kv"><span class="k">records</span><span class="v">'+fmt(sh.records)+'</span></div>'+
    '<div class="kv"><span class="k">tokens</span><span class="v">'+fmt(sh.tokens)+'</span></div>'+
    '<div class="kv"><span class="k">residual PII</span><span class="v">'+sh.pii_residual+'</span></div>'+
    '<div class="kv"><span class="k">determinism</span><span class="v">'+sh.repro+'</span></div>'+
    '<div style="margin-top:8px;font-size:11px;color:#888">language distribution</div><div class="langbar">'+bar+'</div><div style="margin-top:6px">'+leg+'</div>';

  /* gates */
  var order=['license','pii','eval','poison','repro','ran','verified'], gh='';
  order.forEach(function(k){ var it=g[k];
    gh += '<div class="gate"><span class="ic '+(it.ok?'ok':'bad')+'">'+(it.ok?'✓':'✗')+'</span><span>'+it.label+'</span></div>'; });
  document.getElementById('gates').innerHTML=gh;

  accounting();
}

function whyText(v, sh, g){
  if (v==='REPORT_ONLY') return 'Gate policy is REPORT-ONLY — the manifest and evidence are shown, but no admission decision is made.';
  if (v==='ADMIT') return 'Every gate passed with verified evidence — this shard is admitted into the training corpus.';
  if (v==='QUARANTINE') return 'Suspected poisoning — quarantined with evidence preserved; not admitted until investigated.';
  if (v==='BLOCK'){
    if (!g.pii.ok) return 'A residual critical identifier survived scrubbing — the release gate blocks it outright.';
    if (!g.eval.ok) return 'Unresolved evaluation leakage would corrupt benchmark scores — blocked.';
    if (!g.repro.ok) return 'A deterministic rerun did not reproduce the bytes — provenance is untrustworthy, so it is blocked.';
    if (sh.license.decision==='RESTRICTED') return 'The license prohibits training use — blocked regardless of content quality.';
    return 'A required-evidence gate failed under the strict policy — blocked.';
  }
  if (sh.license.decision==='UNKNOWN') return 'The license is unknown — held for review; public availability is not permission.';
  if (g && !g.ran.ok) return 'A required pipeline stage never ran — held for review rather than admitted on faith.';
  return 'A required stage claims a pass but has no versioned evidence — held for review under this policy.';
}

/* ---------- accounting ---------- */
var VCOLOR={ ADMIT:'#147D74', REVIEW:'#E0982B', QUARANTINE:'#B5476B', BLOCK:'#8a1a3a', REPORT_ONLY:'#999' };
function countsAt(p){ var c={}; for (var i=0;i<RAW.length;i++){ var v=verdict(RAW[i],p); c[v]=(c[v]||0)+1; } return c; }
function accounting(){
  var total=RAW.length, c=countsAt(state.policy);
  var order=Object.keys(c).sort(function(a,b){ return c[b]-c[a]; }), rows='';
  for (var i=0;i<order.length;i++){ var k=order[i], n=c[k], w=(n/total)*100, vb=VB[k]||{e:'',w:k};
    rows+='<div class="acct-row"><span class="acct-k">'+vb.e+' '+vb.w+'</span>'+
      '<span style="width:120px"><span class="acct-bar" style="display:block;width:'+w+'%;background:'+(VCOLOR[k]||'#6169B8')+'"></span></span>'+
      '<span class="acct-v">'+n+'</span></div>'; }
  document.getElementById('acct-disp').innerHTML=rows;
  var sw='<table class="sweep"><tr><th>gate policy</th><th>admit</th><th>review</th><th>quar</th><th>block</th></tr>';
  for (var p=0;p<4;p++){ var cc=countsAt(p);
    sw+='<tr'+(p===state.policy?' class="here"':'')+'><td>'+p+' '+POLICIES[p].name+'</td><td>'+(cc.ADMIT||0)+'</td><td>'+(cc.REVIEW||0)+'</td><td>'+(cc.QUARANTINE||0)+'</td><td>'+(cc.BLOCK||0)+'</td></tr>'; }
  sw+='</table>'; document.getElementById('sweep').innerHTML=sw;
}

/* ---------- wiring ---------- */
var sel=document.getElementById('art-select');
for (var i=0;i<RAW.length;i++){ var o=document.createElement('option'); o.value=i; o.textContent=(i+1)+'. '+RAW[i].id; sel.appendChild(o); }
sel.addEventListener('change', function(){ state.idx=parseInt(this.value,10); render(); });
document.getElementById('prev-btn').addEventListener('click', function(){ if (state.idx>0){ state.idx--; render(); } });
document.getElementById('next-btn').addEventListener('click', function(){ if (state.idx<RAW.length-1){ state.idx++; render(); } });
document.addEventListener('keydown', function(e){ if (e.key==='ArrowLeft'&&state.idx>0){ state.idx--; render(); } if (e.key==='ArrowRight'&&state.idx<RAW.length-1){ state.idx++; render(); } });
var slider=document.getElementById('pol-slider');
function updatePolicy(){ state.policy=parseInt(slider.value,10);
  document.getElementById('strict-name').textContent=state.policy+' · '+POLICIES[state.policy].name;
  document.getElementById('strict-desc').textContent=POLICIES[state.policy].desc; render(); }
slider.addEventListener('input', updatePolicy);
updatePolicy();
"""


def build_html(shards):
    data_json = json.dumps(shards, ensure_ascii=False)
    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>Build Manifest — India-First 40B</title>\n'
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
        '  <a href=\"tokenizer.html\">Tokenizer</a>\n'
        '  <a href=\"manifest.html\" class=\"active\">Manifest</a>\n'
        '  <a href=\"v5_brief.html\">V5 Plan</a>\n'
        '  <a href=\"v5_playbook.html\">V5 Plan — Proposal</a>\n'
        '</div></div>\n'
        '<div class="wrap">\n'
        '  <div class="phead">\n'
        '    <h1>Build Manifest</h1>\n'
        '    <p class="dek">Per <em>Open-Build-Manifest.md</em>: the <b>system-of-record</b> that ties the whole '
        'pipeline together. For each shard it records real content &amp; recipe hashes, imports every stage’s result, '
        'checks admission gates, and decides whether the shard may enter the training corpus.</p>\n'
        '  </div>\n'
        '  <details class="explainer" open>\n'
        '    <summary>How to read this page</summary>\n'
        '    <div class="explainer-bd">\n'
        '      <p class="lead">A manifest is not another filter — it is the evidence file for one immutable shard. '
        'Admission is <b>derived from gate checks</b>, never from a caller saying "clean". The verdict:</p>\n'
        '      <div class="verdict-key">\n'
        '        <div class="vk-row"><span class="vk-badge v-admit">✅ ADMIT</span><span>All gates pass with verified evidence — enters the corpus.</span></div>\n'
        '        <div class="vk-row"><span class="vk-badge v-review">🟠 REVIEW</span><span>Resolvable gaps — unknown license, a stage not run or unverified.</span></div>\n'
        '        <div class="vk-row"><span class="vk-badge v-quar">🔴 QUARANTINE</span><span>Suspected poisoning — isolate and investigate.</span></div>\n'
        '        <div class="vk-row"><span class="vk-badge v-block">⛔ BLOCK</span><span>Residual PII, eval leakage, non-reproducible, or license prohibits use.</span></div>\n'
        '      </div>\n'
        '      <p class="note" style="margin-top:12px">The digests are <b>real SHA-256</b> computed in your browser '
        '(same bytes → same hash — that is how a deterministic rerun is checked). The slider sets how strictly to treat '
        '<b>unverified / unknown</b> evidence (the skill’s "fail closed" principle). Hover any underlined term.</p>\n'
        '    </div>\n'
        '  </details>\n'
        '  <div class="strict">\n'
        '    <div class="strict-top"><span class="lbl">Gate policy</span><span class="strict-name" id="strict-name"></span><span class="strict-desc" id="strict-desc"></span></div>\n'
        '    <input type="range" min="0" max="3" step="1" value="2" id="pol-slider">\n'
        '    <div class="strict-ticks"><span>0 report-only</span><span>1 lenient</span><span>2 standard</span><span>3 strict</span></div>\n'
        '  </div>\n'
        '  <div class="art-controls">\n'
        '    <span class="ctrl-label">Shard</span>\n'
        '    <div class="art-nav">\n'
        '      <button class="nav-btn" id="prev-btn">&#8592;</button>\n'
        '      <span class="art-counter" id="art-counter"></span>\n'
        '      <button class="nav-btn" id="next-btn">&#8594;</button>\n'
        '    </div>\n'
        '    <select class="art-select" id="art-select"></select>\n'
        '  </div>\n'
        '  <div class="title-bar"><span class="t" id="art-title"></span><span class="chip" id="art-id"></span></div>\n'
        '  <div class="caption" id="caption"></div>\n'
        '  <div class="verdict" id="verdict"><div class="verdict-hd"><span class="verdict-badge" id="verdict-badge"></span><span class="verdict-why" id="verdict-sub"></span></div></div>\n'
        '  <div class="grid2">\n'
        '    <div class="card"><div class="card-hd">Identity &amp; provenance</div><div class="card-bd" id="identity"></div></div>\n'
        '    <div class="card"><div class="card-hd">Admission gates</div><div class="card-bd" id="gates"></div></div>\n'
        '  </div>\n'
        '  <div class="card"><div class="card-hd">Transformations (imported from the 7 pipeline stages, in order)</div><div class="card-bd" id="transforms"></div></div>\n'
        '  <div class="card"><div class="card-hd">Composition</div><div class="card-bd" id="composition"></div></div>\n'
        '  <details class="more">\n'
        '    <summary>Show corpus index — verdicts across all ' + str(len(shards)) + ' shards</summary>\n'
        '    <div class="more-bd">\n'
        '      <div class="grid2">\n'
        '        <div class="card"><div class="card-hd">Verdicts at current gate policy</div><div class="card-bd" id="acct-disp"></div></div>\n'
        '        <div class="card"><div class="card-hd">Verdicts across every gate policy</div><div class="card-bd" id="sweep"></div></div>\n'
        '      </div>\n'
        '    </div>\n'
        '  </details>\n'
        '</div>\n'
        '<script>' + JS + '</script>\n'
        '</body>\n</html>\n'
    )


if __name__ == "__main__":
    print("Building manifest shards...")
    shards = M.build_sample()
    print("Generating {}...".format(OUTPUT_PATH))
    html = build_html(shards)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print("\nDone. {} written ({} shards).".format(OUTPUT_PATH, len(shards)))
