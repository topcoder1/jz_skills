# Automation Feasibility Analysis Framework

## Why Automation Matters

Products that run without human intervention have fundamentally different
economics: near-zero marginal cost per customer, no headcount scaling with
growth, and the ability for a solo founder to operate at enterprise scale.

BuiltWith ($14M+ ARR, 1 employee) is the canonical example. The question
isn't just "can we build it?" but "can we build it so it runs itself?"

## Component Automation Audit

For every operational function, classify its automation level:

| Level | Classification        | Description                                       | Example                                     |
| ----- | --------------------- | ------------------------------------------------- | ------------------------------------------- |
| A     | Fully Automatable     | Runs unattended, self-heals on failure            | Scheduled web crawler                       |
| B     | AI-Automatable        | AI handles decisions, human reviews occasionally  | Fingerprint generation with validation loop |
| C     | Partially Automatable | Core is automated, edge cases need human          | Anti-bot detection changes                  |
| D     | Human-Assisted        | Automation handles routine, human handles complex | Customer support escalations                |
| E     | Requires Human        | Cannot be automated with current technology       | Legal negotiations, strategic pivots        |

### Standard Product Functions to Audit

For each, assign a level (A-E) and note what makes it automatable or not:

**Data Pipeline:**

- [ ] Data collection / crawling / scraping
- [ ] Data processing / transformation
- [ ] Data validation / quality checks
- [ ] Data storage and indexing
- [ ] Data freshness / re-processing schedules

**Product Core:**

- [ ] Core algorithm / detection / analysis
- [ ] Pattern/signature/model updates
- [ ] Quality assurance of outputs
- [ ] API serving and rate limiting
- [ ] Search and query processing

**Customer Lifecycle:**

- [ ] Marketing site and SEO
- [ ] User onboarding (signup → first value)
- [ ] Billing and subscription management
- [ ] Usage tracking and metering
- [ ] Customer support (L1 — common questions)
- [ ] Customer support (L2 — technical issues)
- [ ] Customer support (L3 — escalations)
- [ ] Churn prevention and re-engagement

**Infrastructure & Ops:**

- [ ] Deployment and releases
- [ ] Monitoring and alerting
- [ ] Auto-scaling
- [ ] Backup and disaster recovery
- [ ] Security patching
- [ ] SSL certificate renewal
- [ ] Log rotation and cleanup

**Business Operations:**

- [ ] Financial reporting / bookkeeping
- [ ] Tax compliance
- [ ] Legal compliance (privacy policy, ToS updates)
- [ ] Competitor monitoring
- [ ] Pricing adjustments

## Self-Validating Loop Pattern

For components classified as "B" (AI-Automatable), describe the validation
loop that eliminates human review:

```
┌─────────────────────────────────────┐
│  1. AI generates output             │
│     (fingerprint, content, config)  │
├─────────────────────────────────────┤
│  2. Test against ground truth       │
│     (known-good dataset, benchmarks)│
├─────────────────────────────────────┤
│  3. Measure quality metrics         │
│     (accuracy, false positive rate) │
├─────────────────────────────────────┤
│  4. Accept if meets thresholds      │
│     (e.g., TP > 90%, FP < 1%)      │
│     Else: refine and retry (→ step 1)│
├─────────────────────────────────────┤
│  5. Deploy automatically            │
│     Alert human only on anomalies   │
└─────────────────────────────────────┘
```

### Ground Truth Sources (no human needed)

| Source Type                 | Example                                               |
| --------------------------- | ----------------------------------------------------- |
| Vendor customer directories | "Built with Shopify" pages, Stripe customer logos     |
| Package manifests           | package.json, requirements.txt in public GitHub repos |
| Competitor public data      | BuiltWith free single-site lookup as benchmark        |
| Synthetic test sites        | Deploy known stacks on test domains, verify detection |
| Historical data             | Previously validated fingerprints as regression tests |
| Community datasets          | Open-source fingerprint DBs (Wappalyzer, WhatWeb)     |

## Solo Operator Viability Assessment

A product is "solo-operable at scale" when:

| Criteria                     | Threshold                                 |
| ---------------------------- | ----------------------------------------- |
| Daily human time required    | < 1 hour/day at 10K customers             |
| Human intervention frequency | < 1x/week for non-routine issues          |
| Customer support ratio       | < 5 tickets/week requiring human response |
| Deployment                   | Fully automated (CI/CD, zero-downtime)    |
| Monitoring                   | Alert-based, not active watching          |
| Revenue per human-hour       | > $500/hour of human involvement          |

### Revenue per Human-Hour Calculation

```
Annual Revenue / (Annual Human Hours on Operations) = $/hour

Example (BuiltWith model):
  $14M revenue / (1 person × 2000 hrs/year) = $7,000/hour

Example (your MVP target):
  $60K revenue / (520 hrs/year = 10hrs/week) = $115/hour
  At $300K revenue: $577/hour ← approaching viability
```

## Automation Risk Patterns

Watch for these patterns that limit automation:

- **Adversarial environments**: Anti-bot systems change frequently,
  requiring reactive adjustments that are hard to fully automate
- **Regulatory changes**: New privacy laws or compliance requirements
  may need human interpretation before implementation
- **Quality drift**: Automated systems can degrade gradually without
  human oversight. Build automated quality monitoring with alerts.
- **Customer trust**: Some customers need to talk to a human. Consider
  whether your market segment accepts fully self-serve.
- **Edge case accumulation**: Automated systems handle 95% of cases well.
  The remaining 5% pile up and eventually need attention.

## Automation Score Interpretation

| Score | Meaning                                  | Solo Operator?                       |
| ----- | ---------------------------------------- | ------------------------------------ |
| 5     | Fully automated end-to-end               | Yes — at any scale                   |
| 4     | 1-2 human touchpoints, rest automated    | Yes — up to ~$5M ARR                 |
| 3     | Daily human tasks, but core is automated | Yes — up to ~$500K ARR               |
| 2     | Significant manual operations            | Risky — needs at least 2-3 people    |
| 1     | Human-intensive at every step            | No — requires proportional headcount |
