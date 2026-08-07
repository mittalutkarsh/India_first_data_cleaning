# Contrastive Perspective Corpus & Surprisal Framework

*Source: India-First 40B proposal, sections B.4–B.5. This document is the reference
specification for the contrastive corpus, the surprisal metrics (F1–F2), and the
activation-geometry framework (F3–F7). It is the method the Session 6 Training Data
Execution System operationalises (contrastive lane, per-token surprisal in the learning
ledger, ΔS-based OPUS selection, and an optional geometry-analysis module).*

---

## B.4 · The contrastive perspective corpus

We collect and author **minimal contrastive pairs** on contested, globally-framed
topics: the **same prefix**, two continuations that differ only in a localized
**framing span** — one Indian-vantage (`y+`), one Western-default (`y-`).

```
prefix : "The economic impact of British colonial rule on India was"
y+     : "a large-scale wealth transfer that deindustrialised Bengal's
          textile economy and lowered per-capita income for decades."
y-     : "a mixed legacy that introduced railways, a civil service,
          and modern administrative institutions."
axes   : { vantage: Indian(+)/Western(-),  chauvinism: none }
```

**Design guard.** `y+` is a *factual* Indian framing (wealth transfer,
deindustrialisation — historically defensible), **not** a chauvinistic one such as
"the British were evil." The **chauvinism axis is tracked separately**, so the
perspective signal can never be satisfied by demonising others.

---

## Surprisal metrics ("the surprise")

### F1 — Standard token surprisal

The negative log-likelihood of a token conditioned on its preceding context:

$$S_M(x_t) = -\log P_M(x_t \mid x_{<t})$$

calculated against a reference model `M` (typically a Western-centric baseline, or the
checkpoint under evaluation). Note: this is identical to the per-token cross-entropy
loss, so the training **learning ledger already produces F1 for free**.

### F2 — Contrastive differential surprisal (the core framing-extraction method)

For a contrastive pair `i`, averaged over the **framing-specific spans**:

$$\Delta S_i = \overline{S_M(\text{Indian framing})} - \overline{S_M(\text{Western framing})}$$

Simple surprisal is a *contaminated* signal — it spikes on sparse tokens such as
numerals or proper nouns, which is why prior work links segment surprisal to rare-word
frequency rather than to vantage. Taking the **delta between opposing framings** negates
this generic noise and isolates *framing-specific* surprisal. A significant positive
`ΔS_i` reveals instances where the Indian continuation is statistically improbable under
the baseline — the precise tokens where cultural vantage diverges.

---

## B.5 · Analytical framework — from data to cultural geometry

The F-metrics operationalise the tiered corpus. **F3 is the established baseline**
(Rimsky et al., 2024; Marks & Tegmark); **F4–F7 are the contribution.**

### F3 — Difference-in-means direction (standard)

The steering vector at layer `ℓ`, averaged over the contrastive set of size `n`:

$$v_\ell = \frac{1}{n}\sum_i \left(a^{+}_{i,\ell} - a^{-}_{i,\ell}\right)$$

where `a+` and `a-` capture internal activations at the framing-specific spans. This is
the established confound against which we benchmark.

### F4 — Surprisal-weighted contrastive direction (the augmentation)

Weight each instance by its differential surprisal:

$$v_\ell = \frac{\sum_i w_i\,(a^{+}_{i,\ell} - a^{-}_{i,\ell})}{\sum_i w_i}, \qquad w_i = f(\Delta S_i)$$

F3 is the uniform special case `w_i ≡ 1`. **Hypothesis H-D:** F4 yields a more
separable, disentangled vector by suppressing low-signal pairs whose framings lack
sufficient divergence.

### F5 — Linear separability / geometric readout (H-A)

Project activations onto the normalized vector `v̂_ℓ = v_ℓ / ‖v_ℓ‖` and measure the
standardized margin between framing classes (Cohen's *d*):

$$d_\ell = \frac{\mu^{+}_\ell - \mu^{-}_\ell}{\sqrt{\tfrac{1}{2}\left((\sigma^{+}_\ell)^2 + (\sigma^{-}_\ell)^2\right)}}$$

plus held-out linear-probe accuracy. Higher `d_ℓ` = a cleaner linear direction. This is
the quantity compared across provenance arms (native vs. translated).

### F6 — Entanglement (the H-D guardrail)

Cosine similarity between the perspective vector and a set of off-target concept
directions `C`:

$$E = \max_{c \in C} \left| \cos(v_\ell, v_c) \right|$$

Lower = more disentangled. If F4 lowers `E` vs. F3, the surprisal weighting is doing its
job.

### F7 — Persistence (H-B)

Re-extract after SFT and DPO:

$$\rho = \cos\!\left(v_\ell^{\text{pre-align}},\, v_\ell^{\text{post-align}}\right) \qquad \text{and} \qquad \frac{d_\ell^{\text{post}}}{d_\ell^{\text{pre}}}$$

calculated for the native-from-scratch checkpoint against a Western-pretrained baseline.
If the native model keeps a stronger, more stable direction, native pretraining earns
its cost.

---

## Evaluation

These metrics are evaluated on **proxy models during training**, comparing **native
against translated** provenance, *before* the full run; the results fix the **data
mixture** and the **vocabulary**.

---

## Mapping into the Session 6 execution system

| Element | Where it lives in the data system |
|---|---|
| Contrastive pairs (B.4) | a distinct **data type / lane** with its own **packing policy** (shared prefix, loss only on framing spans) |
| F1 token surprisal | the **per-token loss** already recorded in the learning ledger |
| F2 differential surprisal `ΔS_i` | a derived per-pair metric in the learning ledger; also an **OPUS acceptance signal** (prefer high-`ΔS`, defer low-signal pairs) |
| Chauvinism axis | a manifest tag carried with each pair, kept separate from the vantage label |
| F3–F7 geometry | an **optional analysis/audit module** that consumes captured activations (machinery is reproducible on a toy model; scientifically meaningful only at scale) |
