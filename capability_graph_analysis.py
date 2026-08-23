#!/usr/bin/env python3
"""Runs every computable item from the '50 things you can do' list against
real registry data and writes a status (ANSWERED/PARTIAL/BLOCKED) for each.

This does not invent numbers for items the current data can't support —
those are marked BLOCKED with the specific missing data type named, per the
anti-fabrication rule this registry has followed since DEC-2026-0003.
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
repos = yaml.safe_load((ROOT / "registry" / "repositories.yaml").read_text())
ventures = yaml.safe_load((ROOT / "registry" / "ventures.yaml").read_text())
capabilities = yaml.safe_load((ROOT / "registry" / "capabilities.yaml").read_text())
platforms = yaml.safe_load((ROOT / "registry" / "platforms.yaml").read_text())
reconciliation = yaml.safe_load((ROOT / "audits" / "reconciliation-summary.yml").read_text())

owned = [r for r in repos if not r["starred"]]
starred = [r for r in repos if r["starred"]]
linked = [r for r in repos if r.get("venture")]

out = {}

# 1. Complete technology inventory
out["1_technology_inventory"] = {
    "total_repositories": len(repos),
    "owned": len(owned),
    "starred": len(starred),
    "by_language_owned": dict(Counter((r["language"] or "unknown") for r in owned).most_common(10)),
    "by_type": dict(Counter(r["type"] for r in repos)),
    "by_capability_category": {c["category"]: sum(len(cc["repositories"]) for cc in capabilities if cc["category"] == c["category"]) for c in [{"category": cat} for cat in {c["category"] for c in capabilities}]},
}

# 2. Venture-to-repository map
out["2_venture_to_repository_map"] = {
    "matched_pairs": len(linked),
    "source": "registry/repositories.yaml[].venture, reconciliation pipeline output",
}

# 3. Orphaned ventures (no repo)
nrr = reconciliation.get("ventures_without_repos", reconciliation.get("no_repo", {}))
out["3_orphaned_ventures"] = {
    "count": reconciliation.get("summary", {}).get("ventures_without_repos", "see audits/ventures-without-repos.yml"),
    "source": "audits/ventures-without-repos.yml",
}

# 4. Orphaned repositories (owned, no venture)
out["4_orphaned_repositories"] = {
    "owned_unmatched": sum(1 for r in owned if not r.get("venture")),
    "source": "audits/unmatched-owned-repos.yml (171 platform/utility, 116 archived, 56 unclassified)",
}

# 5. Duplicate ventures (name-similarity candidates, NOT confirmed dupes)
def norm_name(s: str) -> str:
    s = re.sub(r"^[A-Z]+-\d+-", "", s)  # strip sector-code prefix
    return re.sub(r"[-_]", " ", s).lower().strip()

venture_ids = [v["id"] if isinstance(v, dict) else v for v in (ventures or [])]
venture_norms = [(vid, norm_name(vid)) for vid in venture_ids]
dup_venture_candidates = []
seen = set()
for i, (id1, n1) in enumerate(venture_norms):
    if id1 in seen:
        continue
    cluster = [id1]
    for id2, n2 in venture_norms[i + 1:]:
        if id2 in seen:
            continue
        if SequenceMatcher(None, n1, n2).ratio() > 0.82:
            cluster.append(id2)
            seen.add(id2)
    if len(cluster) > 1:
        dup_venture_candidates.append(cluster)
        seen.add(id1)
out["5_duplicate_venture_candidates"] = {
    "method": "SequenceMatcher ratio > 0.82 on sector-prefix-stripped name — CANDIDATES for human review, not confirmed duplicates",
    "cluster_count": len(dup_venture_candidates),
    "clusters": dup_venture_candidates[:25],
}

# 6. Duplicate repositories (name-similarity candidates)
repo_names = [r["id"] for r in owned]
dup_repo_candidates = []
seen_r = set()
lower_map = defaultdict(list)
for name in repo_names:
    lower_map[name.lower()].append(name)
for lname, variants in lower_map.items():
    if len(variants) > 1:
        dup_repo_candidates.append(sorted(variants))
out["6_duplicate_repository_candidates"] = {
    "method": "exact case-insensitive name collisions among owned repos",
    "cluster_count": len(dup_repo_candidates),
    "clusters": dup_repo_candidates,
}

# 7. Missing / thin capabilities
cap_sorted = sorted(capabilities, key=lambda c: len(c["repositories"]))
out["7_thin_capabilities"] = {
    "method": "capabilities with fewest owned-repo matches — candidates for genuine gaps or taxonomy blind spots",
    "thinnest_5": [{"id": c["id"], "repo_count": len(c["repositories"])} for c in cap_sorted[:5]],
}

# 8/11/13. Reuse reach per repository (capability-overlap proxy, not confirmed technical reuse)
venture_by_capability = defaultdict(set)
for r in repos:
    if r.get("venture") and r.get("capabilities"):
        for c in r["capabilities"]:
            venture_by_capability[c].add(r["venture"])

repo_reach = []
for r in linked:
    if not r.get("capabilities"):
        continue
    reach_ventures = set()
    for c in r["capabilities"]:
        reach_ventures |= venture_by_capability[c]
    reach_ventures.discard(r["venture"])
    repo_reach.append((r["id"], r["venture"], len(reach_ventures)))
repo_reach.sort(key=lambda t: -t[2])
out["8_11_13_repository_reuse_reach"] = {
    "method": "For each repo, union of OTHER ventures whose own repos share >=1 of its capability tags. Proxy for 'if extracted as shared infra, how many ventures could plug in' — NOT confirmed code-level reuse (dependency graph is empty, see item 21).",
    "top_15": [{"repo": rid, "venture": v, "potential_venture_reach": n} for rid, v, n in repo_reach[:15]],
}

# 9/12. Rank capabilities by venture reach (compound-use, capability level)
cap_reach_ranked = sorted(
    ({"capability": c["id"], "category": c["category"], "owned_repos": len(c["repositories"]), "ventures_served": len(venture_by_capability.get(c["id"], set()))} for c in capabilities),
    key=lambda d: -d["ventures_served"],
)
out["9_12_capability_investment_ranking"] = cap_reach_ranked[:15]

# 16. Dominant capabilities per sector
sector_caps = defaultdict(Counter)
for r in linked:
    m = re.match(r"^([A-Z]+)-\d+", r["venture"])
    if not m or not r.get("capabilities"):
        continue
    sector = m.group(1)
    for c in r["capabilities"]:
        sector_caps[sector][c] += 1
out["16_dominant_capability_per_sector"] = {
    sector: counter.most_common(3) for sector, counter in sorted(sector_caps.items())
}

# 17/19. Infrastructure candidates for company-wide standardization
out["17_19_standardize_candidates"] = [
    {"capability": d["capability"], "ventures_served": d["ventures_served"], "owned_repos": d["owned_repos"]}
    for d in cap_reach_ranked if d["ventures_served"] >= 5
]

# 18. Engineering leverage ratio (ventures served per owned repo providing the capability)
leverage = sorted(
    ({"capability": d["capability"], "leverage_ratio": round(d["ventures_served"] / d["owned_repos"], 2) if d["owned_repos"] else None, **d} for d in cap_reach_ranked if d["owned_repos"]),
    key=lambda d: -(d["leverage_ratio"] or 0),
)
out["18_engineering_leverage_ratio"] = leverage[:10]

# 28. Platform candidates: type=Infrastructure repos with highest reuse reach
infra_reach = [t for t in repo_reach if next((r["type"] for r in repos if r["id"] == t[0]), None) == "Infrastructure"]
out["28_platform_candidates"] = [{"repo": rid, "venture": v, "potential_venture_reach": n} for rid, v, n in infra_reach[:10]]

# Explicitly blocked items — named, not silently skipped
out["BLOCKED_items"] = {
    "10_technology_roadmap": "Narrative synthesis, not a standalone computation — see written report, not this JSON.",
    "14_capabilities_per_repository": "Directly readable per-record from registry/repositories.yaml — not a portfolio-level aggregate, omitted here to avoid a 1767-row dump.",
    "15_consolidation_candidates": "Requires reading actual repo contents (step 2 audit), not just names/descriptions.",
    "20_prioritization_narrative": "Judgment call using items 17-19's data, not a separate computation.",
    "21_dependency_graph": "0/1767 repos have a populated 'dependencies' field — no source data exists yet (would require reading package.json/requirements.txt/go.mod per repo).",
    "22_installation_order": "Depends on item 21.",
    "23_optimal_stacks": "Partial via item 16 (per-sector dominant capabilities) — 'optimal' claim would overreach beyond what keyword tagging supports.",
    "24_incompatible_technologies": "Requires real technical audit (item 21 prerequisite).",
    "25_common_infra_dependencies": "Requires item 21.",
    "26_architectural_bottlenecks": "Requires item 21 + real usage/traffic data.",
    "27_single_points_of_failure": "Requires item 21 + production deployment topology data, which does not exist in this registry.",
    "29_library_package_candidates": "Speculative without code-level review; 'developer-tools' capability tag (29 repos) is the closest available proxy.",
    "30_venture_templates": "Narrative synthesis from item 16, not a standalone computation.",
    "31_40_agent_operations": "None of these are wired yet — no MCP tool or script currently exposes this registry to a live agent for query-time use. The data exists to support them; the query interface does not.",
    "41_50_business_monetization": "Requires real revenue/market/licensing data not present in this registry (GitHub metadata only). Can propose CANDIDATES from capability/venture-reach data but cannot compute real economic value, SaaS feasibility, or acquisition valuation.",
}

Path(ROOT / "audits" / "fifty-questions-analysis.json").write_text(json.dumps(out, indent=2, default=str))
print("Wrote audits/fifty-questions-analysis.json")
print()
for k in out:
    print("-", k)
