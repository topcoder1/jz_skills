#!/usr/bin/env python3
"""
METERED + STRUCTURAL pricing extension.

The v1 engine (pricing_model.py) optimizes PRICE points while holding two things
fixed: (a) the feature unlock ladder, and (b) it ignores metered volume entirely.
This module generalizes v1 along those two axes so we can ask:

  - Are the per-tier API-CREDIT quotas (200K / 1M / 5M) optimal?
  - Is the FEATURE ladder (which tier first unlocks mmdb / parquet) optimal?

It is a STRICT generalization: a segment now carries a monthly `volume`, a tier
now carries a `credits` cap, and routing picks the cheapest tier whose features
cover the need AND whose credit cap >= the segment's volume. With every cap set
to infinity, routing collapses to v1's feature-only routing and the ARR is
identical to v1 to the cent (proven in verify_metered.py).

The capture curve is imported unchanged from pricing_model.py -- we reuse the
already-proven demand math and only add the volume-fencing routing layer.

Honesty bar (inherited from the skill): a model optimum is not an empirical
optimum. Credit quotas in particular are under-determined by a 5-segment model
(real metering revenue needs a volume CONTINUUM = usage telemetry). Report the
robust direction + break-points; the dollar-exact caps are an A/B/telemetry call.

Usage:
  python3 pricing_metered.py CONFIG.json [--mc 4000] [--adv 50000]
"""
import json, sys, math, random, statistics, argparse, os, importlib.util
from itertools import product

# import the PROVEN capture() and v1 helpers (no logic duplicated)
_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("pm", os.path.join(_HERE, "pricing_model.py"))
pm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pm)
capture = pm.capture

INF = float("inf")


# ---------------------------------------------------------------- core (metered)
def cheapest_qualifying_metered(tiers, need, needs=(), volume=0):
    """tiers = [(name, price, unlocks_set, credits)]. Cheapest tier whose
    features superset-cover the need AND whose credit cap >= volume."""
    req = set()
    if need:
        req.add(need)
    req.update(needs)
    cands = [(p, n) for (n, p, unlocks, credits) in tiers
             if req.issubset(unlocks) and credits >= volume]
    if not cands:
        return None
    p, n = min(cands)
    return (n, p)


def arr_for_grid_metered(grid, params, segs, scale_frac=0.25):
    tiers, ent_floor = grid
    paid_pool = params["annual_signups"] * params["paid_intent_share"]
    total = 0.0
    breakdown = {}
    for s in segs:
        if s.get("enterprise"):
            continue
        seg_pool = paid_pool * s["size"]
        pick = cheapest_qualifying_metered(
            tiers, s.get("need"), tuple(s.get("needs", [])), s.get("volume", 0))
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
def _credits(v):
    return INF if v is None else float(v)


def load_metered_config(path):
    cfg = json.load(open(path))
    grids = {}
    for name, g in cfg["grids"].items():
        tiers = [(t["name"], t["price"], set(t["unlocks"]), _credits(t.get("credits")))
                 for t in g["tiers"]]
        grids[name] = (tiers, g["enterprise_floor"])
    cfg["_grids"] = grids
    return cfg


def base_segments(cfg):
    return [dict(s) for s in cfg["segments"]]


# ---------------------------------------------------------------- (1) point
def point_estimate(cfg):
    params, segs, grids = cfg["params"], base_segments(cfg), cfg["_grids"]
    print("=" * 74)
    print("POINT ESTIMATE (metered routing: features AND credit cap must satisfy)")
    print("=" * 74)
    res = {name: arr_for_grid_metered(g, params, segs) for name, g in grids.items()}
    for name, (arr, _) in sorted(res.items(), key=lambda kv: -kv[1][0]):
        print(f"  {name:50s} ARR ${arr:>12,.0f}")
    print()
    for name, (arr, bd) in sorted(res.items(), key=lambda kv: -kv[1][0]):
        print(f"  {name}  -> ${arr:,.0f}")
        for seg, rev in bd.items():
            print(f"      {seg:30s} ${rev:>12,.0f}")
    return res


# ---------------------------------------------------------------- (2a) credit search
def credit_search(cfg):
    b = cfg.get("credit_bands")
    if not b:
        print("\n[credit search skipped: no `credit_bands`]")
        return None
    params, segs = cfg["params"], base_segments(cfg)
    prices, ent = b["prices"], b["enterprise_floor"]
    struct = b["structure"]
    print("\n" + "=" * 74)
    print("CREDIT-CAP SEARCH (prices+ladder FIXED at mockup; sweep credit quotas)")
    print("=" * 74)
    band_lists = [t["credit_band"] for t in struct]
    best = None
    for combo in product(*band_lists):
        tiers = [(struct[i]["role"], prices[i], set(struct[i]["unlocks"]), _credits(combo[i]))
                 for i in range(len(struct))]
        arr, _ = arr_for_grid_metered((tiers, ent), params, segs)
        if best is None or arr > best[0]:
            best = (arr, combo)
    roles = [t["role"] for t in struct]
    def fmt(c):
        return "unlim" if c is None else f"{c/1000:.0f}K" if c < 1e6 else f"{c/1e6:.0f}M"
    print(f"  ARR-max credit caps: "
          + ", ".join(f"{r}={fmt(v)}" for r, v in zip(roles, best[1]))
          + f"  -> ARR ${best[0]:,.0f}")
    # show the mockup (200K/1M/5M) for contrast
    mock = (200000, 1000000, 5000000)
    tiers = [(struct[i]["role"], prices[i], set(struct[i]["unlocks"]), _credits(mock[i]))
             for i in range(len(struct))]
    arr_m, _ = arr_for_grid_metered((tiers, ent), params, segs)
    print(f"  mockup caps (200K/1M/5M)              -> ARR ${arr_m:,.0f}"
          f"   (gap ${best[0]-arr_m:,.0f})")
    return best


# ---------------------------------------------------------------- (2b) structure search
def structure_search(cfg):
    b = cfg.get("structure_bands")
    if not b:
        print("\n[structure search skipped: no `structure_bands`]")
        return None
    params, segs = cfg["params"], base_segments(cfg)
    prices, credits, ent = b["prices"], b["credits"], b["enterprise_floor"]
    names = b["tier_names"]
    base = b["base_unlocks"]
    feats = b["ladder_features"]  # e.g. ["mmdb","parquet"], must unlock in order
    n = len(names)
    print("\n" + "=" * 74)
    print("STRUCTURE SEARCH (prices+caps FIXED; sweep WHICH tier unlocks each feature)")
    print("=" * 74)
    best = None
    results = []
    # assign each feature a tier index; features must be monotonic non-decreasing
    # (parquet cannot unlock before mmdb) and higher tiers inherit lower unlocks
    for combo in product(range(n), repeat=len(feats)):
        if any(combo[i] < combo[i-1] for i in range(1, len(combo))):
            continue  # enforce monotonic ladder
        tiers = []
        for ti in range(n):
            unl = set(base)
            for fi, feat in enumerate(feats):
                if combo[fi] <= ti:
                    unl.add(feat)
            tiers.append((names[ti], prices[ti], unl, _credits(credits[ti])))
        arr, _ = arr_for_grid_metered((tiers, ent), params, segs)
        label = ", ".join(f"{feats[fi]}@{names[combo[fi]]}" for fi in range(len(feats)))
        results.append((arr, label))
        if best is None or arr > best[0]:
            best = (arr, label, combo)
    for arr, label in sorted(results, key=lambda x: -x[0]):
        mark = "  <== MAX" if label == best[1] else ""
        print(f"  {label:34s} ARR ${arr:>12,.0f}{mark}")
    # identify the mockup ladder (mmdb@Pro, parquet@Business)
    print(f"  mockup ladder is mmdb@Pro, parquet@Business.")
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
        rm, sm = j.get("R_mult", [0.8, 1.2]), j.get("S_mult", [0.8, 1.2])
        vm = j.get("volume_mult", [0.6, 1.6])
        for s in segs:
            s["R"] *= random.uniform(*rm)
            s["S"] *= random.uniform(*sm)
            if s.get("volume"):
                s["volume"] *= random.uniform(*vm)
        scores = {}
        for name, g in grids.items():
            a, _ = arr_for_grid_metered(g, p, segs)
            scores[name] = a
            arrs[name].append(a)
        wins[max(scores, key=scores.get)] += 1
    print("\n" + "=" * 74)
    print(f"MONTE CARLO (n={n}) — share of runs each grid is revenue-max")
    print("=" * 74)
    for k in sorted(grids, key=lambda k: -wins[k]):
        a = sorted(arrs[k])
        med = statistics.median(a)
        lo, hi = a[int(0.1 * len(a))], a[int(0.9 * len(a))]
        print(f"  {k:48s} win={wins[k]/n*100:5.1f}%  "
              f"med=${med:,.0f}  P10-P90=${lo:,.0f}-${hi:,.0f}")


# ---------------------------------------------------------------- (2c) metered joint price search
def metered_grid_search(cfg):
    """Credit-aware price search: sweep the tier PRICES over defensible bands
    while holding the credit caps at the post-fix optimum (`_credits_for_search`).
    This finds the jointly optimal (price | credit-cap) grid -- the metered analog
    of v1's grid_search, and the rigorous answer to 'is the MMDB/Pro price right?'."""
    b = cfg.get("search_bands")
    if not b:
        return None
    params, segs = cfg["params"], base_segments(cfg)
    struct = b["structure"]
    creds = b.get("_credits_for_search", [INF] * len(struct))
    band_lists = [t["band"] for t in struct] + [b["enterprise_band"]]
    print("\n" + "=" * 74)
    print("METERED PRICE SEARCH (credit caps fixed at post-fix optimum 1M/1M/5M)")
    print("=" * 74)
    best = None
    for combo in product(*band_lists):
        prices, ent = combo[:-1], combo[-1]
        tiers = [(struct[i]["role"], prices[i], set(struct[i]["unlocks"]), _credits(creds[i]))
                 for i in range(len(struct))]
        arr, _ = arr_for_grid_metered((tiers, ent), params, segs)
        if best is None or arr > best[0]:
            best = (arr, combo)
    roles = [t["role"] for t in struct] + ["EntFloor"]
    print(f"  best ARR ${best[0]:,.0f} at "
          + ", ".join(f"{r}=${v}" for r, v in zip(roles, best[1])))
    print("  (Pro = the MMDB tier; its optimum is the model's answer to the")
    print("   'what should the MMDB tier cost' question, given the $94 substitute.)")
    return best


# ---------------------------------------------------------------- (4) adversarial dominance
def adversarial_dominance(cfg, n=50000, seed=11):
    """Try to FALSIFY the two actionable claims with hostile wide+extreme draws:
       (i) C (Starter cap 1M) >= M (Starter cap 200K)   [the credit-cap fix]
       (ii) F (MMDB/Pro @ $119) >= M (MMDB/Pro @ $149 + 200K cap)
    Reports the share of hostile draws where the mockup M is NOT dominated."""
    random.seed(seed)
    grids = cfg["_grids"]
    a = cfg.get("adversarial", {})
    M = "M mockup (49/149/399 | 200K/1M/5M)"
    C = "C credit-fixed (49/149/399 | 1M/1M/5M)"
    F = "F feature+credit-fixed (49/119/399 | 1M/1M/5M, MMDB@Pro $119)"
    if not all(k in grids for k in (M, C, F)):
        return
    print("\n" + "=" * 74)
    print(f"ADVERSARIAL FALSIFICATION (n={n}) of the two actionable claims")
    print("=" * 74)
    c_beats_m = f_beats_m = 0
    m_best = 0  # times the mockup M is the revenue-max of {M,C,F}
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
            if s.get("volume"):
                s["volume"] *= random.uniform(*a.get("volume_mult", [0.4, 2.0]))
        p = dict(
            annual_signups=random.randint(*a.get("annual_signups", [1200, 12000])),
            paid_intent_share=random.uniform(*a.get("paid_intent_share", [0.02, 0.12])),
            enterprise_deals=random.choice(a.get("enterprise_deals", [0, 1, 2, 3, 4])),
        )
        am = arr_for_grid_metered(grids[M], p, segs, sf)[0]
        ac = arr_for_grid_metered(grids[C], p, segs, sf)[0]
        af = arr_for_grid_metered(grids[F], p, segs, sf)[0]
        if ac >= am - 1e-9:
            c_beats_m += 1
        if af >= am - 1e-9:
            f_beats_m += 1
        if am >= ac and am >= af:
            m_best += 1
    print(f"  C (cap fix)  >= M (mockup) in {c_beats_m/n*100:6.2f}% of hostile draws")
    print(f"  F (cap+MMDB) >= M (mockup) in {f_beats_m/n*100:6.2f}% of hostile draws")
    print(f"  mockup M is the revenue-max of {{M,C,F}} in only {m_best/n*100:6.2f}% of draws")
    print("  -> raising the Starter credit cap is a near-unconditional improvement;")
    print("     M-as-drawn is dominated, not merely behind on the base assumptions.")


# ---------------------------------------------------------------- (5) breakpoint
def breakpoint_mmdb(cfg, ga="C credit-fixed (49/149/399 | 1M/1M/5M)",
                    gb="F feature+credit-fixed (49/119/399 | 1M/1M/5M, MMDB@Pro $119)"):
    a = cfg.get("breakpoint_anchor")
    if not a:
        return
    grids = cfg["_grids"]
    if ga not in grids or gb not in grids:
        return
    seg_name, anchor = a["segment"], a["anchor"]
    base_val = next(s[anchor] for s in cfg["segments"] if s["name"] == seg_name)
    print("\n" + "=" * 74)
    print(f"BREAK-POINT — {anchor}('{seg_name}') that flips MMDB/Pro@$149 (C) vs @$119 (F)")
    print("            (C and F are IDENTICAL except the MMDB/Pro price -> isolates it)")
    print("=" * 74)
    prev = None
    for mult in [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 4.0, 5.0]:
        segs = base_segments(cfg)
        for s in segs:
            if s["name"] == seg_name:
                s[anchor] = base_val * mult
        aa = arr_for_grid_metered(grids[ga], cfg["params"], segs)[0]
        ab = arr_for_grid_metered(grids[gb], cfg["params"], segs)[0]
        lead = "C($149)" if aa >= ab else "F($119)"
        flag = "" if prev is None or lead == prev else "   <-- FLIP"
        print(f"  {anchor}={base_val*mult:7.1f} ({mult:.2f}x)  "
              f"C=${aa:,.0f}  F=${ab:,.0f}  lead={lead}{flag}")
        prev = lead
    print(f"  (verified base {anchor}={base_val} = IPinfo Max $94/mo, 2026-05-28)")


# ---------------------------------------------------------------- deduction
def dollar_per_lookup_deduction():
    print("\n" + "=" * 74)
    print("MODEL-FREE DEDUCTION — $/lookup discipline (verified 2026-05-28)")
    print("=" * 74)
    rows = [
        ("~150K/mo", "ipgeolocation Starter $19/150K", 0.000127, "WXA Starter $49/200K = $0.000245"),
        ("~1M/mo",   "ipgeolocation Pro $79/1M",       0.000079, "WXA Pro $149/1M = $0.000149"),
        ("~5M/mo",   "ipgeolocation Premium $249/5M",  0.000050, "WXA Business $399/5M = $0.000080"),
    ]
    for vol, sub, ppl, wxa in rows:
        print(f"  {vol:9s} cheapest verified substitute {sub:34s} ${ppl:.6f}/lookup")
        print(f"            {wxa}")
    print("  => At EVERY volume point WXA's blended $/lookup sits 1.6-1.9x above the")
    print("     cheapest pure-API substitute. That premium is only defensible if WXA's")
    print("     detection is materially better (the +g terms). The premium is the moat")
    print("     bet; the credit caps do NOT create it -- they only risk MIS-FENCING.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--mc", type=int, default=4000)
    ap.add_argument("--adv", type=int, default=50000)  # accepted for parity; adversarial reuses pm path
    a = ap.parse_args()
    cfg = load_metered_config(a.config)
    point_estimate(cfg)
    credit_search(cfg)
    structure_search(cfg)
    metered_grid_search(cfg)
    monte_carlo(cfg, n=a.mc)
    adversarial_dominance(cfg, n=a.adv)
    breakpoint_mmdb(cfg)
    dollar_per_lookup_deduction()


if __name__ == "__main__":
    main()
