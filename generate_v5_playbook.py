"""Generate v5_playbook.html — the procedure for constructing the V5 plan,
in a formal research-proposal register on the shared house style."""

BUDGET_B = 3000.0

# lane, share%, selector keep-fraction, unique-eligible tokens (B), note
PANTRY = [
    ("General web", 37, 0.5, 8000, "ample after deduplication"),
    ("Code", 22, 0.5, 600, "Stack v2, after licensing and deduplication"),
    ("STEM", 12, 0.5, 350, "textbooks and scientific text"),
    ("Agentic", 13, 1.0, 0.08, "must be generated; scraping is insufficient"),
    ("Reasoning", 7, 0.5, 30, "distilled traces; requires scaling"),
    ("Indic", 8, 1.0, 150, "predominantly unverified web; verified tier is limited"),
    ("Safety", 1, 1.0, 15, "curated"),
]

# Surveyed July 2026 (see Sources in Section 1). name, lane, size, metric, best score (date)
BENCHMARKS = [
    ("SWE-bench Verified", "code", "500 verified GitHub issues", "resolved rate (hidden tests pass)", "~76% pass@1, ~81% pass@3 (Jan 2026); frontier 71–77%"),
    ("Terminal-Bench v2", "agentic", "89 terminal tasks", "sandbox task success", "hard; frontier well below human"),
    ("&tau;-bench", "agentic", "165 (115 retail, 50 airline)", "pass^k (all k runs pass)", "frontier pass^1 &lt; 70%; GPT-4o retail 60% &rarr; 25% (pass^1&rarr;pass^8)"),
    ("BFCL v4", "agentic", "function-calling suite", "weighted acc. (agentic 40%, multi-turn 30%)", "continuous leaderboard"),
    ("GAIA", "agentic", "466 questions, 3 levels", "exact-match (tools + web allowed)", "humans ~92%; public agents trail"),
    ("AIME", "reasoning", "30 problems / year", "accuracy", "year-rotated; strong reasoning models high"),
    ("FrontierMath", "reasoning", "338 (295 Tiers 1–3 + 43 Tier 4)", "accuracy", "&gt;50% Tiers 1–3, 25–40% Tier 4 (mid-2026); ~0–6% in 2025"),
    ("MMLU", "general web", "15,908 Q, 57 subjects", "accuracy", "saturated at the top; kept for regression"),
    ("MMLU-Pro", "general web", "12,000+ Q, 14 domains", "accuracy", "harder than MMLU; still has headroom"),
    ("MILU", "indic", "~85,000 MCQs, 11 languages", "accuracy", "Indic understanding; below English MMLU"),
    ("IndicGenBench", "indic", "generation, 29 languages", "chrF / ROUGE / EM", "reference-based; generative"),
]

PROXIES = [
    ("code", "SWE-bench Verified", "HumanEval, MBPP", "164 / ~974 problems"),
    ("reasoning", "AIME, FrontierMath", "GSM8K, MATH-500", "1,319 test / 500 problems"),
    ("general web", "MMLU-Pro", "MMLU", "15,908 questions"),
    ("indic", "MILU, IndicGenBench", "MILU (subset)", "subset of ~85k"),
    ("agentic", "Terminal-Bench, &tau;-bench", "scripted tool-call success rate", "in-house set"),
]

NAV = (
    '<div class="nav"><div class="nav-in">\n'
    '  <span class="brand">India-First 40B</span>\n'
    '  <a href="overview.html">Overview</a>\n'
    '  <a href="data.html">Data</a>\n'
    '  <a href="index.html">Cleaning</a>\n'
    '  <a href="language.html">Language</a>\n'
    '  <a href="quality.html">Quality</a>\n'
    '  <a href="dedup.html">Dedup</a>\n'
    '  <a href="pii.html">PII</a>\n'
    '  <a href="decontam.html">Decontam</a>\n'
    '  <a href="tokenizer.html">Tokenizer</a>\n'
    '  <a href="manifest.html">Manifest</a>\n'
    '  <a href="v5_brief.html">V5 Plan</a>\n'
    '  <a href="v5_playbook.html" class="active">V5 Plan — Procedure</a>\n'
    '</div></div>\n'
)

CSS = """
:root { --bg:#FAFBFD; --ink:#16162A; --indigo:#2E357E; --indigo-soft:#6169B8; --marigold:#E0982B;
  --teal:#147D74; --rose:#B5476B; --line:#E3E4EE; --muted:#656579; --panel:#F1F2F8; }
*, *::before, *::after { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--ink); font-family:"Inter",system-ui,sans-serif; font-size:15px; line-height:1.65; -webkit-font-smoothing:antialiased; }
a { color:var(--indigo); text-decoration:none; } a:hover { text-decoration:underline; }
.nav { position:sticky; top:0; z-index:50; background:rgba(250,251,253,.96); border-bottom:1px solid var(--line); }
.nav-in { max-width:1280px; margin:0 auto; padding:10px 24px; display:flex; align-items:center; gap:13px; flex-wrap:wrap; }
.brand { font-family:"Spectral",serif; font-weight:700; color:var(--indigo); font-size:16px; margin-right:auto; }
.nav a { font-family:"IBM Plex Mono",monospace; font-size:11px; letter-spacing:.02em; color:var(--muted); padding:3px 2px; border-bottom:2px solid transparent; }
.nav a:hover { color:var(--ink); text-decoration:none; } .nav a.active { color:var(--indigo); border-bottom-color:var(--marigold); }
.wrap { max-width:820px; margin:0 auto; padding:0 24px 80px; }
.crumb { font-family:"IBM Plex Mono",monospace; font-size:11px; color:var(--muted); padding:18px 0 0; }
.phead { padding:8px 0 14px; border-bottom:2px solid var(--ink); }
.eyebrow { font-family:"IBM Plex Mono",monospace; font-size:11px; letter-spacing:.13em; text-transform:uppercase; color:var(--marigold); font-weight:600; }
.phead h1 { font-family:"Spectral",serif; font-weight:700; font-size:clamp(26px,3.6vw,38px); margin:8px 0 8px; }
.phead .dek { font-size:15px; color:#33334a; margin:0; }
.sec { margin:28px 0 0; } .sec h2 { font-family:"Spectral",serif; font-size:20px; margin:0 0 6px; }
h3 { font-size:15px; margin:22px 0 4px; color:var(--indigo); }
p { margin:13px 0; } strong { font-weight:600; }
ol, ul { margin:12px 0; padding-left:22px; } li { margin:6px 0; }
.diagram { background:var(--panel); border:1px solid var(--line); border-radius:10px; padding:14px 16px; overflow-x:auto; margin:16px 0; }
.diagram pre { margin:0; font-family:"IBM Plex Mono",monospace; font-size:12px; line-height:1.55; color:#26263c; white-space:pre; }
.tblwrap { overflow-x:auto; }
.egbox { border:1px solid var(--line); border-left:3px solid var(--indigo-soft); border-radius:0 8px 8px 0; background:#fff; padding:11px 14px; margin:10px 0; font-size:13.5px; line-height:1.55; }
.yes { color:var(--teal); font-weight:600; } .no { color:var(--rose); font-weight:600; }
.q { font-family:"IBM Plex Mono",monospace; font-size:12.5px; }
.tbl { width:100%; border-collapse:collapse; font-family:"IBM Plex Mono",monospace; font-size:13px; background:#fff; border:1px solid var(--line); border-radius:12px; overflow:hidden; margin:16px 0; }
.tbl th, .tbl td { padding:8px 11px; border-bottom:1px solid var(--line); text-align:right; }
.tbl th:first-child, .tbl td:first-child { text-align:left; }
.tbl th { font-size:10px; letter-spacing:.05em; text-transform:uppercase; color:var(--muted); background:var(--panel); }
.b { font-weight:600; padding:1px 7px; border-radius:5px; }
.b-ok { background:#e6f5ef; color:#0f7a54; } .b-tight { background:#fbeede; color:#9a5a12; }
.b-starved { background:#fceef2; color:var(--rose); } .b-inf { background:#f7e0e6; color:#8a1a3a; }
.cap { font-size:13px; color:var(--muted); margin-top:-6px; font-style:italic; }
.callout { margin:16px 0; border-left:3px solid var(--marigold); background:#fdf9f1; border-radius:0 8px 8px 0; padding:12px 16px; font-size:14px; color:#4a3a1e; }
.foot { margin-top:30px; padding-top:16px; border-top:1px solid var(--line); font-size:13.5px; color:var(--muted); }
code { font-family:"IBM Plex Mono",monospace; font-size:12.5px; background:var(--panel); padding:1px 5px; border-radius:4px; }
"""


def pantry_rows():
    out = ""
    for lane, share, keep, avail, note in PANTRY:
        trained = share / 100 * BUDGET_B
        presented = trained / keep
        executable = min(trained, avail * 4)
        if executable < trained * 0.5:
            cls, lab = "b-inf", "INFEASIBLE"
        elif executable < trained * 0.999:
            cls, lab = "b-starved", "STARVED"
        elif presented > avail * 1.5:
            cls, lab = "b-tight", "TIGHT"
        else:
            cls, lab = "b-ok", "ENOUGH"
        avail_s = ("%.2fB" % avail) if avail < 1 else "{:,}B".format(int(avail))
        out += ("<tr><td>%s</td><td>%d%%</td><td>~%dB</td><td>~%dB</td><td>~%s</td>"
                "<td><span class=\"b %s\">%s</span></td></tr>\n"
                % (lane, share, round(trained), round(presented), avail_s, cls, lab))
    return out


def bench_rows():
    return "".join(
        "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>\n" % b
        for b in BENCHMARKS)


def proxy_rows():
    return "".join(
        "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>\n" % p
        for p in PROXIES)


def build_html():
    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>Constructing the V5 Plan — Procedure</title>\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link href="https://fonts.googleapis.com/css2?family=Spectral:wght@600;700'
        '&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">\n'
        '<style>' + CSS + '</style>\n</head>\n<body>\n' + NAV +
        '<div class="wrap">\n'
        '  <div class="crumb"><a href="v5_brief.html">V5 Plan</a> / Construction procedure</div>\n'
        '  <div class="phead">\n'
        '    <div class="eyebrow">V5 mixture &amp; curriculum</div>\n'
        '    <h1>Construction Procedure</h1>\n'
        '    <p class="dek">The recommended order of construction, and the supply analysis that constrains the '
        'allocation. Quantities use an illustrative 3-trillion update-token budget.</p>\n'
        '  </div>\n'

        '  <div class="sec"><h2>1. Define the target benchmarks</h2>\n'
        '    <p>The specification is written backward from a fixed set of benchmarks. This section states how that set '
        'is chosen, records the actual benchmarks with their sizes and current best scores, and traces one benchmark '
        'instance end to end so that the token accounting used later is concrete. Figures were collected in July 2026 '
        'and are cited at the end of the section; where a state-of-the-art score moves quickly, the date is attached to '
        'the number.</p>\n'

        '    <h3>1.1 Selection procedure</h3>\n'
        '    <p>A capability lane admits a benchmark only if the benchmark passes five tests. Each test is stated once, '
        'then shown with a benchmark it admits and a benchmark it rejects.</p>\n'

        '    <p><strong>1. Direct measurement.</strong> The benchmark must exercise the capability itself, not a proxy '
        'for it.</p>\n'
        '    <div class="egbox"><span class="yes">Admitted &mdash; SWE-bench.</span> The model receives a real bug '
        'report and the full repository, must return a code patch, and 44 unit tests are executed on that patch. Fixing '
        'the bug is the capability; running the tests measures it directly.<br>\n'
        '    <span class="no">Rejected &mdash; a Python quiz.</span> <span class="q">&ldquo;Which keyword defines a '
        'function? (a) def &nbsp;(b) func &nbsp;(c) function &nbsp;(d) lambda&rdquo;</span> A model can pick (a) from '
        'memory while being unable to write a function that runs. The quiz measures recognition, which only correlates '
        'with the skill we want.</div>\n'

        '    <p><strong>2. Machine-checkable metric.</strong> The score must come from execution or a verifier, not a '
        'human or model rating.</p>\n'
        '    <div class="egbox"><span class="yes">Admitted &mdash; GSM8K.</span> The gold answer is a number, for '
        'example <span class="q">18</span>. The harness reads the model&rsquo;s final number and checks it equals 18 &mdash; '
        'same input, same score, every time, in milliseconds.<br>\n'
        '    <span class="no">Rejected &mdash; &ldquo;rate this answer 1&ndash;5&rdquo;.</span> Two graders, or two runs '
        'of an LLM judge, return 3 and 4 for the same answer. The score is not reproducible, so it cannot be trusted '
        'inside a cheap proxy run.</div>\n'

        '    <p><strong>3. Contamination resistance.</strong> There must be a held-out, temporal, or private variant, so '
        'the score cannot be obtained by training on the test.</p>\n'
        '    <div class="egbox"><span class="yes">Admitted &mdash; SWE-bench Live.</span> It draws GitHub issues created '
        '<em>after</em> the model&rsquo;s data cutoff, so the model could not have seen them during training.<br>\n'
        '    <span class="no">Rejected &mdash; a fixed public quiz already in the crawl.</span> If the 500 questions sit '
        'in Common Crawl, a model can memorise the answer key and report 95% while having learned nothing. The number '
        'describes recall of the test, not capability.</div>\n'

        '    <p><strong>4. Public and reproducible.</strong> The items, harness, and metric must be published, so a '
        'reported number can be rerun.</p>\n'
        '    <div class="egbox"><span class="yes">Admitted &mdash; HumanEval.</span> 164 problems and the grading '
        'harness are on GitHub; anyone reruns them and gets the same figure.<br>\n'
        '    <span class="no">Rejected &mdash; a vendor eval reported only as &ldquo;92%&rdquo;.</span> With no items and '
        'no harness, the 92% cannot be checked or compared against our own model.</div>\n'

        '    <p><strong>5. Headroom.</strong> The frontier score must sit below about 90%, or there is no gradient left '
        'to optimise against.</p>\n'
        '    <div class="egbox"><span class="yes">Admitted &mdash; FrontierMath Tier 4.</span> The best systems score '
        '25&ndash;40% (mid-2026), so an improvement from 30% to 40% is real signal.<br>\n'
        '    <span class="no">Rejected as a primary target &mdash; original GSM8K.</span> Frontier models already reach '
        '~97%; moving 97.0 to 97.3 tells us almost nothing. It is still useful as a small-scale proxy (see §1.5).</div>\n'

        '    <p>Each admitted benchmark is recorded with six fields. Filled in for SWE-bench Verified:</p>\n'
        '    <div class="diagram"><pre>\n'
        'version .......... SWE-bench Verified (500), snapshot 2024-08\n'
        'size ............. 500 issues\n'
        'metric ........... resolved rate (all hidden tests pass)\n'
        'best score (date)  ~76% pass@1 (Jan 2026)\n'
        'decontamination .. repository-disjoint; prefer the Live / temporal variant\n'
        '1B/3B proxy ...... HumanEval, MBPP\n'
        '</pre></div>\n'

        '    <p>Each benchmark, and later each training document, is filed under exactly one primary lane. Take a '
        'concrete document: a 12,000-token Hindi tutorial that walks through fixing a Python sorting bug with '
        'step-by-step reasoning. It touches four capabilities at once &mdash; Indic, code, reasoning, and long-context. '
        'The rule files it under one primary lane (code, its core task) and stores the rest as tags '
        '<span class="q">{language: hi, reasoning: yes, length: long}</span>.</p>\n'
        '    <div class="egbox"><span class="no">Without the rule:</span> the same 12,000 tokens are counted in code '
        '<em>and</em> Indic <em>and</em> reasoning <em>and</em> long-context = 48,000 counted tokens, and the budget in '
        '§5 is inflated 4&times;.<br>\n'
        '    <span class="yes">With the rule:</span> 12,000 tokens counted once, under code; the tags still let the plan '
        'report how much code data is also Indic or long.</div>\n'

        '    <h3>1.2 The benchmark set</h3>\n'
        '    <div class="diagram"><pre>\n'
        'CAPABILITY LANE        TARGET BENCHMARK(S)                  SUPPLYING DATASET\n'
        '---------------        ---------------------------          -------------------------------\n'
        'code            -----> SWE-bench Verified (500)       <---- Stack v2 + generated repo-fix traces\n'
        '                       SWE-bench Pro / Live (temporal)\n'
        'agentic         -----> Terminal-Bench (89), GAIA (466) <--- generated tool-use trajectories\n'
        '                       tau-bench (165), BFCL v4              (plan + act + reflect)\n'
        'reasoning/math  -----> AIME (30/yr), FrontierMath (338) <--- distilled step-by-step traces\n'
        'general web     -----> MMLU (15,908), MMLU-Pro (12k+)  <---- DCLM / FineWeb\n'
        'indic           -----> MILU (~85k), IndicGenBench (29)  <--- Sangraha / IndicCorp / Wikipedia\n'
        '</pre></div>\n'
        '    <p>The arrow direction is the substance of the plan: the benchmark on the left fixes the capability, and '
        'the dataset on the right is chosen to satisfy it.</p>\n'

        '    <h3>1.3 Benchmark inventory</h3>\n'
        '    <div class="tblwrap"><table class="tbl"><tr><th>Benchmark</th><th>Lane</th><th>Size</th><th>Metric</th>'
        '<th>Best score (date)</th></tr>\n' + bench_rows() + '</table></div>\n'
        '    <p>Two design consequences follow. First, the code and agentic lanes are graded by execution and the '
        'reasoning lanes by exact answers; the model is scored on what it produces, not on the tool logs it reads, which '
        'is why §3 counts loss-bearing tokens rather than raw trace size. Second, the Indic lane is measured by MILU '
        '(understanding) and IndicGenBench (generation) together, because a high MILU score with weak generation would '
        'describe a model that recognises Hindi but cannot write it; Indic results are therefore reported as a '
        'macro-average across languages and a worst-language figure, not a single average.</p>\n'

        '    <h3>1.4 One instance, traced end to end</h3>\n'
        '    <p>The phrase &ldquo;resolved rate on 500 issues&rdquo; hides what a single graded item is. One '
        'representative SWE-bench Verified instance, with concrete numbers:</p>\n'
        '    <div class="diagram"><pre>\n'
        'INSTANCE (representative)\n'
        'repository at a fixed commit ..... ~1,400 Python files, ~600,000 lines\n'
        'issue text handed to the model ... ~180 words   [CONTEXT: read, no loss taken]\n'
        'required output (gold patch) ..... diff over 2 files, +14 / -3 lines\n'
        '                                   [SUPERVISED TARGET: loss taken on these tokens]\n'
        'grading in a sandbox ............. 3 fail-to-pass tests  (must flip fail -> pass)\n'
        '                                  41 pass-to-pass tests  (must not regress)\n'
        'resolved = 1 if all 44 tests pass, else 0\n\n'
        'benchmark score = mean resolved over 500 instances\n'
        '                = 380 / 500 = 0.76        (the ~76% figure, made concrete)\n'
        '</pre></div>\n'
        '    <p>This fixes three quantities the plan depends on. The trainable content per item is small: the 600,000-line '
        'repository is read as context, and the supervised target is a 17-line diff, so a code sample contributes far '
        'fewer loss-bearing tokens than its raw size implies (§3). The reward is verifiable, computed by executing 44 '
        'tests, so the same item can be scored inside a cheap proxy run. And the supplying dataset is defined by the '
        'target: Stack v2 provides raw code but not the issue-to-patch structure, so the code lane also requires '
        'generated repository-fix trajectories, recorded as a supply gap in §6.</p>\n'

        '    <h3>1.5 Proxy benchmarks for the 1B and 3B runs</h3>\n'
        '    <p>The headline benchmarks return near-zero at 1B and cannot decide anything during validation (§10). '
        'Concretely, at 1B a model resolves 0 of 500 SWE-bench issues &mdash; it cannot yet produce a working patch &mdash; '
        'so the score is 0 for every recipe and cannot separate them. On HumanEval the same 1B model solves roughly '
        '15&ndash;20 of 164 problems, and that number does move between recipes, so it can rank them. Each lane therefore '
        'names a proxy with signal at small scale.</p>\n'
        '    <div class="tblwrap"><table class="tbl"><tr><th>Lane</th><th>Headline benchmark</th><th>1B/3B proxy</th>'
        '<th>Proxy size</th></tr>\n' + proxy_rows() + '</table></div>\n'
        '    <p>The proxy establishes the direction of an effect and the rank of two recipes, never the absolute number, '
        'because rankings shift with scale.</p>\n'

        '    <h3>1.6 What this method does not do</h3>\n'
        '    <ul>\n'
        '      <li><strong>A benchmark set can be over-fit.</strong> Composing data backward from a fixed set risks '
        'teaching the test format. For example, train on 5,000 paraphrased copies of the SWE-bench issue texts and the '
        'reported resolved rate can rise ten points while the model is no better at unseen bugs. §11 pairs this method '
        'with a decontamination policy and a private, temporally held-out set; without that pairing, a reported gain is '
        'not trustworthy.</li>\n'
        '      <li><strong>It measures only listed capabilities.</strong> Anything absent from the set is invisible to '
        'the plan. For example, nothing here measures legal drafting or Hindi poetry, so the plan cannot tell whether '
        'the model can do them. General-web coverage (MMLU, MMLU-Pro) is retained partly to guard against regressing '
        'capabilities no targeted benchmark names.</li>\n'
        '      <li><strong>Generative Indic quality is only partly machine-checkable.</strong> IndicGenBench uses '
        'reference-based metrics (chrF, ROUGE) that correlate imperfectly with human judgement. For example, two correct '
        'Hindi translations of one English sentence can score chrF 0.55 and 0.72 purely from word choice, so a lower '
        'score need not mean a worse translation. The Indic result therefore carries more uncertainty than the '
        'execution-graded lanes and is flagged as such.</li>\n'
        '    </ul>\n'

        '    <p class="cap">Sources: SWE-bench Verified (<a href="https://epoch.ai/benchmarks/swe-bench-verified">Epoch AI</a>, '
        '<a href="https://arxiv.org/abs/2310.06770">Jimenez et&nbsp;al.</a>); Terminal-Bench '
        '(<a href="https://arxiv.org/abs/2601.11868">arXiv</a>); &tau;-bench '
        '(<a href="https://github.com/sierra-research/tau2-bench">Sierra</a>); BFCL '
        '(<a href="https://gorilla.cs.berkeley.edu/leaderboard.html">Gorilla</a>); GAIA '
        '(<a href="https://arxiv.org/abs/2311.12983">arXiv</a>); FrontierMath '
        '(<a href="https://epoch.ai/frontiermath/the-benchmark">Epoch AI</a>); MMLU-Pro '
        '(<a href="https://arxiv.org/abs/2406.01574">arXiv</a>); MILU '
        '(<a href="https://arxiv.org/abs/2411.02538">arXiv</a>); IndicGenBench '
        '(<a href="https://arxiv.org/abs/2404.16816">arXiv</a>).</p>\n'
        '  </div>\n'

        '  <div class="sec"><h2>2. Map each benchmark to a dataset</h2>\n'
        '    <p>Each target is associated with the dataset that develops the corresponding capability — a procedure '
        'sometimes termed composing backward. A capability lane without an identified source dataset is not a plan but an '
        'aspiration, and is recorded as such.</p></div>\n'

        '  <div class="sec"><h2>3. Establish the trainable inventory</h2>\n'
        '    <p>Effective inventory is measured, not assumed. Published corpus sizes are upper bounds; the usable quantity '
        'is reduced by licensing, deduplication, quality filtering, contamination removal, and re-tokenisation. Two '
        'measures are recorded per lane: the number of samples (variety) and the number of tokens (depth). For chat and '
        'agent data, only the model-generated positions are supervised — user turns and tool outputs are loss-masked — so '
        'the loss-bearing token count is materially smaller than the raw trace size. In ordinary causal pre-training, by '
        'contrast, every position is a training target.</p></div>\n'

        '  <div class="sec"><h2>4. Specify the allocation</h2>\n'
        '    <p>A share of the budget is assigned to each lane, summing to 100%, and each share is expressed in tokens '
        '(share &times; budget) so that it can be reconciled against inventory.</p></div>\n'

        '  <div class="sec"><h2>5. Apply the selector keep-fraction and reconcile against supply</h2>\n'
        '    <p>The online selector retains only a fraction of the data it screens; consequently the quantity that must be '
        '<em>presented</em> exceeds the quantity <em>trained</em> on. At a keep-fraction of 0.5, presented = trained &divide; '
        '0.5. Reconciling presented tokens against unique available supply is the decisive check, and it materially '
        'changes the assessment of the code and STEM lanes.</p>\n'
        '    <table class="tbl"><tr><th>Lane</th><th>Share</th><th>Trained</th><th>Presented</th><th>Unique avail.</th><th>Status</th></tr>\n'
        + pantry_rows() +
        '    </table>\n'
        '    <p class="cap">Presented = trained &divide; selector keep-fraction. Status compares presented tokens against '
        'unique eligible supply and the permitted repetition limit (≤4 epochs).</p></div>\n'

        '  <div class="sec"><h2>6. Classify lane feasibility</h2>\n'
        '    <p>The reconciliation identifies which lanes are supply-constrained. The <strong>agentic</strong> lane is '
        'infeasible under current inventory: at approximately 2,000 trainable tokens per trajectory, the requirement '
        'corresponds to on the order of 10<sup>8</sup> trajectories, which cannot be obtained by scraping. The '
        '<strong>reasoning</strong> lane is starved. <strong>Long context</strong> is not represented as a lane at all: '
        'sequence length is a property that data in other lanes already possesses (a long legal document in Indic is both '
        'Indic and long), and treating it as an independent lane double-counts tokens. It is instead specified as a '
        'per-phase packing constraint. The principal remedy for the constrained lanes is generation and distillation; the '
        'most efficient lever is trace design, since trajectories that include planning, reasoning, and reflection yield '
        'several times more trainable tokens per trajectory than bare tool calls.</p></div>\n'

        '  <div class="sec"><h2>7. Decompose the Indic allocation</h2>\n'
        '    <p>The Indic allocation is reported across four provenance tiers. The verified tier binds hardest: genuinely '
        'verified material across the target languages amounts to only a few billion unique tokens, so at a repetition '
        'limit of four epochs the maximum trainable verified quantity is small, and any larger verified figure would imply '
        'excessive repetition. The verified tier is therefore capped at its supported level and the remainder is carried '
        'by the unverified and translated tiers, with the associated quality risk stated. Per-language protection is '
        'expressed as minimum token counts, not as a per-language percentage of the total budget, since the latter would '
        'exceed the entire Indic allocation once summed across all languages.</p></div>\n'

        '  <div class="sec"><h2>8. Specify floors and the annealing reserve</h2>\n'
        '    <p>Protected minima are enforced at batch granularity rather than as run-level averages; a run-level floor '
        'permits the selector to suppress a lane throughout training and satisfy the constraint only in aggregate. Safety '
        'is represented as an explicit lane so that its floor is consistent with a mixture summing to 100%. The annealing '
        'reserve is held within the budget, not added to it, and its contribution is validated against a control run '
        'without annealing.</p></div>\n'

        '  <div class="sec"><h2>9. Define the curriculum phases</h2>\n'
        '    <p>The single mixture is expanded into a small number of phases — broad, general-web-dominant data first, '
        'followed by code, science, and reasoning, with the scarce lanes concentrated later and the premium data reserved '
        'for the final phase. Each phase specifies its own budget, maximum sequence length, and mixture summing to 100%; '
        'the budget-weighted average of the phase mixtures reproduces the global mixture. Transitions between phases are '
        'gradual, to avoid the gradient instability associated with abrupt distribution shifts. Difficulty is assigned by '
        'measurement — for example, the failure rate of a reference model, or pass@k on verifiable items — rather than by '
        'inspection, and the reasoning-depth label is defined by the shortest correct trace to avoid inducing length '
        'inflation.</p></div>\n'

        '  <div class="sec"><h2>10. Define the validation protocol</h2>\n'
        '    <p>Every quantity is treated as a hypothesis and tested at the 1B and 3B scales before full-scale commitment. '
        'Evaluations are chosen to exhibit signal at those scales; the most demanding benchmarks return near-zero at 1B '
        'and are uninformative there. Capability contrasts are amplified (for example, 4% versus 12% Indic) to establish '
        'the direction of an effect, and recipes are promoted on rank stability across scales rather than on absolute '
        'scores, which shift with scale.</p></div>\n'

        '  <div class="sec"><h2>11. Prioritise data acquisition</h2>\n'
        '    <p>The supply-constrained lanes define the acquisition queue for the cleaning pipeline, in order: agentic '
        'trajectory generation, reasoning-trace distillation, long-document collection, and additional verified Indic '
        'material (textbooks, government records, and news, since encyclopaedic text alone is insufficient). The mixture '
        'plan thereby determines the priorities of the upstream pipeline.</p></div>\n'

        '  <div class="callout">The complete plan is provided as <code>V5_PLAN.md</code>, and the arithmetic above is '
        'reproduced and validated by <code>mixture.py</code>, which derives the global mixture from the phase mixtures, '
        'applies the selector keep-fraction, and exits with an error if any phase mixture does not sum to 100% or any lane '
        'is infeasible.</div>\n'

        '  <div class="foot"><a href="v5_brief.html">&larr; Specification brief</a></div>\n'
        '</div>\n</body>\n</html>\n'
    )


if __name__ == "__main__":
    with open("v5_playbook.html", "w", encoding="utf-8") as f:
        f.write(build_html())
    print("Done. v5_playbook.html written.")
