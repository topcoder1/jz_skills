# Cost Estimation Frameworks

## The Three Estimation Dimensions

Always estimate and present these three separately — they tell very different
stories depending on team composition:

| Dimension        | What It Measures                             | Example                    |
|------------------|----------------------------------------------|----------------------------|
| **Effort**       | Total person-months of work needed           | 16 person-months           |
| **Calendar time**| Wall-clock months to completion              | 16 months (solo) or 9 months (2 devs) |
| **Cash cost**    | Actual money spent (sweat equity = $0)       | $5K (solo+AI) or $136K (with contractor) |

### Why This Matters

A solo founder with Claude Code might have:
- High effort (16 person-months)
- Long calendar time (16 months — one person doing everything)
- Near-zero cash cost ($5K for AI tools)

The same project with a contractor:
- Similar effort (23 person-months — less AI leverage)
- Shorter calendar time (13 months — two people in parallel)
- High cash cost ($136K — contractor salary)

**Always ask during Discovery:** Is the user optimizing for speed (hire help)
or cash (sweat equity + AI)? This changes the entire cost picture.

### Calendar Time Calculation

```
effective_team = 1 + (additional_devs × 0.75)    # Brooks's law: 75% efficiency per added dev
calendar_months = effort_person_months / effective_team
```

### Cash Cost Calculation

```
cash_cost = (contractor_count × contractor_rate × calendar_months)
          + (founder_salary × calendar_months)    # $0 if sweat equity
          + (ai_tools_monthly × calendar_months)  # ~$350/mo for Claude + Copilot
```

Note: cash_cost covers development labor + tools only. Infrastructure, SaaS,
and hidden costs are separate line items.

## T-shirt Sizing (Quick Mode)

Fast estimation for initial viability checks. Map complexity and team size
to approximate duration and cost.

### Duration Estimates

| Complexity | Solo Dev    | Small Team (2-4) | Team (5-10)  | Large Team (10+) |
|------------|-------------|-------------------|--------------|-------------------|
| Simple     | 4-8 weeks   | 2-4 weeks         | 1-2 weeks    | 1 week            |
| Moderate   | 3-6 months  | 2-3 months        | 1-2 months   | 3-6 weeks         |
| Complex    | 9-18 months | 6-9 months        | 4-6 months   | 3-4 months        |
| Extreme    | 2-3+ years  | 12-18 months      | 9-12 months  | 6-9 months        |

### Cost Ranges (USD, development only)

| Complexity | Freelance/Solo   | Small Agency     | Mid Agency       | Enterprise       |
|------------|------------------|------------------|------------------|------------------|
| Simple     | $10K-30K         | $25K-75K         | $50K-150K        | $100K-300K       |
| Moderate   | $30K-100K        | $75K-250K        | $150K-500K       | $300K-1M         |
| Complex    | $100K-500K       | $250K-750K       | $500K-2M         | $1M-5M           |
| Extreme    | $500K-2M         | $750K-3M         | $2M-10M          | $5M-20M+         |

## Function Point Analysis (Standard Mode)

### Step 1: Identify Function Types

| Type                         | Description                               | Weight  |
|------------------------------|-------------------------------------------|---------|
| External Inputs (EI)         | Data entry screens, API write endpoints   | 4 FP    |
| External Outputs (EO)        | Reports, dashboards, API read endpoints   | 5 FP    |
| External Inquiries (EQ)      | Search, lookup, status check              | 4 FP    |
| Internal Logical Files (ILF) | Database tables, data stores              | 10 FP   |
| External Interface Files (EIF)| External data sources consumed            | 7 FP    |

### Step 2: Adjust for Complexity

Multiply each count by complexity factor:

| Complexity | EI  | EO  | EQ  | ILF | EIF |
|------------|-----|-----|-----|-----|-----|
| Low        | 3   | 4   | 3   | 7   | 5   |
| Average    | 4   | 5   | 4   | 10  | 7   |
| High       | 6   | 7   | 6   | 15  | 10  |

### Step 3: Calculate Adjusted Function Points

Apply Value Adjustment Factor (VAF) based on 14 general system characteristics,
each rated 0-5:

1. Data communications
2. Distributed data processing
3. Performance objectives
4. Heavily used configuration
5. Transaction rate
6. Online data entry
7. End-user efficiency
8. Online update
9. Complex processing
10. Reusability
11. Installation ease
12. Operational ease
13. Multiple sites
14. Facilitate change

VAF = 0.65 + (0.01 × sum of ratings)
Adjusted FP = Unadjusted FP × VAF

### Step 4: Convert to Effort

Industry benchmarks (hours per function point):
- Simple applications: 8-12 hours/FP
- Average applications: 12-16 hours/FP
- Complex applications: 16-24 hours/FP

## COCOMO II (Deep Mode)

### Basic Formula

```
Effort (person-months) = a × (KLOC)^b × EAF
Schedule (months) = c × (Effort)^d
```

### Mode Parameters

| Mode           | a    | b    | c    | d    | Project Type                        |
|----------------|------|------|------|------|-------------------------------------|
| Organic        | 2.4  | 1.05 | 2.5  | 0.38 | Small team, familiar domain         |
| Semi-detached  | 3.0  | 1.12 | 2.5  | 0.35 | Medium team, mixed experience       |
| Embedded       | 3.6  | 1.20 | 2.5  | 0.32 | Large team, complex constraints     |

### Effort Adjustment Factor (EAF)

Multiply these cost drivers (0.75-1.65 each):

| Driver                  | Very Low | Low  | Nominal | High | Very High |
|-------------------------|----------|------|---------|------|-----------|
| Required reliability    | 0.75     | 0.88 | 1.00    | 1.15 | 1.40      |
| Database size           | —        | 0.94 | 1.00    | 1.08 | 1.16      |
| Product complexity      | 0.70     | 0.85 | 1.00    | 1.15 | 1.30      |
| Analyst capability      | 1.46     | 1.19 | 1.00    | 0.86 | 0.71      |
| Programmer capability   | 1.42     | 1.17 | 1.00    | 0.86 | 0.70      |
| Platform experience     | 1.19     | 1.09 | 1.00    | 0.91 | 0.85      |
| Language experience     | 1.14     | 1.07 | 1.00    | 0.95 | —         |
| Tool use                | 1.24     | 1.10 | 1.00    | 0.91 | 0.82      |
| Schedule constraint     | 1.23     | 1.08 | 1.00    | 1.04 | 1.10      |

EAF = product of all applicable driver values

### KLOC Estimation by Technology

| Technology/Framework    | Lines per Function Point | Notes                    |
|-------------------------|--------------------------|--------------------------|
| Python / Ruby           | 15-20                    | High-level scripting     |
| JavaScript / TypeScript | 20-30                    | Web applications         |
| Java / C#               | 30-50                    | Enterprise applications  |
| Go / Rust               | 25-40                    | Systems programming      |
| SQL                     | 10-15                    | Database logic           |
| Infrastructure as Code  | 15-25                    | Terraform, CloudFormation|

## Rate Cards (2025-2026 Market Rates, USD)

### Hourly Rates by Role and Region

| Role                    | US Senior  | US Mid     | US Junior  | Offshore   |
|-------------------------|------------|------------|------------|------------|
| Frontend Developer      | $150-200   | $100-150   | $60-100    | $30-60     |
| Backend Developer       | $150-220   | $100-160   | $60-100    | $30-65     |
| Full-Stack Developer    | $160-230   | $110-170   | $65-110    | $35-70     |
| DevOps / SRE            | $170-250   | $120-180   | $70-120    | $40-75     |
| Data Engineer           | $160-240   | $110-170   | $65-110    | $35-70     |
| ML / AI Engineer        | $180-280   | $130-200   | $80-130    | $45-85     |
| UI/UX Designer          | $120-180   | $80-130    | $50-80     | $25-50     |
| Product Manager         | $140-200   | $100-150   | $60-100    | $30-55     |
| QA Engineer             | $120-170   | $80-130    | $50-80     | $25-45     |
| Technical Lead          | $180-280   | $130-200   | —          | $50-90     |

### Engagement Model Multipliers

| Model           | Multiplier | Best For                              |
|-----------------|------------|---------------------------------------|
| Freelance       | 1.0x       | Short-term, specialized tasks         |
| Small agency    | 1.3-1.5x   | Full projects, managed delivery       |
| Mid agency      | 1.5-2.0x   | Complex projects, enterprise clients  |
| Enterprise firm | 2.0-3.0x   | Large-scale, compliance-heavy         |
| In-house team   | 1.4-1.8x   | Ongoing product development (benefits + overhead) |

## Operating Cost Templates

### Infrastructure Cost by Scale Tier (Monthly)

| Component           | Startup (<1K) | Growth (1K-10K) | Scale (10K-100K) | Enterprise (100K+) |
|---------------------|---------------|-----------------|-------------------|---------------------|
| Compute (servers)   | $50-200       | $200-1,000      | $1,000-5,000      | $5,000-50,000       |
| Database            | $0-50         | $50-300         | $300-2,000        | $2,000-20,000       |
| Object storage      | $0-10         | $10-50          | $50-500           | $500-5,000          |
| CDN / bandwidth     | $0-20         | $20-100         | $100-1,000        | $1,000-10,000       |
| Search (Elastic/etc)| $0            | $50-200         | $200-1,000        | $1,000-10,000       |
| Cache (Redis)       | $0-15         | $15-100         | $100-500          | $500-5,000          |
| Email delivery      | $0-20         | $20-100         | $100-500          | $500-5,000          |
| Monitoring/logging  | $0-30         | $30-150         | $150-500          | $500-3,000          |
| **Monthly total**   | **$50-350**   | **$400-2,000**  | **$2,000-11,000** | **$11,000-108,000** |

### SaaS Tooling Costs (Monthly)

| Tool Category        | Free Tier | Startup     | Growth       | Enterprise   |
|----------------------|-----------|-------------|--------------|--------------|
| Auth (Auth0/Clerk)   | $0        | $25-100     | $100-500     | $500-5,000   |
| Error tracking       | $0        | $25-50      | $50-200      | $200-1,000   |
| Analytics            | $0        | $0-50       | $50-500      | $500-5,000   |
| Customer support     | $0        | $50-100     | $100-500     | $500-3,000   |
| CI/CD                | $0        | $0-50       | $50-200      | $200-1,000   |
| Feature flags        | $0        | $0-25       | $25-200      | $200-1,000   |

## Hidden Costs Checklist (MANDATORY)

Walk through every item. Mark each as applicable or N/A with estimated cost:

- [ ] Security audit / penetration testing ($5K-50K)
- [ ] Compliance certification — SOC 2, HIPAA, PCI-DSS ($10K-100K+)
- [ ] Legal review — terms of service, privacy policy ($2K-15K)
- [ ] Accessibility audit and remediation (WCAG 2.1) ($5K-25K)
- [ ] Documentation and technical writing ($5K-20K)
- [ ] Performance testing and load testing ($3K-15K)
- [ ] Disaster recovery and backup setup ($2K-10K)
- [ ] CI/CD pipeline setup and maintenance ($2K-10K)
- [ ] Domain, SSL, DNS setup ($100-500/yr)
- [ ] Design system and brand assets ($5K-30K)
- [ ] Third-party API costs at production scale (varies)
- [ ] Data migration from existing systems ($5K-50K)
- [ ] Training and onboarding materials ($2K-10K)
- [ ] Customer support tooling setup ($1K-5K)
- [ ] Analytics and tracking implementation ($2K-10K)
- [ ] Monitoring and alerting configuration ($1K-5K)
- [ ] Content creation (initial content, seed data) ($2K-20K)
- [ ] Insurance — cyber liability, E&O ($1K-10K/yr)

## Build vs. Buy Decision Matrix

For each major component, evaluate:

| Factor               | Build                | Buy/Use SaaS         | Weight |
|----------------------|----------------------|-----------------------|--------|
| Core differentiator? | Build if yes         | Buy if no             | High   |
| Time to market       | Slower               | Faster                | High   |
| Long-term cost       | Lower at scale       | Higher at scale       | Medium |
| Control & customization | Full control      | Limited               | Medium |
| Maintenance burden   | On your team         | On vendor             | Medium |
| Risk of vendor lock-in | None              | Moderate to high      | Low    |

**Rule of thumb**: Build what differentiates you. Buy everything else.

## AI Productivity Adjustment

Modern development with AI coding assistants significantly changes effort
estimates. Apply the appropriate multiplier based on the team's AI tooling:

| AI Level   | Multiplier | Tools / Approach                                    |
|------------|------------|-----------------------------------------------------|
| None       | 0% saved   | Traditional development, no AI assistance           |
| Low        | 20% saved  | Basic code completion (GitHub Copilot autocomplete) |
| Moderate   | 35% saved  | AI pair programming (Copilot Chat, Cursor Tab)      |
| High       | 50% saved  | AI agent coding (Claude Code, Devin, Windsurf)      |
| Very High  | 65% saved  | AI-first development (AI writes most code, human reviews) |

### When to Apply

- **Always ask** the user about their planned AI tooling during Discovery
- Apply to **development effort only** — infrastructure, SaaS, and support costs are unaffected
- AI multiplier reduces **person-hours**, which reduces cost but may not reduce calendar time proportionally (some tasks are sequential regardless of speed)
- The multiplier applies best to **well-understood patterns** (CRUD, APIs, dashboards). Reduce the multiplier for novel/research-heavy work.

### Adjustment Rules

- For components rated complexity 1-2 (off-the-shelf, light custom): use full AI multiplier
- For components rated complexity 3 (moderate custom): use 75% of the AI multiplier
- For components rated complexity 4-5 (significant/research): use 50% of the AI multiplier
- For infrastructure and DevOps work: use 50% of the AI multiplier

### Script Usage

All estimation operations accept `ai_level` or `ai_multiplier`:
```bash
echo '{"operation": "cocomo", "kloc": 50, "mode": "semi-detached", "ai_level": "high"}' | python3 estimate.py
echo '{"operation": "tshirt", "complexity": "complex", "team_size": "small", "ai_multiplier": 0.4}' | python3 estimate.py
```

The output includes an `ai_adjustment` section showing traditional vs. adjusted effort.

## ROI Calculation

```
Development Cost = effort_hours × blended_rate
Annual Operating Cost = infrastructure + SaaS + support + maintenance
Annual Revenue = users × conversion_rate × ARPU

Year 1 ROI = (Revenue_Y1 - Operating_Y1 - Development) / Development × 100
Year 3 ROI = (Cumulative_Revenue - Cumulative_Operating - Development) / Development × 100

Payback Period = Development / (Monthly_Revenue - Monthly_Operating)
```

Conservative: Use 50% of projected revenue
Base case: Use 75% of projected revenue
Optimistic: Use 100% of projected revenue
