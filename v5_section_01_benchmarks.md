# Section 1 — Defining the target benchmarks

The plan is written backward from a fixed set of benchmarks. This section states how that set is chosen, records the actual benchmarks with their sizes and current best scores, and traces one benchmark instance end to end so the accounting used later in the plan is concrete.

Numbers below were collected in July 2026 and are cited in the Sources list. Where a figure moves quickly (a state-of-the-art score), the date is attached to the number.

---

## 1.1 The selection procedure

A capability lane earns a benchmark only if the benchmark passes five tests:

1. **Direct measurement.** It measures the target capability itself, not a correlate. A coding lane is measured by whether a patch makes tests pass, not by a multiple-choice quiz about Python.
2. **Machine-checkable metric.** The score comes from code execution or a verifier, not a human or model rating. This keeps the signal reproducible and cheap to compute during proxy runs.
3. **Contamination resistance.** The benchmark has a held-out, temporal, or private variant, so a high score cannot be bought by training on the test.
4. **Public and reproducible.** The items, the harness, and the metric are published, so a reported number can be rerun.
5. **Headroom.** The frontier score is below about 90%. A benchmark that frontier models already saturate gives no gradient to optimize against.

Each admitted benchmark is recorded with six fields: version/snapshot, size, metric, current best score with its date, the decontamination rule, and a small-model proxy that produces signal at 1B and 3B (Section 10 explains why the headline benchmarks cannot serve that role).

Each benchmark is then assigned to exactly one **primary capability lane**. A benchmark that touches several capabilities (many do) is filed under the capability it most directly tests, and its other demands are recorded as tags. This one-lane rule is what keeps the token accounting in Section 5 from counting the same data twice.

---

## 1.2 The benchmark set (diagram first)

```
CAPABILITY LANE        TARGET BENCHMARK(S)                 SUPPLYING DATASET
─────────────────      ─────────────────────────────      ───────────────────────────
code            ─────► SWE-bench Verified (500)      ◄──── Stack v2 + generated repo-fix traces
                       SWE-bench Pro / Live (temporal)
agentic         ─────► Terminal-Bench (89)           ◄──── generated tool-use trajectories
                       τ-bench (165), BFCL v4               (plan + act + reflect)
                       GAIA (466)
reasoning/math  ─────► AIME (30/yr), FrontierMath (338) ◄── distilled step-by-step traces
general web     ─────► MMLU (15,908), MMLU-Pro (12k+) ◄──── DCLM / FineWeb
indic           ─────► MILU (~85k), IndicGenBench (29 langs) ◄─ Sangraha / IndicCorp / Wikipedia
```

The arrow direction is the point of the whole plan: the benchmark on the left fixes the capability, and the dataset on the right is chosen to satisfy it. Section 2 formalizes the right-hand column.

---

## 1.3 The benchmark inventory

| Benchmark | Lane | Size | Metric | Best score (date) | Contamination rule |
|---|---|---|---|---|---|
| SWE-bench Verified | code | 500 human-verified GitHub issues | resolved rate (hidden tests pass) | ~76% pass@1, ~81% pass@3 (Jan 2026); frontier 71–77% | repo-disjoint + prefer Live/temporal variant |
| Terminal-Bench (v2) | agentic | 89 hand-built terminal tasks | task success in a sandbox | (hard; frontier well below human) | held-out task set; no task text in training |
| τ-bench | agentic | 165 tasks (115 retail, 50 airline) | pass^k (all k runs succeed) | frontier pass^1 below 70%; GPT-4o retail ~60% pass^1 → ~25% pass^8 | dedup against published tool schemas |
| BFCL v4 | agentic | function-calling suite (multi-turn, web, memory) | weighted accuracy (agentic 40%, multi-turn 30%) | leaderboard, updated continuously | dedup against published API sets |
| GAIA | agentic | 466 questions, 3 levels | exact-match, tools+web allowed | humans ~92%; public agents trail | test answers withheld by the harness |
| AIME | reasoning | 30 problems/year (integer answers) | accuracy | strong reasoning models high; year-rotated | use held-out year; remove solutions |
| FrontierMath | reasoning | 338 (295 Tiers 1–3 + 43 Tier 4) | accuracy | >50% Tiers 1–3, 25–40% Tier 4 (mid-2026); ~0–6% in 2025 | problems + solutions excluded from training |
| MMLU | general web | 15,908 questions, 57 subjects | accuracy | saturated at the top; kept for regression | n-gram + near-dup removal vs test |
| MMLU-Pro | general web | 12,000+ questions, 14 domains | accuracy | harder MMLU; still has headroom | n-gram + near-dup removal vs test |
| MILU | indic | ~85,000 MCQs, 11 languages, 41 subjects | accuracy | Indic understanding; below English MMLU | n-gram + near-dup removal vs test |
| IndicGenBench | indic | generation across 29 languages | task-specific (ROUGE/chrF/EM) | generative, not MCQ | n-gram + near-dup removal vs test |

Two design notes fall directly out of this table.

First, the code and agentic lanes are measured by execution, and the reasoning lanes by exact answers. That is why Section 3 counts *loss-bearing* tokens rather than raw trace size: the model is graded on what it produces, not on the tool logs it reads.

Second, the Indic lane is measured by MILU (understanding) and IndicGenBench (generation) together, because a high MILU score with weak generation would describe a model that recognizes Hindi but cannot write it. The plan therefore reports Indic results as a macro-average across languages and a worst-language number, not a single Indic average.

---

## 1.4 One instance, traced end to end

The abstraction "resolved rate on 500 issues" hides what a single graded item actually is. Here is one representative SWE-bench Verified instance with concrete numbers.

```
INSTANCE (representative)
├── Repository at a fixed commit:  ~1,400 Python files, ~600,000 lines
├── Issue text handed to the model: ~180 words describing a bug
│      └─ this is CONTEXT — the model reads it, no loss is taken on it
├── Required output (the gold patch): a diff over 2 files, +14 / −3 lines
│      └─ this is the SUPERVISED TARGET — loss is taken on these tokens
└── Grading in a sandbox:
       3 fail-to-pass tests   (must flip from fail → pass)
      41 pass-to-pass tests   (must stay passing, i.e. no regression)
       resolved = 1  if all 44 pass, else 0
```

The instance score is a single bit. The benchmark score is the mean of that bit over 500 instances:

```
resolved_rate = (# instances with all tests passing) / 500
              = 380 / 500  = 0.76      ← the ~76% figure above, made concrete
```

This trace fixes three quantities the rest of the plan depends on:

- **Trainable content per item is small.** The repository (600K lines) is read, not trained on. The supervised target is a 17-line diff. A code-lane sample therefore contributes far fewer loss-bearing tokens than its raw size suggests, which is exactly the correction applied in Section 3.
- **The reward is verifiable.** The 44-test outcome is a hard label, computed by execution. No human or model judgment enters the loop, so the same item can be scored inside a cheap proxy run.
- **The supplying dataset is defined by the target.** To move this number, the plan needs many (repository, issue, gold-patch, tests) tuples. Stack v2 supplies raw code, but not the issue-to-patch structure, so the code lane also requires generated repository-fix trajectories. Section 6 records this as a supply gap.

---

## 1.5 Proxy benchmarks for the 1B and 3B runs

The headline benchmarks return near-zero at 1B, so they cannot decide anything during the cheap validation runs (Section 10). Each lane therefore also names a proxy that shows signal at small scale.

| Lane | Headline benchmark | 1B/3B proxy | Proxy size |
|---|---|---|---|
| code | SWE-bench Verified | HumanEval, MBPP | 164 / ~974 problems |
| reasoning | AIME, FrontierMath | GSM8K, MATH-500 | 1,319 test / 500 problems |
| general web | MMLU-Pro | MMLU | 15,908 questions |
| indic | MILU, IndicGenBench | MILU (subset) | subset of ~85k |
| agentic | Terminal-Bench, τ-bench | scripted tool-call success rate | in-house set |

The proxy is used only to establish the *direction* of an effect and the *rank* of two recipes, never the absolute number, because rankings shift with scale.

---

## 1.6 What this method does not do

The method has three known limits, stated so they are not mistaken for coverage.

- **A benchmark set can be over-fit.** Composing data backward from a fixed set risks teaching the test format rather than the capability. Section 11 pairs this method with a decontamination policy and a private, temporally-held-out set; without that pairing, any reported gain is suspect.
- **It measures only listed capabilities.** Anything absent from the set is invisible to the plan. General-web coverage (MMLU, MMLU-Pro) is kept partly as a guard against silently regressing the capabilities no targeted benchmark names.
- **Generative Indic quality is only partially machine-checkable.** IndicGenBench uses reference-based metrics (chrF, ROUGE) that correlate imperfectly with human judgment, so the Indic result carries more uncertainty than the execution-graded lanes, and is flagged as such rather than reported as a hard number.

---

## Sources

- SWE-bench Verified — Epoch AI benchmark page: https://epoch.ai/benchmarks/swe-bench-verified ; SWE-bench (Jimenez et al.): https://arxiv.org/abs/2310.06770
- Terminal-Bench: https://arxiv.org/abs/2601.11868 ; https://github.com/harbor-framework/terminal-bench
- τ-bench (Sierra) / τ²-bench: https://sierra.ai/blog/tau-bench-shaping-development-evaluation-agents ; https://github.com/sierra-research/tau2-bench
- Berkeley Function Calling Leaderboard (BFCL) v3/v4: https://gorilla.cs.berkeley.edu/leaderboard.html ; https://gorilla.cs.berkeley.edu/blogs/13_bfcl_v3_multi_turn.html
- GAIA (Mialon et al.): https://arxiv.org/abs/2311.12983
- FrontierMath (Epoch AI): https://epoch.ai/frontiermath/the-benchmark ; https://arxiv.org/abs/2411.04872
- MMLU-Pro (Wang et al.): https://arxiv.org/abs/2406.01574 ; MMLU (Hendrycks et al.): https://arxiv.org/abs/2009.03300
- MILU (AI4Bharat): https://arxiv.org/abs/2411.02538 ; https://github.com/AI4Bharat/MILU
- IndicGenBench (Google Research): https://arxiv.org/abs/2404.16816
- Proxies: HumanEval https://arxiv.org/abs/2107.03374 · MBPP https://arxiv.org/abs/2108.07732 · GSM8K https://arxiv.org/abs/2110.14168 · MATH https://arxiv.org/abs/2103.03874
