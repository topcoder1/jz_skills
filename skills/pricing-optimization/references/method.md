# Pricing optimization — economic model & proof methodology

## Why "maximize total value = maximize ARR" here

For software/data products the marginal cost of serving one more lookup,
download, or API call is ≈ 0. Fixed costs (infra, data acquisition, a proxy-COGS
floor) are an OPEX floor applied as a global contribution check, not a per-unit
cost. So the revenue-maximizing price is also the value-maximizing price — there
is no per-unit margin trade-off pulling the optimum down. This is what makes a
pure WTP/capture model legitimate; it would NOT hold for a product with material
per-unit COGS, where you'd maximize `(price - unit_cost) * quantity` instead.

## Second-degree price discrimination (versioning)

Buyers self-sort into tiers by their feature + volume needs. The design lever is
*which tier first unlocks each capability* (e.g. daily MMDB, Parquet). Put a
capability too low and you (a) give it away to buyers who'd pay more and (b)
remove the upsell ladder; put it too high and you lose buyers who need it to a
substitute. The grid search optimizes the price points; the *structure* (unlock
ladder) is the higher-order decision and is usually held fixed per candidate grid.

## The capture curve

For a segment with binding constraint `c = min(R, S + g)`:

```
P(buy at price p) = 1 / (1 + exp((p - c) / k)),   k = scale_frac * c
```

- `R` — reservation price: the max $/mo this buyer will pay at all.
- `S` — best substitute price: the feature-equivalent competitor's current price.
- `g` — signed gap adjustment: a quality/coverage edge (+) or penalty (−) vs the
  substitute. E.g. a product with 30× worse coverage carries a large negative `g`
  for coverage-first buyers; a product with sales-gated/expensive substitutes has
  a high effective `S` and wins easily.
- `scale_frac` — within-segment price elasticity. 0.25 gives 50% capture at
  `p=c`, ~73% at `0.75c`, ~27% at `1.25c`. Sweep it in [0.10, 0.50] under
  adversarial testing.

The constraint is `min(R, S+g)` because a buyer is lost both when the price
exceeds what they'll pay (R) AND when it exceeds the substitute-adjusted ceiling
(S+g) — whichever binds first.

## Revenue accounting

```
annual_paid_pool = annual_signups * paid_intent_share
Revenue(segment) = annual_paid_pool * size_share * P(buy) * price * 12
Revenue(enterprise) = deal_count * ACV_floor * 12
ARR(grid) = Σ Revenue(segment) + Revenue(enterprise)
```

Enterprise is modeled separately (deal_count × ACV) because it's sold, not
self-serve-captured — a logistic curve on a list price doesn't describe it.

## The proof stack (why each layer exists)

1. **Closed-form / interior-max cross-check.** Confirms the grid-search optimum
   is a true revenue maximum (derivative flips + → − through it), ruling out a
   search bug or a band-cap artifact. Two independent methods agreeing = not an
   artifact.
2. **Monte Carlo sensitivity.** Jitters uncertain inputs ±25% (sizes, anchors)
   and the funnel; reports win-share and P10–P90 ARR bands. Establishes the
   ranking isn't knife-edge on the base point estimate.
3. **Adversarial falsification.** Wide + extreme hostile draws (0.4–1.6× sizes,
   0.5–1.6× anchors, 0.10–0.50 elasticity) that actively try to flip the ranking.
   Reports how often each alternative wins. This is the real robustness test —
   MC explores "plausible", adversarial explores "could it EVER".
4. **Break-point isolation.** For the load-bearing anchor, the exact value where
   the decision flips. Converts "robust" into a falsifiable statement: "the
   substitute would have to be 50% above its published price."
5. **Model-free deductions.** 1–2 proofs from verified prices + substitution
   principle alone. The strongest evidence because they survive every modeling
   assumption being wrong. Example shape: "entry tier is 63% above a verified
   feature-equivalent substitute → no rational buyer pays a 63% premium → that
   segment is structurally lost, independent of any size/elasticity assumption."

## What this method CANNOT prove

- The true segment sizes / shares (these are assumptions; MC bounds the impact).
- The actual elasticity (swept, not measured).
- That buyers behave rationally re: substitutes (brand, switching cost, inertia
  all push real capture below the model).
- The single "correct" price to the dollar.

The only rigorous proof of pricing optimality is a live A/B / price test. The
model's job is to (a) eliminate dominated options with high confidence and (b)
narrow the live test to 2–3 defensible candidates. Always state this.

## Anchoring discipline

- Pull substitute prices **live**, not from memory. Record source + date.
- Re-verify before each major pricing decision — this market moves fast.
- If a price is gated behind "contact sales", treat the substitute as high and
  inaccessible (raises effective S), but flag the uncertainty.
- An estimated (not verified) anchor must be labeled, and the conclusion's
  sensitivity to it shown via break-point.
