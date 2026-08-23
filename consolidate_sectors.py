#!/usr/bin/env python3
"""
Consolidate sectors in the capital flow graph seed from 19 → 13.

Mapping:

EDUCATION + EDUCATION-TRAINING       → EDUCATION
TECHNOLOGY + SOFTWARE-TECHNOLOGY     → TECHNOLOGY
CONSTRUCTION                         → OPERATIONS
REAL-ESTATE                         → FINANCIAL
UNKNOWN                              → fix to best-guess sector

BEAUTY-WELLNESS + FITNESS-SPORTS     → BEAUTY-WELLNESS  (option A: 13 sectors)
  OR keep separate                   → FITNESS-SPORTS     (option B: 14 sectors)

Outputs updated: registry/capital-flow-graph-seed.yaml (sector field in venture nodes)
"""
import yaml, json
from pathlib import Path

reg = Path('/Users/divinejohns/Documents/Obsidian Vault/worldwidebro-company-registry')

# Load seed
with open(reg / 'registry/capital-flow-graph-seed.yaml') as f:
    seed = yaml.safe_load(f)

# Sector consolidation map
sector_map = {
    'education': 'education',
    'education-training': 'education',
    'technology': 'technology',
    'software-technology': 'technology',
    'construction': 'operations',
    'real-estate': 'financial',
    'unknown': 'operations',  # best-guess for the 1 unknown; should be fixed at source
    'fitness-sports': 'fitness-sports',  # OPTION B: keep separate (14 sectors)
    # For OPTION A (13 sectors): change to:
    # 'fitness-sports': 'beauty-wellness',  # merge into beauty-wellness
}

# Count old sectors
old_sector_counts = {}
for node in seed['nodes']['ventures']:
    old_sector = node.get('sector', '?')
    old_sector_counts[old_sector] = old_sector_counts.get(old_sector, 0) + 1

print("=== PRE-CONSOLIDATION SECTORS ===")
for s, c in sorted(old_sector_counts.items(), key=lambda x: -x[1]):
    print(f"  {s:30} {c:4}")
print(f"  Total: {sum(old_sector_counts.values())}")
print()

# Apply consolidation
for node in seed['nodes']['ventures']:
    old_sector = node.get('sector', '?')
    new_sector = sector_map.get(old_sector, old_sector)
    node['sector'] = new_sector

# Count new sectors
new_sector_counts = {}
for node in seed['nodes']['ventures']:
    new_sector = node.get('sector', '?')
    new_sector_counts[new_sector] = new_sector_counts.get(new_sector, 0) + 1

print("=== POST-CONSOLIDATION SECTORS ===")
for s, c in sorted(new_sector_counts.items(), key=lambda x: -x[1]):
    print(f"  {s:30} {c:4}")
print(f"  Total sectors: {len(new_sector_counts)}")
print(f"  Total ventures: {sum(new_sector_counts.values())}")
print()

# Update seed metadata
seed['sector_consolidation'] = {
    'from_count': len(old_sector_counts),
    'to_count': len(new_sector_counts),
    'mapping': sector_map,
    'option': 'A' if sector_map.get('fitness-sports') == 'beauty-wellness' else 'B',
    'pre_consolidation': dict(sorted(old_sector_counts.items(), key=lambda x: -x[1])),
    'post_consolidation': dict(sorted(new_sector_counts.items(), key=lambda x: -x[1])),
}

# Write updated seed
out_path = reg / 'registry' / 'capital-flow-graph-seed.yaml'
with open(out_path, 'w') as f:
    yaml.dump(seed, f, default_flow_style=False, sort_keys=False)

print(f"Updated seed written to: {out_path}")
print(f"Sectors consolidated: {len(old_sector_counts)} → {len(new_sector_counts)}")
print(f"Option: {seed['sector_consolidation']['option']} ({'13 sectors' if seed['sector_consolidation']['option'] == 'A' else '14 sectors'})")
