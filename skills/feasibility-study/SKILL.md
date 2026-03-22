---
name: feasibility-study
description: >
  Comprehensive product feasibility study with effort and cost estimation.
  Analyzes technical, economic, market, operational, and schedule feasibility
  using the TELOS framework. Produces a structured report with go/no-go
  recommendation and confidence levels.
  Use when asked to "feasibility study", "estimate cost to build",
  "is this worth building", "effort estimate", "cost-benefit analysis",
  "should we build this", or "how much would it cost to build".
  Proactively suggest when a user describes a product idea and asks whether
  it is viable, how long it would take, or how much it would cost.
user-invocable: true
argument-hint: <product-or-url> [--depth quick|standard|deep]
---

# Feasibility Study

Perform a comprehensive product feasibility study. Analyze the product across
five dimensions (TELOS), estimate effort and cost, assess risks, and produce
a structured report with a go/no-go recommendation.

## Depth Modes

Parse `$ARGUMENTS` for `--depth` flag. Default to `standard` if not specified.

| Mode     | Scope                                    | Estimation Method     |
|----------|------------------------------------------|-----------------------|
| quick    | Technical + Economic only, skip research | T-shirt sizing        |
| standard | Full TELOS analysis with research        | Function points       |
| deep     | Full TELOS + detailed TCO + market sizing| COCOMO II + full TCO  |

## Phase 0: Parse Input and Configure

1. Parse `$ARGUMENTS` to extract:
   - Product name or URL (first positional argument)
   - Depth mode (`--depth quick|standard|deep`, default: `standard`)
2. If a URL is provided, fetch it with WebFetch to understand the product
3. If a product description is provided, confirm your understanding
4. Print: `Starting feasibility study: {product} | Depth: {mode}`

## Phase 1: Discovery

Ask the user 3-5 targeted questions to understand the opportunity. Use
AskUserQuestion for each. **Smart-skip**: if the URL/description already
answers a question, skip it and state what you inferred.

**Required context (must have all before proceeding):**
1. **Product**: What is the product? What does it do? (pre-fill from URL analysis)
2. **Users**: Who is the target user? What problem does it solve for them?
3. **Business model**: How will it make money? (SaaS, marketplace, one-time, etc.)
4. **Constraints**: Budget range, timeline expectations, team size/skills available?
5. **Success metrics**: What does success look like? Scale targets?

After gathering answers, print a brief summary:
```
## Understanding
- Product: ...
- Target users: ...
- Business model: ...
- Constraints: ...
- Success metrics: ...
```

## Gate 1: Sufficient Context

Verify you have minimum viable context to proceed. Checklist:
- [ ] Product is clearly defined
- [ ] Target user is identified
- [ ] Business model is understood (or explicitly "to be determined")
- [ ] At least one constraint is known

If any critical gap exists, ask ONE targeted follow-up question. Do not
proceed until the checklist passes.

## Phase 2: Research

> **Skip this phase for `--depth quick`**

Use WebSearch to research:
1. **Competitive landscape**: Find 3-5 direct competitors or similar products
2. **Market signals**: Market size indicators, growth trends, recent funding
3. **Technical precedents**: Open source projects, published architectures, known challenges

For each competitor found, note: name, URL, pricing, key differentiators.

If WebSearch is unavailable, note the limitation and proceed with the
information provided by the user. Do NOT block on research availability.

Print a brief research summary before proceeding.

## Phase 3: TELOS Analysis

Analyze each dimension. Read the corresponding reference file on demand.
Score each dimension 1-5 and provide evidence for the score.

### 3a. Technical Feasibility

Read `references/technical-analysis.md` for the framework.

Analyze:
- **Architecture complexity**: Classify as Simple / Moderate / Complex / Extreme
- **Core components**: List major technical components needed
- **Technology stack**: Recommend stack, flag any unproven technologies
- **Integration complexity**: External APIs, data sources, third-party services
- **Scalability path**: What changes at 10x, 100x scale
- **Technical unknowns**: What needs prototyping or proof-of-concept

Output: Technical Feasibility Score (1-5) with one-paragraph rationale.

### 3b. Economic Feasibility

Read `references/cost-estimation.md` for frameworks and rate cards.

**For quick mode**: Use T-shirt sizing only.
**For standard mode**: Use function point estimation.
**For deep mode**: Run `scripts/estimate.py` with COCOMO parameters.

Estimate:
- **Development cost**: Broken down by component/phase
- **Team composition**: Roles needed, headcount, duration
- **Infrastructure cost**: Monthly/annual hosting, third-party services
- **Operating cost**: Year 1, Year 2, Year 3 projections
- **Hidden costs**: Walk through the hidden costs checklist (mandatory)
- **Revenue projection**: Based on business model and market size
- **ROI analysis**: Payback period, 3-year ROI

All estimation script operations support AI productivity adjustment. Always
ask the user about their AI tooling and apply the appropriate multiplier:

```bash
# With AI assistance level (named)
echo '{"operation": "cocomo", "kloc": <kloc>, "mode": "semi-detached", "ai_level": "high"}' | python3 ${CLAUDE_SKILL_DIR}/scripts/estimate.py

# With custom AI multiplier (0.0-1.0)
echo '{"operation": "function_points", "unadjusted_fp": 320, "complexity": "complex", "ai_multiplier": 0.4}' | python3 ${CLAUDE_SKILL_DIR}/scripts/estimate.py
```

AI levels: `none` (0%), `low` (20%), `moderate` (35%), `high` (50%), `very_high` (65%)

Output: Economic Feasibility Score (1-5) with cost summary table.

### 3c. Market Feasibility

> **For quick mode**: Brief competitive check only, no deep market sizing.

Read `references/market-analysis.md` for the framework.

Analyze:
- **Market size**: TAM / SAM / SOM estimates
- **Competitive landscape**: Position vs. competitors found in Phase 2
- **Differentiation**: What makes this different? Is it defensible?
- **Moat assessment**: None / Shallow / Deep — with justification
- **Timing**: Too early / Right time / Too late

Output: Market Feasibility Score (1-5) with positioning summary.

### 3d. Operational Feasibility

Analyze:
- **Team requirements**: Roles, skills, hiring difficulty
- **Process requirements**: Development methodology, release cadence
- **Support model**: Customer support needs, SLA expectations
- **Organizational readiness**: Does the team have the skills? What gaps exist?

Output: Operational Feasibility Score (1-5) with team summary.

### 3e. Schedule Feasibility

Analyze:
- **Phase breakdown**: Discovery → MVP → Beta → Launch → Scale
- **Milestone timeline**: Calendar estimates for each phase
- **Critical path**: What must happen sequentially vs. in parallel
- **Dependencies**: External dependencies, blockers, long-lead items
- **Schedule risks**: What could cause delays

Output: Schedule Feasibility Score (1-5) with timeline table.

## Gate 2: Analysis Complete

Verify all dimensions are scored:
- [ ] Technical score assigned (1-5) with evidence
- [ ] Economic score assigned (1-5) with cost estimates
- [ ] Market score assigned (1-5) — skip detailed for quick mode
- [ ] Operational score assigned (1-5)
- [ ] Schedule score assigned (1-5) with timeline
- [ ] Confidence level noted for each score (Low / Medium / High)

Do not proceed until all scores are assigned.

## Phase 4: Risk Assessment

> **Skip this phase for `--depth quick`**

Read `references/risk-assessment.md` for the framework.

1. Identify the top 5-10 risks across all TELOS dimensions
2. Score each risk: Likelihood (1-5) x Impact (1-5) = Risk Score
3. Classify: Critical (20-25) / High (12-19) / Medium (6-11) / Low (1-5)
4. For every Critical and High risk, propose a specific mitigation strategy
5. Check against the Red Flags checklist

Output: Risk matrix table sorted by risk score (highest first).

## Phase 5: Synthesis and Recommendation

1. Calculate weighted overall score:
   - Technical: 25% weight
   - Economic: 25% weight
   - Market: 20% weight
   - Operational: 15% weight
   - Schedule: 15% weight

2. Map to recommendation:
   - Score >= 3.5: **GO** — proceed with development
   - Score 2.5-3.49: **CONDITIONAL GO** — proceed if conditions are met
   - Score < 2.5: **NO-GO** — do not proceed as planned

3. State:
   - Overall score and recommendation
   - Confidence level (Low / Medium / High)
   - Top 3 key assumptions that could change the recommendation
   - 3-5 concrete recommended next steps

## Phase 6: Report Generation

Read `references/report-template.md` for the output format.

1. Generate the complete feasibility report
2. Save to: `feasibility-report-{product-name}-{YYYY-MM-DD}.md` in the current
   working directory
3. Print the Executive Summary section to the user inline
4. Tell the user where the report was saved
5. Ask: "Report generated. Would you like to adjust any section, explore a
   specific dimension deeper, or change the depth level?"

## Important Rules

1. **Evidence required**: Every score needs concrete evidence. No "probably" or
   "likely" without data. If confidence is low, say so explicitly.
2. **Hidden costs are mandatory**: Never skip the hidden costs checklist in
   economic analysis. These are the costs that blow up budgets.
3. **Honest confidence levels**: If you lack data for a dimension, score
   confidence as Low and note what additional research would help.
4. **No false precision**: Use ranges, not exact numbers. "$150K-250K" is
   better than "$187,500" when the estimate is rough.
5. **The report is the deliverable**: Always produce the markdown report file.
   The inline summary is a preview, not a substitute.
6. **Graceful degradation**: If WebSearch is unavailable, proceed with provided
   info and note the limitation. Never block on tool availability.
7. **Respect depth mode**: Quick mode should feel fast. Don't over-analyze.
   Deep mode should feel thorough. Don't cut corners.
