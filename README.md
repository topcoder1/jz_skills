# Feasibility Study — Claude Code Skill

A Claude Code skill that performs comprehensive product feasibility studies with effort and cost estimation.

Analyzes any product idea or existing product across five dimensions using the **TELOS framework**:
- **Technical** — Architecture complexity, tech stack, scalability
- **Economic** — Development cost, operating cost, ROI, hidden costs
- **Legal/Compliance** — Regulatory, IP, data privacy
- **Operational** — Team requirements, processes, support model
- **Schedule** — Timeline, milestones, critical path

Produces a structured feasibility report with a **GO / NO-GO / CONDITIONAL GO** recommendation.

## Installation

### Option 1: Claude Code Plugin (recommended)

```bash
# From local path
claude plugin add /path/to/jz_skills

# From GitHub (after pushing)
claude plugin add github:your-username/jz_skills
```

### Option 2: Symlink to Personal Skills

```bash
ln -s /path/to/jz_skills/skills/feasibility-study ~/.claude/skills/feasibility-study
```

### Option 3: Project-Local

Copy or symlink into any project's `.claude/skills/` directory:

```bash
ln -s /path/to/jz_skills/skills/feasibility-study /your-project/.claude/skills/feasibility-study
```

## Usage

```
/feasibility-study BuiltWith.com
/feasibility-study "A mobile app for tracking food trucks" --depth quick
/feasibility-study "Enterprise compliance SaaS" --depth deep
```

### Depth Modes

| Mode       | Scope                                     | Estimation Method  | Speed    |
|------------|-------------------------------------------|--------------------|----------|
| `quick`    | Technical + Economic only, skip research  | T-shirt sizing     | ~5 min   |
| `standard` | Full TELOS analysis with research         | Function points    | ~15 min  |
| `deep`     | Full TELOS + detailed TCO + market sizing | COCOMO II          | ~30 min  |

### Input

You can provide:
- A **URL** of an existing product to analyze (e.g., `BuiltWith.com`)
- A **product description** in quotes (e.g., `"AI-powered code review tool"`)
- A **combination** of both

The skill will ask 3-5 clarifying questions before starting analysis.

### Output

A markdown feasibility report saved to your working directory:

```
feasibility-report-{product-name}-{YYYY-MM-DD}.md
```

The report includes:
- Executive summary with GO/NO-GO recommendation
- Scores (1-5) for each TELOS dimension with evidence
- Development cost estimate with team composition
- Operating cost projections (Years 1-3)
- Hidden costs checklist
- Competitive landscape analysis
- Risk assessment matrix with mitigations
- Phased timeline with milestones
- Recommended next steps

## Estimation Script

The skill includes a Python calculation script (`scripts/estimate.py`) that handles deterministic computations. You can also use it standalone:

```bash
# COCOMO II estimation
echo '{"operation": "cocomo", "kloc": 50, "mode": "semi-detached"}' | python3 scripts/estimate.py

# T-shirt sizing
echo '{"operation": "tshirt", "complexity": "complex", "team_size": "small"}' | python3 scripts/estimate.py

# ROI calculation
echo '{"operation": "roi", "development_cost": 500000, "annual_operating_cost": 60000, "annual_revenue": 200000}' | python3 scripts/estimate.py
```

## License

MIT
