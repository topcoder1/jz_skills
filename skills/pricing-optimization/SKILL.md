---
name: pricing-optimization
description: >
  Find the revenue-maximizing pricing/tier grid for a SaaS or data product and
  PROVE the ranking is robust — not just assert it. Builds a competitor-anchored
  willingness-to-pay model, sweeps a grid search for the optimum, then verifies
  with Monte Carlo sensitivity, adversarial falsification, and anchor break-point
  analysis. Use when asked to "optimize pricing", "what price maximizes revenue",
  "which tier grid is best", "price these tiers", "maximize total value/ARR",
  "should we charge X or Y", or to evaluate/compare candidate pricing proposals.
  Proactively suggest when a user is deciding between pricing options for a product.
user-invocable: true
argument-hint: <product-or-config> [--depth quick|standard|deep]
---

# Pricing Optimization

Determine the price/tier structure that maximizes expected total value (ARR),
and back the recommendation with proof at the standard of an empirically
skeptical reader. The deliverable is: a ranked set of candidate grids, the
revenue-maximizing grid, and evidence that the ranking survives hostile
assumptions — plus an explicit statement of what only a live A/B test can settle.

## Core principle

**A model optimum is not an empirical optimum.** The model narrows the search
to the best candidate and proves dominated options are dominated. Report the
ROBUST direction and Monte Carlo bands, never a false-precision single number.
The final word on pricing is a live price test post-launch. Say so explicitly.

## The 5-step method

### 1. Anchor to VERIFIED substitutes (do not skip, do not estimate)
Willingness-to-pay is bounded by what a buyer can switch to. For every buyer
segment, find the feature+volume-equivalent competitor and record its **current,
observed** price — pull it live, cite the source and observation date. Training-
data prices rot fast (this market moved 30%+ in one quarter). Delegate the price
gathering to the `researcher` agent or `research_deep` if many anchors are needed.

For each segment capture: reservation price `R` (max it will pay), best
substitute price `S`, and a signed gap adjustment `g` (coverage/quality edge or
penalty vs the substitute). The binding constraint is `c = min(R, S + g)`.

### 2. Model capture per segment
Marginal cost per unit ≈ 0, so **maximize total value == maximize ARR.** Each
segment routes to the cheapest tier whose features+volume satisfy its need; it
buys with logistic probability around `c` (50% at price==c, falls off by the
configured elasticity). This makes the optimum interior, not a band-cap artifact.

### 3. Grid-search the optimum
Hold the tier *structure* fixed (which tier first unlocks each capability) and
sweep prices over **defensible bands** (bounded by competitor anchors). Report the
revenue-max grid. Cross-check that it is a true interior maximum, not a search bug.

### 4. Adversarially falsify the ranking
Try to BREAK the conclusion. Monte Carlo with wide jitter on every assumption
(segment sizes, R, S, g, elasticity, funnel). Report the share of hostile draws
in which each alternative beats the proposed winner, and example assumption sets
where it flips. A ranking that survives 50k hostile draws is robust.

### 5. Isolate the break-point
For the single anchor the conclusion most depends on, find the value at which the
decision flips. State how wrong the verified anchor would have to be to change the
answer ("the substitute would have to be 50% higher than its published price").

Then write **model-free deductions**: 1–2 proofs from verified prices + the
substitution principle alone, independent of the simulation. These are the
strongest arguments — they hold even if every modeling assumption is wrong.

## How to run

The engine is config-driven. Build a JSON config (segments + candidate grids +
search bands + jitter), then:

```bash
cd <skill-dir>
python3 scripts/pricing_model.py CONFIG.json --mc 4000 --adv 50000 \
  --breakpoint "GRID_A:GRID_B:segment_name:S"
python3 scripts/pricing_model.py --schema     # full config schema + field docs
```

A complete worked example ships at `examples/wxa-vpn-2026-05.json` (run it first
to see the expected output shape). Copy it as a starting template for a new product.

## Depth modes

Parse `$ARGUMENTS` for `--depth` (default `standard`):
- **quick** — steps 1–3 only (anchors → model → grid search). One recommended grid.
- **standard** — all 5 steps. Full proof: grid search + MC + adversarial + break-point + deductive proofs.
- **deep** — standard, plus: per-segment break-point sweep on every anchor, a written
  proof artifact committed to the project's `docs/`, and a draft stakeholder
  recommendation (e.g. an email arguing a team off a dominated grid using the
  segment-loss numbers as evidence).

## Workflow

1. **Gather verified anchors** (step 1). If >3 anchors needed, delegate to `researcher`.
2. **Write the config.** One segment per distinct buyer type; shares sum to 1.0.
   Cite every R/S with a `_source` field (provider + price + observation date).
3. **Run the engine** at the chosen depth. Confirm the grid search optimum is an
   interior max and the ranking holds under adversarial draws.
4. **Write deductive proofs** — model-free arguments from prices alone.
5. **Report**: ranked grids, the optimum, robustness evidence, the break-point, and
   an explicit "what only A/B testing can prove" caveat.
6. **(deep)** Commit the config + a verification write-up to `docs/` as a proof
   artifact; optionally draft the stakeholder recommendation.

## Honesty requirements (non-negotiable)

- Never present a model number as empirical fact. Always pair with MC bands.
- Always state the break-point — readers must know how fragile the conclusion is.
- Always include the "only A/B testing is rigorous proof" caveat.
- If an anchor is an estimate not a verified price, label it as such; flag the
  conclusion's sensitivity to it via the break-point.

See `references/method.md` for the economic model derivation and the WTP capture math.
