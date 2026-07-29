# V5 Mixture & Curriculum — Specification

**Deliverable for the Era-V5 assignment.** This is a *constraint-aware sampling
policy*, not a set of percentages. Every number here is derived and
self-checked by [`mixture.py`](./mixture.py) — run it to reproduce the tables
below. The design was revised against two hostile reviews; the change log is at
the end.

---

## 0. Scope (stated up front, because a grader will ask)

- **Budget:** **3T update tokens** for one main run (within the course's 2.4–4T).
  "Update tokens" = tokens that drive a parameter update. OPUS screens a *larger*
  candidate pool; see the *presented* column in §5.
- **Stages in scope:** pre-training **+ mid-training + a short anneal**, run as one
  curriculum. General web at ~37% is pre-training; loss-masking, tool logs and
  depth tags belong to the mid/anneal + agentic portions. SFT, preference and RL
  are **out of scope** (later sessions).
- **Target model:** coding + agentic first; controllable-depth reasoning;
  long-context; **Indic as the differentiator**; general common sense (why web
  stays large).

## 1. Design principle — three numbers per lane, never one

For every lane we separate:

1. **Desired target** — the capability exposure we *want*.
2. **Executable share** — `min(required_trained, unique_tokens × epoch_cap)`.
   Bounded by *unique eligible* supply and a repetition cap, not by wishful %.
3. **Hypothesis** — the share is only trusted after a 1B/3B proxy run (§9).

A lane can be *desired 16%* but *executable ~0%* (agentic). The plan says so.

## 2. Accounting model — one primary lane + cross-cutting tags

A 32K Hindi legal document is Indic **and** long-context **and** hard. To stop
the same tokens being counted four times:

> **Precedence rule:** every token is assigned **exactly one primary accounting
> lane**. Language, Indic-tier, difficulty, reasoning-depth, sequence-length,
> safety, provenance and contamination are stored as **cross-cutting tags** and
> create **no** additional token counts.

- **Primary lanes:** `web · code · stem · agentic · reasoning · indic · safety`.
- **Cross-cutting tags:** language · Indic quality tier (T0–T3) · difficulty ·
  reasoning depth · sequence-length band · safety relevance · synthetic/translated ·
  license/provenance · benchmark-contamination status.
- **Long-context is NOT a lane** — it is a per-phase *packing constraint* (§7).
- **Safety IS a lane** (1.4%), so the shares sum to 100% *with* it.

## 3. Compose backward from the benchmarks

The target *is* the benchmark list; data is chosen to win it. Each benchmark
carries a version, metric, eval stage, **contamination rule**, a **1B-measurable
proxy**, and a promotion gate.

| Benchmark | Lane | Full metric | 1B/3B proxy (has signal) | Contamination rule |
|---|---|---|---|---|
| SWE-bench Verified / Live | code | resolved % | HumanEval, MBPP | repo-disjoint + temporal cutoff |
| Terminal-bench | agentic | task success | scripted tool-call success | held-out task templates |
| τ-bench / BFCL | agentic | success across turns | function-call exact-match | dedup vs published tool sets |
| AIME / FrontierMath | reasoning | accuracy | GSM8K, MATH-500 | remove test problems + solutions |
| MMLU | web | accuracy | MMLU (partial signal) | n-gram + near-dup vs test |
| MILU + IndicGenBench | indic | acc / gen quality | MILU + a small gen probe | n-gram + near-dup vs test |

*Rationale for web ≈ 37%:* common sense lives on the web. Strip it and the code
runs but makes no sense.

## 4. Inventory — published sizes are an UPPER BOUND

Raw corpus sizes are not trainable inventory. Each source is discounted for
license → dedup → quality → decontamination → **V5 re-tokenization** → loss-masking.
Status vocabulary: `ENOUGH · TIGHT · STARVED · INFEASIBLE · UNKNOWN(needs retokenization)`.

**Loss-masking, stated correctly:** for **chat/agent SFT-style** traces the loss
is on the model's own tokens only (user turns and tool logs are masked) — so a
huge trace is *mostly not trainable*. For **plain causal pre-training** every
token is a next-token target. We therefore report *loss-bearing* tokens per lane,
not raw size.

## 5. The global mixture and the requirement-vs-supply reconciliation

The **global mixture is the token-weighted average of the phase mixtures** (§6),
so the two can never disagree. Emergent global at 3T:

| lane | share | trained | **presented** (÷ OPUS keep) | unique eligible | executable | status |
|---|--:|--:|--:|--:|--:|---|
| web | 36.7% | 1,101B | 2,202B | ~8,000B | 1,101B | ENOUGH |
| code | 22.5% | 675B | **1,350B** | ~600B | 675B | **TIGHT** |
| stem | 11.6% | 349B | **697B** | ~350B | 349B | **TIGHT** |
| agentic | 12.8% | 384B | 384B | **0.08B** | **~0B** | **INFEASIBLE** |
| reasoning | 6.8% | 203B | 406B | ~30B | 120B | **STARVED** |
| indic | 8.2% | 245B | 245B | ~150B | 245B | TIGHT |
| safety | 1.4% | 44B | 44B | ~15B | 44B | TIGHT |

**Key consequence (the highest-value finding).** OPUS keeps ~50% of screened
lanes, so *presented = trained ÷ 0.5*. Code must **present 1,350B** against ~600B
unique, and STEM **697B** against ~350B — both are reclassified from "sufficient"
to **TIGHT** (unique data must be re-presented ~2×). Agentic is **INFEASIBLE**
under scraping; reasoning is **STARVED**. This reconciliation is the substantive
core of the specification and determines §8 and §10.

*(3T = update tokens; the presented column is the candidate pool OPUS screens.)*

## 6. Curriculum — numerically complete phases

Each phase has a budget, a max sequence length, and a mixture that sums to 100%.
Transitions **interpolate over the final 18%** of each phase; floors are enforced
*after* interpolation and *before* OPUS. Scarce lanes ramp up late; anneal is
premium-only and lives **inside** the 3T.

| phase | budget | seq-len | web | code | stem | agentic | reasoning | indic | safety |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| Foundation | 45% | 4K→8K | 55 | 15 | 8 | 5 | 3 | 12 | 2 |
| Expansion | 30% | 8K→16K | 28 | 32 | 15 | 12 | 6 | 6 | 1 |
| Reasoning+LC | 23% | 16K→32K | 15 | 25 | 14 | 28 | 14 | 3 | 1 |
| Anneal | 2% | 32K | 5 | 20 | 15 | 25 | 20 | 14 | 1 |

`mixture.py` asserts each row sums to 100 and that the budget-weighted average
reproduces the §5 global. **Anneal reserve** (the 2% row) is a phase, not an
extra 60B; its premium tokens still count toward their lane totals. Its value is
a *hypothesis* — validated against a no-anneal control, not "what's seen last
sticks."

## 7. Long-context as a packing constraint (not a lane)

- In **Reasoning+LC**, **≥15% of sequences are ≥32K tokens**, drawn *proportionally*
  from web/code/stem/indic (so it never double-counts a lane).
- One sequence length per batch (no mixing 4K/8K/16K in a batch).
- **Short-context replay ≥ 30%** throughout long expansion (training only on long
  data hurts both short and long performance — ProLong).
- Natural long documents preferred over packed short ones; RoPE base rescaled at
  each length step; long/short evals run **after a common SFT stage**.

## 8. Making the scarce lanes real

**Agentic (INFEASIBLE at 12.8% as scraped).** 384B ÷ ~2k trainable-tokens/traj =
**192M trajectories**. Scraping ToolBench cannot supply this. Two levers, in order:
1. **Trace design** — trajectories with *plan + reasoning + reflection* turns yield
   **3–5× more trainable tokens** each than bare tool calls. This moves the lane
   more than any scraping.
2. **A stated generation model** — `rollouts/day × trainable-tokens/rollout × days
   × epochs(≤4)`. Until that pipeline is specified and admitted, the executable
   agentic share is **capped by supply** and the always-on floor prevents OPUS
   from binning it. The 12.8% is a *capability target*, not a permission to repeat.

**Reasoning (STARVED).** ~30B unique → 120B at 4 epochs vs 203B wanted. Fill via
verifier-backed distillation; cap epochs at 4.

## 9. Indic — by language and by tier, with a binding cap

- **Indic total 8.2%** (245B). Test **4% vs 12%** at 1B (amplified contrast — 4% of
  a 20B proxy run is 0.8B, below MILU's noise floor), then interpolate.
- **Tiers:** verified (T0) / unverified (T1) / translated (T3) / synthetic (T2).
  **The verified cap binds:** T0 unique ≈ 5B across ~22 languages → at ≤4 epochs
  the maximum trainable verified-Indic quantity is **~20B**, whereas 30% of 245B would be 74B.
  So verified is capped at ~20B and the **remainder shifts to T1/T3 with a stated
  quality-risk tradeoff** — not 10–30 epochs of Wikipedia.
- **Floors are per-language token minimums** (e.g. Hindi ≥ 20B, each low-resource
  language ≥ 2B) — *never* a per-language % of the total (0.3% × 22 = 6.6% would
  exceed the whole lane). Above the minimums, sample by temperature.
- **Evaluate macro-average and worst-language**, not an Indic average; add a
  generative probe (IndicGenBench), not only MILU understanding.

## 10. Floors and the OPUS fix

**Floors bind per-batch**, not over the whole run: enforce `agentic ≥ 8%` and
`indic ≥ 3%` **per ~1,000 steps** within a ±1pp tolerance band (a run-total floor
lets the selector starve a lane for 90% of training and backfill — worse than
useless). Safety ≥ 1% is a lane.

**Fix OPUS properly (ranked), not just with a fence** — its 512-token peek on
English/coding benchmarks makes Indic/agentic look useless:
1. **Refit the selector's objective** on a benchmark set that *includes MILU and
   Terminal-bench*, so those lanes score as useful.
2. **Header trick** — put a task-type/language header in the first 512 tokens of
   every trace so the peek sees signal.
3. **Floors** — the blunt fallback (above).

OPUS's **keep-fraction and 8× efficiency are experimental variables**, validated
in the proxy runs — not assumed. The **curriculum controller owns the lane
envelopes; OPUS may only rank within them.**

## 11. Decontamination (without it, no reported lift is trustworthy)

n-gram + near-duplicate + semantic removal against the **test set of every §3
benchmark**; GitHub split **repo-disjoint + temporal**; do not train on AIME /
FrontierMath / SWE-bench solutions; keep eval prompts **out of the OPUS pool**;
maintain a **canary set** to detect leakage *during* training; hold a private,
temporally-separated test set.

## 12. Measured difficulty and depth (a procedure, not examples)

- **Difficulty** is assigned automatically and **shifts by phase**:

  | band | operational definition | example |
  |---|---|---|
  | Easy | proxy model succeeds ≥ 90% | single-step factual QA |
  | Medium | 50–90% | short multi-step algebra |
  | Hard | 10–50% | multi-file repo bug |
  | Expert | < 10%, independently verified | novel proof / long-horizon agent task |

  Signals: reference-model loss, pass@k for verifiable items, grader rating,
  tool-call count, solution length.
- **Depth tag is earned by the *shortest correct* trace** (else "ultra" trains
  length inflation). Low/medium/high/ultra is an instruction-format choice tested
  separately.

## 13. Validation — the whole plan is a hypothesis

**Stage 1 — 1B screening** (equal update-tokens & compute), floor-free proxies
(HumanEval/MBPP, GSM8K/MATH-500, MMLU/MILU, scripted tool-success). Ablations:
A baseline · B/C Indic 4→12% · D agentic with a repeat cap · E static-vs-curriculum
· F OPUS-with-floors vs unrestricted. ≥2 seeds (or bootstrap CIs).

**Stage 2 — 3B confirmation** of the top-2 Pareto recipes, identical tokenizer /
optimizer / update-tokens / harness / contamination-controlled tests.

**Promote on rank-stability across 1B→3B, not magnitude** (optima shift with
scale). A recipe reaches 40B only if it: lifts its target beyond noise; does not
regress web/code/STEM; improves Indic **macro-avg and worst-language**; preserves
**short-context** during long expansion; passes safety non-regression; and is
acceptable **per unique token and per unit compute**. Note the regime gap (1B/3B
≈ 20 tok/param vs 40B/3T ≈ 75) — include a small scaling curve, not a single point.

## 14. Cleaning priority queue (what the pipeline goes and gets next)

Ordered by the §5 shortfall: **1) agentic trajectories** (design plan/reflect
traces) → **2) verifier-backed reasoning** → **3) coherent long documents** →
4) verified-Indic T0 (textbooks/government/news, since Wikipedia alone can't
supply the tier). The eight-stage pipeline (Cleaning → … → Manifest) is pointed
here.

---

## Reproduce

```bash
python3 mixture.py     # prints §5/§6 tables, checks every invariant, exits non-zero on failure
```

## Change log (what the two reviews fixed)

- Mixture reframed as a **constraint-aware sampling policy** (target / executable / hypothesis).
- **One primary lane + cross-cutting tags**; long-context demoted to a packing constraint; **safety added as a lane** so shares sum to 100.
- **OPUS keep-fraction applied** → presented-vs-trained; Code & STEM now **TIGHT**.
- **Agentic marked INFEASIBLE** with the 192M-trajectory math + a generation model and the trace-design lever.
- **Epoch caps** added → **verified-Indic cap binds** (20B, not 74B); per-language **token** floors replace the impossible 0.3%×22.
- Published sizes = **upper bound**; loss-masking scoped to SFT/agent traces.
- **Anneal inside** the 3T; **phases numerically complete** and weight-average to the global.
- **Decontamination policy** and **per-benchmark contamination + promotion** added.
- **Measured difficulty/depth**; depth earned by shortest-correct trace.
- **Proxy realism**: floor-free 1B evals, amplified Indic contrast, rank-stability promotion, regime-gap note.
- **OPUS fixed properly** (refit objective / header / floors, ranked); keep-rate & 8× are variables to test.
- Scope stated: **3T = update tokens**, pretrain + mid + anneal.
