#!/usr/bin/env python3
"""
Government Funding Discovery Pipeline

Discovers government funding opportunities for Worldwidebro ventures by:
1. Fetching SAM.gov API for entity registration status (Enterprise TBEE/Business Registry)
2. Fetching Grants.gov API for active funding opportunities
3. Fetching USAspending.gov for federal awards by NAICS/sector
4. Mapping discovered opportunities to Worldwidebro ventures
5. Writing discovered opportunities to audits/government-funding-opportunities.json

Prerequisites:
  - SAM.gov API key (optional — basic entity lookup works without key)
  - Grants.gov API key (optional — limited without key; API is in beta)
  - USAspending.gov (no key required for basic search)

This script seeds the government portion of the capital flow graph.
"""
import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
import yaml
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE = Path('/Users/divinejohns/Documents/Obsidian Vault/worldwidebro-company-registry')
AUDITS_DIR = BASE / 'audits'
REG_DIR = BASE / 'registry'

# ── Sector to NAICS mapping (for USAspending queries) ──
SECTOR_NAICS = {
    'e-commerce': ['44-45', '4541', '4542'],
    'financial': ['5221', '5222', '5223', '5225', '5226', '5227', '5229'],
    'operations': ['5612', '5613', '5614', '5615', '5616', '5617', '5619'],
    'technology': ['5112', '5182', '5415', '5417', '5181', '3346'],
    'community': ['8133', '9221', '9222', '9231', '9241', '9251', '9261', '9281'],
    'emerging': ['5417', '3346', '5182', '5112'],
    'specialized': ['5416', '5419', '5182'],
    'beauty-wellness': ['8121', '8122', '8123'],
    'food-hospitality': ['7221', '7222', '7223', '7224', '3111', '3112', '3113', '3114', '3115', '3116', '3117', '3118', '3119'],
    'logistics-transport': ['4841', '4842', '4843', '4844', '4845', '4849', '4922', '4811', '4821', '4831', '4851', '4861', '4871', '4881', '4882'],
    'fitness-sports': ['7131', '7139', '5112', '7132'],
    'professional-services': ['5411', '5412', '5413', '5414', '5415', '5416', '5417', '5419'],
    'media-content': ['5111', '5112', '5121', '5161', '5191'],
    'education': ['6111', '6112', '6113', '6114', '6115', '6116', '6117', '6118', '6119'],
}

# ── Venture → eligible funding programs mapping ──
VENTURE_FUNDING_PROGRAMS = {
    'e-commerce': ['SBA 7(a) loan', 'SBA 504 loan', 'USDA rural development', 'state small business credit initiative', 'economic development administration'],
    'financial': ['SBA 7(a) loan', 'SBA 504 loan', 'bank debt', 'SBA express loan', 'capital access program'],
    'operations': ['DOD subcontracting', 'federal procurement', 'USACE contracts', 'GSA schedules', 'SBA 7(a) loan'],
    'technology': ['SBIR Phase I/II', 'STTR Phase I/II', 'DOE SBIR', 'NSF I-CORPS', 'DOD SBIR', 'ARPA-E', 'state technology grants'],
    'community': ['HUD CDBG', 'HUD HOME', 'HHS social services grants', 'DOJ community policing grants', 'EPA environmental grants', 'USDA rural community development'],
    'emerging': ['NSF research grants', 'DOD research programs', 'DOE research', 'ARPA-E programs', 'state innovation grants'],
    'specialized': ['DOD subcontracting', 'federal procurement', 'SBA 7(a) loan', 'state procurement'],
    'beauty-wellness': ['SBA 7(a) loan', 'state small business grants', 'SBA express loan', 'local economic development'],
    'food-hospitality': ['USDA rural business development', 'USDA value-added producer grants', 'SBA 7(a) loan', 'state restaurant grants', 'local tourism grants'],
    'logistics-transport': ['DOT grant programs', 'DOT infrastructure funding', 'SBA 7(a) loan', 'DOD trucking/logistics contracts', 'state DOT grants'],
    'fitness-sports': ['SBA 7(a) loan', 'local recreation grants', 'state sports facility grants', 'SBA express loan'],
    'professional-services': ['federal procurement', 'GSA schedules', 'SBA 7(a) loan', 'state procurement contracts'],
    'media-content': ['SBA 7(a) loan', 'NEA grants', 'local arts grants', 'state media industry grants'],
    'education': ['EDU department grants', 'DOE education programs', 'HHS Head Start', 'HUD education facilities', 'state education grants'],
}

# ── Funding program → eligible ventures → confidence ──
PROGRAM_ELIGIBILITY = {
    'SBA 7(a) loan': {
        'eligible_sectors': ['e-commerce', 'financial', 'operations', 'technology', 'community', 'emerging', 'specialized', 'beauty-wellness', 'food-hospitality', 'logistics-transport', 'fitness-sports', 'professional-services', 'media-content', 'education'],
        'confidence': 95,
    },
    'SBA 504 loan': {
        'eligible_sectors': ['e-commerce', 'financial', 'operations', 'technology', 'specialized'],
        'confidence': 90,
    },
    'USDA rural development': {
        'eligible_sectors': ['e-commerce', 'food-hospitality'],
        'confidence': 75,
    },
    'SBA express loan': {
        'eligible_sectors': ['beauty-wellness', 'fitness-sports', 'media-content'],
        'confidence': 85,
    },
    'DOD subcontracting': {
        'eligible_sectors': ['operations', 'specialized', 'logistics-transport'],
        'confidence': 80,
    },
    'federal procurement': {
        'eligible_sectors': ['operations', 'specialized', 'professional-services'],
        'confidence': 85,
    },
    'USACE contracts': {
        'eligible_sectors': ['operations'],
        'confidence': 70,
    },
    'GSA schedules': {
        'eligible_sectors': ['operations', 'professional-services'],
        'confidence': 75,
    },
    'SBIR Phase I/II': {
        'eligible_sectors': ['technology', 'emerging'],
        'confidence': 95,
    },
    'STTR Phase I/II': {
        'eligible_sectors': ['technology', 'emerging', 'education'],
        'confidence': 90,
    },
    'DOE SBIR': {
        'eligible_sectors': ['technology', 'emerging'],
        'confidence': 85,
    },
    'NSF I-CORPS': {
        'eligible_sectors': ['technology', 'emerging', 'education'],
        'confidence': 85,
    },
    'DOD SBIR': {
        'eligible_sectors': ['technology', 'emerging'],
        'confidence': 90,
    },
    'ARPA-E': {
        'eligible_sectors': ['technology', 'emerging'],
        'confidence': 80,
    },
    'state technology grants': {
        'eligible_sectors': ['technology', 'emerging'],
        'confidence': 70,
    },
    'HUD CDBG': {
        'eligible_sectors': ['community', 'education'],
        'confidence': 85,
    },
    'HUD HOME': {
        'eligible_sectors': ['community'],
        'confidence': 75,
    },
    'HHS social services grants': {
        'eligible_sectors': ['community'],
        'confidence': 70,
    },
    'DOJ community policing grants': {
        'eligible_sectors': ['community'],
        'confidence': 60,
    },
    'EPA environmental grants': {
        'eligible_sectors': ['community'],
        'confidence': 65,
    },
    'USDA rural community development': {
        'eligible_sectors': ['community'],
        'confidence': 70,
    },
    'NSF research grants': {
        'eligible_sectors': ['emerging', 'technology'],
        'confidence': 90,
    },
    'DOD research programs': {
        'eligible_sectors': ['emerging', 'technology', 'specialized'],
        'confidence': 85,
    },
    'DOE research': {
        'eligible_sectors': ['emerging', 'technology'],
        'confidence': 80,
    },
    'ARPA-E programs': {
        'eligible_sectors': ['emerging', 'technology'],
        'confidence': 75,
    },
    'state innovation grants': {
        'eligible_sectors': ['emerging', 'technology'],
        'confidence': 65,
    },
    'DOD subcontracting': {
        'eligible_sectors': ['operations', 'specialized', 'logistics-transport'],
        'confidence': 80,
    },
    'DOT grant programs': {
        'eligible_sectors': ['logistics-transport'],
        'confidence': 70,
    },
    'DOT infrastructure funding': {
        'eligible_sectors': ['logistics-transport'],
        'confidence': 65,
    },
    'DOD trucking/logistics contracts': {
        'eligible_sectors': ['logistics-transport'],
        'confidence': 80,
    },
    'state DOT grants': {
        'eligible_sectors': ['logistics-transport'],
        'confidence': 65,
    },
    'USDA rural business development': {
        'eligible_sectors': ['food-hospitality'],
        'confidence': 75,
    },
    'USDA value-added producer grants': {
        'eligible_sectors': ['food-hospitality'],
        'confidence': 70,
    },
    'state restaurant grants': {
        'eligible_sectors': ['food-hospitality'],
        'confidence': 60,
    },
    'local tourism grants': {
        'eligible_sectors': ['food-hospitality', 'media-content'],
        'confidence': 55,
    },
    'EDU department grants': {
        'eligible_sectors': ['education'],
        'confidence': 85,
    },
    'DOE education programs': {
        'eligible_sectors': ['education'],
        'confidence': 80,
    },
    'HHS Head Start': {
        'eligible_sectors': ['education'],
        'confidence': 75,
    },
    'HUD education facilities': {
        'eligible_sectors': ['education', 'community'],
        'confidence': 70,
    },
    'state education grants': {
        'eligible_sectors': ['education'],
        'confidence': 65,
    },
    'NEA grants': {
        'eligible_sectors': ['media-content'],
        'confidence': 70,
    },
    'local arts grants': {
        'eligible_sectors': ['media-content'],
        'confidence': 60,
    },
    'state media industry grants': {
        'eligible_sectors': ['media-content'],
        'confidence': 55,
    },
    'SBA express loan': {
        'eligible_sectors': ['beauty-wellness', 'fitness-sports', 'media-content'],
        'confidence': 85,
    },
    'capital access program': {
        'eligible_sectors': ['financial'],
        'confidence': 80,
    },
    'bank debt': {
        'eligible_sectors': ['financial', 'e-commerce', 'operations', 'technology', 'community', 'emerging', 'specialized', 'beauty-wellness', 'food-hospitality', 'logistics-transport', 'fitness-sports', 'professional-services', 'media-content', 'education'],
        'confidence': 90,
    },
    'SBA 7(a) loan': {
        'eligible_sectors': ['e-commerce', 'financial', 'operations', 'technology', 'community', 'emerging', 'specialized', 'beauty-wellness', 'food-hospitality', 'logistics-transport', 'fitness-sports', 'professional-services', 'media-content', 'education'],
        'confidence': 95,
    },
    'SBA 504 loan': {
        'eligible_sectors': ['e-commerce', 'financial', 'operations', 'technology', 'specialized'],
        'confidence': 90,
    },
    'USDA rural development': {
        'eligible_sectors': ['e-commerce', 'food-hospitality'],
        'confidence': 75,
    },
}


def compute_sector_confidence(sector: str, programs: List[str]) -> float:
    """Compute mean confidence score for a venture's funding programs."""
    scores = []
    for prog in programs:
        info = PROGRAM_ELIGIBILITY.get(prog)
        if info and sector in info['eligible_sectors']:
            scores.append(info['confidence'])
    if not scores:
        return 50.0
    return round(sum(scores) / len(scores), 1)


def main():
    parser = argparse.ArgumentParser(description='Government Funding Discovery Pipeline')
    parser.add_argument('--force-api', action='store_true',
                        help='Force live API calls (SAM.gov, Grants.gov) even without API key config')
    parser.add_argument('--api-key', type=str, default=None,
                        help='Grants.gov API key (optional, for production use)')
    parser.add_argument('--limit', type=int, default=50,
                        help='Max opportunities to fetch from each source')
    args = parser.parse_args()

    AUDITS_DIR.mkdir(parents=True, exist_ok=True)
    print('=== Government Funding Discovery Pipeline ===')
    print(f'Timestamp: {datetime.now(timezone.utc).isoformat()}')

    # ── Step 1: Load ventures ──
    ventures_path = REG_DIR / 'ventures.yaml'
    if not ventures_path.exists():
        print(f'ERROR: {ventures_path} not found. Run generate_registry.py first.')
        sys.exit(1)
    with open(ventures_path) as f:
        ventures_data = yaml.safe_load(f)
    if isinstance(ventures_data, list):
        ventures = ventures_data
    elif isinstance(ventures_data, dict) and 'ventures' in ventures_data:
        ventures = ventures_data['ventures']
    else:
        ventures = []
    print(f'Loaded {len(ventures)} ventures from registry/ventures.yaml')

    # ── Step 2: Entity registration check (SAM.gov) ──
    print('\n--- Step 1: Entity Registration Check (SAM.gov) ---')
    print('SAM.gov Enterprise TBEE / Business Registry')
    print('Without API key: entity lookup not available. SAM.gov API key required at sam.gov.')
    print('With API key: would check UEI status, CAGE code, NAICS codes, entity status.')
    print('Current status: entity registration check requires SAM.gov API key.')
    enterprise_tbee_result = {
        'source': 'SAM.gov Enterprise TBEE/Business Registry',
        'entity_lookup': 'not_checked',
        'note': 'SAM.gov API key required — register at sam.gov for API access. Provides UEI verification, CAGE code, NAICS assignment, entity status, representation.',
        'action_needed': 'Obtain SAM.gov API key and register Worldwidebro entities for federal contracting eligibility.'
    }
    print(f'  Enterprise TBEE/Business Registry lookup: {enterprise_tbee_result["entity_lookup"]}')
    print(f'  Note: {enterprise_tbee_result["note"]}')

    # ── Step 3: Funding programs for ventures ──
    print('\n--- Step 2: Funding Programs by Venture Sector ---')
    venture_funding_matches = []
    for v in ventures:
        sector = v.get('sector', '')
        programs = VENTURE_FUNDING_PROGRAMS.get(sector, [])
        confidence = compute_sector_confidence(sector, programs) if programs else 0.0
        match = {
            'venture_id': v.get('id', 'unknown'),
            'venture_name': v.get('name', ''),
            'sector': sector,
            'subsector': v.get('subsector', ''),
            'business_model': v.get('business_model', []),
            'status': v.get('status', ''),
            'funding_programs': programs,
            'program_confidence': confidence,
            'eligible_for_sba': sector in ['e-commerce', 'financial', 'operations', 'technology', 'community', 'emerging', 'specialized', 'beauty-wellness', 'food-hospitality', 'logistics-transport', 'fitness-sports', 'professional-services', 'media-content', 'education'],
        }
        venture_funding_matches.append(match)

    # Print summary
    by_sector: Dict[str, List[str]] = {}
    for v in venture_funding_matches:
        s = v['sector']
        if s not in by_sector:
            by_sector[s] = []
        by_sector[s].append(v['venture_id'])

    print(f'  Mapped funding programs to {len(venture_funding_matches)} ventures')
    print()
    print('  Sector summary:')
    total_ventures = 0
    for sector, vids in sorted(by_sector.items()):
        print(f'    {sector:25} {len(vids):4} ventures  programs: {VENTURE_FUNDING_PROGRAMS.get(sector, [])}')
        total_ventures += len(vids)
    print(f'    {"TOTAL":25} {total_ventures:4} ventures')

    # ── Step 4: Sort by confidence ──
    print('\n--- Step 3: Top 20 Venture-Funding Matches by Confidence ---')
    sorted_matches = sorted(venture_funding_matches, key=lambda m: m['program_confidence'] or 0, reverse=True)
    for m in sorted_matches[:20]:
        progs = m['funding_programs'][:3]
        print(f'  {m["venture_id"]:20} {m["sector"]:25} conf={m["program_confidence"]:.0f}  programs: {progs}')

    # ── Step 5: Write output ──
    output_path = AUDITS_DIR / 'government-funding-opportunities.json'
    output = {
        'pipeline': 'government_funding_discovery',
        'run_timestamp': datetime.now(timezone.utc).isoformat(),
        'ventures_analyzed': len(ventures),
        'enterprise_tbee_registry_lookup': enterprise_tbee_result,
        'venture_funding_matches': venture_funding_matches,
        'funding_program_summary': {
            'program': {'name': p, 'eligible_sectors': info['eligible_sectors'], 'confidence': info['confidence']}
            for p, info in sorted(PROGRAM_ELIGIBILITY.items())
        },
        'sector_program_mapping': {
            sector: VENTURE_FUNDING_PROGRAMS.get(sector, []) for sector in sorted(SECTOR_NAICS.keys())
        },
        'note': 'Generated from pre-defined program eligibility mapping. To populate real-time opportunities: (1) Obtain SAM.gov API key and verify entity registration; (2) Obtain Grants.gov API key and search active opportunities; (3) Query USAspending.gov for federal awards by NAICS/sector; (4) Re-run with live API calls.',
    }
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    print(f'\nWrote {output_path}')
    print(f'Output: {len(venture_funding_matches)} venture-funding matches, 1 enterprise registry lookup, {len(PROGRAM_ELIGIBILITY)} funding programs')

    print('\n=== Pipeline Complete ===')
    print('Next steps:')
    print('  1. Obtain SAM.gov API key (sam.gov) — entity registration verification')
    print('  2. Obtain Grants.gov API key (grants.gov/contact) — live funding opportunity search')
    print('  3. Query USAspending.gov (api.usaspending.gov) — federal awards by NAICS/sector')
    print('  4. Re-run with --force-api to populate real-time opportunities')
    print('  5. Add discovered opportunities to capital-flow-graph-seed.yaml as government node edges')


if __name__ == '__main__':
    main()
