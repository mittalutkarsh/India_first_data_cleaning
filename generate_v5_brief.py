"""Generate v5_brief.html — V5 mixture & curriculum specification brief,
written in a formal research-proposal register on the shared house style."""

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
    '  <a href="v5_brief.html" class="active">V5 Plan</a>\n'
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
.phead { padding:34px 0 14px; border-bottom:2px solid var(--ink); }
.eyebrow { font-family:"IBM Plex Mono",monospace; font-size:11px; letter-spacing:.13em; text-transform:uppercase; color:var(--marigold); font-weight:600; }
.phead h1 { font-family:"Spectral",serif; font-weight:700; font-size:clamp(26px,3.6vw,38px); margin:8px 0 8px; }
.phead .dek { font-size:15px; color:#33334a; margin:0; }
.sec { margin:30px 0 0; } .sec h2 { font-family:"Spectral",serif; font-size:22px; margin:0 0 8px; }
p { margin:14px 0; } strong { font-weight:600; }
.tbl { width:100%; border-collapse:collapse; font-size:14px; background:#fff; border:1px solid var(--line); border-radius:12px; overflow:hidden; margin:14px 0; }
.tbl th, .tbl td { text-align:left; padding:10px 14px; border-bottom:1px solid var(--line); vertical-align:top; }
.tbl th { font-family:"IBM Plex Mono",monospace; font-size:10px; letter-spacing:.06em; text-transform:uppercase; color:var(--muted); background:var(--panel); }
.tbl td:first-child { font-weight:600; white-space:nowrap; }
.callout { margin:16px 0; border-left:3px solid var(--marigold); background:#fdf9f1; border-radius:0 8px 8px 0; padding:12px 16px; font-size:14px; color:#4a3a1e; }
.foot { margin-top:30px; padding-top:16px; border-top:1px solid var(--line); font-size:13.5px; color:var(--muted); }
code { font-family:"IBM Plex Mono",monospace; font-size:12.5px; background:var(--panel); padding:1px 5px; border-radius:4px; }
"""

COMPONENTS = [
    ("Budget allocation", "A share of the token budget is assigned to each capability lane — general web, code, STEM, agentic, reasoning, Indic, and safety — with the shares summing to 100%."),
    ("Indic decomposition", "The Indic allocation is reported across four provenance tiers — verified, unverified web, translated, and synthetic — rather than as a single figure."),
    ("Scarce lanes", "The agentic, reasoning, and long-context requirements are stated explicitly, and each is mapped to the dataset or generation process that supplies it."),
    ("Protected minima", "Per-lane and per-language floors are specified and enforced at batch granularity, below which the online selector may not reduce a lane."),
    ("Annealing reserve", "A reserve of high-quality data is held within the budget and admitted only during the final low-learning-rate phase."),
    ("Difficulty and length bands", "Data is banded by measured difficulty and by reasoning length, with the operational definition of each band stated."),
    ("Curriculum schedule", "The mixture is specified per phase, with defined, gradual transitions between adjacent phases."),
    ("Validation protocol", "Every quantity is designated a hypothesis to be tested at the 1B and 3B scales before it is committed at full scale."),
]


def build_html():
    comp_rows = "".join("<tr><td>%s</td><td>%s</td></tr>\n" % (n, d) for n, d in COMPONENTS)
    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>V5 Mixture &amp; Curriculum — Specification Brief</title>\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link href="https://fonts.googleapis.com/css2?family=Spectral:wght@600;700'
        '&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">\n'
        '<style>' + CSS + '</style>\n</head>\n<body>\n' + NAV +
        '<div class="wrap">\n'
        '  <div class="phead">\n'
        '    <div class="eyebrow">V5 mixture &amp; curriculum</div>\n'
        '    <h1>Specification Brief</h1>\n'
        '    <p class="dek">The required components of the V5 data-mixture and curriculum plan, and the rationale for each.</p>\n'
        '  </div>\n'

        '  <div class="sec">\n'
        '    <h2>1. Motivation</h2>\n'
        '    <p>The allocation of a fixed pre-training token budget across capability domains is the principal determinant '
        'of model behaviour. Architectural choices are now largely standardised and contribute comparatively little to the '
        'final capability profile; the composition and ordering of the training data do not. Because the budget is fixed, '
        'every allocation to one capability is necessarily withdrawn from another. The mixture is therefore a capacity '
        'decision rather than a configuration detail, and it determines the resulting model’s behaviour more directly than '
        'any other design choice available at this stage.</p>\n'
        '  </div>\n'

        '  <div class="sec">\n'
        '    <h2>2. Scope</h2>\n'
        '    <p>This plan concerns a single training run of approximately 3 trillion update tokens, encompassing the '
        'pre-training, mid-training, and annealing phases. Supervised fine-tuning, preference optimisation, and '
        'reinforcement learning are treated in later stages and are outside the scope of this document. Unless stated '
        'otherwise, quoted token counts denote parameter-update tokens; the candidate pool screened by the online data '
        'selector is correspondingly larger.</p>\n'
        '  </div>\n'

        '  <div class="sec">\n'
        '    <h2>3. Required components</h2>\n'
        '    <p>A complete specification comprises the following components. Each is elaborated, with quantities, in the '
        'accompanying plan (<code>V5_PLAN.md</code>) and construction procedure.</p>\n'
        '    <table class="tbl"><tr><th style="width:22%">Component</th><th>Requirement</th></tr>\n' + comp_rows + '</table>\n'
        '  </div>\n'

        '  <div class="sec">\n'
        '    <h2>4. Rationale for a large general-web allocation</h2>\n'
        '    <p>A substantial general-web allocation is retained deliberately. General world knowledge and commonsense '
        'reasoning are concentrated in heterogeneous web text and are not adequately represented in code, mathematical, or '
        'agentic corpora. A model trained predominantly on code and tool-use data acquires strong procedural competence but '
        'insufficient world knowledge, and consequently fails on tasks that require commonsense inference. The general-web '
        'allocation is thus a requirement for general capability, not a residual.</p>\n'
        '  </div>\n'

        '  <div class="sec">\n'
        '    <h2>5. Treatment of supply constraints</h2>\n'
        '    <p>Desired allocations must be distinguished from executable allocations. A lane’s executable share is bounded '
        'by its unique eligible supply and a permitted repetition limit; where the desired share exceeds this bound, the '
        'lane is supply-constrained and the specification must record it as such rather than assert an infeasible figure. '
        'The agentic, reasoning, and long-context lanes are supply-constrained under current inventory, and the plan '
        'addresses each through generation, distillation, and — for long context — reclassification as a per-phase packing '
        'constraint rather than an independent lane.</p>\n'
        '    <div class="callout">Published corpus sizes are treated as upper bounds. Effective inventory is established '
        'only after licensing, deduplication, quality filtering, contamination removal, re-tokenisation with the target '
        'tokenizer, and loss-masking are accounted for.</div>\n'
        '  </div>\n'

        '  <div class="sec">\n'
        '    <h2>6. Basis of assessment</h2>\n'
        '    <p>The plan is assessed on the quality of its justification rather than on adherence to any prescribed values. '
        'Each quantity is expected to withstand scrutiny from an informed reviewer. Allocations that the available inventory '
        'cannot support, quantities asserted without supporting evidence, and any curriculum decision presented without a '
        'validation path are treated as deficiencies. The submission is a written specification whose numbers are '
        'defensible individually.</p>\n'
        '  </div>\n'

        '  <div class="foot">Companion documents: the construction procedure '
        '(<a href="v5_playbook.html">V5 Plan — Proposal</a>), the full plan (<code>V5_PLAN.md</code>), and a verification '
        'script (<code>mixture.py</code>) that derives the global mixture from the phase mixtures and validates every '
        'invariant.</div>\n'
        '</div>\n</body>\n</html>\n'
    )


if __name__ == "__main__":
    with open("v5_brief.html", "w", encoding="utf-8") as f:
        f.write(build_html())
    print("Done. v5_brief.html written.")
