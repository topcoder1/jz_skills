# Risk Assessment Framework

## Risk Taxonomy

### Technical Risks

- Architecture won't scale to target load
- Key technology is immature, poorly supported, or nearing end-of-life
- Integration with external systems fails or is unreliable
- Performance requirements are unachievable with chosen stack
- Data migration is more complex than estimated
- Security vulnerabilities in custom-built components
- Technical debt accumulates faster than expected

### Market Risks

- Insufficient demand — users don't want the product
- Pricing pressure from competitors or free alternatives
- Competitor launches superior product during development
- Market timing is wrong (too early or too late)
- Customer acquisition cost exceeds projections
- Target market is too small to sustain the business
- Regulatory changes disrupt the market

### Operational Risks

- Cannot hire required talent in time or budget
- Key person dependency — single points of failure on the team
- Vendor lock-in to a critical third-party service
- Process gaps in development, deployment, or support
- Team lacks domain expertise
- Communication breakdowns in distributed teams
- Scope creep beyond original feasibility parameters

### Financial Risks

- Development budget overrun (most common: 50-200% over estimate)
- Revenue ramp slower than projected
- Cash flow timing — expenses front-loaded, revenue delayed
- Hidden costs not identified during estimation
- Currency fluctuation (for offshore development)
- Funding dependent on milestones not yet achieved

### Legal / Regulatory Risks

- Data privacy non-compliance (GDPR, CCPA, HIPAA)
- Intellectual property disputes or patent infringement
- Terms of service violations (web scraping, API usage)
- Industry-specific regulations missed
- Licensing issues with open-source dependencies
- Contractual liability exposure

## Risk Scoring Matrix

Score each risk on two dimensions:

### Likelihood Scale

| Score | Level          | Description                    |
| ----- | -------------- | ------------------------------ |
| 1     | Rare           | Very unlikely to occur         |
| 2     | Unlikely       | Could occur but not expected   |
| 3     | Possible       | Reasonable chance of occurring |
| 4     | Likely         | More likely to occur than not  |
| 5     | Almost Certain | Expected to occur              |

### Impact Scale

| Score | Level    | Description                                      |
| ----- | -------- | ------------------------------------------------ |
| 1     | Minimal  | Minor inconvenience, easily absorbed             |
| 2     | Low      | Some rework needed, minor cost/schedule impact   |
| 3     | Medium   | Significant rework, notable cost/schedule impact |
| 4     | High     | Major rework, threatens project viability        |
| 5     | Critical | Project failure, business-threatening            |

### Risk Score = Likelihood x Impact

| Risk Score | Classification | Action Required                            |
| ---------- | -------------- | ------------------------------------------ |
| 20-25      | Critical       | Immediate mitigation plan required         |
| 12-19      | High           | Mitigation plan required before proceeding |
| 6-11       | Medium         | Monitor and have contingency plan          |
| 1-5        | Low            | Accept and monitor                         |

## Risk Response Strategies

| Strategy     | When to Use                                | Example                                     |
| ------------ | ------------------------------------------ | ------------------------------------------- |
| **Avoid**    | Risk is too high, alternative exists       | Choose proven tech over experimental        |
| **Transfer** | Risk can be shifted to a third party       | Use managed database instead of self-hosted |
| **Mitigate** | Reduce likelihood or impact                | Build prototype to validate architecture    |
| **Accept**   | Risk is low or cost of mitigation too high | Acknowledge and set aside contingency       |

## Risk Register Template

| #   | Risk Description | Category | L (1-5) | I (1-5) | Score | Class | Mitigation Strategy | Owner |
| --- | ---------------- | -------- | ------- | ------- | ----- | ----- | ------------------- | ----- |
| 1   |                  |          |         |         |       |       |                     |       |
| 2   |                  |          |         |         |       |       |                     |       |

## Red Flag Patterns

These patterns significantly increase project risk. Flag any that apply:

- [ ] **No clear revenue model**: "We'll figure out monetization later"
- [ ] **Solution looking for a problem**: Technology-driven, not user-driven
- [ ] **Single point of failure**: One person holds all critical knowledge
- [ ] **"We'll figure it out later"**: Deferring critical technical decisions
- [ ] **Scope equals competitor**: Building the same thing, not something better
- [ ] **No unfair advantage**: Nothing prevents competitors from copying
- [ ] **Regulatory blind spot**: Operating in regulated space without legal review
- [ ] **Dependency on uncontrolled third party**: Critical feature requires API/service you don't control
- [ ] **Linear scaling costs**: Each new user adds proportional cost with no efficiency gains
- [ ] **Unvalidated demand**: No evidence users will pay, only anecdotal interest
- [ ] **Team skill gap**: Core capability requires expertise the team doesn't have
- [ ] **Overly optimistic timeline**: No buffer for unknowns, assumes everything goes right

## Contingency Budget Guidelines

Based on project complexity and risk profile:

| Risk Profile   | Contingency Buffer |
| -------------- | ------------------ |
| Low risk       | 10-15% of budget   |
| Medium risk    | 15-25% of budget   |
| High risk      | 25-40% of budget   |
| Very high risk | 40-60% of budget   |

Apply to both cost and schedule estimates.
