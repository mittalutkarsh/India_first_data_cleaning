"""
Generate decontam.html — interactive evaluation-decontamination preview.

Follows decontaminate_SKILL.md (freeze the eval benchmark; scan training
records against it; classify the contamination class; route the TRAINING side;
report clean-subset coverage & benchmark inflation) and
decontaminate_threshold-calibration.md (named threshold bundles).

Cross-lingual/semantic detection and real poisoning validation are documented
offline tiers. The engine (normalize, question/source coverage, answer-linkage,
poisoning heuristic, routing) is a 1:1 mirror of the verified reference and is
re-checked in Node. Run: python3 generate_decontam_preview.py
"""

import json
import os
import decontam_sample as D

OUTPUT_PATH = "decontam.html"


CSS = """
:root {
  --bg:#FAFBFD; --ink:#16162A; --indigo:#2E357E; --indigo-soft:#6169B8;
  --marigold:#E0982B; --teal:#147D74; --rose:#B5476B; --line:#E3E4EE; --muted:#656579; --panel:#F1F2F8;
}
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
.explainer-bd .lead { margin:0 0 12px; } .explainer-bd b { color:var(--ink); }
.verdict-key { display:flex; flex-direction:column; gap:6px; margin:10px 0 4px; }
.vk-row { display:flex; align-items:center; gap:10px; font-size:13px; }
.vk-badge { font-weight:700; font-size:11px; padding:2px 9px; border-radius:6px; min-width:170px; text-align:center; }
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
.title-bar a { font-family:"IBM Plex Mono",monospace; font-size:11px; color:var(--muted); }
.chip { font-family:"IBM Plex Mono",monospace; font-size:10px; font-weight:600; letter-spacing:.04em; padding:2px 8px; border-radius:5px; }
.chip.synthetic { background:#fbeada; color:#9a5a12; } .chip.real { background:#eef6f4; color:var(--teal); }
.caption { margin:12px 0 0; padding:10px 14px; border-left:3px solid var(--marigold); background:#fdf9f1; border-radius:0 8px 8px 0; font-size:13.5px; color:#5a4520; } .caption b { color:#8a5a12; }

.verdict { margin:14px 0; border:1px solid var(--line); border-radius:12px; overflow:hidden; }
.verdict-hd { padding:14px 18px 6px; display:flex; align-items:center; gap:12px; flex-wrap:wrap; }
.verdict-badge { font-weight:700; font-size:16px; padding:7px 15px; border-radius:9px; }
.v-keep { background:#eef6f4; color:var(--teal); }
.v-remove { background:#fceef2; color:var(--rose); }
.v-review { background:#fdf3e3; color:#9a5a12; }
.v-quar { background:#fceef2; color:#8a1a3a; }
.verdict-code { font-family:"IBM Plex Mono",monospace; font-size:10.5px; color:var(--muted); }
.verdict-why { padding:2px 18px 14px; font-size:14px; color:#26263c; line-height:1.55; }
.gloss { border-bottom:1px dotted currentColor; cursor:help; }

.card { border:1px solid var(--line); border-radius:12px; background:#fff; overflow:hidden; }
.card-hd { padding:9px 15px; border-bottom:1px solid var(--line); background:var(--panel); font-family:"IBM Plex Mono",monospace; font-size:10px; font-weight:600; letter-spacing:.09em; text-transform:uppercase; color:var(--indigo); }
.card-bd { padding:14px 15px; }
.match { display:flex; gap:12px; align-items:baseline; flex-wrap:wrap; font-size:13px; }
.bpill { font-family:"IBM Plex Mono",monospace; font-size:10px; font-weight:600; padding:2px 8px; border-radius:5px; background:#eef0fb; color:var(--indigo); }
.cls { font-family:"IBM Plex Mono",monospace; font-size:11px; color:var(--rose); }
.metrics { margin-top:10px; }
.metrics .kv { font-size:12.5px; color:#33334a; margin:2px 0; }
.metrics code { background:var(--panel); padding:1px 5px; border-radius:4px; font-size:11px; }
.nomatch { font-size:13px; color:var(--teal); }

.text-view { border:1px solid var(--line); border-radius:12px; background:#fff; margin-top:13px; }
.text-body { padding:15px; max-height:200px; overflow-y:auto; font-size:13.5px; line-height:1.8; white-space:pre-wrap; word-break:break-word; }
.ov { background:#fceef2; color:#8a1a3a; border-radius:3px; padding:0 2px; }

.bench { display:grid; grid-template-columns:repeat(auto-fill,minmax(150px,1fr)); gap:8px; }
.bcard { border:1px solid var(--line); border-radius:9px; padding:9px 10px; font-size:12px; }
.bcard.dirty { border-color:#e6b8c6; background:#fdf0f4; }
.bcard.clean { border-color:#cfe6e1; background:#f2faf8; }
.bcard .bid { font-family:"IBM Plex Mono",monospace; font-weight:700; }
.bcard .bst { font-family:"IBM Plex Mono",monospace; font-size:10px; }
.dirty .bst { color:var(--rose); } .clean .bst { color:var(--teal); }
.impact { display:flex; gap:24px; flex-wrap:wrap; margin-top:12px; }
.impact .m { }
.impact .mn { font-family:"IBM Plex Mono",monospace; font-weight:700; font-size:22px; color:var(--indigo); }
.impact .ml { font-size:11px; color:var(--muted); }
.illus { font-size:11.5px; color:var(--muted); margin-top:8px; font-style:italic; }

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
var DATA = JSON.parse(document.getElementById('articles-data').textContent);
var RAW = DATA.training, BENCH = DATA.benchmark;
var state = { idx:0, policy:3 };

var STOP = 'की का के है में और को पर से यह एक हैं था कि जो सा कौन हो होता कर तो ही इस उस'.split(' ');
var STOPSET = {}; STOP.forEach(function(w){ STOPSET[w]=1; });
var POISON_CUES = ['उत्तर हमेशा','हमेशा लिख','always answer','जब भी'];

function esc(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function escAttr(s){ return esc(s).replace(/"/g,'&quot;'); }
function norm(t){ return t.toLowerCase().replace(/[^A-Za-z0-9ऀ-ॣ०-ॿ\s]/g,' ').replace(/\s+/g,' ').trim(); }
function words(t){ return norm(t).split(' ').filter(function(w){ return w.length; }); }
function content(t){ var o={}; words(t).forEach(function(w){ if (!STOPSET[w] && w.length>=2) o[w]=1; }); return o; }
function coverage(itemWords, recSet){ var k=Object.keys(itemWords); if (!k.length) return 0;
  var hit=0; k.forEach(function(w){ if (recSet[w]) hit++; }); return hit/k.length; }
function ansPresent(ans, rec){ var a=ans.toLowerCase().trim(); return a && rec.toLowerCase().indexOf(a)!==-1; }

var BUNDLES = {
  0:{name:'OFF', desc:'No decontamination — nothing removed, so you can see every match first.'},
  1:{name:'EXACT_ONLY', desc:'Remove only verbatim question copies and question+answer leaks.', cov:2.0},
  2:{name:'CONSERVATIVE', desc:'Also remove very close reworded copies (≥90% key-word overlap).', cov:0.90},
  3:{name:'BALANCED', desc:'Remove clear near-copies (≥80% overlap) too.', cov:0.80},
  4:{name:'AGGRESSIVE', desc:'Remove looser near-copies (≥70% overlap) too.', cov:0.70}
};

/* classify a training record vs the frozen benchmark (mirror of Python) */
function classify(rec, policy){
  var nrec=norm(rec.text), recSet={}; words(rec.text).forEach(function(w){ recSet[w]=1; });
  if (policy>=1){
    for (var i=0;i<BENCH.length;i++){ var it=BENCH[i];
      if (ansPresent(it.answer, rec.text) && POISON_CUES.some(function(c){ return rec.text.indexOf(c)!==-1; }))
        return { disp:'QUARANTINE_POISONING', bid:it.id, cls:'poisoning' }; }
  }
  if (policy===0){
    var bestId='', bestCov=0;
    for (var j=0;j<BENCH.length;j++){ var c=coverage(content(BENCH[j].question), recSet); if (c>bestCov){ bestCov=c; bestId=BENCH[j].id; } }
    return { disp:'KEEP_CLEAN', bid:(bestCov>0?bestId:''), cls:'none' };
  }
  var b=BUNDLES[policy];
  for (var g=0;g<BENCH.length;g++){ var it2=BENCH[g], qc=coverage(content(it2.question),recSet);
    if ((nrec.indexOf(norm(it2.question))!==-1 || qc>=0.8) && ansPresent(it2.answer,rec.text))
      return { disp:'REMOVE_SOLUTION_LEAK', bid:it2.id, cls:'ground_truth' }; }
  for (var e=0;e<BENCH.length;e++){ if (nrec.indexOf(norm(BENCH[e].question))!==-1)
      return { disp:'REMOVE_EXACT_EVAL', bid:BENCH[e].id, cls:'exact' }; }
  if (policy>=2){ for (var n=0;n<BENCH.length;n++){ var qcn=coverage(content(BENCH[n].question),recSet);
      if (qcn>=b.cov) return { disp:'REMOVE_NEAR_EVAL', bid:BENCH[n].id, cls:'near' }; } }
  for (var t=0;t<BENCH.length;t++){ var it3=BENCH[t], qct=coverage(content(it3.question),recSet);
    if (it3.profile==='QA-en' && qct<0.34 && ansPresent(it3.answer,rec.text))
      return { disp:'REVIEW', bid:it3.id, cls:'translation' }; }
  for (var s=0;s<BENCH.length;s++){ var it4=BENCH[s], qcs=coverage(content(it4.question),recSet),
      scs=coverage(content(it4.source),recSet);
    if (scs>=0.6 && qcs<0.5) return { disp:'KEEP_SOURCE_FAMILIARITY', bid:it4.id, cls:'source_only' }; }
  return { disp:'KEEP_CLEAN', bid:'', cls:'none' };
}

var PLAIN = {
  KEEP_CLEAN:{e:'✅',w:'KEEP (clean)',c:'v-keep'},
  KEEP_SOURCE_FAMILIARITY:{e:'✅',w:'KEEP (source only)',c:'v-keep'},
  REMOVE_EXACT_EVAL:{e:'✂️',w:'REMOVE (exact match)',c:'v-remove'},
  REMOVE_NEAR_EVAL:{e:'✂️',w:'REMOVE (near-copy)',c:'v-remove'},
  REMOVE_SOLUTION_LEAK:{e:'🚫',w:'REMOVE (answer leak)',c:'v-remove'},
  REVIEW:{e:'🟠',w:'REVIEW',c:'v-review'},
  QUARANTINE_POISONING:{e:'🔴',w:'QUARANTINE (poison)',c:'v-quar'}
};
var GLOSS = {
  KEEP_CLEAN:'No benchmark item leaks into this record — safe to train on.',
  KEEP_SOURCE_FAMILIARITY:'Only the underlying source passage overlaps, not the question or answer. Seeing a public passage is not cheating.',
  REMOVE_EXACT_EVAL:'The record contains a benchmark question verbatim — remove the training copy.',
  REMOVE_NEAR_EVAL:'The record is a reworded version of a benchmark question (high key-word overlap).',
  REMOVE_SOLUTION_LEAK:'The record contains a benchmark question together with its answer/solution — the highest-risk leak.',
  REVIEW:'A benchmark answer appears but the question does not match lexically — likely a translated leak. Confirm with the cross-lingual tier.',
  QUARANTINE_POISONING:'A planted instruction ties a trigger to a benchmark answer — quarantined as suspected poisoning (validation is a separate step).',
  coverage:'Fraction of the benchmark question’s key words that appear in this record.',
  source_familiarity:'The model saw a background passage but not the task-specific question/answer.',
  clean_subset:'Share of benchmark items with no detected leak — only these give a trustworthy score.',
  inflation:'How much a benchmark score would be overstated if the model memorized the leaked items.'
};
function glossOf(c){ return GLOSS[c]||c; }
function gloss(term, key){ return '<span class="gloss" title="'+escAttr(glossOf(key))+'">'+esc(term)+'</span>'; }
function pct(x){ return Math.round(x*100)+'%'; }

/* benchmark contamination at a policy: item is dirty if some record removes/quarantines against it */
function benchStatus(policy){
  var dirty={};
  for (var i=0;i<RAW.length;i++){ var r=classify(RAW[i], policy);
    if (r.bid && (r.disp.indexOf('REMOVE')===0 || r.disp==='QUARANTINE_POISONING' || r.disp==='REVIEW')) dirty[r.bid]=r.disp; }
  return dirty;
}

/* ---------- render ---------- */
function render(){
  var rec=RAW[state.idx], res=classify(rec, state.policy);

  document.getElementById('art-title').textContent=rec.title;
  var kindEl=document.getElementById('art-kind'); kindEl.textContent=rec.kind==='synthetic'?'SYNTHETIC':'REAL — Wikipedia';
  kindEl.className='chip '+(rec.kind==='synthetic'?'synthetic':'real');
  var urlEl=document.getElementById('art-url'); urlEl.href=rec.url; urlEl.style.display=rec.kind==='synthetic'?'none':'';
  document.getElementById('art-counter').textContent=(state.idx+1)+' of '+RAW.length;
  document.getElementById('prev-btn').disabled=state.idx===0;
  document.getElementById('next-btn').disabled=state.idx===RAW.length-1;
  document.getElementById('art-select').value=state.idx;
  var capEl=document.getElementById('caption');
  if (rec.caption){ capEl.innerHTML='<b>What this example shows:</b> '+esc(rec.caption); capEl.style.display=''; }
  else capEl.style.display='none';

  var pv=PLAIN[res.disp]; var badge=document.getElementById('verdict-badge');
  badge.className='verdict-badge '+pv.c; badge.textContent=pv.e+' '+pv.w;
  var codeEl=document.getElementById('verdict-code'); codeEl.textContent=res.disp; codeEl.title=glossOf(res.disp);
  document.getElementById('verdict-sub').textContent=whyText(res, rec);

  /* matched benchmark item */
  var host=document.getElementById('match');
  if (!res.bid){ host.innerHTML='<div class="nomatch">✓ No benchmark item matches this record — it is not evaluation data.</div>'; }
  else {
    var it=BENCH.filter(function(b){ return b.id===res.bid; })[0];
    var recSet={}; words(rec.text).forEach(function(w){ recSet[w]=1; });
    var qcov=coverage(content(it.question), recSet), scov=coverage(content(it.source), recSet);
    host.innerHTML =
      '<div class="match"><span class="bpill">benchmark '+it.id+'</span><span>'+it.profile+'</span>'+
      (res.cls!=='none'?'<span class="cls">class: '+res.cls+'</span>':'')+'</div>'+
      '<div class="metrics">'+
        '<div class="kv">'+gloss('Question key-word overlap','coverage')+': <code>'+pct(qcov)+'</code></div>'+
        '<div class="kv">Verbatim question present: <code>'+(norm(it.question).length && norm(rec.text).indexOf(norm(it.question))!==-1?'yes':'no')+'</code></div>'+
        '<div class="kv">Benchmark answer present: <code>'+(ansPresent(it.answer,rec.text)?'yes':'no')+'</code></div>'+
        '<div class="kv">'+gloss('Source-passage overlap','source_familiarity')+': <code>'+pct(scov)+'</code></div>'+
      '</div>';
  }

  /* record text with matched question key-words highlighted */
  var it2 = res.bid ? BENCH.filter(function(b){ return b.id===res.bid; })[0] : null;
  var qwords = it2 ? content(it2.question) : {};
  var html='', hl=0;
  rec.text.split(/(\s+)/).forEach(function(tok){
    var key=norm(tok);
    if (key && qwords[key]){ html += '<span class="ov">'+esc(tok)+'</span>'; hl++; } else html += esc(tok);
  });
  if (hl===0){
    var noteMap = {
      none:'No benchmark question or answer appears in this record — nothing to highlight, which is why it is kept.',
      source_only:'Only the benchmark item’s background passage overlaps — the question’s key-words are not here.',
      translation:'The benchmark answer appears, but the question is in another language, so no key-words line up (this is the lexical blind spot the cross-lingual tier covers).',
      poisoning:'The benchmark answer is present inside a planted instruction rather than as a matching question.'
    };
    html += '<div class="trunc-note">' + (noteMap[res.cls] || 'No benchmark question key-words appear in this record.') + '</div>';
  }
  var isTrunc=rec.full_len>rec.text.length;
  document.getElementById('text-body').innerHTML=html+(isTrunc?'<div class="trunc-note">first '+rec.text.length+' of '+rec.full_len+' chars</div>':'');

  benchImpact();
  accounting();
}

function whyText(res, rec){
  if (state.policy===0) return 'Decontamination is OFF — matches are detected but nothing is removed yet.';
  var m={
    KEEP_CLEAN:'No benchmark question or answer appears here — the record is clean and kept.',
    KEEP_SOURCE_FAMILIARITY:'This only repeats a benchmark item’s background passage, not the question or answer — that is source familiarity, not contamination, so it is kept.',
    REMOVE_EXACT_EVAL:'This record reproduces a benchmark question word-for-word — the training copy is removed so the test still measures real ability.',
    REMOVE_NEAR_EVAL:'This is the same benchmark question lightly reworded — a near-copy, removed at this policy.',
    REMOVE_SOLUTION_LEAK:'This pairs a benchmark question with its answer — training on it would just teach the test key, so it is removed.',
    REVIEW:'A benchmark answer shows up but the question is in another language, so the lexical scan can’t confirm it — sent to review for the cross-lingual tier.',
    QUARANTINE_POISONING:'This looks like a planted instruction forcing a benchmark answer — quarantined as suspected poisoning for investigation.'
  };
  return m[res.disp]||'';
}

/* ---------- benchmark impact panel ---------- */
function benchImpact(){
  var dirty=benchStatus(state.policy), host=document.getElementById('bench'), cards='';
  var nClean=0;
  for (var i=0;i<BENCH.length;i++){ var it=BENCH[i], isDirty=!!dirty[it.id];
    if (!isDirty) nClean++;
    cards += '<div class="bcard '+(isDirty?'dirty':'clean')+'"><span class="bid">'+it.id+'</span> '+
      '<span style="color:#888">'+it.profile+'</span><br><span class="bst">'+(isDirty?'contaminated':'clean ✓')+'</span></div>'; }
  host.innerHTML=cards;
  var total=BENCH.length, cov=nClean/total;
  /* illustrative inflation: assume memorized dirty items -> 100%, clean items -> 60% */
  var CLEAN_ACC=0.60, full=((total-nClean)*1.0 + nClean*CLEAN_ACC)/total, infl=full-CLEAN_ACC;
  document.getElementById('impact').innerHTML =
    '<div class="m"><div class="mn">'+pct(cov)+'</div><div class="ml">'+gloss('clean-subset coverage','clean_subset')+'</div></div>'+
    '<div class="m"><div class="mn">'+nClean+' / '+total+'</div><div class="ml">benchmark items usable</div></div>'+
    '<div class="m"><div class="mn">+'+pct(infl)+'</div><div class="ml">'+gloss('illustrative inflation','inflation')+'</div></div>';
  document.getElementById('illus').textContent =
    'Illustrative: if the model memorised the '+(total-nClean)+' contaminated item(s) (100%) and scored '+pct(CLEAN_ACC)+' on the rest, the headline score would read '+pct(full)+' vs a true '+pct(CLEAN_ACC)+'.';
}

/* ---------- corpus accounting ---------- */
var DCOLOR={ KEEP_CLEAN:'#147D74', KEEP_SOURCE_FAMILIARITY:'#3aa89c', REMOVE_EXACT_EVAL:'#B5476B',
  REMOVE_NEAR_EVAL:'#c0718d', REMOVE_SOLUTION_LEAK:'#8a1a3a', REVIEW:'#E0982B', QUARANTINE_POISONING:'#8a1a3a' };
function countsAt(p){ var c={}; for (var i=0;i<RAW.length;i++){ var d=classify(RAW[i],p).disp; c[d]=(c[d]||0)+1; } return c; }
function removedOf(c){ var s=0; for (var k in c){ if (k.indexOf('REMOVE')===0||k==='QUARANTINE_POISONING') s+=c[k]; } return s; }

function accounting(){
  var total=RAW.length, c=countsAt(state.policy);
  var order=Object.keys(c).sort(function(a,b){ return c[b]-c[a]; }), rows='';
  for (var i=0;i<order.length;i++){ var k=order[i], n=c[k], w=(n/total)*100, pv=PLAIN[k]||{e:'',w:k};
    rows+='<div class="acct-row"><span class="acct-k">'+pv.e+' '+pv.w+' <span style="color:#999;font-size:11px">'+k+'</span></span>'+
      '<span style="width:110px"><span class="acct-bar" style="display:block;width:'+w+'%;background:'+(DCOLOR[k]||'#6169B8')+'"></span></span>'+
      '<span class="acct-v">'+n+'</span></div>'; }
  document.getElementById('acct-disp').innerHTML=rows;

  var sw='<table class="sweep"><tr><th>policy</th><th>removed</th><th>review</th><th>kept</th></tr>';
  for (var p=0;p<5;p++){ var cc=countsAt(p), rem=removedOf(cc), rev=cc.REVIEW||0, kept=total-rem-rev;
    sw+='<tr'+(p===state.policy?' class="here"':'')+'><td>'+p+' '+BUNDLES[p].name+'</td><td>'+rem+'</td><td>'+rev+'</td><td>'+kept+'</td></tr>'; }
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
  document.getElementById('strict-name').textContent=state.policy+' · '+BUNDLES[state.policy].name;
  document.getElementById('strict-desc').textContent=BUNDLES[state.policy].desc; render(); }
slider.addEventListener('input', updatePolicy);
updatePolicy();
"""


def build_html(training):
    data = {"benchmark": [{"id": b["id"], "profile": b["profile"], "question": b["question"],
                            "answer": b["answer"], "source": b["source"]} for b in D.BENCHMARK],
            "training": training}
    data_json = json.dumps(data, ensure_ascii=False)
    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>Decontamination — India-First 40B</title>\n'
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
        '  <a href=\"decontam.html\" class=\"active\">Decontam</a>\n'
        '  <a href=\"tokenizer.html\">Tokenizer</a>\n'
        '  <a href=\"manifest.html\">Manifest</a>\n'
        '</div></div>\n'
        '<div class="wrap">\n'
        '  <div class="phead">\n'
        '    <h1>Decontamination</h1>\n'
        '    <p class="dek">Per <em>decontaminate_SKILL.md</em>: keep the <b>evaluation benchmark</b> honest. Freeze the '
        'test items, scan the <b>training corpus</b> for copies of them, and remove the <b>training</b> side — so the '
        'benchmark still measures real ability, not memorization.</p>\n'
        '  </div>\n'
        '  <details class="explainer" open>\n'
        '    <summary>How to read this page</summary>\n'
        '    <div class="explainer-bd">\n'
        '      <p class="lead">Each training record is checked against a frozen benchmark (' + str(len(D.BENCHMARK)) +
        ' items). If a benchmark question — or its answer — leaks into training, that record is routed:</p>\n'
        '      <div class="verdict-key">\n'
        '        <div class="vk-row"><span class="vk-badge v-keep">✅ KEEP (clean / source)</span><span>No item leaks, or only its background passage overlaps.</span></div>\n'
        '        <div class="vk-row"><span class="vk-badge v-remove">✂️ REMOVE</span><span>An exact / near copy, or a question+answer leak — dropped from training.</span></div>\n'
        '        <div class="vk-row"><span class="vk-badge v-review">🟠 REVIEW</span><span>A likely translated leak the lexical scan can’t confirm.</span></div>\n'
        '        <div class="vk-row"><span class="vk-badge v-quar">🔴 QUARANTINE</span><span>Suspected benchmark-answer poisoning.</span></div>\n'
        '      </div>\n'
        '      <p class="note" style="margin-top:12px">Seeing a public <b>source passage</b> is not cheating; a question '
        '<b>with its answer</b> is the worst case. The slider selects a threshold bundle (from '
        '<em>threshold-calibration.md</em>). The impact panel shows the <b>clean-subset</b> — only uncontaminated items '
        'give a trustworthy score. Cross-lingual/semantic matching and real poisoning validation are documented offline '
        'tiers. Hover any underlined term.</p>\n'
        '    </div>\n'
        '  </details>\n'
        '  <div class="strict">\n'
        '    <div class="strict-top"><span class="lbl">Threshold</span><span class="strict-name" id="strict-name"></span><span class="strict-desc" id="strict-desc"></span></div>\n'
        '    <input type="range" min="0" max="4" step="1" value="3" id="strict-slider">\n'
        '    <div class="strict-ticks"><span>0 off</span><span>1 exact</span><span>2 conservative</span><span>3 balanced</span><span>4 aggressive</span></div>\n'
        '  </div>\n'
        '  <div class="art-controls">\n'
        '    <span class="ctrl-label">Training record</span>\n'
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
        '    <div class="verdict-hd"><span class="verdict-badge" id="verdict-badge"></span><span class="verdict-code gloss" id="verdict-code"></span></div>\n'
        '    <div class="verdict-why" id="verdict-sub"></div>\n'
        '  </div>\n'
        '  <div class="card"><div class="card-hd">Matched benchmark item &amp; evidence</div><div class="card-bd"><div id="match"></div></div></div>\n'
        '  <div class="text-view"><div class="card-hd" style="border-bottom:1px solid var(--line)">Training record — matched question key-words highlighted</div><div class="text-body" id="text-body"></div></div>\n'
        '  <div class="card" style="margin-top:13px"><div class="card-hd">Benchmark impact at this threshold</div><div class="card-bd">'
        '<div class="bench" id="bench"></div><div class="impact" id="impact"></div><div class="illus" id="illus"></div></div></div>\n'
        '  <details class="more">\n'
        '    <summary>Show corpus accounting across all ' + str(len(training)) + ' training records</summary>\n'
        '    <div class="more-bd">\n'
        '      <div class="acct-grid">\n'
        '        <div class="card"><div class="card-hd">Routing at current threshold</div><div class="card-bd" id="acct-disp"></div></div>\n'
        '        <div class="card"><div class="card-hd">Removed / review / kept across thresholds</div><div class="card-bd" id="sweep"></div></div>\n'
        '      </div>\n'
        '    </div>\n'
        '  </details>\n'
        '</div>\n'
        '<script>' + JS + '</script>\n'
        '</body>\n</html>\n'
    )


if __name__ == "__main__":
    print("Building decontamination corpus...")
    training = D.build_sample()
    print("Generating {}...".format(OUTPUT_PATH))
    html = build_html(training)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    n_syn = sum(1 for a in training if a["kind"] == "synthetic")
    print("\nDone. {} written ({} benchmark items; {} training: {} synthetic + {} real).".format(
        OUTPUT_PATH, len(D.BENCHMARK), len(training), n_syn, len(training) - n_syn))
