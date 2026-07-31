"""
Generate dedup.html — interactive Deduplication preview.

Follows Deduplication.md: fingerprint-normalize -> shingles -> MinHash/LSH
candidate generation -> verified Jaccard + containment -> connected-component
clusters -> keep one representative, route the rest. A strictness slider picks
a named policy bundle (threshold-calibration.md). Semantic/paraphrase and
event-level dedup need embeddings and are a documented offline tier, not run.

The decision logic (fingerprint, shingles, Jaccard, containment, clustering,
routing) is a 1:1 mirror of the verified reference; the generated JS is also
run in Node and checked against Python. Run: python3 generate_dedup_preview.py
"""

import json
import os
import dedup_sample

OUTPUT_PATH = "dedup.html"


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
.nav-in { max-width:1280px; margin:0 auto; padding:10px 24px; display:flex; align-items:center; gap:18px; flex-wrap:wrap; }
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
.art-counter { font-family:"IBM Plex Mono",monospace; font-size:12px; color:var(--muted); min-width:68px; text-align:center; }
.art-select { font-family:"Inter",sans-serif; font-size:13px; padding:5px 10px; border:1px solid var(--line);
  border-radius:7px; background:#fff; max-width:360px; }

.title-bar { margin:16px 0 0; padding:12px 15px; background:#fff; border:1px solid var(--line);
  border-radius:10px; display:flex; align-items:baseline; gap:12px; flex-wrap:wrap; }
.title-bar .t { font-family:"Spectral",serif; font-weight:600; font-size:19px; }
.title-bar a { font-family:"IBM Plex Mono",monospace; font-size:11px; color:var(--muted); }
.chip { font-family:"IBM Plex Mono",monospace; font-size:10px; font-weight:600; letter-spacing:.04em; padding:2px 8px; border-radius:5px; }
.chip.synthetic { background:#fbeada; color:#9a5a12; } .chip.real { background:#eef6f4; color:var(--teal); }
.caption { margin:12px 0 0; padding:10px 14px; border-left:3px solid var(--marigold); background:#fdf9f1;
  border-radius:0 8px 8px 0; font-size:13.5px; color:#5a4520; } .caption b { color:#8a5a12; }

.verdict { margin:14px 0; border:1px solid var(--line); border-radius:12px; overflow:hidden; }
.verdict-hd { padding:14px 18px 6px; display:flex; align-items:center; gap:12px; flex-wrap:wrap; }
.verdict-badge { font-weight:700; font-size:17px; padding:7px 15px; border-radius:9px; }
.v-accept { background:#eef6f4; color:var(--teal); }
.v-strip { background:#fdf3e3; color:#9a5a12; }
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

.member { display:grid; grid-template-columns:26px 1fr 150px 96px; gap:10px; align-items:center;
  padding:7px 0; border-bottom:1px dashed var(--line); font-size:13px; }
.member:last-child { border-bottom:none; }
.member.isrep { background:#f6faf8; margin:0 -15px; padding:8px 15px; border-radius:8px; border-bottom:none; }
.m-ico { font-size:15px; text-align:center; }
.m-title { overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.m-bar { height:12px; background:var(--panel); border-radius:6px; overflow:hidden; }
.m-fill { height:100%; background:var(--indigo-soft); }
.m-sim { font-family:"IBM Plex Mono",monospace; font-size:11px; color:var(--muted); text-align:right; }
.solo { font-size:13px; color:var(--teal); }

.text-view { border:1px solid var(--line); border-radius:12px; background:#fff; margin-top:13px; }
.text-body { padding:15px; max-height:240px; overflow-y:auto; font-size:13.5px; line-height:1.75;
  white-space:pre-wrap; word-break:break-word; }

.kv { font-size:12.5px; color:#33334a; margin:3px 0; }
.kv code { background:var(--panel); padding:1px 5px; border-radius:4px; font-size:11px; }

.acct-grid { display:grid; grid-template-columns:1fr 1fr; gap:13px; }
@media (max-width:860px){ .acct-grid { grid-template-columns:1fr; } }
.acct-row { display:flex; align-items:center; gap:10px; font-size:13px; padding:5px 0; border-bottom:1px dashed var(--line); }
.acct-row:last-child { border-bottom:none; }
.acct-k { flex:1; } .acct-v { font-family:"IBM Plex Mono",monospace; font-weight:600; color:var(--indigo); }
.acct-bar { height:10px; border-radius:5px; }
.clist { font-size:12.5px; }
.clist .crow { padding:6px 0; border-bottom:1px dashed var(--line); }
.clist .crow:last-child { border-bottom:none; }
.sweep { width:100%; border-collapse:collapse; font-size:12.5px; margin-top:6px; }
.sweep th, .sweep td { padding:5px 8px; text-align:right; border-bottom:1px solid var(--line); font-family:"IBM Plex Mono",monospace; }
.sweep th:first-child, .sweep td:first-child { text-align:left; }
.sweep tr.here { background:#f5f6fd; }
.trunc-note { font-family:"IBM Plex Mono",monospace; font-size:10.5px; color:var(--muted);
  margin-top:12px; padding-top:9px; border-top:1px dashed var(--line); }
"""


JS = r"""
var RAW = JSON.parse(document.getElementById('articles-data').textContent);
var state = { idx: 0, strictness: 3 };

var SHINGLE=5, NPERM=112, BANDS=14, ROWS=8;

/* ---------- fingerprint + shingles (mirror of the verified Python) ---------- */
function fingerprint(text){
  var t = text.toLowerCase();
  t = t.replace(/[^A-Za-z0-9ऀ-ॣ०-ॿ\s]/g, ' ');
  t = t.replace(/\s+/g, ' ').trim();
  return t;
}
function shingleSet(fp){
  var words = fp.split(' ').filter(function(w){ return w.length; });
  var s = {};
  if (words.length < SHINGLE){ if (words.length) s[words.join(' ')]=1; return s; }
  for (var i=0;i<=words.length-SHINGLE;i++) s[words.slice(i,i+SHINGLE).join(' ')]=1;
  return s;
}
function strHash(s){ var h=2166136261>>>0; for (var i=0;i<s.length;i++){ h^=s.charCodeAt(i); h=Math.imul(h,16777619)>>>0; } return h>>>0; }
function keys(o){ return Object.keys(o); }
function jaccard(A,B){
  var ka=keys(A), kb=keys(B);
  if (!ka.length && !kb.length) return 1; if (!ka.length || !kb.length) return 0;
  var small=ka.length<kb.length?A:B, big=ka.length<kb.length?B:A, inter=0;
  for (var k in small){ if (big[k]) inter++; }
  var uni = ka.length+kb.length-inter;
  return uni ? inter/uni : 0;
}
function containment(A,B){
  var ka=keys(A).length, kb=keys(B).length; if (!ka||!kb) return 0;
  var small=ka<kb?A:B, big=ka<kb?B:A, inter=0;
  for (var k in small){ if (big[k]) inter++; }
  return inter/Math.min(ka,kb);
}
function minhash(sh){
  var ks=keys(sh); if (!ks.length) return new Array(NPERM).fill(0);
  var sig=[];
  for (var p=0;p<NPERM;p++){ var m=0xffffffff;
    for (var i=0;i<ks.length;i++){ var h=strHash(p+'|'+ks[i]); if (h<m) m=h; }
    sig.push(m); }
  return sig;
}
function lshKeys(sig){ var out=[]; for (var b=0;b<BANDS;b++){ out.push(b+':'+sig.slice(b*ROWS,(b+1)*ROWS).join('_')); } return out; }

/* precompute per document */
var DOCS = RAW.map(function(a){
  var fp = fingerprint(a.text), sh = shingleSet(fp);
  return { raw:a, fp:fp, sh:sh, nsh:keys(sh).length,
           rawhash:strHash(a.text), fphash:strHash(fp), sig:minhash(sh) };
});

/* ---------- policy bundles ---------- */
var BUNDLES = {
  0:{name:'OFF', desc:'No deduplication — every copy is kept. A baseline to compare against.'},
  1:{name:'EXACT_ONLY', desc:'Remove only byte- or normalization-identical copies.', jac:1.01, cont:2.0},
  2:{name:'CONSERVATIVE_NEAR', desc:'Also remove very close near-copies (≥90% word overlap).', jac:0.90, cont:0.95},
  3:{name:'BALANCED_NEAR', desc:'Remove clear near-copies (≥80% overlap) and copied spans.', jac:0.80, cont:0.90},
  4:{name:'AGGRESSIVE_LEXICAL', desc:'Remove looser near-copies too (≥70% overlap).', jac:0.70, cont:0.80}
};

/* ---------- cluster + route (mirror of Python) ---------- */
var _cache = {};
function clusterAll(strictness){
  if (_cache[strictness]) return _cache[strictness];
  var n=DOCS.length, parent=[]; for (var i=0;i<n;i++) parent.push(i);
  function find(x){ while(parent[x]!==x){ parent[x]=parent[parent[x]]; x=parent[x]; } return x; }
  function union(x,y){ parent[find(x)]=find(y); }
  var edges={};
  if (strictness!==0){ var b=BUNDLES[strictness];
    for (var i2=0;i2<n;i2++){ for (var j=i2+1;j<n;j++){
      if (DOCS[i2].rawhash===DOCS[j].rawhash || DOCS[i2].fphash===DOCS[j].fphash){ edges[i2+'-'+j]={kind:'exact'}; union(i2,j); continue; }
      if (strictness===1) continue;
      var jac=jaccard(DOCS[i2].sh,DOCS[j].sh);
      if (jac>=b.jac){ edges[i2+'-'+j]={kind:'near',jac:jac}; union(i2,j); continue; }
      var cont=containment(DOCS[i2].sh,DOCS[j].sh);
      var lo=Math.min(DOCS[i2].nsh,DOCS[j].nsh), hi=Math.max(DOCS[i2].nsh,DOCS[j].nsh);
      if (cont>=b.cont && lo<0.7*hi){ edges[i2+'-'+j]={kind:'containment',cont:cont}; union(i2,j); }
    }}
  }
  var comps={}; for (var k=0;k<n;k++){ var r=find(k); (comps[r]=comps[r]||[]).push(k); }
  var disp=new Array(n), rep=new Array(n);
  for (var root in comps){ var mem=comps[root];
    if (mem.length===1){ disp[mem[0]]='KEEP_CANONICAL'; rep[mem[0]]=mem[0]; continue; }
    var repIdx=mem[0];
    for (var mi=0;mi<mem.length;mi++){ var m=mem[mi];
      if (DOCS[m].raw.text.length>DOCS[repIdx].raw.text.length ||
         (DOCS[m].raw.text.length===DOCS[repIdx].raw.text.length && m<repIdx)) repIdx=m; }
    for (var mj=0;mj<mem.length;mj++){ var mm=mem[mj]; rep[mm]=repIdx;
      if (mm===repIdx){ disp[mm]='KEEP_CANONICAL'; continue; }
      if (DOCS[mm].rawhash===DOCS[repIdx].rawhash || DOCS[mm].fphash===DOCS[repIdx].fphash){ disp[mm]='EXCLUDE_EXACT'; continue; }
      var cont2=containment(DOCS[mm].sh,DOCS[repIdx].sh);
      if (DOCS[mm].nsh<0.7*DOCS[repIdx].nsh && cont2>=(BUNDLES[strictness].cont||0.9)) disp[mm]='STRIP_DUPLICATE_SPAN';
      else disp[mm]='EXCLUDE_NEAR';
    }
  }
  _cache[strictness]={disp:disp, rep:rep, comps:comps, edges:edges, find:function(x){var p=[];for(var i=0;i<n;i++)p.push(i);/*noop*/} };
  /* store component lookup by member */
  var compOf={}; for (var rt in comps){ comps[rt].forEach(function(m){ compOf[m]=comps[rt]; }); }
  _cache[strictness].compOf=compOf;
  return _cache[strictness];
}

/* ---------- plain labels + glosses ---------- */
var PLAIN = {
  KEEP_CANONICAL:{emoji:'👑', word:'KEEP (canonical)', cls:'v-accept'},
  EXCLUDE_EXACT:{emoji:'✂️', word:'DROP (exact copy)', cls:'v-exclude'},
  EXCLUDE_NEAR:{emoji:'✂️', word:'DROP (near-copy)', cls:'v-exclude'},
  STRIP_DUPLICATE_SPAN:{emoji:'✂️', word:'STRIP (copied span)', cls:'v-strip'},
  REVIEW_CLUSTER:{emoji:'🟠', word:'REVIEW', cls:'v-review'}
};
var GLOSS = {
  KEEP_CANONICAL:'Kept — either unique, or chosen as the single representative of a group of duplicates.',
  EXCLUDE_EXACT:'Dropped — identical to the kept copy once punctuation and spacing are normalized.',
  EXCLUDE_NEAR:'Dropped — a lexical near-duplicate of the kept copy (high word overlap).',
  STRIP_DUPLICATE_SPAN:'The whole document is a passage copied out of a longer kept article (containment).',
  fingerprint:'A normalized view (lowercased, punctuation stripped) used only for comparison — the training text is untouched.',
  shingle:'A 5-word sliding window. Two documents are compared by how many shingles they share.',
  jaccard:'Shared shingles ÷ total distinct shingles. 1.0 = identical word-sets, 0 = nothing in common.',
  containment:'Shared shingles ÷ the SMALLER document’s shingles. High = the short doc sits inside the long one.',
  minhash:'A short fixed-length signature that estimates Jaccard without comparing full shingle sets.',
  lsh:'Locality-sensitive hashing: buckets signatures so likely matches collide, avoiding all-pairs comparison at scale.',
  canonical:'The one representative kept from a duplicate cluster (here: the longest / most complete copy).'
};
function glossOf(c){ return GLOSS[c]||c; }
function gloss(term,key){ return '<span class="gloss" title="'+escAttr(GLOSS[key]||key)+'">'+esc(term)+'</span>'; }
function esc(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function escAttr(s){ return esc(s).replace(/"/g,'&quot;'); }
function pct(x){ return Math.round(x*100)+'%'; }

/* ---------- render ---------- */
function render(){
  var C = clusterAll(state.strictness);
  var i = state.idx, d = DOCS[i], art = d.raw;
  var disp = C.disp[i], repIdx = C.rep[i], members = C.compOf[i];

  document.getElementById('art-title').textContent = art.title;
  var kindEl=document.getElementById('art-kind');
  kindEl.textContent = art.kind==='synthetic'?'SYNTHETIC':'REAL — Wikipedia';
  kindEl.className='chip '+(art.kind==='synthetic'?'synthetic':'real');
  var urlEl=document.getElementById('art-url'); urlEl.href=art.url; urlEl.style.display=art.kind==='synthetic'?'none':'';
  document.getElementById('art-counter').textContent=(i+1)+' of '+DOCS.length;
  document.getElementById('prev-btn').disabled=i===0;
  document.getElementById('next-btn').disabled=i===DOCS.length-1;
  document.getElementById('art-select').value=i;

  var capEl=document.getElementById('caption');
  if (art.caption){ capEl.innerHTML='<b>What this example shows:</b> '+esc(art.caption); capEl.style.display=''; }
  else capEl.style.display='none';

  var pv=PLAIN[disp]||{emoji:'',word:disp,cls:''};
  var badge=document.getElementById('verdict-badge'); badge.className='verdict-badge '+pv.cls; badge.textContent=pv.emoji+' '+pv.word;
  var codeEl=document.getElementById('verdict-code'); codeEl.textContent=disp; codeEl.title=glossOf(disp);
  document.getElementById('verdict-sub').textContent = whyText(disp, i, repIdx, members);

  /* cluster card */
  var host=document.getElementById('cluster');
  if (members.length===1){
    host.innerHTML='<div class="solo">✓ No duplicates found at this strictness — this document is unique and kept as-is.</div>';
  } else {
    var rows='';
    var order=members.slice().sort(function(a,b){
      if (a===repIdx) return -1; if (b===repIdx) return 1;
      return jaccard(DOCS[b].sh,DOCS[repIdx].sh)-jaccard(DOCS[a].sh,DOCS[repIdx].sh);
    });
    for (var o=0;o<order.length;o++){ var m=order[o], md=C.disp[m], mp=PLAIN[md]||{emoji:''};
      var isrep=(m===repIdx);
      var simTxt, simW;
      if (isrep){ simTxt='representative'; simW=0; }
      else { var jc=jaccard(DOCS[m].sh,DOCS[repIdx].sh);
             if (DOCS[m].fphash===DOCS[repIdx].fphash){ simTxt='identical'; simW=100; }
             else { simW=Math.round(jc*100); simTxt=simW+'% overlap'; } }
      rows += '<div class="member'+(isrep?' isrep':'')+(m===i?'':'')+'">'+
        '<div class="m-ico">'+mp.emoji+'</div>'+
        '<div class="m-title">'+(m===i?'<b>':'')+esc(DOCS[m].raw.title)+(m===i?'</b> ← viewing':'')+'</div>'+
        '<div class="m-bar">'+(isrep?'':'<div class="m-fill" style="width:'+simW+'%"></div>')+'</div>'+
        '<div class="m-sim">'+simTxt+'</div></div>';
    }
    host.innerHTML=rows;
  }

  /* details: fingerprint / shingles / minhash / lsh */
  var cand = lshCandidateCount(i);
  document.getElementById('mech').innerHTML =
    '<div class="kv">'+gloss('Fingerprint','fingerprint')+' (compared, not trained on): <code>'+esc(d.fp.slice(0,90))+(d.fp.length>90?'…':'')+'</code></div>'+
    '<div class="kv">'+gloss('Shingles','shingle')+': <b>'+d.nsh+'</b> distinct 5-word windows</div>'+
    '<div class="kv">'+gloss('MinHash','minhash')+' signature: <b>'+NPERM+'</b> values &nbsp;·&nbsp; '+
      gloss('LSH','lsh')+': <b>'+BANDS+'</b> bands × <b>'+ROWS+'</b> rows → <b>'+cand+'</b> candidate match(es) for this doc</div>'+
    '<div class="kv" style="color:#999">Candidate probability at similarity s: 1 − (1 − s^'+ROWS+')^'+BANDS+' — LSH finds likely pairs so we never compare all pairs at scale.</div>';

  var isTrunc=art.full_len>art.text.length;
  document.getElementById('text-body').innerHTML=esc(art.text)+
    (isTrunc?'<div class="trunc-note">Showing first '+art.text.length+' of '+art.full_len+' chars</div>':'');

  accounting();
}

function whyText(disp, i, repIdx, members){
  if (state.strictness===0) return 'Deduplication is OFF — every document is kept so you can see the corpus before any removal.';
  if (disp==='KEEP_CANONICAL'){
    if (members.length===1) return 'No substantial word-overlap with any other document — kept as a unique original. (Translations count as unique here: they share almost no words with their source.)';
    return 'The most complete copy in a group of '+members.length+' near-identical documents — kept as the single representative; the rest are removed.';
  }
  var rep=DOCS[repIdx];
  if (disp==='EXCLUDE_EXACT') return 'Identical to “'+rep.raw.title+'” once punctuation and spacing are normalized — pure redundancy, so it is dropped and that copy is kept.';
  if (disp==='STRIP_DUPLICATE_SPAN'){ var c=Math.round(containment(DOCS[i].sh,rep.sh)*100);
    return 'This whole document appears as a passage inside the longer article “'+rep.raw.title+'” ('+c+'% contained) — the copied span is redundant.'; }
  var jc=Math.round(jaccard(DOCS[i].sh,rep.sh)*100);
  return jc+'% word-overlap with the kept copy “'+rep.raw.title+'” — a near-duplicate, dropped so the model does not see the same text twice.';
}

function lshCandidateCount(i){
  var mine={}; lshKeys(DOCS[i].sig).forEach(function(k){ mine[k]=1; });
  var c=0;
  for (var j=0;j<DOCS.length;j++){ if (j===i) continue;
    var hit=false; var kj=lshKeys(DOCS[j].sig);
    for (var b=0;b<kj.length;b++){ if (mine[kj[b]]){ hit=true; break; } }
    if (hit) c++; }
  return c;
}

/* ---------- corpus accounting ---------- */
var DISP_COLOR={ KEEP_CANONICAL:'#147D74', EXCLUDE_EXACT:'#B5476B', EXCLUDE_NEAR:'#B5476B',
  STRIP_DUPLICATE_SPAN:'#E0982B', REVIEW_CLUSTER:'#E0982B' };
function countsAt(s){ var C=clusterAll(s), c={}; for (var i=0;i<C.disp.length;i++){ c[C.disp[i]]=(c[C.disp[i]]||0)+1; } return c; }
function keptOf(c){ return c.KEEP_CANONICAL||0; }
function removedOf(c){ return (c.EXCLUDE_EXACT||0)+(c.EXCLUDE_NEAR||0)+(c.STRIP_DUPLICATE_SPAN||0); }

function accounting(){
  var total=DOCS.length, c=countsAt(state.strictness);
  var order=Object.keys(c).sort(function(a,b){ return c[b]-c[a]; }), rows='';
  for (var i=0;i<order.length;i++){ var k=order[i], n=c[k], w=(n/total)*100, pv=PLAIN[k]||{word:k,emoji:''};
    rows+='<div class="acct-row"><span class="acct-k">'+pv.emoji+' '+pv.word+' <span style="color:#999;font-size:11px">'+k+'</span></span>'+
      '<span style="width:120px"><span class="acct-bar" style="display:block;width:'+w+'%;background:'+(DISP_COLOR[k]||'#6169B8')+'"></span></span>'+
      '<span class="acct-v">'+n+'</span></div>'; }
  document.getElementById('acct-disp').innerHTML=rows;

  var C=clusterAll(state.strictness), cl='';
  var comps=C.comps, shown=0;
  for (var rt in comps){ var mem=comps[rt]; if (mem.length<2) continue; shown++;
    var repIdx=C.rep[mem[0]];
    var names=mem.map(function(m){ var mp=PLAIN[C.disp[m]]||{emoji:''}; return mp.emoji+' '+esc(DOCS[m].raw.title); });
    cl+='<div class="crow">Cluster of '+mem.length+': '+names.join(' &nbsp; ')+'</div>'; }
  if (!shown) cl='<div class="solo">No duplicate clusters at this strictness — every document is unique.</div>';
  document.getElementById('acct-clusters').innerHTML=cl;

  var kept=keptOf(c), rem=removedOf(c);
  document.getElementById('acct-summary').innerHTML=
    '<div class="acct-row"><span class="acct-k">Kept</span><span class="acct-v">'+kept+' / '+total+'  ('+pct(kept/total)+')</span></div>'+
    '<div class="acct-row"><span class="acct-k">Removed (exact + near + span)</span><span class="acct-v">'+rem+'</span></div>'+
    '<div class="acct-row"><span class="acct-k">Active policy</span><span class="acct-v">'+BUNDLES[state.strictness].name+'</span></div>';

  var sw='<table class="sweep"><tr><th>strictness</th><th>kept</th><th>removed</th></tr>';
  for (var s=0;s<5;s++){ var cc=countsAt(s);
    sw+='<tr'+(s===state.strictness?' class="here"':'')+'><td>'+s+' '+BUNDLES[s].name+'</td><td>'+keptOf(cc)+'</td><td>'+removedOf(cc)+'</td></tr>'; }
  sw+='</table>'; document.getElementById('sweep').innerHTML=sw;
}

/* ---------- wiring ---------- */
var sel=document.getElementById('art-select');
for (var i=0;i<DOCS.length;i++){ var o=document.createElement('option'); o.value=i; o.textContent=(i+1)+'. '+DOCS[i].raw.title; sel.appendChild(o); }
sel.addEventListener('change', function(){ state.idx=parseInt(this.value,10); render(); });
document.getElementById('prev-btn').addEventListener('click', function(){ if (state.idx>0){ state.idx--; render(); } });
document.getElementById('next-btn').addEventListener('click', function(){ if (state.idx<DOCS.length-1){ state.idx++; render(); } });
document.addEventListener('keydown', function(e){ if (e.key==='ArrowLeft'&&state.idx>0){ state.idx--; render(); } if (e.key==='ArrowRight'&&state.idx<DOCS.length-1){ state.idx++; render(); } });
var slider=document.getElementById('strict-slider');
function updateStrict(){ state.strictness=parseInt(slider.value,10);
  document.getElementById('strict-name').textContent=state.strictness+' · '+BUNDLES[state.strictness].name;
  document.getElementById('strict-desc').textContent=BUNDLES[state.strictness].desc; render(); }
slider.addEventListener('input', updateStrict);
updateStrict();
"""


def build_html(articles):
    data_json = json.dumps(articles, ensure_ascii=False)
    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>Deduplication — India-First 40B</title>\n'
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
        '  <a href=\"dedup.html\" class=\"active\">Dedup</a>\n'
        '  <a href=\"pii.html\">PII</a>\n'
        '  <a href=\"decontam.html\">Decontam</a>\n'
        '  <a href=\"tokenizer.html\">Tokenizer</a>\n'
        '  <a href=\"manifest.html\">Manifest</a>\n'
        '  <a href=\"v5_brief.html\">V5 Plan</a>\n'
        '  <a href=\"v5_playbook.html\">V5 Plan — Proposal</a>\n'
        '</div></div>\n'
        '<div class="wrap">\n'
        '  <div class="phead">\n'
        '    <h1>Deduplication</h1>\n'
        '    <p class="dek">Per <em>Deduplication.md</em>: remove redundant <b>copies</b> so the model doesn’t waste '
        'compute or memorize repeated text — while protecting real diversity (translations and independent articles '
        'are <b>not</b> duplicates).</p>\n'
        '  </div>\n'
        '  <details class="explainer" open>\n'
        '    <summary>How to read this page</summary>\n'
        '    <div class="explainer-bd">\n'
        '      <p class="lead">Documents are compared by their <b>word-shingles</b> (5-word windows). Overlap is scored '
        'with <b>Jaccard</b> similarity; matching documents form a <b>cluster</b>; one representative is kept and the '
        'rest are routed:</p>\n'
        '      <div class="verdict-key">\n'
        '        <div class="vk-row"><span class="vk-badge v-accept">👑 KEEP (canonical)</span><span>Unique, or the one copy kept from a duplicate group.</span></div>\n'
        '        <div class="vk-row"><span class="vk-badge v-exclude">✂️ DROP (exact)</span><span>Identical once normalized — pure redundancy.</span></div>\n'
        '        <div class="vk-row"><span class="vk-badge v-exclude">✂️ DROP (near-copy)</span><span>High word-overlap with the kept copy.</span></div>\n'
        '        <div class="vk-row"><span class="vk-badge v-strip">✂️ STRIP (span)</span><span>A passage copied out of a longer kept article.</span></div>\n'
        '      </div>\n'
        '      <p class="note" style="margin-top:12px">No single cut-off is right, so the <b>strictness slider</b> selects '
        'a named policy bundle (from <em>threshold-calibration.md</em>): drag it and watch which near-copies get removed. '
        'MinHash/LSH (in the details) is how these matches are found cheaply at scale. Semantic paraphrase and '
        'same-event dedup need embeddings — a documented offline tier, not run here. Hover any underlined term.</p>\n'
        '    </div>\n'
        '  </details>\n'
        '  <div class="strict">\n'
        '    <div class="strict-top">\n'
        '      <span class="lbl">Strictness</span>\n'
        '      <span class="strict-name" id="strict-name"></span>\n'
        '      <span class="strict-desc" id="strict-desc"></span>\n'
        '    </div>\n'
        '    <input type="range" min="0" max="4" step="1" value="3" id="strict-slider">\n'
        '    <div class="strict-ticks"><span>0 off</span><span>1 exact</span><span>2 conservative</span>'
        '<span>3 balanced</span><span>4 aggressive</span></div>\n'
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
        '    <div class="card-hd">Its duplicate cluster — who it matches, and which one is kept</div>\n'
        '    <div class="card-bd"><div id="cluster"></div></div>\n'
        '  </div>\n'
        '  <div class="text-view">\n'
        '    <div class="card-hd" style="border-bottom:1px solid var(--line)">The document</div>\n'
        '    <div class="text-body" id="text-body"></div>\n'
        '  </div>\n'
        '  <details class="more">\n'
        '    <summary>Show the matching machinery — fingerprint, shingles, MinHash / LSH</summary>\n'
        '    <div class="more-bd"><div id="mech"></div></div>\n'
        '  </details>\n'
        '  <details class="more">\n'
        '    <summary>Show corpus accounting — clusters &amp; removal across all ' + str(len(articles)) + ' documents</summary>\n'
        '    <div class="more-bd">\n'
        '      <div class="acct-grid">\n'
        '        <div class="card"><div class="card-hd">Decisions at current strictness</div><div class="card-bd" id="acct-disp"></div></div>\n'
        '        <div class="card"><div class="card-hd">Summary</div><div class="card-bd" id="acct-summary"></div></div>\n'
        '      </div>\n'
        '      <div class="card" style="margin-top:13px"><div class="card-hd">Duplicate clusters found</div><div class="card-bd clist" id="acct-clusters"></div></div>\n'
        '      <div class="card" style="margin-top:13px"><div class="card-hd">Removal across every strictness bundle</div><div class="card-bd" id="sweep"></div></div>\n'
        '    </div>\n'
        '  </details>\n'
        '</div>\n'
        '<script>' + JS + '</script>\n'
        '</body>\n</html>\n'
    )


if __name__ == "__main__":
    print("Building dedup corpus...")
    articles = dedup_sample.build_sample()
    print("Generating {}...".format(OUTPUT_PATH))
    html = build_html(articles)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    n_syn = sum(1 for a in articles if a["kind"] == "synthetic")
    print("\nDone. {} written ({} docs: {} synthetic + {} real).".format(
        OUTPUT_PATH, len(articles), n_syn, len(articles) - n_syn))
