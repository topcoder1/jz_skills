# Feasibility Report Template

Use this template to generate the final report. Replace all `{placeholders}`
with actual values from the analysis.

---

# Feasibility Study: {Product Name}

**Date:** {YYYY-MM-DD}
**Depth:** {Quick | Standard | Deep}
**Overall Score:** {X.X}/5.0
**Recommendation:** {GO | NO-GO | CONDITIONAL GO}
**Confidence:** {Low | Medium | High}

---

## Executive Summary

{One paragraph summarizing: what was analyzed, key finding, recommendation,
estimated effort range, estimated cost range. This should stand alone — a
reader should understand the conclusion from this paragraph alone.}

---

## 1. Product Overview

**Product:** {Name and one-line description}
**Target Users:** {Who uses this and what problem it solves}
**Business Model:** {How it makes money}
**Success Metrics:** {Key targets for success}

---

## 2. Technical Feasibility — {Score}/5 (Confidence: {L/M/H})

**Architecture Complexity:** {Simple | Moderate | Complex | Extreme}

**Core Components:**
| Component | Complexity (1-5) | Build vs. Buy | Notes |
|-----------|-------------------|---------------|-------|
| {name}    | {score}           | {Build/Buy}   | {note}|

**Technology Stack Recommendation:**
- Frontend: {recommendation}
- Backend: {recommendation}
- Database: {recommendation}
- Infrastructure: {recommendation}

**Technical Risks:** {Key technical concerns}

**Assessment:** {One paragraph explaining the score}

---

## 3. Economic Feasibility — {Score}/5 (Confidence: {L/M/H})

### Development Cost Estimate

| Phase / Component  | Effort (person-months) | Cost Range (USD)  |
|--------------------|------------------------|-------------------|
| {phase/component}  | {X-Y}                 | ${min}-${max}     |
| **Total**          | **{X-Y}**             | **${min}-${max}** |

**Estimation Method:** {T-shirt | Function Points | COCOMO II}

### Team Composition

| Role              | Count | Duration  | Monthly Cost |
|-------------------|-------|-----------|--------------|
| {role}            | {n}   | {months}  | ${cost}      |

### Operating Costs (Annual)

| Category          | Year 1       | Year 2       | Year 3       |
|-------------------|--------------|--------------|--------------|
| Infrastructure    | ${amount}    | ${amount}    | ${amount}    |
| SaaS Tooling      | ${amount}    | ${amount}    | ${amount}    |
| Support/Ops       | ${amount}    | ${amount}    | ${amount}    |
| **Total**         | **${total}** | **${total}** | **${total}** |

### Hidden Costs Identified

{List of applicable hidden costs from the checklist with estimated amounts}

### Revenue Projection

| Scenario      | Year 1      | Year 2       | Year 3       |
|---------------|-------------|--------------|--------------|
| Conservative  | ${amount}   | ${amount}    | ${amount}    |
| Base case     | ${amount}   | ${amount}    | ${amount}    |
| Optimistic    | ${amount}   | ${amount}    | ${amount}    |

**ROI (3-year, base case):** {X}%
**Payback Period:** {X} months

**Assessment:** {One paragraph explaining the score}

---

## 4. Market Feasibility — {Score}/5 (Confidence: {L/M/H})

**Market Size:**
- TAM: ${amount}
- SAM: ${amount}
- SOM: ${amount}

**Competitive Landscape:**
| Competitor    | Pricing     | Key Strength       | Key Weakness        |
|---------------|-------------|--------------------|--------------------|
| {name}        | ${pricing}  | {strength}         | {weakness}          |

**Differentiation:** {What makes this product different}
**Moat Assessment:** {None | Shallow | Deep} — {justification}
**Market Timing:** {Too Early | Right Time | Too Late} — {justification}

**Assessment:** {One paragraph explaining the score}

---

## 5. Operational Feasibility — {Score}/5 (Confidence: {L/M/H})

**Team Requirements:**
| Role                  | Needed | Availability | Hiring Difficulty |
|-----------------------|--------|--------------|-------------------|
| {role}                | {n}    | {status}     | {Easy/Med/Hard}   |

**Key Operational Considerations:**
{Bullet list of process, support, and organizational factors}

**Assessment:** {One paragraph explaining the score}

---

## 6. Schedule Feasibility — {Score}/5 (Confidence: {L/M/H})

**Phase Breakdown:**
| Phase          | Duration      | Key Deliverables              |
|----------------|---------------|-------------------------------|
| Discovery      | {X weeks}     | {deliverables}                |
| MVP            | {X months}    | {deliverables}                |
| Beta           | {X months}    | {deliverables}                |
| Launch         | {X weeks}     | {deliverables}                |
| Scale          | {Ongoing}     | {deliverables}                |
| **Total to Launch** | **{X months}** |                          |

**Critical Path:** {What must happen sequentially}
**Schedule Risks:** {Key factors that could cause delays}

**Assessment:** {One paragraph explaining the score}

---

## 7. Automation Feasibility — {Score}/5 (Confidence: {L/M/H})

**Solo Operator Viability:** {Yes at any scale | Yes up to $XM ARR | Risky | No}

**Component Automation Audit:**
| Function                    | Level | Classification        | Notes                      |
|-----------------------------|-------|-----------------------|----------------------------|
| {function}                  | {A-E} | {classification}      | {what makes it A/B/C/D/E}  |

**Self-Validating Loops:**
{For any AI-automated components, describe the validation loop and ground truth sources}

**Human Intervention Points:**
{List remaining points where a human must intervene, frequency, and time per intervention}

**Revenue per Human-Hour:** ${X}/hour at projected Year 2 revenue

**Assessment:** {One paragraph explaining the score}

---

## 8. Risk Assessment

| # | Risk                  | Category   | L | I | Score | Class    | Mitigation                |
|---|-----------------------|------------|---|---|-------|----------|---------------------------|
| 1 | {risk description}    | {category} | {L} | {I} | {S} | {class} | {mitigation strategy}    |

**Red Flags Identified:** {List any red flag patterns that apply, or "None"}

---

## 8. Recommendation

### Verdict: {GO | NO-GO | CONDITIONAL GO}

**Overall Score:** {X.X}/5.0 (Confidence: {L/M/H})

| Dimension    | Score | Weight | Weighted |
|--------------|-------|--------|----------|
| Technical    | {X}/5 | 20%    | {X.XX}   |
| Economic     | {X}/5 | 20%    | {X.XX}   |
| Market       | {X}/5 | 15%    | {X.XX}   |
| Operational  | {X}/5 | 10%    | {X.XX}   |
| Schedule     | {X}/5 | 10%    | {X.XX}   |
| Automation   | {X}/5 | 25%    | {X.XX}   |
| **Total**    |       | 100%   | **{X.XX}** |

{If CONDITIONAL GO: List the conditions that must be met}

### Key Assumptions
1. {Assumption that, if wrong, could change the recommendation}
2. {Assumption}
3. {Assumption}

### Recommended Next Steps
1. {Concrete action item}
2. {Concrete action item}
3. {Concrete action item}
4. {Concrete action item}
5. {Concrete action item}

---

## Appendix

**Estimation Methodology:** {Description of methods used}
**Data Sources:** {List of sources consulted}
**Assumptions Log:** {Full list of assumptions made during analysis}
**Confidence Notes:** {Explanation of low-confidence areas and what would improve them}
