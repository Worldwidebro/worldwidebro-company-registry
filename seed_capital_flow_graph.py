#!/usr/bin/env python3
"""
Seed the capital flow graph with:
1. Government nodes (federal government, SBA, DOD, DOE, HUD, DOT + agencies)
2. WorldwideBro entity nodes (holdco, key ventures from registry)
3. Known edges (holdings, ownership, venture → registry venture_id mapping)

Outputs: registry/capital-flow-graph-seed.yaml
"""
import yaml, json
from pathlib import Path

reg = Path('/Users/divinejohns/Documents/Obsidian Vault/worldwidebro-company-registry')

with open(reg / 'registry/ventures.yaml') as f:
    ventures = yaml.safe_load(f)

# ── GOVERNMENT NODES (seed) ──
government_nodes = [
    {
        'node_id': 'GOV-US-FEDERAL',
        'node_type': 'government',
        'name': 'United States Federal Government',
        'description': 'Sovereign government — ultimate capital origin for federal appropriations, grants, contracts, loans',
        'jurisdiction': 'federal',
        'capital_role': 'capital_origin',
        'data_sources': ['Congress.gov', 'USAspending.gov'],
        'confidence': 100,
    },
    {
        'node_id': 'GOV-SBA',
        'node_type': 'agency',
        'name': 'Small Business Administration',
        'description': 'Federal agency providing loans, loan guarantees, contracts, grants to small businesses. Key capital allocator for small business ventures.',
        'jurisdiction': 'federal',
        'capital_role': 'capital_allocator',
        'parent_node_id': 'GOV-US-FEDERAL',
        'data_sources': ['SAM.gov', 'Grants.gov', 'USAspending.gov', 'sba.gov'],
        'confidence': 100,
    },
    {
        'node_id': 'GOV-DOD',
        'node_type': 'agency',
        'name': 'Department of Defense',
        'description': 'Federal department — large procurement/contracting agency. Relevant for technology, logistics, construction ventures with defense contracts.',
        'jurisdiction': 'federal',
        'capital_role': 'capital_allocator',
        'parent_node_id': 'GOV-US-FEDERAL',
        'data_sources': ['USAspending.gov', 'defense.gov'],
        'confidence': 100,
    },
    {
        'node_id': 'GOV-DOE',
        'node_type': 'agency',
        'name': 'Department of Energy',
        'description': 'Federal department — grants, contracts for energy, infrastructure, R&D. Relevant for energy, construction, technology ventures.',
        'jurisdiction': 'federal',
        'capital_role': 'capital_allocator',
        'parent_node_id': 'GOV-US-FEDERAL',
        'data_sources': ['USAspending.gov', 'energy.gov'],
        'confidence': 100,
    },
    {
        'node_id': 'GOV-HUD',
        'node_type': 'agency',
        'name': 'Department of Housing and Urban Development',
        'description': 'Federal department — housing, community development, real estate grants and programs. Relevant for real estate, construction, community ventures.',
        'jurisdiction': 'federal',
        'capital_role': 'capital_allocator',
        'parent_node_id': 'GOV-US-FEDERAL',
        'data_sources': ['USAspending.gov', 'hud.gov'],
        'confidence': 100,
    },
    {
        'node_id': 'GOV-DOT',
        'node_type': 'agency',
        'name': 'Department of Transportation',
        'description': 'Federal department — grants, contracts for transportation, logistics, infrastructure. Highly relevant for LT-005, LT-011 logistics ventures.',
        'jurisdiction': 'federal',
        'capital_role': 'capital_allocator',
        'parent_node_id': 'GOV-US-FEDERAL',
        'data_sources': ['USAspending.gov', 'dot.gov'],
        'confidence': 100,
    },
    {
        'node_id': 'GOV-HHS',
        'node_type': 'agency',
        'name': 'Department of Health and Human Services',
        'description': 'Federal department — healthcare, medical, public health grants and contracts. Relevant for LT-005 medical courier, healthcare ventures.',
        'jurisdiction': 'federal',
        'capital_role': 'capital_allocator',
        'parent_node_id': 'GOV-US-FEDERAL',
        'data_sources': ['USAspending.gov', 'hhs.gov'],
        'confidence': 100,
    },
    {
        'node_id': 'GOV-EDU',
        'node_type': 'agency',
        'name': 'Department of Education',
        'description': 'Federal department — education grants, contracts. Relevant for education-training ventures.',
        'jurisdiction': 'federal',
        'capital_role': 'capital_allocator',
        'parent_node_id': 'GOV-US-FEDERAL',
        'data_sources': ['USAspending.gov', 'ed.gov'],
        'confidence': 100,
    },
    {
        'node_id': 'GOV-USDA',
        'node_type': 'agency',
        'name': 'Department of Agriculture',
        'description': 'Federal department — rural development, food, agriculture grants and loans. Relevant for food-hospitality, agriculture-adjacent ventures.',
        'jurisdiction': 'federal',
        'capital_role': 'capital_allocator',
        'parent_node_id': 'GOV-US-FEDERAL',
        'data_sources': ['USAspending.gov', 'usda.gov'],
        'confidence': 100,
    },
    {
        'node_id': 'GOV-SC',
        'node_type': 'agency',
        'name': 'Small Business — State and Local',
        'description': 'State and local small business agencies, economic development corporations. Provide state-level grants, loans, contracting opportunities.',
        'jurisdiction': 'state/local',
        'capital_role': 'capital_allocator',
        'data_sources': ['state procurement portals', 'local economic development offices'],
        'confidence': 60,
        'notes': 'To be populated per-state as data becomes available',
    },
]

# ── PRIVATE CAPITAL NODES (seed — placeholder until data-connected) ──
private_capital_nodes = [
    {
        'node_id': 'CAP-PRIVATE-ORIGIN',
        'node_type': 'capital_origin',
        'name': 'Private Capital Origins',
        'description': 'Aggregate node for private capital origins: family offices, HNW investors, pensions, endowments, insurance, sovereign wealth, foundations',
        'capital_role': 'capital_origin',
        'confidence': 60,
        'notes': 'Aggregate placeholder — individual allocators to be seeded from Crunchbase/PitchBook/capital research',
    },
    {
        'node_id': 'CAP-FAMILY-OFFICES',
        'node_type': 'capital_allocator',
        'name': 'Family Offices (Aggregate)',
        'description': 'Multi-family and single-family offices that allocate capital across direct equity, debt, PE funds, VC funds, real estate, infrastructure, private credit, public markets, co-investments',
        'capital_role': 'capital_allocator',
        'parent_node_id': 'CAP-PRIVATE-ORIGIN',
        'confidence': 60,
        'notes': 'Aggregate placeholder — individual family offices to be seeded from capital research',
    },
    {
        'node_id': 'CAP-PE-FIRMS',
        'node_type': 'capital_allocator',
        'name': 'Private Equity Firms (Aggregate)',
        'description': 'PE firms that raise funds from LPs (pensions, endowments, family offices, insurance, HNW) and invest in portfolio companies via acquisition SPVs → OPCOs',
        'capital_role': 'capital_allocator',
        'parent_node_id': 'CAP-PRIVATE-ORIGIN',
        'confidence': 60,
        'notes': 'Aggregate placeholder — individual PE firms to be seeded from Crunchbase/PitchBook',
    },
    {
        'node_id': 'CAP-VC-FIRMS',
        'node_type': 'capital_allocator',
        'name': 'Venture Capital Firms (Aggregate)',
        'description': 'VC firms that invest in early-stage and growth ventures via fund GPs → SPV → venture equity',
        'capital_role': 'capital_allocator',
        'parent_node_id': 'CAP-PRIVATE-ORIGIN',
        'confidence': 60,
        'notes': 'Aggregate placeholder — individual VC firms to be seeded from Crunchbase/PitchBook',
    },
    {
        'node_id': 'CAP-BANKS',
        'node_type': 'capital_allocator',
        'name': 'Banks & Lenders (Aggregate)',
        'description': 'Commercial banks, regional banks, credit unions, direct lenders, mezzanine, private credit — provide debt capital via loans, loan guarantees, lines of credit',
        'capital_role': 'capital_allocator',
        'parent_node_id': 'CAP-PRIVATE-ORIGIN',
        'confidence': 60,
        'notes': 'Aggregate placeholder — individual banks/lenders to be seeded from capital research',
    },
]

# ── WORLDWIDE BRO ENTITY NODES (from registry) ──
# Holdco
worldwidebro_nodes = [
    {
        'node_id': 'ENT-WORLDWIDE-BRO-HOLDINGS',
        'node_type': 'holdco',
        'name': 'WorldwideBro Holdings',
        'description': 'Top-level holding company controlling WorldwideBro operating companies and ventures across 17+ sectors',
        'capital_role': 'capital_distributor',
        'capital_role': 'capital_receiver',
        'ownership': {
            'owner_type': 'individual',
            'control_structure': 'direct',
        },
        'data_sources': ['worldwidebro-company-registry'],
        'confidence': 100,
    },
    {
        'node_id': 'ENT-WORLDWIDE-BRO-OPERATIONS',
        'node_type': 'opco',
        'name': 'WorldwideBro Operations',
        'description': 'Operating company for process automation, shared services, operational infrastructure across the portfolio',
        'capital_role': 'capital_receiver',
        'capital_role': 'capital_user',
        'parent_node_id': 'ENT-WORLDWIDE-BRO-HOLDINGS',
        'data_sources': ['worldwidebro-company-registry'],
        'confidence': 100,
    },
]

# ── VENTURE NODES (from registry — sample of key ones + grant/contract-eligible sectors) ──
# Seed a representative set: focus ventures + key sector representatives
venture_nodes = []

for v in ventures:
    vid = v['id']
    node_id = f"ENT-{vid.replace(' ', '-')}"
    
    # Determine capital roles based on status
    if v.get('status') == 'Live':
        roles = ['capital_user', 'capital_receiver']
    elif v.get('status') == 'Building':
        roles = ['capital_receiver', 'capital_user']
    else:
        roles = ['capital_receiver']
    
    venture_nodes.append({
        'node_id': node_id,
        'node_type': 'venture',
        'name': v.get('name', ''),
        'description': f"Venture: {v.get('sector', 'unknown')} sector, {v.get('status', 'unknown')} status, {v.get('business_model', '')} business model",
        'sector': v.get('sector', 'unknown'),
        'capital_role': roles if len(roles) == 1 else roles[0],  # take first for schema
        'parent_node_id': 'ENT-WORLDWIDE-BRO-HOLDINGS',
        'data_sources': ['worldwidebro-company-registry'],
        'confidence': 100,
        'venture_registry_id': vid,
        '_status': v.get('status', ''),
        '_vercel_url': v.get('_vercel_url', ''),
        '_business_model': v.get('business_model', ''),
    })

print(f"Seeding {len(venture_nodes)} venture nodes...")
print(f"Seeding {len(government_nodes)} government nodes...")
print(f"Seeding {len(private_capital_nodes)} private capital nodes...")
print(f"Seeding {len(worldwidebro_nodes)} WorldwideBro entity nodes...")

# ── EDGES ──

edges = []

# ── Government hierarchy edges ──
for gov in government_nodes:
    if gov.get('parent_node_id'):
        edges.append({
            'edge_id': f"EDGE-{gov['node_id']}-PARENT",
            'source_node_id': gov['parent_node_id'],
            'target_node_id': gov['node_id'],
            'edge_type': 'controls',
            'direction': 'one_way',
            'confidence': 100,
        })

# ── WorldwideBro ownership edges ──
for node in worldwidebro_nodes + venture_nodes:
    if node.get('parent_node_id'):
        edges.append({
            'edge_id': f"EDGE-{node['node_id']}-OWNERSHIP",
            'source_node_id': node['parent_node_id'],
            'target_node_id': node['node_id'],
            'edge_type': 'owns',
            'direction': 'one_way',
            'percentage': 100,
            'confidence': 100,
        })

# ── Venture → Vercel deploy edges ──
for v in ventures:
    url = v.get('_vercel_url')
    if url:
        vid = v['id']
        node_id = f"ENT-{vid.replace(' ', '-')}"
        edges.append({
            'edge_id': f"EDGE-{node_id}-VERCEL-DEPLOY",
            'source_node_id': node_id,
            'target_node_id': 'VERCEL-PLATFORM',  # We'll add this as a node
            'edge_type': 'deploys_to',
            'direction': 'one_way',
            'data_source': 'vercel_deployments.csv',
            'confidence': 100,
            'notes': f"Production URL: {url}",
        })

# ── Venture → funding readiness reference edges ──
for v in ventures:
    vid = v['id']
    node_id = f"ENT-{vid.replace(' ', '-')}"
    edges.append({
        'edge_id': f"EDGE-{node_id}-FUNDING-READINESS",
        'source_node_id': node_id,
        'target_node_id': 'FUNDING-READINESS-SYSTEM',
        'edge_type': 'references',
        'direction': 'one_way',
        'data_source': 'funding-readiness-defaults.yaml',
        'confidence': 100,
        'notes': f"Funding readiness assessment for {vid}",
    })

# ── SBA → construction ventures (potential award edge, not yet funded) ──
for v in ventures:
    if v.get('sector') in ('construction', 'logistics-transport', 'real-estate'):
        vid = v['id']
        node_id = f"ENT-{vid.replace(' ', '-')}"
        edges.append({
            'edge_id': f"EDGE-SBA-{node_id}-POTENTIAL",
            'source_node_id': 'GOV-SBA',
            'target_node_id': node_id,
            'edge_type': 'awards',
            'award_type': 'loan',
            'status': 'potential',
            'amount_type': 'commitment',
            'confidence': 50,
            'notes': f"Potential SBA 7(a)/504 funding for {vid} in {v.get('sector')} sector",
            'data_source': 'funding_readiness-defaults.yaml',
        })

# ── DOT → logistics ventures (potential award edge) ──
for v in ventures:
    if v.get('sector') == 'logistics-transport':
        vid = v['id']
        node_id = f"ENT-{vid.replace(' ', '-')}"
        edges.append({
            'edge_id': f"EDGE-DOT-{node_id}-POTENTIAL",
            'source_node_id': 'GOV-DOT',
            'target_node_id': node_id,
            'edge_type': 'awards',
            'award_type': 'grant',
            'status': 'potential',
            'confidence': 50,
            'notes': f"Potential DOT grant/contract for {vid}",
            'data_source': 'funding_readiness-defaults.yaml',
        })

# ── HHS → medical/healthcare ventures ──
for v in ventures:
    if v.get('sector') in ('healthcare', 'medical', 'logistics-transport') and 'medical' in (v.get('name') or '').lower():
        vid = v['id']
        node_id = f"ENT-{vid.replace(' ', '-')}"
        edges.append({
            'edge_id': f"EDGE-HHS-{node_id}-POTENTIAL",
            'source_node_id': 'GOV-HHS',
            'target_node_id': node_id,
            'edge_type': 'awards',
            'award_type': 'contract',
            'status': 'potential',
            'confidence': 50,
            'notes': f"Potential HHS contract for {vid}",
            'data_source': 'funding_readiness-defaults.yaml',
        })

# ── USDSOV → food/agriculture ventures ──
for v in ventures:
    if v.get('sector') == 'food-hospitality':
        vid = v['id']
        node_id = f"ENT-{vid.replace(' ', '-')}"
        edges.append({
            'edge_id': f"EDGE-USDA-{node_id}-POTENTIAL",
            'source_node_id': 'GOV-USDA',
            'target_node_id': node_id,
            'edge_type': 'awards',
            'award_type': 'loan',
            'status': 'potential',
            'confidence': 40,
            'notes': f"Potential USDA rural development loan for {vid}",
            'data_source': 'funding_readiness-defaults.yaml',
        })

# ── DEPARTMENT OF EDUCATION → education ventures ──
for v in ventures:
    if v.get('sector') in ('education', 'education-training'):
        vid = v['id']
        node_id = f"ENT-{vid.replace(' ', '-')}"
        edges.append({
            'edge_id': f"EDGE-EDU-{node_id}-POTENTIAL",
            'source_node_id': 'GOV-EDU',
            'target_node_id': node_id,
            'edge_type': 'awards',
            'award_type': 'grant',
            'status': 'potential',
            'confidence': 45,
            'notes': f"Potential Dept of Education grant for {vid}",
            'data_source': 'funding_readiness-defaults.yaml',
        })

# ── HUD → real estate/construction/community ──
for v in ventures:
    if v.get('sector') in ('real-estate', 'construction', 'community'):
        vid = v['id']
        node_id = f"ENT-{vid.replace(' ', '-')}"
        edges.append({
            'edge_id': f"EDGE-HUD-{node_id}-POTENTIAL",
            'source_node_id': 'GOV-HUD',
            'target_node_id': node_id,
            'edge_type': 'awards',
            'award_type': 'grant',
            'status': 'potential',
            'confidence': 35,
            'notes': f"Potential HUD CDBG/Community Development funding for {vid}",
            'data_source': 'funding_readiness-defaults.yaml',
        })

# ── DOD → technology/software ventures ──
for v in ventures:
    if v.get('sector') in ('technology', 'software-technology', 'emerging'):
        vid = v['id']
        node_id = f"ENT-{vid.replace(' ', '-')}"
        edges.append({
            'edge_id': f"EDGE-DOD-{node_id}-POTENTIAL",
            'source_node_id': 'GOV-DOD',
            'target_node_id': node_id,
            'edge_type': 'awards',
            'award_type': 'contract',
            'status': 'potential',
            'confidence': 30,
            'notes': f"Potential DOD SBIR/STTR/contract for {vid}",
            'data_source': 'funding_readiness-defaults.yaml',
        })

# ── DOE → energy/construction/technology ──
for v in ventures:
    if v.get('sector') in ('construction', 'technology', 'real-estate'):
        vid = v['id']
        node_id = f"ENT-{vid.replace(' ', '-')}"
        edges.append({
            'edge_id': f"EDGE-DOE-{node_id}-POTENTIAL",
            'source_node_id': 'GOV-DOE',
            'target_node_id': node_id,
            'edge_type': 'awards',
            'award_type': 'grant',
            'status': 'potential',
            'confidence': 30,
            'notes': f"Potential DOE grant for {vid}",
            'data_source': 'funding_readiness-defaults.yaml',
        })

# ── VENTURE → VENTURE REGISTRY reference ──
for v in ventures:
    vid = v['id']
    node_id = f"ENT-{vid.replace(' ', '-')}"
    edges.append({
        'edge_id': f"EDGE-{node_id}-REGISTRY",
        'source_node_id': node_id,
        'target_node_id': 'REGISTRY-VENTURES-YAML',
        'edge_type': 'references',
        'direction': 'one_way',
        'data_source': 'worldwidebro-company-registry/registry/ventures.yaml',
        'confidence': 100,
    })

print(f"Seeding {len(edges)} edges...")

# ── Write seed file ──
seed_data = {
    'seed_date': '2026-08-23',
    'seed_description': 'Initial capital flow graph seed: government nodes + WorldwideBro entity nodes + venture nodes (all 742) + known/potential edges',
    'nodes': {
        'government': government_nodes,
        'private_capital': private_capital_nodes,
        'worldwidebro_entities': worldwidebro_nodes,
        'ventures': venture_nodes,
    },
    'edges': edges,
    'node_counts': {
        'government': len(government_nodes),
        'private_capital': len(private_capital_nodes),
        'worldwidebro_entities': len(worldwidebro_nodes),
        'ventures': len(venture_nodes),
        'total': len(government_nodes) + len(private_capital_nodes) + len(worldwidebro_nodes) + len(venture_nodes),
    },
    'edge_counts': {
        'total': len(edges),
        'ownership': len([e for e in edges if e.get('edge_type') == 'owns']),
        'controls': len([e for e in edges if e.get('edge_type') == 'controls']),
        'deploys_to': len([e for e in edges if e.get('edge_type') == 'deploys_to']),
        'references': len([e for e in edges if e.get('edge_type') == 'references']),
        'potential_awards': len([e for e in edges if e.get('status') == 'potential']),
    },
}

out_path = reg / 'registry' / 'capital-flow-graph-seed.yaml'
with open(out_path, 'w') as f:
    yaml.dump(seed_data, f, default_flow_style=False, sort_keys=False)

print(f"\nWrote seed to: {out_path}")
print(f"Total nodes: {seed_data['node_counts']['total']}")
print(f"Total edges: {seed_data['edge_counts']['total']}")
print(f"  Ownership edges: {seed_data['edge_counts']['ownership']}")
print(f"  Control edges: {seed_data['edge_counts']['controls']}")
print(f"  Vercel deploy edges: {seed_data['edge_counts']['deploys_to']}")
print(f"  Reference edges: {seed_data['edge_counts']['references']}")
print(f"  Potential award edges: {seed_data['edge_counts']['potential_awards']}")
print()
print("Seed complete.")
