# Section 1 — Defining the target benchmarks

The plan is written backward from a fixed set of benchmarks. This section states how that set is chosen, records the actual benchmarks with their sizes and current best scores, and traces one benchmark instance end to end so the accounting used later in the plan is concrete. Every rule below is stated once and then shown on a real benchmark it admits and one it rejects.

Numbers below were collected in July 2026 and are cited in the Sources list. Where a figure moves quickly (a state-of-the-art score), the date is attached to the number.

---

## 1.1 The selection procedure

A capability lane admits a benchmark only if the benchmark passes five tests. Each test is stated once, then shown with a benchmark it admits and a benchmark it rejects.

**1. Direct measurement.** The benchmark must exercise the capability itself, not a proxy for it.

> ✅ **Admitted — SWE-bench.** The model receives a real bug report and the full repository, must return a code patch, and 44 unit tests are executed on that patch. Fixing the bug is the capability; running the tests measures it directly.
>
> ✗ **Rejected — a Python quiz.** *"Which keyword defines a function? (a) def (b) func (c) function (d) lambda"* — a model can pick (a) from memory while being unable to write a function that runs. The quiz measures recognition, which only correlates with the skill we want.

**2. Machine-checkable metric.** The score must come from execution or a verifier, not a human or model rating.

> ✅ **Admitted — GSM8K.** The gold answer is a number, for example `18`. The harness reads the model's final number and checks it equals 18 — same input, same score, every time, in milliseconds.
>
> ✗ **Rejected — "rate this answer 1–5".** Two graders, or two runs of an LLM judge, return 3 and 4 for the same answer. The score is not reproducible, so it cannot be trusted inside a cheap proxy run.

**3. Contamination resistance.** There must be a held-out, temporal, or private variant, so the score cannot be obtained by training on the test.

> ✅ **Admitted — SWE-bench Live.** It draws GitHub issues created *after* the model's data cutoff, so the model could not have seen them during training.
>
> ✗ **Rejected — a fixed public quiz already in the crawl.** If the 500 questions sit in Common Crawl, a model can memorise the answer key and report 95% while having learned nothing. The number describes recall of the test, not capability.

**4. Public and reproducible.** The items, harness, and metric must be published, so a reported number can be rerun.

> ✅ **Admitted — HumanEval.** 164 problems and the grading harness are on GitHub; anyone reruns them and gets the same figure.
>
> ✗ **Rejected — a vendor eval reported only as "92%".** With no items and no harness, the 92% cannot be checked or compared against our own model.

**5. Headroom.** The frontier score must sit below about 90%, or there is no gradient left to optimise against.

> ✅ **Admitted — FrontierMath Tier 4.** The best systems score 25–40% (mid-2026), so an improvement from 30% to 40% is real signal.
>
> ✗ **Rejected as a primary target — original GSM8K.** Frontier models already reach ~97%; moving 97.0 to 97.3 tells us almost nothing. It is still useful as a small-scale proxy (see §1.5).

Each admitted benchmark is recorded with six fields. Filled in for SWE-bench Verified:

```
version .......... SWE-bench Verified (500), snapshot 2024-08
size ............. 500 issues
metric ........... resolved rate (all hidden tests pass)
best score (date)  ~76% pass@1 (Jan 2026)
decontamination .. repository-disjoint; prefer the Live / temporal variant
1B/3B proxy ...... HumanEval, MBPP
```

Each benchmark, and later each training document, is filed under exactly one **primary lane**. Take a concrete document: a 12,000-token Hindi tutorial that walks through fixing a Python sorting bug with step-by-step reasoning. It touches four capabilities at once — Indic, code, reasoning, and long-context. The rule files it under one primary lane (code, its core task) and stores the rest as tags `{language: hi, reasoning: yes, length: long}`.

> ✗ **Without the rule:** the same 12,000 tokens are counted in code *and* Indic *and* reasoning *and* long-context = 48,000 counted tokens, and the budget in §5 is inflated 4×.
>
> ✅ **With the rule:** 12,000 tokens counted once, under code; the tags still let the plan report how much code data is also Indic or long.

---

## 1.2 The benchmark set (diagram first)

```
CAPABILITY LANE        TARGET BENCHMARK(S)                  SUPPLYING DATASET
---------------        ---------------------------          -------------------------------
code            -----> SWE-bench Verified (500)       <---- Stack v2 + generated repo-fix traces
                       SWE-bench Pro / Live (temporal)
agentic         -----> Terminal-Bench (89), GAIA (466) <--- generated tool-use trajectories
                       tau-bench (165), BFCL v4              (plan + act + reflect)
reasoning/math  -----> AIME (30/yr), FrontierMath (338) <--- distilled step-by-step traces
general web     -----> MMLU (15,908), MMLU-Pro (12k+)  <---- DCLM / FineWeb
indic           -----> MILU (~85k), IndicGenBench (29)  <--- Sangraha / IndicCorp / Wikipedia
```

The arrow direction is the substance of the plan: the benchmark on the left fixes the capability, and the dataset on the right is chosen to satisfy it. Section 2 formalizes the right-hand column.

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

Two design consequences follow. First, the code and agentic lanes are graded by execution and the reasoning lanes by exact answers; the model is scored on what it produces, not on the tool logs it reads, which is why §3 counts *loss-bearing* tokens rather than raw trace size. Second, the Indic lane is measured by MILU (understanding) and IndicGenBench (generation) together, because a high MILU score with weak generation would describe a model that recognises Hindi but cannot write it; Indic results are therefore reported as a macro-average across languages and a worst-language figure, not a single average.

---

## 1.4 One instance, traced end to end

The phrase "resolved rate on 500 issues" hides what a single graded item is. One representative SWE-bench Verified instance, with concrete numbers:

```
INSTANCE (representative)
repository at a fixed commit ..... ~1,400 Python files, ~600,000 lines
issue text handed to the model ... ~180 words   [CONTEXT: read, no loss taken]
required output (gold patch) ..... diff over 2 files, +14 / -3 lines
                                   [SUPERVISED TARGET: loss taken on these tokens]
grading in a sandbox ............. 3 fail-to-pass tests  (must flip fail -> pass)
                                  41 pass-to-pass tests  (must not regress)
resolved = 1 if all 44 tests pass, else 0

benchmark score = mean resolved over 500 instances
                = 380 / 500 = 0.76        (the ~76% figure, made concrete)
```

This fixes three quantities the plan depends on. The trainable content per item is small: the 600,000-line repository is read as context, and the supervised target is a 17-line diff, so a code sample contributes far fewer loss-bearing tokens than its raw size implies (§3). The reward is verifiable, computed by executing 44 tests, so the same item can be scored inside a cheap proxy run. And the supplying dataset is defined by the target: Stack v2 provides raw code but not the issue-to-patch structure, so the code lane also requires generated repository-fix trajectories, recorded as a supply gap in §6.

---

## 1.5 Proxy benchmarks for the 1B and 3B runs

The headline benchmarks return near-zero at 1B and cannot decide anything during validation (§10). Concretely, at 1B a model resolves 0 of 500 SWE-bench issues — it cannot yet produce a working patch — so the score is 0 for every recipe and cannot separate them. On HumanEval the same 1B model solves roughly 15–20 of 164 problems, and that number does move between recipes, so it can rank them. Each lane therefore names a proxy with signal at small scale.

| Lane | Headline benchmark | 1B/3B proxy | Proxy size |
|---|---|---|---|
| code | SWE-bench Verified | HumanEval, MBPP | 164 / ~974 problems |
| reasoning | AIME, FrontierMath | GSM8K, MATH-500 | 1,319 test / 500 problems |
| general web | MMLU-Pro | MMLU | 15,908 questions |
| indic | MILU, IndicGenBench | MILU (subset) | subset of ~85k |
| agentic | Terminal-Bench, τ-bench | scripted tool-call success rate | in-house set |

The proxy establishes the *direction* of an effect and the *rank* of two recipes, never the absolute number, because rankings shift with scale.

---

## 1.6 What this method does not do

The method has three known limits, stated so they are not mistaken for coverage.

- **A benchmark set can be over-fit.** Composing data backward from a fixed set risks teaching the test format. For example, train on 5,000 paraphrased copies of the SWE-bench issue texts and the reported resolved rate can rise ten points while the model is no better at unseen bugs. Section 11 pairs this method with a decontamination policy and a private, temporally held-out set; without that pairing, a reported gain is not trustworthy.
- **It measures only listed capabilities.** Anything absent from the set is invisible to the plan. For example, nothing here measures legal drafting or Hindi poetry, so the plan cannot tell whether the model can do them. General-web coverage (MMLU, MMLU-Pro) is retained partly to guard against regressing capabilities no targeted benchmark names.
- **Generative Indic quality is only partly machine-checkable.** IndicGenBench uses reference-based metrics (chrF, ROUGE) that correlate imperfectly with human judgement. For example, two correct Hindi translations of one English sentence can score chrF 0.55 and 0.72 purely from word choice, so a lower score need not mean a worse translation. The Indic result therefore carries more uncertainty than the execution-graded lanes and is flagged as such.

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
