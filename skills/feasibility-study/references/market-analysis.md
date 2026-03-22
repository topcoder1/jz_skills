# Market Analysis Framework

## Market Sizing (TAM / SAM / SOM)

### Definitions

- **TAM** (Total Addressable Market): Total revenue opportunity if 100% market share
- **SAM** (Serviceable Addressable Market): Segment of TAM you can reach with your product
- **SOM** (Serviceable Obtainable Market): Realistic share you can capture in 1-3 years

### Top-Down Methodology

Start with industry-level data and narrow down:

1. Find total industry revenue (analyst reports, trade associations)
2. Filter to your segment (geography, customer type, use case)
3. Apply reachability filter (distribution, pricing, product fit)

```
TAM = Industry Revenue × Relevant Segment %
SAM = TAM × Reachability %
SOM = SAM × Realistic Capture % (typically 1-5% for startups)
```

### Bottom-Up Methodology

Start with unit economics and scale up:

1. Identify number of potential customers
2. Estimate conversion rate
3. Multiply by average revenue per user (ARPU)

```
SOM = Reachable Customers × Expected Conversion % × ARPU × 12
SAM = Total Addressable Customers × Expected Conversion % × ARPU × 12
TAM = All Possible Customers × ARPU × 12
```

**Use both methods** and compare. If they're wildly different, investigate.

## Competitive Analysis

### Direct Competitors

Products that solve the same problem for the same user:
- Name, URL, founding year
- Pricing model and tiers
- Key features (top 5-10)
- Estimated user base / revenue (if available)
- Strengths and weaknesses
- Recent funding or acquisitions

### Indirect Competitors

Products that solve adjacent problems or serve the same user differently:
- What alternatives do users currently use?
- Manual processes or workarounds
- Tangentially related tools

### Feature Comparison Matrix

| Feature              | Our Product | Competitor A | Competitor B | Competitor C |
|----------------------|-------------|--------------|--------------|--------------|
| Core feature 1       | ?           | Y/N          | Y/N          | Y/N          |
| Core feature 2       | ?           | Y/N          | Y/N          | Y/N          |
| Pricing (starting)   | ?           | $XX/mo       | $XX/mo       | $XX/mo       |
| Free tier            | ?           | Y/N          | Y/N          | Y/N          |
| API access           | ?           | Y/N          | Y/N          | Y/N          |
| Mobile support       | ?           | Y/N          | Y/N          | Y/N          |

### Pricing Comparison

| Tier       | Our Product | Competitor A | Competitor B | Competitor C |
|------------|-------------|--------------|--------------|--------------|
| Free       |             |              |              |              |
| Starter    |             |              |              |              |
| Pro        |             |              |              |              |
| Enterprise |             |              |              |              |

## Differentiation Assessment

### Sustainable Advantage Checklist

- [ ] **Network effects**: Product gets better as more people use it
- [ ] **Data advantage**: Proprietary dataset that's hard to replicate
- [ ] **Brand/trust**: Established reputation in the space
- [ ] **Switching costs**: High cost for users to move to a competitor
- [ ] **Technical moat**: Patent, proprietary algorithm, or unique capability
- [ ] **Distribution advantage**: Existing channel, partnerships, or audience
- [ ] **Regulatory barrier**: License, certification, or compliance advantage
- [ ] **Cost structure**: Fundamentally lower cost to serve

### Moat Classification

| Level   | Description                                          | Duration    |
|---------|------------------------------------------------------|-------------|
| None    | Features easily replicated, no switching costs       | 0-6 months  |
| Shallow | Some differentiation, but competitors can catch up   | 6-18 months |
| Deep    | Significant structural advantage, hard to replicate  | 18+ months  |

## Business Model Archetypes

| Model         | Revenue Source          | Key Metric        | Typical Margin |
|---------------|-------------------------|--------------------|----------------|
| SaaS          | Monthly/annual subs     | MRR, churn rate    | 70-85%         |
| Marketplace   | Transaction fees        | GMV, take rate     | 10-30%         |
| Usage-based   | Per-unit consumption    | Usage volume       | 50-80%         |
| Freemium      | Upgrade from free tier  | Conversion rate    | 70-85%         |
| Enterprise    | Annual contracts        | ACV, NRR           | 75-90%         |
| Data/API      | API calls or data access| API volume         | 60-80%         |
| Advertising   | Ad impressions/clicks   | DAU, CPM           | 40-60%         |

## Unit Economics Template

| Metric                              | Value     | Benchmark    |
|--------------------------------------|-----------|--------------|
| Customer Acquisition Cost (CAC)      | $         | Varies       |
| Lifetime Value (LTV)                 | $         | > 3x CAC     |
| LTV:CAC Ratio                        |           | > 3:1        |
| Monthly churn rate                   | %         | < 5% (SMB), < 1% (Enterprise) |
| Payback period                       | months    | < 12 months  |
| Average Revenue Per User (ARPU)      | $/month   |              |
| Gross margin                         | %         | > 70% (SaaS) |
| Net Revenue Retention (NRR)          | %         | > 100%       |

## Market Timing Assessment

| Signal                            | Too Early       | Right Time        | Too Late          |
|-----------------------------------|-----------------|-------------------|-------------------|
| User awareness of the problem     | Low             | Growing           | Saturated         |
| Existing solutions                | None/primitive  | Some, with gaps   | Many, mature      |
| Enabling technology               | Not ready       | Just ready        | Commoditized      |
| Regulatory environment            | Unclear         | Favorable         | Restrictive       |
| Recent funding in the space       | None            | Growing           | Declining         |
| Customer willingness to pay       | Skeptical       | Willing           | Demanding/cheap   |
