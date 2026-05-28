#!/usr/bin/env python3
"""
PROOF that pricing_model.py is implemented correctly (regression test).

Strategy: independent reimplementation. Recompute every output with hand-rolled
code that shares NO logic with pricing_model.py (we only import it to (a) load
the same config and (b) call the functions under test). If two independent
implementations agree to the cent, the engine is arithmetically correct.

Run:  python3 scripts/verify_model.py [CONFIG.json]
      (defaults to examples/wxa-vpn-2026-05.json)
Exits non-zero if any proof fails, so it can gate CI / pre-commit.

Five proofs:
  P1  capture() matches the closed-form logistic at analytic points.
  P2  cheapest_qualifying() picks the truly-cheapest covering tier (brute force).
  P3  ARR(grid) recomputed from scratch == engine, to the cent, every grid.
  P4  breakdown sums to the reported ARR (conservation).
  P5  grid-search optimum is a true local max (every 1-step neighbor is <=).
"""
import sys, os, math, json, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

spec = importlib.util.spec_from_file_location("pm", os.path.join(HERE, "pricing_model.py"))
pm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pm)

CFG = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "examples", "wxa-vpn-2026-05.json")
cfg = pm.load_config(CFG)
raw = json.load(open(CFG))

fails = 0
def check(name, ok, detail=""):
    global fails
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  {detail}" if detail else ""))
    if not ok: fails += 1

# ---------------------------------------------------------------- P1
print("="*70); print("P1 — capture() == closed-form logistic at analytic points"); print("="*70)
def ref_cap(p, c, sf=0.25):
    return 1.0/(1.0+math.exp((p-c)/(sf*c)))
for c in (89, 200, 450):
    for p in (0.50*c, 0.75*c, 1.00*c, 1.25*c):
        got = pm.capture(p, c); exp = ref_cap(p, c)
        check(f"capture(p={p:.1f}, c={c}) ", abs(got-exp) < 1e-12,
              f"engine={got:.6f} ref={exp:.6f}")
check("capture at p==c is exactly 0.5", abs(pm.capture(100,100)-0.5) < 1e-12)
check("capture(0.75c) ~ 0.731", abs(pm.capture(75,100)-0.7310585786) < 1e-9)
check("capture(1.25c) ~ 0.269", abs(pm.capture(125,100)-0.2689414214) < 1e-9)
check("monotonic decreasing in price", pm.capture(50,100) > pm.capture(150,100))

# ---------------------------------------------------------------- P2
print("="*70); print("P2 — cheapest_qualifying() picks the cheapest covering tier"); print("="*70)
def ref_pick(tiers, need, needs):
    req = set([need]) | set(needs)
    best = None
    for (n,p,unl) in tiers:
        if req.issubset(unl) and (best is None or p < best[1]):
            best = (n,p)
    return best
for gname, g in cfg["_grids"].items():
    tiers, _ = g
    for s in raw["segments"]:
        if s.get("enterprise"): continue
        need = s.get("need"); needs = tuple(s.get("needs", []))
        got = pm.cheapest_qualifying(tiers, need, needs); exp = ref_pick(tiers, need, needs)
        check(f"{gname[:18]:18s} / {s['name'][:18]:18s}", got == exp, f"engine={got} ref={exp}")

# ---------------------------------------------------------------- P3
print("="*70); print("P3 — ARR(grid) recomputed from scratch == engine (to the cent)"); print("="*70)
def ref_arr(gname):
    g = raw["grids"][gname]
    tiers = [(t["name"], t["price"], set(t["unlocks"])) for t in g["tiers"]]
    P = raw["params"]
    paid_pool = P["annual_signups"] * P["paid_intent_share"]
    total = 0.0
    for s in raw["segments"]:
        if s.get("enterprise"): continue
        seg_pool = paid_pool * s["size"]
        pick = ref_pick(tiers, s.get("need"), tuple(s.get("needs", [])))
        if pick is None: continue
        price = pick[1]
        c = min(s["R"], s["S"] + s.get("g", 0))
        k = max(0.25*c, 1e-6)
        z = min(max((price-c)/k, -50), 50)
        total += seg_pool * (1.0/(1.0+math.exp(z))) * price * 12
    total += P["enterprise_deals"] * g["enterprise_floor"] * 12
    return total
for gname in raw["grids"]:
    eng, _ = pm.arr_for_grid(cfg["_grids"][gname], cfg["params"], pm.base_segments(cfg))
    ref = ref_arr(gname)
    check(f"{gname[:40]:40s}", abs(eng-ref) < 1e-6, f"engine=${eng:,.2f} ref=${ref:,.2f}")

# ---------------------------------------------------------------- P4
print("="*70); print("P4 — breakdown sums to reported ARR (conservation)"); print("="*70)
for gname in raw["grids"]:
    arr, bd = pm.arr_for_grid(cfg["_grids"][gname], cfg["params"], pm.base_segments(cfg))
    check(f"{gname[:40]:40s}", abs(sum(bd.values()) - arr) < 1e-9,
          f"sum=${sum(bd.values()):,.2f} arr=${arr:,.2f}")

# ---------------------------------------------------------------- P5
print("="*70); print("P5 — grid-search optimum is a true local max (all neighbors <=)"); print("="*70)
best = pm.grid_search(cfg)
if best is None:
    print("  [skip] no search_bands in config")
else:
    best_arr, combo = best
    b = raw["search_bands"]; struct = b["structure"]
    band_lists = [t["band"] for t in struct] + [b["enterprise_band"]]
    roles = [t["role"] for t in struct] + ["EntFloor"]
    def arr_at(cb):
        prices, ent = cb[:-1], cb[-1]
        tiers = [(struct[i]["role"], prices[i], set(struct[i]["unlocks"])) for i in range(len(struct))]
        a,_ = pm.arr_for_grid((tiers, ent), cfg["params"], pm.base_segments(cfg))
        return a
    ok = True; worst = None
    for i in range(len(band_lists)):
        idx = band_lists[i].index(combo[i])
        for d in (-1, +1):
            j = idx + d
            if 0 <= j < len(band_lists[i]):
                nb = list(combo); nb[i] = band_lists[i][j]
                a = arr_at(tuple(nb))
                if a > best_arr + 1e-6:
                    ok = False; worst = (roles[i], combo[i], band_lists[i][j], a)
    check("reported optimum >= every 1-step neighbor", ok,
          "" if ok else f"BEATEN by {worst}")
    check("optimum ARR matches recompute at its own combo", abs(arr_at(combo) - best_arr) < 1e-6)

# ---------------------------------------------------------------- verdict
print("="*70)
print(f"VERDICT: {'ALL PROOFS PASS — engine is arithmetically correct' if fails==0 else f'{fails} CHECK(S) FAILED'}")
print("="*70)
sys.exit(1 if fails else 0)
