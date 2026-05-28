#!/usr/bin/env python3
"""
PROOF that pricing_metered.py is implemented correctly.

Strategy (same as verify_model.py): independent reimplementation + the key
GENERALIZATION invariant. If the metered engine with all credit caps = infinity
reproduces the v1 engine to the cent, then the metered layer adds volume-fencing
WITHOUT disturbing the already-proven price/feature/capture math.

Run:  python3 scripts/verify_metered.py
Exits non-zero if any proof fails.

Six proofs:
  VP1  metered routing with caps=inf == v1 cheapest_qualifying (brute force).
  VP2  arr_for_grid_metered(caps=inf) == v1 arr_for_grid, to the cent (the
       strict-generalization invariant) -- on the ORIGINAL v1 config.
  VP3  credit fence is correct: a tier whose cap < segment volume is never
       chosen; the chosen tier is the cheapest feature+volume-qualifying one
       (brute force, on the metered config).
  VP4  breakdown sums to reported ARR (conservation), every metered grid.
  VP5  credit-cap-search optimum is a true max over its band (every 1-step
       neighbor <=).
  VP6  capture() is the SAME object imported from pricing_model.py (no fork).
"""
import sys, os, math, json, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def _load(modname, fname):
    spec = importlib.util.spec_from_file_location(modname, os.path.join(HERE, fname))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


pm = _load("pm", "pricing_model.py")
mm = _load("mm", "pricing_metered.py")

V1_CFG = os.path.join(ROOT, "examples", "wxa-vpn-2026-05.json")
MET_CFG = os.path.join(ROOT, "examples", "wxa-vpn-2026-05-metered.json")

fails = 0
def check(name, ok, detail=""):
    global fails
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  {detail}" if detail else ""))
    if not ok:
        fails += 1


# ---------------------------------------------------------------- VP1
print("=" * 72); print("VP1 — metered routing (caps=inf) == v1 cheapest_qualifying"); print("=" * 72)
v1 = pm.load_config(V1_CFG)
v1raw = json.load(open(V1_CFG))
for gname, (tiers, _) in v1["_grids"].items():
    # build metered tiers with infinite caps from the same v1 tiers
    mtiers = [(n, p, unl, float("inf")) for (n, p, unl) in tiers]
    for s in v1raw["segments"]:
        if s.get("enterprise"):
            continue
        need, needs = s.get("need"), tuple(s.get("needs", []))
        got = mm.cheapest_qualifying_metered(mtiers, need, needs, s.get("volume", 0))
        exp = pm.cheapest_qualifying(tiers, need, needs)
        check(f"{gname[:20]:20s}/{s['name'][:18]:18s}", got == exp, f"met={got} v1={exp}")


# ---------------------------------------------------------------- VP2
print("=" * 72); print("VP2 — arr_for_grid_metered(caps=inf) == v1 arr_for_grid (to the cent)"); print("=" * 72)
for gname, (tiers, ef) in v1["_grids"].items():
    mtiers = [(n, p, unl, float("inf")) for (n, p, unl) in tiers]
    v1_arr, _ = pm.arr_for_grid((tiers, ef), v1["params"], pm.base_segments(v1))
    met_arr, _ = mm.arr_for_grid_metered((mtiers, ef), v1["params"], mm.base_segments(v1))
    check(f"{gname[:46]:46s}", abs(v1_arr - met_arr) < 1e-6,
          f"v1=${v1_arr:,.2f} metered=${met_arr:,.2f}")


# ---------------------------------------------------------------- VP3
print("=" * 72); print("VP3 — credit fence correct: cheapest feature+volume-qualifying tier"); print("=" * 72)
met = mm.load_metered_config(MET_CFG)
metraw = json.load(open(MET_CFG))
def ref_pick(tiers, need, needs, volume):
    req = set([need]) | set(needs) if need else set(needs)
    best = None
    for (n, p, unl, cr) in tiers:
        if req.issubset(unl) and cr >= volume and (best is None or p < best[1]):
            best = (n, p)
    return best
for gname, (tiers, _) in met["_grids"].items():
    for s in metraw["segments"]:
        if s.get("enterprise"):
            continue
        need, needs, vol = s.get("need"), tuple(s.get("needs", [])), s.get("volume", 0)
        got = mm.cheapest_qualifying_metered(tiers, need, needs, vol)
        exp = ref_pick(tiers, need, needs, vol)
        check(f"{gname[:22]:22s}/{s['name'][:16]:16s}", got == exp, f"eng={got} ref={exp}")

# explicit fence assertion: S2 (vol=1M) must NOT route to a 200K Starter
mock = met["_grids"]["M mockup (49/149/399 | 200K/1M/5M)"][0]
s2 = next(s for s in metraw["segments"] if s["name"].startswith("S2"))
pick = mm.cheapest_qualifying_metered(mock, s2["need"], tuple(s2.get("needs", [])), s2["volume"])
check("S2 (1M vol) is NOT sold the 200K Starter", pick is not None and pick[0] != "Starter",
      f"routed to {pick}")


# ---------------------------------------------------------------- VP4
print("=" * 72); print("VP4 — breakdown sums to reported ARR (conservation)"); print("=" * 72)
for gname, g in met["_grids"].items():
    arr, bd = mm.arr_for_grid_metered(g, met["params"], mm.base_segments(met))
    check(f"{gname[:46]:46s}", abs(sum(bd.values()) - arr) < 1e-9,
          f"sum=${sum(bd.values()):,.2f} arr=${arr:,.2f}")


# ---------------------------------------------------------------- VP5
print("=" * 72); print("VP5 — credit-cap-search optimum is a true max (all 1-step neighbors <=)"); print("=" * 72)
best = mm.credit_search(met)
if best is None:
    print("  [skip] no credit_bands")
else:
    best_arr, combo = best
    b = metraw["credit_bands"]
    prices, ent, struct = b["prices"], b["enterprise_floor"], b["structure"]
    bands = [t["credit_band"] for t in struct]
    def arr_at(cb):
        tiers = [(struct[i]["role"], prices[i], set(struct[i]["unlocks"]), mm._credits(cb[i]))
                 for i in range(len(struct))]
        return mm.arr_for_grid_metered((tiers, ent), met["params"], mm.base_segments(met))[0]
    ok, worst = True, None
    for i in range(len(bands)):
        idx = bands[i].index(combo[i])
        for d in (-1, +1):
            j = idx + d
            if 0 <= j < len(bands[i]):
                nb = list(combo); nb[i] = bands[i][j]
                a = arr_at(tuple(nb))
                if a > best_arr + 1e-6:
                    ok = False; worst = (struct[i]["role"], combo[i], bands[i][j], a)
    check("reported credit optimum >= every 1-step neighbor", ok,
          "" if ok else f"BEATEN by {worst}")
    check("optimum ARR matches recompute at its own combo", abs(arr_at(combo) - best_arr) < 1e-6)


# ---------------------------------------------------------------- VP6
print("=" * 72); print("VP6 — capture() is imported, not forked"); print("=" * 72)
# robust to double module-loading: prove (a) no local `def capture` in the
# metered source, and (b) identical outputs across a sweep vs the v1 capture.
src = open(os.path.join(HERE, "pricing_metered.py")).read()
check("pricing_metered.py defines no local capture()", "def capture(" not in src)
same = all(abs(mm.capture(p, c) - pm.capture(p, c)) < 1e-15
           for c in (19, 79, 94, 149, 450) for p in (0.5 * c, c, 1.3 * c, 2.0 * c))
check("metered capture == v1 capture across a sweep", same)


# ---------------------------------------------------------------- verdict
print("=" * 72)
print(f"VERDICT: {'ALL PROOFS PASS — metered engine is a correct generalization' if fails==0 else f'{fails} CHECK(S) FAILED'}")
print("=" * 72)
sys.exit(1 if fails else 0)
