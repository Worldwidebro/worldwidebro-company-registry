# Capital Flow Graph — System Documentation

**Date:** 2026-08-23
**Related:** funding-readiness.json (readiness scoring) → capital-flow-node.json (capital flow entities) → capital-flow-edge.json (capital flow relationships)

---

## Purpose

The funding-readiness schema answers: **Is a venture fundable?**

The capital flow graph answers: **Where does money come from, who controls it, how does it flow to ventures, and how does it cycle back?**

Together they form a complete capital intelligence layer: readiness + origin + flow + cycle.

## The Architecture

```
                    CAPITAL ORIGIN
                         │
       ┌─────────────────┼─────────────────┐
       ▼                 ▼                 ▼
   GOVERNMENT          PRIVATE           MARKETS
       │                 │                 │
       ▼                 ▼                 ▼
   PROGRAMS           FAMILY OFFICE     BANKS
       │              INSTITUTIONS       FUNDS
       ▼                 │                 │
 GRANTS/CONTRACTS        └────────┬────────┘
       │                          ▼
       ▼                    INVESTMENT VEHICLE
     PRIME                       │
       │                         ▼
 SUBCONTRACTOR                 FUND
       │                         │
       ▼                         ▼
    VENDOR                     SPV
       │                         │
       └──────────────┬──────────┘
                      ▼
                    HOLDCO
                      │
             ┌────────┼────────┐
             ▼        ▼        ▼
            OPCO     OPCO     PROJECT
             │        │        │
             ▼        ▼        ▼
          REVENUE   REVENUE   ASSET
             │        │        │
             └────────┼────────┘
                      ▼
                    CASH FLOW
                      │
          ┌───────────┼────────────┐
          ▼           ▼            ▼
       REINVEST     DEBT       DISTRIBUTION
          │                        │
          ▼                        ▼
       GROWTH                 OWNERS/INVESTORS
```

## Node Types (18 categories)

| Type | Role in Capital Flow | Example |
|------|---------------------|---------|
| government | Capital origin (public) | Federal government, state government |
| agency | Government allocator | SBA, DOE, DOD, HHS, DOT |
| program | Government funding program | SBIR, STTR, USDA Rural, HUD CDBG |
| funding_opportunity | Specific funding call | Solicitation, NOFO, RFP, RFQ |
| award | Award made to a recipient | Grant awarded, contract awarded, loan disbursed |
| prime | First recipient of government funding | Prime contractor, prime grantee |
| subaward | Funding passed to subrecipient | Subgrant, subcontract dollar value |
| subcontract | Contractual relationship below prime | Subcontractor agreement |
| contractor | Entity performing work under contract | Engineering firm, construction company |
| vendor | Entity supplying goods/services | Software vendor, equipment supplier |
| project | Specific project/program funded | Road construction project, research project |
| asset | Physical or intangible asset | Vehicle, equipment, building, IP, land |
| opco | Operating company | Logistics OpCo, Construction OpCo |
| spv | Special purpose vehicle | Project SPV, acquisition SPV, holdcos SPV |
| holdco | Holding company controlling OPCOs | WorldwideBro Holdings |
| family_office | Private capital allocator | Single-family office, multi-family office |
| pe_firm | Private equity firm | PE manager with Fund I/II/III |
| vc_firm | Venture capital firm | Early-stage or growth VC |
| bank | Banking/lending institution | Commercial bank, regional bank, credit union |
| lender | Credit provider | Direct lender, mezzanine, private credit |
| lp | Limited partner in a fund | Pension fund, endowment, family office, HNW |
| gp | General partner of a fund | PE fund GP, VC fund GP |
| fund | Investment fund vehicle | PE fund, VC fund, fund-of-funds |
| employee | Worker/personnel | W-2 employee, contractor, agent |
| customer | Revenue source | Business customer, consumer, government client |
| venture | Worldwidebro venture from registry | LT-011, CON-001, RE-001, etc. |

## Edge Types (32 relationship types)

### Capital Flow (where money goes)
| Edge Type | Meaning |
|-----------|---------|
| appropriates | Government/Congress appropriates budget to agency/program |
| funds | Allocator provides capital to recipient |
| awards | Agency awards grant/contract/loan to recipient |
| subawards | Prime passes funding to subrecipient |
| invests_in | Investor puts capital into entity |
| owns | Entity holds ownership stake in another |
| controls | Entity has control (board, voting, operational) |
| lends_to | Lender provides debt to borrower |
| guarantees | Guarantor guarantees an obligation |
| borrows_from | Entity borrows from a lender |
| distributes | Entity distributes cash to owners/investors |
| reinvests | Entity reinvests cash flow into growth |
| generates_revenue | Entity generates revenue from operations |
| pays | Entity makes a payment |
| charges | Entity charges a fee/commission |
| bills | Entity sends an invoice |
| allocates_to | Allocator allocates capital to a vehicle/entity |

### Operational (how work happens)
| Edge Type | Meaning |
|-----------|---------|
| contracts_with | Entity has a contract with another |
| subcontracts_with | Entity has a subcontract with another |
| subcontracts_to | Entity subcontracts work to another |
| supplies | Vendor supplies goods/services to entity |
| employs | Entity employs a worker/agent |
| operates | Entity operates a project/venture/OPCO |
| partners_with | Entities are partners in a venture |
| joint_venture_with | Entities form a JV |
| purchases_from | Entity purchases from a vendor |
| sells_to | Entity sells to a customer |
| sponsors | Entity sponsors a project/program |
| underwrites | Entity underwrites an obligation/investment |

### Structural (how entities relate)
| Edge Type | Meaning |
|-----------|---------|
| spin_offs | Entity spins off a new entity |
| merges_with | Two entities merge |
| acquires | Entity acquires another |
| receives_from | Entity receives funding/capital from another |
| pays_to | Entity pays to another |
| subawards_to | Prime subawards to subrecipient |

---

## How This Connects to the Existing Registry

```
VENTURE REGISTRY (742 ventures)
  ├── sector
  ├── business_model
  ├── lifecycle_stage
  ├── revenue
  ├── capabilities
  └── funding_readiness (12-dimension score + fundable_at + sources_eligible)

CAPITAL FLOW GRAPH (new layer)
  ├── nodes: government, agency, program, award, prime, subaward, contractor,
  │          vendor, project, asset, opco, spv, holdco, family_office, pe_firm,
  │          vc_firm, bank, lender, lp, gp, fund, employee, customer, venture
  └── edges: appropriates, funds, awards, subawards, contracts_with, invests_in,
            owns, controls, lends_to, guarantees, borrows_from, operates,
            supplies, employs, generates_revenue, pays, distributes, reinvests,
            and 18 more

FUNDING READINESS + CAPITAL FLOW = COMPLETE CAPITAL INTELLIGENCE
  ├── Which ventures are fundable? → funding_readiness.overall ≥ 70
  ├── Who funds them? → capital_flow_graph: edges where venture is target
  ├── Through what channel? → edge.edge_type (awards, subcontracts, invests_in, lends_to)
  ├── How much? → edge.amount + edge.amount_type
  ├── What's the cycle? → edges from venture → pays/reinvests/distributes → back to capital origins
```

## Seed Nodes — What We Know Today

These are nodes we can populate from existing data:

```yaml
# GOVERNMENT NODES (from existing knowledge)
- GOV-FEDERAL:
    node_type: government
    name: United States Federal Government
    capital_role: capital_origin
    jurisdiction: federal

- GOV-SBA:
    node_type: agency
    name: Small Business Administration
    capital_role: capital_allocator
    jurisdiction: federal
    data_sources: [SAM.gov, Grants.gov, USAspending]

- GOV-DOD:
    node_type: agency
    name: Department of Defense
    capital_role: capital_allocator
    jurisdiction: federal

- GOV-DOE:
    node_type: agency
    name: Department of Energy
    capital_role: capital_allocator
    jurisdiction: federal

- GOV-HUD:
    node_type: agency
    name: Department of Housing and Urban Development
    capital_role: capital_allocator
    jurisdiction: federal

- GOV-DOT:
    node_type: agency
    name: Department of Transportation
    capital_role: capital_allocator
    jurisdiction: federal
    # Relevant to LT-005, LT-011 logistics ventures

# VENTURE/CAPITAL NODES (from registry)
- ENT-WORLDWIDE BRO-HOLDINGS:
    node_type: holdco
    name: WorldwideBro Holdings
    capital_role: capital_distributor
    ownership:
      owner_type: individual
      control_structure: direct

- ENT-LT-011-DISPATCH-SOFTWARE:
    node_type: venture
    name: LT-011 Dispatch Software
    capital_role: capital_receiver
    capital_role: capital_user
    sector: logistics-transport
    funding_readiness_reference: LT-011

- ENT-CON-001-ACE-CONSTRUCTION:
    node_type: venture
    name: CON-001 Ace Construction
    capital_role: capital_receiver
    capital_role: capital_user
    sector: construction
    funding_readiness_reference: CON-001
    # Potential SBA 7(a)/504 borrower, government construction contracts
```

## Edges We Can Seed From Known Relationships

```yaml
# LT-011 Dispatch Software ← WorldwideBro Holdings (owns/controls)
- EDGE-001:
    edge_type: owns
    source_node_id: ENT-WORLDWIDE-BRO-HOLDINGS
    target_node_id: ENT-LT-011-DISPATCH-SOFTWARE
    percentage: 100
    direction: one_way

# CON-001 Ace Construction ← WorldwideBro Holdings (owns/controls)
- EDGE-002:
    edge_type: owns
    source_node_id: ENT-WORLDWIDE-BRO-HOLDINGS
    target_node_id: ENT-CON-001-ACE-CONSTRUCTION
    percentage: 100
    direction: one_way

# SBA ← CON-001 (potential funding path)
- EDGE-003:
    edge_type: awards
    source_node_id: GOV-SBA
    target_node_id: ENT-CON-001-ACE-CONSTRUCTION
    edge_type: awards
    award_type: loan
    amount_type: commitment
    status: potential  # not yet funded, but eligible
    data_source: funding_readiness_defaults.yaml
    confidence: 50  # inferred from venture type + sector + SBA focus
```

## The Key Questions This System Enables

### Capital Origin Questions
1. **Where does money enter the ecosystem?** — trace all edges where edge_type = appropriates/funds/awards/invests_in pointing TO nodes in the graph
2. **How much public capital flows through each sector?** — sum edge.amount where source_node is government/agency/program and target sector matches
3. **Which agencies are the biggest allocators to our sectors?** — group edges by source agency, sum amounts, filter by sector relevance

### Prime/Subcontractor Questions
4. **Who are the prime recipients in our supply chain?** — find all prime nodes that have subawards/contracts_with edges pointing to vendors/contractors in our sectors
5. **Which primes subcontract to ventures like ours?** — traverse subcontracts_with edges from primes to vendor/contractor nodes matching our venture profiles
6. **What's the typical subcontracting chain depth?** — follow subawards edges recursively, count levels

### Capital Vehicle Questions
7. **Which family offices invest in our sectors?** — find family_office nodes with invests_in edges to entities in our sectors
8. **Which PE/VC firms own companies like ours?** — find pe_firm/vc_firm nodes with owns edges to opco/venture nodes in our sectors
9. **What SPV structures exist for projects like ours?** — find spv nodes with operates edges to project nodes in our sectors

### Funding Readiness + Capital Flow Integration
10. **For each fundable venture, who are the specific capital sources?** — join funding_readiness.venture_id where overall ≥ 70 with capital_flow_graph edges where target = that venture
11. **Which funding sources does the capital flow graph confirm?** — cross-reference funding_sources_eligible (from readiness) with actual edges (from capital flow graph)
12. **Where are the gaps between readiness and actual capital connected to our ventures?** — ventures with high readiness but no incoming capital edges = ready but unfunded; ventures with incoming edges but low readiness = funded but underprepared

### Circular Flow Questions
13. **How does capital cycle back?** — trace edges from venture → generates_revenue → pays/reinvests/distributes → back to holdco/family_office/investors → new funding → new projects
14. **What's the reinvestment rate?** — sum reinvests edges / sum generates_revenue edges per venture/opco
15. **Where does capital bottleneck?** — find nodes where incoming edges >> outgoing edges = capital accumulates; where outgoing >> incoming = capital drains

### Staffing/Agent Questions (what you asked)
16. **How many employees/agents does each venture need?** — count employs edges from venture/opco to employee nodes, grouped by function
17. **What's the labor cost per venture?** — sum employee compensation along employs edges
18. **Which ventures share personnel?** — find employee nodes connected to multiple venture/opco nodes
19. **Where are the hiring gaps?** — ventures with high readiness but few/no employs edges = needs staff

---

## How to Build This

### Phase 1 — Seed the graph with what we know (1-2 weeks)
1. Create the schema files (done: capital-flow-node.json, capital-flow-edge.json)
2. Seed government nodes (federal agencies, SBA, key programs) — mostly static, can be bulk-loaded
3. Seed WorldwideBro entity nodes (holdco, existing ventures, opcos) — from registry
4. Seed known edges (holdings, ownership, venture → opco mappings)
5. Write a graph query layer (Python + Neo4j or in-memory graph + JSON)

### Phase 2 — Connect to public data (2-4 weeks)
1. USAspending API — fetch federal awards by recipient, NAICS, agency, fiscal year
2. Grants.gov — fetch funding opportunities by sector, eligibility
3. SAM.gov — verify entity registrations, UEIs
4. Map awards → prime → subaward → contractor/vendor nodes
5. Match NAICS codes to our venture sectors
6. Identify which of our ventures are eligible for which awards

### Phase 3 — Private capital (ongoing)
1. Crunchbase/PitchBook API — PE/VC ownership, family office investments
2. State/local contract data — each state's procurement portal
3. Build private capital nodes (family offices, PE firms, VC firms, banks) with invests_in/owns edges
4. Connect to our ventures where there's actual investment or ownership

### Phase 4 — Operational staffing layer (ongoing)
1. Define employee/agent node types per venture function
2. Map venture → required roles → estimated headcount → estimated cost
3. Track employs edges as ventures hire (real or planned)
4. Enable "how many agents/employees needed" queries across the portfolio

---

## Files in Registry

```
schemas/
  capital-flow-node.json          # Node schema (18 node types)
  capital-flow-edge.json          # Edge schema (32 edge types)

audits/
  capital-flow-graph-report.md    # This documentation

registry/
  capital-flow-graph-seed.yaml    # Seed nodes + edges from known data

compute_capital_flow_seed.py     # Script to seed initial graph from registry
```

## Relationship to Funding Readiness

```
FUNDING READINESS (venture-level)
  ├── venture_id → overall score → funding_status → fundable_at → funding_sources_eligible
  └── Answers: "Is this venture fundable, at what level, from what sources?"

CAPITAL FLOW GRAPH (ecosystem-level)
  ├── nodes: capital origins, allocators, vehicles, recipients, projects, assets
  ├── edges: how capital flows between nodes (appropriates, funds, awards, invests_in, owns, lends_to, etc.)
  └── Answers: "Where does capital come from, who controls it, how does it flow, how does it cycle?"

INTEGRATED:
  ├── Funding readiness tells you if a venture is ready
  ├── Capital flow graph tells you which specific nodes/edges can fund it
  ├── Combined: "LT-011 is FUNDING_READY_WITH_GAPS (overall 65), and the capital flow graph shows
  │            SBA (GOV-SBA) → awards → construction/logistics ventures in our sectors,
  │            but LT-011 has no incoming edges yet → gap: apply for SBA funding"
  └── This is the complete capital intelligence layer.
```

## Notes

- SPV structure and legal entity formation require attorneys and CPAs. The graph models the STRUCTURE (who owns what, how capital flows) but doesn't provide legal advice.
- USAspending and Grants.gov provide public data for the government portion. Crunchbase/PitchBook provide data for the private portion.
- The graph should grow as you add ventures, connect to public data, and map your own capital flows.
- This is a LOT of data to populate. Start small: seed government nodes + WorldwideBro entity nodes + known edges. Expand as you connect to APIs and map actual flows.
