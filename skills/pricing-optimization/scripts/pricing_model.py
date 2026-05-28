#!/usr/bin/env python3
"""
Config-driven pricing optimization + proof engine.

Given a JSON config describing buyer SEGMENTS (with competitor-anchored
willingness-to-pay) and one or more candidate tier GRIDS, this:

  1. POINT ESTIMATE   — expected ARR per candidate grid (with per-segment
                        breakdown), under base assumptions.
  2. GRID SEARCH      — sweeps price points in the configured defensible
                        bands to find the revenue-maximizing grid.
  3. MONTE CARLO      — jitters every uncertain assumption and reports the
                        share of runs each grid wins + ARR P10-P90 bands.
  4. ADVERSARIAL      — hostile wide+extreme draws that TRY to falsify the
                        ranking; reports how often the ranking flips and
                        example assumption sets where it does.
  5. BREAK-POINT      — for a chosen anchor, the value at which the ranking
                        between two named grids flips (how wrong the anchor
                        would have to be to change the decision).

Economic model (second-degree price discrimination / SaaS versioning):
  Marginal cost per unit ~= 0, so maximize total value == maximize ARR.
  A buyer in segment s:
    t* = cheapest tier whose features+volume satisfy the segment's NEED
    P(buy at price p) = logistic capture around constraint c = min(R, S+g)
       where R = reservation price, S = best substitute price,
             g = coverage/quality gap adjustment (signed).
  Revenue_s = annual_paid_pool * size_s * P(buy) * price * 12.
  Enterprise modeled as deal_count * ACV floor.

A model optimum is NOT an empirical optimum. Report the ROBUST direction and
the Monte Carlo bands, not a false-precision single number. The final word on
pricing is a live A/B test post-launch.

Usage:
  python3 pricing_model.py CONFIG.json [--mc 4000] [--adv 50000]
                                       [--breakpoint GRID_A:GRID_B:segment:anchor]
  python3 pricing_model.py --schema      # print the config schema + example
"""
import json, sys, math, random, statistics, argparse


# ---------------------------------------------------------------- core model
def cheapest_qualifying(tiers, need, needs=()):
    """tiers = [(name, price, unlocks_set)]. Cheapest tier whose `unlocks`
    superset-covers the capability requirement for this segment."""
    req = set()
    if need:
        req.add(need)
    req.update(needs)
    cands = [(p, n) for (n, p, unlocks) in tiers if req.issubset(unlocks)]
    if not cands:
        return None
    p, n = min(cands)
    return (n, p)


def capture(price, constraint, scale_frac=0.25):
    """Logistic demand: P(buy at price) given binding constraint c.
    50% at price==c, ~73% at 0.75c, ~27% at 1.25c. Exponent clamped so
    extreme adversarial draws can't OverflowError."""
    k = max(scale_frac * constraint, 1e-6)
    z = min(max((price - constraint) / k, -50), 50)
    return 1.0 / (1.0 + math.exp(z))


def arr_for_grid(grid, params, segs, scale_frac=0.25):
    tiers, ent_floor = grid
    funnel = params["annual_signups"]
    paid_pool = funnel * params["paid_intent_share"]
    total = 0.0
    breakdown = {}
    for s in segs:
        if s.get("enterprise"):
            continue
        seg_pool = paid_pool * s["size"]
        pick = cheapest_qualifying(tiers, s.get("need"), tuple(s.get("needs", [])))
        if pick is None:
            breakdown[s["name"]] = 0.0
            continue
        _, price = pick
        constraint = min(s["R"], s["S"] + s.get("g", 0))
        rev = seg_pool * capture(price, constraint, scale_frac) * price * 12
        total += rev
        breakdown[s["name"]] = rev
    ent = params["enterprise_deals"] * ent_floor * 12
    total += ent
    breakdown["__enterprise__"] = ent
    return total, breakdown


# ---------------------------------------------------------------- config load
def load_config(path):
    cfg = json.load(open(path))
    grids = {}
    for name, g in cfg["grids"].items():
        tiers = [(t["name"], t["price"], set(t["unlocks"])) for t in g["tiers"]]
        grids[name] = (tiers, g["enterprise_floor"])
    cfg["_grids"] = grids
    return cfg


def base_segments(cfg):
    # deep copy so jitter never mutates the source
    return [dict(s) for s in cfg["segments"]]


# ---------------------------------------------------------------- (1) point
def point_estimate(cfg):
    params, segs, grids = cfg["params"], base_segments(cfg), cfg["_grids"]
    print("=" * 70)
    print("POINT ESTIMATE (base assumptions)")
    print("=" * 70)
    res = {}
    for name, g in grids.items():
        arr, bd = arr_for_grid(g, params, segs)
        res[name] = (arr, bd)
    for name, (arr, _) in sorted(res.items(), key=lambda kv: -kv[1][0]):
        print(f"  {name:48s} ARR ${arr:>12,.0f}")
    print()
    for name, (arr, bd) in res.items():
        print(f"  {name}  -> ${arr:,.0f}")
        for seg, rev in bd.items():
            print(f"      {seg:30s} ${rev:>12,.0f}")
    return res


# ---------------------------------------------------------------- (2) search
def grid_search(cfg):
    params, segs = cfg["params"], base_segments(cfg)
    b = cfg.get("search_bands")
    if not b:
        print("\n[grid search skipped: no `search_bands` in config]")
        return None
    struct = b["structure"]  # ordered list of {role, unlocks, band}
    print("\n" + "=" * 70)
    print("GRID SEARCH (revenue-max over defensible bands)")
    print("=" * 70)
    best = None
    from itertools import product
    band_lists = [t["band"] for t in struct] + [b["enterprise_band"]]
    for combo in product(*band_lists):
        prices, ent = combo[:-1], combo[-1]
        tiers = [(t["role"], prices[i], set(t["unlocks"]))
                 for i, t in enumerate(struct)]
        arr, _ = arr_for_grid((tiers, ent), params, segs)
        if best is None or arr > best[0]:
            best = (arr, combo)
    roles = [t["role"] for t in struct] + ["EntFloor"]
    print(f"  best ARR ${best[0]:,.0f} at "
          + ", ".join(f"{r}={v}" for r, v in zip(roles, best[1])))
    return best


# ---------------------------------------------------------------- (3) MC
def monte_carlo(cfg, n=4000, seed=7):
    random.seed(seed)
    grids = cfg["_grids"]
    j = cfg.get("jitter", {})
    wins = {k: 0 for k in grids}
    arrs = {k: [] for k in grids}
    for _ in range(n):
        p = dict(
            annual_signups=random.randint(*j.get("annual_signups", [1800, 9600])),
            paid_intent_share=random.uniform(*j.get("paid_intent_share", [0.03, 0.10])),
            enterprise_deals=random.choice(j.get("enterprise_deals", [0, 1, 1, 2, 2, 3])),
        )
        segs = base_segments(cfg)
        sz = j.get("size_mult", [0.75, 1.25])
        for s in segs:
            s["size"] *= random.uniform(*sz)
        tot = sum(s["size"] for s in segs)
        for s in segs:
            s["size"] /= tot
        rm = j.get("R_mult", [0.8, 1.2])
        sm = j.get("S_mult", [0.8, 1.2])
        for s in segs:
            s["R"] *= random.uniform(*rm)
            s["S"] *= random.uniform(*sm)
        scores = {}
        for name, g in grids.items():
            a, _ = arr_for_grid(g, p, segs)
            scores[name] = a
            arrs[name].append(a)
        wins[max(scores, key=scores.get)] += 1
    print("\n" + "=" * 70)
    print(f"MONTE CARLO (n={n}) — share of runs each grid is revenue-max")
    print("=" * 70)
    for k in sorted(grids, key=lambda k: -wins[k]):
        a = sorted(arrs[k])
        med = statistics.median(a)
        lo, hi = a[int(0.1 * len(a))], a[int(0.9 * len(a))]
        print(f"  {k:44s} win={wins[k]/n*100:5.1f}%  "
              f"med=${med:,.0f}  P10-P90=${lo:,.0f}-${hi:,.0f}")


# ---------------------------------------------------------------- (4) adversarial
def adversarial(cfg, n=50000, seed=11):
    random.seed(seed)
    grids = cfg["_grids"]
    names = list(grids)
    if len(names) < 2:
        return
    a = cfg.get("adversarial", {})
    # ranking we are trying to defend = descending point-estimate ARR
    pe = {k: arr_for_grid(g, cfg["params"], base_segments(cfg))[0]
          for k, g in grids.items()}
    order = sorted(names, key=lambda k: -pe[k])
    print("\n" + "=" * 70)
    print(f"ADVERSARIAL FALSIFICATION (n={n}) of ranking  "
          + " > ".join(order))
    print("=" * 70)
    flips = {k: 0 for k in names}  # times grid k beats the point-estimate winner
    winner = order[0]
    full_order_held = 0
    for _ in range(n):
        sf = random.uniform(*a.get("scale", [0.10, 0.50]))
        segs = base_segments(cfg)
        for s in segs:
            s["size"] *= random.uniform(*a.get("size_mult", [0.40, 1.60]))
        tot = sum(s["size"] for s in segs)
        for s in segs:
            s["size"] /= tot
        for s in segs:
            s["R"] *= random.uniform(*a.get("R_mult", [0.5, 1.6]))
            s["S"] *= random.uniform(*a.get("S_mult", [0.5, 1.6]))
            if s.get("g"):
                s["g"] *= random.uniform(*a.get("g_mult", [0.3, 2.0]))
        p = dict(
            annual_signups=random.randint(*a.get("annual_signups", [1200, 12000])),
            paid_intent_share=random.uniform(*a.get("paid_intent_share", [0.02, 0.12])),
            enterprise_deals=random.choice(a.get("enterprise_deals", [0, 1, 2, 3, 4])),
        )
        scores = {k: arr_for_grid(g, p, segs, sf)[0] for k, g in grids.items()}
        win = max(scores, key=scores.get)
        for k in names:
            if scores[k] > scores[winner]:
                flips[k] += 1
        if [k for k in sorted(names, key=lambda k: -scores[k])] == order:
            full_order_held += 1
    print(f"  point-estimate winner: {winner}")
    for k in names:
        if k == winner:
            continue
        print(f"  {k:44s} beats {winner} in {flips[k]/n*100:6.2f}% of hostile draws")
    print(f"  full ranking held intact in {full_order_held/n*100:6.2f}% of draws")
    print("  -> a ranking that survives wide+extreme hostile draws is robust,")
    print("     not an artifact of the base assumptions.")


# ---------------------------------------------------------------- (5) breakpoint
def breakpoint(cfg, spec):
    """spec = 'GRID_A:GRID_B:segment_name:anchor'  where anchor in {R,S,g}.
    Sweep the anchor for that segment and report where A and B swap rank."""
    ga, gb, seg_name, anchor = spec.split(":")
    grids = cfg["_grids"]
    print("\n" + "=" * 70)
    print(f"BREAK-POINT — {anchor} of '{seg_name}' that flips {ga} vs {gb}")
    print("=" * 70)
    base_val = next(s[anchor] for s in cfg["segments"] if s["name"] == seg_name)
    prev = None
    for mult in [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0]:
        segs = base_segments(cfg)
        for s in segs:
            if s["name"] == seg_name:
                s[anchor] = base_val * mult
        aa = arr_for_grid(grids[ga], cfg["params"], segs)[0]
        ab = arr_for_grid(grids[gb], cfg["params"], segs)[0]
        lead = ga if aa >= ab else gb
        flag = "" if prev is None or lead == prev else "   <-- FLIP"
        print(f"  {anchor}={base_val*mult:8.1f} ({mult:.2f}x)  "
              f"{ga}=${aa:,.0f}  {gb}=${ab:,.0f}  lead={lead}{flag}")
        prev = lead
    print(f"  (verified base {anchor}={base_val})")


SCHEMA = '''Config schema (JSON):
{
  "params": {"annual_signups": int, "paid_intent_share": float,
             "enterprise_deals": int},
  "segments": [
    {"name": str, "size": float (shares sum to 1.0),
     "need": "api_low"|"api_mid"|... (capability token),
     "needs": ["mmdb","parquet", ...]  (extra required unlocks, optional),
     "R": reservation $/mo, "S": substitute $/mo, "g": gap adj $/mo (signed),
     "enterprise": true (optional; handled via enterprise_floor not capture)}
  ],
  "grids": {
    "label": {"tiers": [{"name": str, "price": $/mo, "unlocks": [tokens]}],
              "enterprise_floor": $/mo}
  },
  "search_bands": {                      (optional; enables grid search)
    "structure": [{"role": str, "unlocks": [tokens], "band": [prices]}],
    "enterprise_band": [floors]
  },
  "jitter": {"annual_signups":[lo,hi], "paid_intent_share":[lo,hi],
             "enterprise_deals":[...], "size_mult":[lo,hi],
             "R_mult":[lo,hi], "S_mult":[lo,hi]},          (MC; optional)
  "adversarial": { ...same keys, wider; plus "scale":[lo,hi], "g_mult":[lo,hi] }
}
Anchor every R/S to a VERIFIED competitor price observed recently. Cite the
source + observation date in the config (use a "_source" field per segment).'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config", nargs="?")
    ap.add_argument("--mc", type=int, default=4000)
    ap.add_argument("--adv", type=int, default=50000)
    ap.add_argument("--breakpoint", default=None)
    ap.add_argument("--schema", action="store_true")
    a = ap.parse_args()
    if a.schema or not a.config:
        print(SCHEMA)
        return
    cfg = load_config(a.config)
    point_estimate(cfg)
    grid_search(cfg)
    monte_carlo(cfg, n=a.mc)
    adversarial(cfg, n=a.adv)
    if a.breakpoint:
        breakpoint(cfg, a.breakpoint)


if __name__ == "__main__":
    main()
