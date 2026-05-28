#!/usr/bin/env python3
"""
PREMIUM-POSITIONING SENSITIVITY (config-driven).

Answers: "Can we position as the premium vendor, and how does that change the
pricing model?" -- as a verified frontier, not an assertion.

In the proven engine willingness-to-pay is c = min(R, S+g) and demand is logistic
around c with steepness k = scale_frac*c. "Premium positioning" decomposes into a
bet on TWO quantities, only one of which pricing controls:

  g  (differentiation premium) : $/mo buyers pay ABOVE the substitute S because
                                 WXA is materially better (you EARN this with
                                 provable data superiority; capped by R).
  k  (price-sensitivity)       : how fast buyers defect to the cheaper substitute
                                 as price rises (low k = loyal/sticky).

Three results, all reproducible:

  (1) CEILING PROOF      revenue-max price p* NEVER exceeds c=min(R,S+g). Loyalty
                         (low k) only lets p* approach c, never cross it. So you
                         cannot price above a substitute by branding alone -- only
                         by raising c (recognized differentiation g), itself <= R.
  (2) g/k FRONTIER       lambda* (ARR-max multiplier on a value-anchored vector)
                         as a function of (g_premium, scale_frac).
  (3) PER-TIER FRONTIER  each tier's revenue-max price vs ITS OWN substitute --
                         shows premium is asymmetric: a lever at the top (no
                         self-serve substitute) and a trap at the bottom.

Usage:  python3 premium_positioning.py [CONFIG.json]
Default config: examples/wxa-vpn-2026-05-metered.json
"""
import os, sys, math, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
spec = importlib.util.spec_from_file_location("mm", os.path.join(HERE, "pricing_metered.py"))
mm = importlib.util.module_from_spec(spec); spec.loader.exec_module(mm)

CFG = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    ROOT, "examples", "wxa-vpn-2026-05-metered.json")
cfg = mm.load_metered_config(CFG)
params = cfg["params"]


# ----------------------------------------------------------------- (1) ceiling
def revmax_price(c, k, hi_mult=30):
    ps = [x / 10 for x in range(1, int(c * hi_mult))]
    return max(ps, key=lambda p: p * mm.capture(p, c, k))

def ceiling_proof():
    print("=" * 78)
    print("(1) CEILING PROOF — revenue-max price p* never exceeds c = min(R, S+g)")
    print("=" * 78)
    print("    c        k      p*      p*/c    p* > c ?")
    bug = False
    # use the three binding constraints S+g for the non-trivial segments
    cs = sorted({min(s["R"], s["S"] + s.get("g", 0))
                 for s in cfg["segments"] if not s.get("enterprise")})
    for c in cs:
        for k in (0.45, 0.35, 0.25, 0.15, 0.10, 0.05):
            p = revmax_price(c, k)
            over = p > c + 1e-6
            bug = bug or over
            print(f"    {c:6.0f} {k:6.2f} {p:7.1f} {p/c:7.3f}    {'YES-BUG' if over else 'no'}")
        print()
    print("    PROOF:", "FAILED" if bug else "p* < c for every (c,k).",
          "Loyalty (low k) raises p* toward c but never past it.")
    print("    => A premium ABOVE the substitute requires raising c (the +g term),")
    print("       not lowering price-sensitivity. c is itself hard-capped by R.\n")
    return not bug


# ----------------------------------------------------------- (2) g/k frontier
BASE_PRICES = {"Starter": 49.0, "Pro": 119.0, "Business": 399.0}
BASE_ENT = 2000.0
CAPS = {"Starter": 1_000_000, "Pro": 1_000_000, "Business": 5_000_000}
UNL = {"Starter": {"api_low", "api_mid"},
       "Pro": {"api_low", "api_mid", "mmdb"},
       "Business": {"api_low", "api_mid", "mmdb", "parquet"}}
ORDER = ("Starter", "Pro", "Business")

def grid_scaled(lmbda):
    tiers = [(r, BASE_PRICES[r] * lmbda, UNL[r], float(CAPS[r])) for r in ORDER]
    return (tiers, BASE_ENT * lmbda)

def segs_gp(gp):
    segs = mm.base_segments(cfg)
    for s in segs:
        if not s.get("enterprise"):
            s["g"] = s.get("g", 0) + gp
    return segs

LAMBDAS = [round(0.8 + 0.05 * i, 2) for i in range(33)]  # 0.80..2.40
def best_lambda(gp, sf):
    segs = segs_gp(gp)
    best = None
    for lm in LAMBDAS:
        a = mm.arr_for_grid_metered(grid_scaled(lm), params, segs, sf)[0]
        if best is None or a > best[1] + 1e-9:
            best = (lm, a)
    return best

def gk_frontier():
    print("=" * 78)
    print("(2) g/k FRONTIER — lambda* (ARR-max multiplier on the value price vector)")
    print("    lambda<=1.00 => premium destroys value; lambda>1.00 => premium pays")
    print("=" * 78)
    G = [0, 25, 50, 75, 100, 150, 200]
    K = [0.10, 0.15, 0.20, 0.25, 0.35, 0.45]
    hdr = "    g\\k  " + "".join(f"{k:>7.2f}" for k in K)
    print(hdr); print("    " + "-" * (len(hdr) - 4))
    for gp in G:
        row = f"    +{gp:<4d}" + "".join(f"{best_lambda(gp, k)[0]:>7.2f}" for k in K)
        nrc = sum(1 for s in cfg["segments"] if not s.get("enterprise")
                  and s["S"] + s.get("g", 0) + gp >= s["R"])
        print(row + f"   [{nrc}/4 R-capped]")
    print("    NOTE: a uniform multiplier is a blunt instrument -- lambda*>1 here is")
    print("    driven by ONE underpriced tier (see (3)); it overshoots others. The")
    print("    per-tier view is the actionable one.\n")


# --------------------------------------------------------- (3) per-tier frontier
# Verified substitutes per tier's dominant buyer. Values match the committed
# config (S3 substitute = $94) so the displayed ratio and the computed optimum
# use the SAME anchor. LIVE VERIFICATION (2026-05-28) of the load-bearing IPinfo
# fact: the $49/$74/$94 plans are API-LOOKUP subscriptions; the downloadable
# named-provider MMDB is SALES-GATED at every self-serve tier ("not included in
# self-serve plans... contact our sales team", no published price). So the $74-$94
# anchor is correct ONLY for API access -- a WXA tier that ships a downloadable
# MMDB FILE faces no self-serve substitute and belongs in the premium-lever column
# with Business/Enterprise, NOT capped at $74/$94. The Pro anchor below ($94) is
# therefore the API-access substitute (IPinfo Max API), held config-consistent so
# ratio and optimum share one number; treat the MMDB-download capability as a lever.
# Business is also two buyers: residential-attribution (IPinfo Max API $94, self-
# serve) vs bulk-Parquet (Spur/IPQS $900, NOT self-serve anywhere). The $399 tier
# bundles ~10x-different substitutes (packaging problem). The $900 anchor below is
# the bulk-Parquet buyer.
TIER_SUB = {
    "Starter":  ("ipgeolocation Pro 1M (S2)",          79,  130),
    "Pro":      ("IPinfo Max API (MMDB dl sales-gated)", 94, 200),
    "Business": ("Spur/IPQS bulk Parquet (S4)",         900, 750),
}
BANDS = {"Starter": range(19, 160, 2),
         "Pro": range(49, 420, 2),
         "Business": range(299, 1000, 5)}

def grid_prices(prices):
    return ([(r, prices[r], UNL[r], float(CAPS[r])) for r in ORDER], BASE_ENT)

def best_price(tier, sf):
    prices = dict(BASE_PRICES); best = None
    for p in BANDS[tier]:
        prices[tier] = float(p)
        a = mm.arr_for_grid_metered(grid_prices(prices), params, mm.base_segments(cfg), sf)[0]
        if best is None or a > best[1] + 1e-9:
            best = (float(p), a)
    return best[0]

def per_tier_frontier():
    print("=" * 78)
    print("(3) PER-TIER FRONTIER — revenue-max price vs the tier's OWN substitute")
    print("=" * 78)
    for sf, lab in [(0.25, "default k=0.25"), (0.12, "premium-loyal k=0.12")]:
        print(f"\n    ---- {lab} ----")
        print(f"    {'tier':9s} {'price*':>7s} {'sub':>6s} {'ratio':>7s}  verdict")
        for t in ORDER:
            p = best_price(t, sf); name, S, R = TIER_SUB[t]
            ratio = p / S
            v = ("at/below substitute -> NOT a premium lever" if ratio <= 1.02
                 else "modest premium defensible" if ratio <= 1.35
                 else "strong premium (substitute costly/absent)")
            print(f"    {t:9s} ${p:>6.0f} ${S:>5.0f} {ratio:>6.2f}x  {v}")
    print("\n    => premium is ASYMMETRIC. Levers (no self-serve substitute): Business")
    print("       bulk-Parquet (sub $900), Enterprise (none), AND the downloadable-MMDB")
    print("       feature (IPinfo MMDB dl is sales-gated, verified 2026-05-28). Traps")
    print("       (cheap self-serve substitute exists): Starter (sub $79) and Pro priced")
    print("       as plain API access (IPinfo Max API $94). The $94 Pro anchor caps API")
    print("       access only -- the MMDB download is a lever, not a $94-capped product.\n")


if __name__ == "__main__":
    print(f"config: {CFG}\n")
    ok = ceiling_proof()
    gk_frontier()
    per_tier_frontier()
    print("HONESTY BAR: g and R (the premium thesis) are ASSUMPTIONS; the substitute")
    print("anchors S are verified 2026-05-28. The dollar-exact answer is a live A/B")
    print("price test. This frontier tells you HOW MUCH differentiation you must")
    print("deliver+communicate (raise g) to earn a premium -- it cannot grant one.")
    sys.exit(0 if ok else 1)
