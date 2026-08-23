# Funding Readiness Registry

**Date:** 2026-08-23
**Source:** Derived from funding-readiness.json schema + venture registry data
**Status:** Template initialized — needs per-venture assessment

## Purpose

Answer the question: **Which of the 788 ventures are fundable today, and what's missing before each can apply for $25K, $100K, $500K, or $1M+?**

Every venture gets a funding readiness assessment across 12 dimensions (0-100 each), producing an overall score and a funding status.

## Scoring Dimensions

| Dimension | Score 0-100 | What it measures |
|-----------|-------------|------------------|
| legal | 0-100 | Business identity: legal name, EIN, formation docs, licenses, registrations, ownership structure, beneficial ownership, NAICS/SIC classification |
| banking | 0-100 | Banking & financial infrastructure: business bank account, merchant account, payment processor, accounting system, bookkeeping |
| accounting | 0-100 | Financial records: bank statements, credit-card history, AR/AP, cash-flow records, balance sheet, P&L, cash-flow statement |
| credit | 0-100 | Credit profiles: D&B, Experian Business, Equifax Business, trade references, vendor accounts, Net-30, business credit cards, debt-to-income, existing debt schedule |
| revenue | 0-100 | Revenue data: current revenue, MRR, ARR, revenue history, concentration, customer count, ACV, gross margin, EBITDA, growth, AR aging, signed contracts, purchase orders |
| documentation | 0-100 | Documentation: loan/grant/investor applications, funding memo, cap table, ownership breakdown, debt schedule, personal financial statement, tax returns, financial projections, supporting contracts |
| business_plan | 0-100 | Business plan: executive summary, problem, solution, target market, competitive analysis, business model, pricing, GTM, ops plan, management team, projections, funding request, use of funds, repayment/exit strategy |
| collateral | 0-100 | Collateral & risk: equipment, vehicles, real estate, inventory, AR, IP, securities, personal guarantees, insurance, business continuity plan, risk assessment |
| investor_readiness | 0-100 | Investor readiness: pitch deck, investment thesis, TAM/SAM/SOM, traction, product, competitive moat, CAC, LTV, retention, growth metrics, cap table, valuation, data room |
| grant_readiness | 0-100 | Grant readiness: eligibility (geographic, industry, entity), project description, community/economic impact, budget, timeline, matching funds, financial documentation, organizational capacity, reporting plan, certifications |
| sba_bank_readiness | 0-100 | SBA/bank readiness: business registration, EIN, good standing, bank account, financial statements, tax returns, debt schedule, business plan, personal financial statement, credit history, collateral info, loan purpose, cash-flow projections, repayment ability |
| alternative_funding | 0-100 | Alternative funding: revenue-based financing, equipment financing, PO financing, invoice factoring, asset-based lending, business credit cards, vendor financing, crowdfunding readiness |

## Overall Score & Status

```yaml
overall: <average of 12 dimensions, 0-100>
funding_status: <one of:>
  - NOT_FUNDABLE              (overall < 20)
  - FUNDING_NOT_STARTED       (20-40, minimal infrastructure)
  - FUNDING_IN_PROGRESS       (40-60, some pieces in place)
  - FUNDING_READY_WITH_GAPS   (60-80, fundable at some levels with gaps)
  - FUNDING_READY             (80-95, fundable across most sources)
  - EXISTS_FUNDING            (95-100, already has funding or fully ready)
```

## Fundable At Levels

```yaml
fundable_at:
  micro:    <true/false>   # < $25K (grants, microloans, credit cards, RBF)
  small:    <true/false>   # $25K-$100K (SBA microloans, friends/family, crowdfunding)
  medium:   <true/false>   # $100K-$500K (SBA 7(a), angel, equipment financing, PO financing)
  large:    <true/false>   # $500K-$2M (SBA 7(a)/504, VC, strategic, bank term loan)
  enterprise: <true/false> # $2M+ (VC, PE, large bank, acquisition financing)
```

Scoring thresholds:
- micro: overall ≥ 40
- small: overall ≥ 55
- medium: overall ≥ 70
- large: overall ≥ 80
- enterprise: overall ≥ 90

## Funding Sources Eligible

Computed from readiness scores. Each source has a minimum overall threshold.

| Source | Minimum Overall | Notes |
|--------|-----------------|-------|
| grants | 40 | Community/nonprofit focus, eligibility-driven |
| microloans | 50 | SBA microloan programs, CDFIs |
| business_credit_cards | 45 | Requires banking + credit profile |
| revenue_based_financing | 70 | Requires revenue history |
| equipment_financing | 50 | Requires collateral (equipment) |
| po_financing | 65 | Requires signed POs, revenue |
| invoice_factoring | 60 | Requires AR, revenue |
| asset_based_lending | 55 | Requires collateral |
| vendor_financing | 40 | Vendor-specific |
| crowdfunding | 50 | Requires marketing, audience |
| angel_investment | 70 | Requires business plan, traction |
| venture_capital | 80 | Requires growth metrics, moat, team |
| strategic_investment | 75 | Requires strategic fit, product |
| sba_7a | 75 | Requires SBA readiness, collateral, business plan |
| sba_504 | 80 | Requires real estate/equipment collateral |
| bank_term_loan | 70 | Requires credit, collateral, cash-flow projections |
| private_equity | 85 | Requires scale, EBITDA, growth |
| government_contracts | 60 | Requires compliance, capacity, registrations |

## Gap Analysis

Each assessment produces a `funding_gaps` array identifying:
- Which dimensions score below fundable thresholds
- What action is needed to close each gap
- Estimated effort (low/medium/high) to close

Example:
```yaml
funding_gaps:
  - dimension: credit
    current_score: 20
    target_score: 65
    gap_description: "No D&B profile, no business credit history"
    action_needed: "Register with D&B, establish Net-30 vendor accounts, build trade references"
    estimated_effort: medium

  - dimension: collateral
    current_score: 10
    target_score: 50
    gap_description: "No equipment, vehicles, or real estate documented as collateral"
    action_needed: "Inventory owned assets, document IP, obtain insurance"
    estimated_effort: high
```

## Default/Initial Assessment (all ventures)

When no per-venture assessment exists, apply these defaults derived from registry data:

| Dimension | Default Score | Rationale |
|-----------|--------------|-----------|
| legal | 100 | All 742 ventures have legal identity (ID, name, sector) in registry |
| banking | 50 | 64 ventures have Vercel deploys (payment processing likely), rest unknown |
| accounting | 20 | Zero ventures have financial data in registry |
| credit | 10 | No D&B/Experian data in registry |
| revenue | 10 | Zero ventures have revenue data (0 of 742) |
| documentation | 80 | Good registry docs, schemas exist |
| business_plan | 75 | Venture definitions exist with sector and purpose |
| collateral | 15 | No collateral data in registry |
| investor_readiness | 30 | Some have Vercel + descriptions, no pitch decks or metrics |
| grant_readiness | 50 | Community/nonprofit ventures likely eligible; others unknown |
| sba_bank_readiness | 30 | Registry has legal identity, no financials or collateral |
| alternative_funding | 35 | No revenue or collateral data for most |

**Default overall: ~45** → `FUNDING_IN_PROGRESS`

This means: as a baseline, all 742 ventures are somewhere between "minimal infrastructure" and "some pieces in place" — mostly because we have legal identity and registry documentation but no financial data, credit profiles, or collateral documentation.

## Per-Venture Reassessment

Once a venture has:
- Deployed product with payment processing → banking score increases
- Revenue tracking → revenue score increases
- D&B profile → credit score increases
- EIN + bank account → banking score increases
- Business plan document → business_plan score increases
- Pitch deck + metrics → investor_readiness increases
- Equipment/vehicles/RE → collateral increases

The system should re-assess each venture when new data arrives (Vercel deploy, payment processor connected, revenue reported, etc.).

## Files

- `schemas/funding-readiness.json` — JSON Schema for funding readiness records
- `registry/funding-readiness-template.yaml` — Template for per-venture assessment
- `registry/funding-readiness-defaults.yaml` — Default assessment applied to all ventures without per-venture data
- `audits/funding-readiness-report.md` — Roll-up report across all ventures

## Questions This System Enables

1. **Which ventures are fundable today?** → Filter overall ≥ 70
2. **What's missing for each venture to reach $25K fundable?** → funding_gaps where micro = false
3. **What's the aggregate funding capacity?** → Sum of (revenue × multiple) by readiness tier
4. **Which ventures need EIN + bank account first?** → Filter where legal < 100 or banking < 90
5. **Which ventures are grant-eligible?** → Filter where grant_readiness ≥ 50
6. **Which ventures could use revenue-based financing?** → Filter where revenue ≥ 60
7. **How many ventures are SBA-ready?** → Filter where sba_bank_readiness ≥ 75
