#!/usr/bin/env python3
"""
Compute default funding readiness for all ventures and write to registry.
Applies baseline scores derived from registry data (legal=100, banking=50, etc.)
Computes overall, funding_status, fundable_at, and funding_sources_eligible.
"""
import yaml, json
from pathlib import Path

reg = Path('/Users/divinejohns/Documents/Obsidian Vault/worldwidebro-company-registry')

with open(reg / 'registry/ventures.yaml') as f:
    ventures = yaml.safe_load(f)

# ── Default dimension scores (from funding-readiness-report.md) ──
DEFAULTS = {
    'legal': 100,
    'banking': 50,
    'accounting': 20,
    'credit': 10,
    'revenue': 10,
    'documentation': 80,
    'business_plan': 75,
    'collateral': 15,
    'investor_readiness': 30,
    'grant_readiness': 50,
    'sba_bank_readiness': 30,
    'alternative_funding': 35,
}

# ── Funding status thresholds ──
def funding_status(score):
    if score < 20: return 'NOT_FUNDABLE'
    if score < 40: return 'FUNDING_NOT_STARTED'
    if score < 60: return 'FUNDING_IN_PROGRESS'
    if score < 80: return 'FUNDING_READY_WITH_GAPS'
    if score < 95: return 'FUNDING_READY'
    return 'EXISTS_FUNDING'

# ── Fundable at thresholds ──
def fundable_at(score):
    return {
        'micro': score >= 40,
        'small': score >= 55,
        'medium': score >= 70,
        'large': score >= 80,
        'enterprise': score >= 90,
    }

# ── Funding sources eligible ──
def funding_sources(score):
    sources = []
    if score >= 40: sources.append('grants')
    if score >= 45: sources.append('business_credit_cards')
    if score >= 50: sources.append('microloans')
    if score >= 50: sources.append('crowdfunding')
    if score >= 55: sources.append('vendor_financing')
    if score >= 60: sources.append('invoice_factoring')
    if score >= 60: sources.append('government_contracts')
    if score >= 65: sources.append('po_financing')
    if score >= 70: sources.append('revenue_based_financing')
    if score >= 70: sources.append('angel_investment')
    if score >= 70: sources.append('bank_term_loan')
    if score >= 75: sources.append('sba_7a')
    if score >= 75: sources.append('strategic_investment')
    if score >= 80: sources.append('venture_capital')
    if score >= 80: sources.append('sba_504')
    if score >= 85: sources.append('private_equity')
    return sources

# ── Compute for all ventures ──
records = {}
for v in ventures:
    vid = v['id']
    dims = dict(DEFAULTS)
    
    # Adjust for Vercel deploy (banking likely higher)
    if v.get('_vercel_url'):
        dims['banking'] = max(dims['banking'], 70)
    
    # Adjust for Live status (revenue likely higher)
    if v.get('status') == 'Live':
        dims['revenue'] = max(dims['revenue'], 40)
        dims['banking'] = max(dims['banking'], 80)
        dims['business_plan'] = max(dims['business_plan'], 85)
    
    # Adjust for Building status (some traction)
    if v.get('status') == 'Building':
        dims['business_plan'] = max(dims['business_plan'], 80)
        dims['investor_readiness'] = max(dims['investor_readiness'], 40)
    
    # Adjust for grant-eligible sectors (community, nonprofit)
    sector = v.get('sector', '')
    if sector in ('community', 'beauty-wellness', 'education-training', 'food-hospitality'):
        dims['grant_readiness'] = max(dims['grant_readiness'], 65)
    
    overall = round(sum(dims.values()) / len(dims))
    
    records[vid] = {
        'venture_id': vid,
        'assessed_date': '2026-08-23',
        'assessor': 'default',
        'dimensions': dims,
        'overall': overall,
        'funding_status': funding_status(overall),
        'funding_gaps': [],
        'fundable_at': fundable_at(overall),
        'funding_sources_eligible': funding_sources(overall),
        'notes': '',
    }

# ── Write defaults YAML ──
out = reg / 'registry' / 'funding-readiness-defaults.yaml'
with open(out, 'w') as f:
    yaml.dump(records, f, default_flow_style=False, sort_keys=False)

print(f"Wrote {len(records)} funding readiness records to {out}")
print()

# ── Summary stats ──
from collections import Counter
status_dist = Counter(r['funding_status'] for r in records.values())
overall_dist = Counter()
for r in records.values():
    ov = r['overall']
    bucket = f"{ov//10*10}-{(ov//10+1)*10-1}"
    overall_dist[bucket] += 1

print("=== FUNDING READINESS — DEFAULT ASSESSMENT ===")
print(f"Total ventures: {len(records)}")
print()
print("Status distribution:")
for status in ['NOT_FUNDABLE', 'FUNDING_NOT_STARTED', 'FUNDING_IN_PROGRESS',
               'FUNDING_READY_WITH_GAPS', 'FUNDING_READY', 'EXISTS_FUNDING']:
    cnt = status_dist.get(status, 0)
    print(f"  {status:30} {cnt:4}")
print()
print("Overall score distribution:")
for bucket in sorted(overall_dist.keys()):
    print(f"  {bucket:6} → {(int(bucket.split('-')[0])+int(bucket.split('-')[1]))//2:3} avg    {overall_dist[bucket]:4} ventures")
print()
print("Fundable at levels:")
fundable_counts = {'micro': 0, 'small': 0, 'medium': 0, 'large': 0, 'enterprise': 0}
for r in records.values():
    for level in fundable_counts:
        if r['fundable_at'][level]:
            fundable_counts[level] += 1
for level, cnt in fundable_counts.items():
    label = {'micro': '<25K', 'small': '25K-100K', 'medium': '100K-500K', 'large': '500K-2M', 'enterprise': '2M+'}[level]
    print(f"  {level:10} ({label:12}) {cnt:4} ventures")
print()
print("Top funding sources eligible (by venture count):")
source_counts = Counter()
for r in records.values():
    for src in r['funding_sources_eligible']:
        source_counts[src] += 1
for src, cnt in source_counts.most_common(10):
    print(f"  {src:30} {cnt:4} ventures")
print()

# ── Which ventures are fundable today (overall ≥ 70)? ──
fundable_now = [(vid, r['overall'], r['funding_status']) for vid, r in records.items() if r['overall'] >= 70]
fundable_now.sort(key=lambda x: -x[1])
print(f"=== VENTURES FUNDABLE TODAY (overall ≥ 70): {len(fundable_now)} ===")
for vid, ov, status in fundable_now:
    dims = records[vid]['dimensions']
    print(f"  {vid:35} | {ov:3} | {status:30} | sources: {', '.join(records[vid]['funding_sources_eligible'])}")
print()

# ── Which ventures have the biggest gaps? ──
# Find ventures where key dimensions are low
print("=== TOP GAPS ACROSS ALL VENTURES ===")
gap_dims = ['credit', 'revenue', 'collateral', 'investor_readiness']
for dim in gap_dims:
    avg = sum(r['dimensions'][dim] for r in records.values()) / len(records)
    min_val = min(r['dimensions'][dim] for r in records.values())
    max_val = max(r['dimensions'][dim] for r in records.values())
    print(f"  {dim:25} avg={avg:.0f}  min={min_val}  max={max_val}")

print()
print("Done.")
