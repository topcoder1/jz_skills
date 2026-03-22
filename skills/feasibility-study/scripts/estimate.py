#!/usr/bin/env python3
"""
Deterministic cost and effort estimation calculations.

Reads JSON from stdin, writes JSON to stdout.
Uses Python stdlib only — no pip dependencies.

Supported operations:
  cocomo          - COCOMO II effort/schedule estimation
  function_points - Function point to effort conversion
  tshirt          - T-shirt sizing to cost range mapping
  tco             - Total cost of ownership projection
  roi             - ROI and payback period calculation

Usage:
  echo '{"operation": "cocomo", "kloc": 50, "mode": "semi-detached"}' | python3 estimate.py
"""

import json
import math
import sys

# --- COCOMO II Parameters ---

COCOMO_PARAMS = {
    "organic": {"a": 2.4, "b": 1.05, "c": 2.5, "d": 0.38},
    "semi-detached": {"a": 3.0, "b": 1.12, "c": 2.5, "d": 0.35},
    "embedded": {"a": 3.6, "b": 1.20, "c": 2.5, "d": 0.32},
}

# Blended monthly cost by region (USD, fully loaded)
MONTHLY_RATES = {
    "us_senior": 20000,    # ~$120/hr fully loaded
    "us_mid": 14000,       # ~$85/hr fully loaded
    "us_junior": 9000,     # ~$55/hr fully loaded
    "offshore": 6000,      # ~$36/hr fully loaded
    "blended_us": 15000,   # Mixed seniority US team
    "blended_mixed": 10000, # US leads + offshore devs
}

# --- T-shirt Sizing Parameters ---

TSHIRT_ESTIMATES = {
    "simple": {
        "solo": {"weeks": (4, 8), "cost": (10000, 30000)},
        "small": {"weeks": (2, 4), "cost": (25000, 75000)},
        "team": {"weeks": (1, 2), "cost": (50000, 150000)},
        "large": {"weeks": (1, 1), "cost": (100000, 300000)},
    },
    "moderate": {
        "solo": {"weeks": (12, 24), "cost": (30000, 100000)},
        "small": {"weeks": (8, 12), "cost": (75000, 250000)},
        "team": {"weeks": (4, 8), "cost": (150000, 500000)},
        "large": {"weeks": (3, 6), "cost": (300000, 1000000)},
    },
    "complex": {
        "solo": {"weeks": (36, 72), "cost": (100000, 500000)},
        "small": {"weeks": (24, 36), "cost": (250000, 750000)},
        "team": {"weeks": (16, 24), "cost": (500000, 2000000)},
        "large": {"weeks": (12, 16), "cost": (1000000, 5000000)},
    },
    "extreme": {
        "solo": {"weeks": (104, 156), "cost": (500000, 2000000)},
        "small": {"weeks": (48, 72), "cost": (750000, 3000000)},
        "team": {"weeks": (36, 48), "cost": (2000000, 10000000)},
        "large": {"weeks": (24, 36), "cost": (5000000, 20000000)},
    },
}

# --- Functions ---


def cocomo(data):
    """
    COCOMO II estimation.

    Input:
      kloc: estimated thousands of lines of code
      mode: organic | semi-detached | embedded
      eaf: effort adjustment factor (optional, default 1.0)

    Output:
      effort_person_months, schedule_months, team_size, cost estimates
    """
    kloc = data["kloc"]
    mode = data.get("mode", "semi-detached")
    eaf = data.get("eaf", 1.0)

    if mode not in COCOMO_PARAMS:
        return {"error": f"Invalid mode: {mode}. Use: organic, semi-detached, embedded"}

    params = COCOMO_PARAMS[mode]

    effort_pm = params["a"] * (kloc ** params["b"]) * eaf
    schedule_months = params["c"] * (effort_pm ** params["d"])
    team_size = effort_pm / schedule_months if schedule_months > 0 else 0

    costs = {}
    for region, rate in MONTHLY_RATES.items():
        costs[region] = round(effort_pm * rate)

    return {
        "effort_person_months": round(effort_pm, 1),
        "schedule_months": round(schedule_months, 1),
        "team_size": round(team_size, 1),
        "kloc": kloc,
        "mode": mode,
        "eaf": eaf,
        "cost_by_region": costs,
    }


def function_points(data):
    """
    Function point to effort conversion.

    Input:
      unadjusted_fp: total unadjusted function points
      vaf: value adjustment factor (optional, default 1.0)
      complexity: simple | average | complex
      hours_per_fp: override hours per FP (optional)

    Output:
      adjusted_fp, effort_hours, effort_person_months, cost estimates
    """
    ufp = data["unadjusted_fp"]
    vaf = data.get("vaf", 1.0)
    complexity = data.get("complexity", "average")

    hours_map = {"simple": 10, "average": 14, "complex": 20}
    hours_per_fp = data.get("hours_per_fp", hours_map.get(complexity, 14))

    adjusted_fp = ufp * vaf
    effort_hours = adjusted_fp * hours_per_fp
    effort_pm = effort_hours / 160  # 160 hours per person-month

    costs = {}
    for region, monthly_rate in MONTHLY_RATES.items():
        hourly = monthly_rate / 160
        costs[region] = round(effort_hours * hourly)

    return {
        "unadjusted_fp": ufp,
        "vaf": vaf,
        "adjusted_fp": round(adjusted_fp, 1),
        "hours_per_fp": hours_per_fp,
        "effort_hours": round(effort_hours),
        "effort_person_months": round(effort_pm, 1),
        "cost_by_region": costs,
    }


def tshirt(data):
    """
    T-shirt sizing estimation.

    Input:
      complexity: simple | moderate | complex | extreme
      team_size: solo | small | team | large

    Output:
      duration range, cost range
    """
    complexity = data.get("complexity", "moderate")
    team = data.get("team_size", "small")

    if complexity not in TSHIRT_ESTIMATES:
        return {"error": f"Invalid complexity: {complexity}. Use: simple, moderate, complex, extreme"}
    if team not in TSHIRT_ESTIMATES[complexity]:
        return {"error": f"Invalid team_size: {team}. Use: solo, small, team, large"}

    est = TSHIRT_ESTIMATES[complexity][team]

    return {
        "complexity": complexity,
        "team_size": team,
        "duration_weeks_min": est["weeks"][0],
        "duration_weeks_max": est["weeks"][1],
        "duration_months_min": round(est["weeks"][0] / 4.33, 1),
        "duration_months_max": round(est["weeks"][1] / 4.33, 1),
        "cost_min": est["cost"][0],
        "cost_max": est["cost"][1],
    }


def tco(data):
    """
    Total cost of ownership projection.

    Input:
      development_cost: one-time development cost
      monthly_infrastructure: monthly infra cost
      monthly_saas: monthly SaaS tooling cost
      monthly_support: monthly support/ops cost
      annual_growth_rate: YoY cost growth rate (default 0.2 = 20%)
      years: projection period (default 3)

    Output:
      yearly breakdown, cumulative TCO
    """
    dev_cost = data["development_cost"]
    monthly_infra = data.get("monthly_infrastructure", 0)
    monthly_saas = data.get("monthly_saas", 0)
    monthly_support = data.get("monthly_support", 0)
    growth = data.get("annual_growth_rate", 0.2)
    years = data.get("years", 3)

    projections = []
    cumulative = dev_cost

    for year in range(1, years + 1):
        multiplier = (1 + growth) ** (year - 1)
        infra = round(monthly_infra * 12 * multiplier)
        saas = round(monthly_saas * 12 * multiplier)
        support = round(monthly_support * 12 * multiplier)
        annual_ops = infra + saas + support
        cumulative += annual_ops

        projections.append({
            "year": year,
            "infrastructure": infra,
            "saas_tooling": saas,
            "support_ops": support,
            "annual_operating": annual_ops,
            "cumulative_tco": round(cumulative),
        })

    return {
        "development_cost": dev_cost,
        "projections": projections,
        "total_tco": round(cumulative),
        "years": years,
    }


def roi(data):
    """
    ROI and payback period calculation.

    Input:
      development_cost: one-time development cost
      annual_operating_cost: yearly operating cost
      annual_revenue: yearly revenue (or projected)
      years: projection period (default 3)
      revenue_growth_rate: YoY revenue growth (default 0.5 = 50%)
      cost_growth_rate: YoY cost growth (default 0.2 = 20%)

    Output:
      yearly P&L, cumulative ROI, payback period
    """
    dev_cost = data["development_cost"]
    annual_ops = data["annual_operating_cost"]
    annual_rev = data["annual_revenue"]
    years = data.get("years", 3)
    rev_growth = data.get("revenue_growth_rate", 0.5)
    cost_growth = data.get("cost_growth_rate", 0.2)

    projections = []
    cumulative_revenue = 0
    cumulative_cost = dev_cost
    payback_month = None

    for year in range(1, years + 1):
        rev = round(annual_rev * (1 + rev_growth) ** (year - 1))
        ops = round(annual_ops * (1 + cost_growth) ** (year - 1))
        net = rev - ops

        cumulative_revenue += rev
        cumulative_cost += ops

        cumulative_profit = cumulative_revenue - cumulative_cost
        roi_pct = (cumulative_profit / dev_cost * 100) if dev_cost > 0 else 0

        projections.append({
            "year": year,
            "revenue": rev,
            "operating_cost": ops,
            "net_income": net,
            "cumulative_revenue": cumulative_revenue,
            "cumulative_cost": round(cumulative_cost),
            "cumulative_profit": round(cumulative_profit),
            "cumulative_roi_pct": round(roi_pct, 1),
        })

        # Estimate payback month (linear interpolation within the year)
        if payback_month is None and cumulative_profit >= 0:
            if year == 1:
                # Payback within first year
                monthly_net = net / 12
                if monthly_net > 0:
                    months_needed = math.ceil(dev_cost / monthly_net)
                    payback_month = min(months_needed, 12)
            else:
                prev_profit = projections[-2]["cumulative_profit"]
                if prev_profit < 0:
                    fraction = abs(prev_profit) / (cumulative_profit - prev_profit)
                    payback_month = round((year - 1) * 12 + fraction * 12)

    return {
        "development_cost": dev_cost,
        "projections": projections,
        "payback_months": payback_month,
        "final_roi_pct": projections[-1]["cumulative_roi_pct"] if projections else 0,
    }


# --- Main ---

OPERATIONS = {
    "cocomo": cocomo,
    "function_points": function_points,
    "tshirt": tshirt,
    "tco": tco,
    "roi": roi,
}


def main():
    try:
        data = json.loads(sys.stdin.read())
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON input: {e}"}))
        sys.exit(1)

    operation = data.get("operation")
    if not operation:
        print(json.dumps({"error": "Missing 'operation' field", "available": list(OPERATIONS.keys())}))
        sys.exit(1)

    if operation not in OPERATIONS:
        print(json.dumps({"error": f"Unknown operation: {operation}", "available": list(OPERATIONS.keys())}))
        sys.exit(1)

    try:
        result = OPERATIONS[operation](data)
        print(json.dumps(result, indent=2))
    except KeyError as e:
        print(json.dumps({"error": f"Missing required field: {e}"}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"error": f"Calculation error: {e}"}))
        sys.exit(1)


if __name__ == "__main__":
    main()
