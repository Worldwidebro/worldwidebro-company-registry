#!/usr/bin/env python3
"""
Generate sample tasks for the Work OS task execution engine.
Creates 3 sample tasks:
1. SYSTEM-COMPLETE-CHECK — verify the full system is wired end-to-end (what we have)
2. LT-011-PROD-READY — verify LT-011 Dispatch Software production readiness
3. REPO-COUNT-VERIFY — verify registry repo counts
"""
import yaml
from pathlib import Path

BASE = Path('/Users/divinejohns/Documents/Obsidian Vault/worldwidebro-company-registry')
TASKS_DIR = BASE / 'work_os' / 'tasks'

def write_task(task_id, objective, owner, description, priority, sector_focus,
               inputs, dependencies, actions, acceptance_criteria, notes=None):
    task = {
        'id': task_id,
        'task_type': 'system-verification',
        'objective': objective,
        'owner': owner,
        'description': description,
        'priority': priority,
        'sector_focus': sector_focus,
        'inputs': inputs,
        'dependencies': dependencies,
        'actions': actions,
        'acceptance_criteria': acceptance_criteria,
    }
    if notes:
        task['notes'] = notes

    path = TASKS_DIR / f'{task_id}.yaml'
    with open(path, 'w') as f:
        yaml.dump(task, f, default_flow_style=False, sort_keys=False)
    return path

# ── TASK 1: SYSTEM-COMPLETE-CHECK ──
t1_actions = [
    {'type': 'check', 'check_type': 'yaml_parse',
     'path': str(BASE / 'registry/ventures.yaml'),
     'description': 'Parse ventures.yaml to verify 742 ventures load cleanly'},
    {'type': 'terminal', 'command': 'cd /Users/divinejohns/Documents/Obsidian\\ Vault/worldwidebro-company-registry && python3 -c "import yaml; v=yaml.safe_load(open(\'registry/ventures.yaml\')); print(f\'Ventures: {len(v)}\')"',
     'description': 'Count ventures in registry'},
    {'type': 'terminal', 'command': 'cd /Users/divinejohns/Documents/Obsidian\\ Vault/worldwidebro-company-registry && git log --oneline -5',
     'description': 'Show last 5 commits to verify push state'},
    {'type': 'check', 'check_type': 'file_exists',
     'path': str(BASE / 'schemas/funding-readiness.json'),
     'description': 'Verify funding-readiness.json schema exists'},
    {'type': 'check', 'check_type': 'file_exists',
     'path': str(BASE / 'schemas/capital-flow-node.json'),
     'description': 'Verify capital-flow-node.json schema exists'},
    {'type': 'check', 'check_type': 'file_exists',
     'path': str(BASE / 'schemas/capital-flow-edge.json'),
     'description': 'Verify capital-flow-edge.json schema exists'},
    {'type': 'check', 'check_type': 'file_exists',
     'path': str(BASE / 'schemas/business-taxonomy.json'),
     'description': 'Verify business-taxonomy.json schema exists'},
    {'type': 'check', 'check_type': 'file_exists',
     'path': str(BASE / 'registry/capital-flow-graph-seed.yaml'),
     'description': 'Verify capital-flow-graph-seed.yaml exists (759 nodes, 2711 edges)'},
    {'type': 'check', 'check_type': 'file_exists',
     'path': str(BASE / 'registry/funding-readiness-defaults.yaml'),
     'description': 'Verify funding-readiness-defaults.yaml exists (742 venture defaults)'},
    {'type': 'check', 'check_type': 'file_exists',
     'path': str(BASE / 'audits/financial-analysis.md'),
     'description': 'Verify financial-analysis.md exists'},
    {'type': 'check', 'check_type': 'file_exists',
     'path': str(BASE / 'audits/capital-flow-graph-report.md'),
     'description': 'Verify capital-flow-graph-report.md exists'},
    {'type': 'check', 'check_type': 'file_exists',
     'path': str(BASE / 'audits/funding-readiness-report.md'),
     'description': 'Verify funding-readiness-report.md exists'},
    {'type': 'check', 'check_type': 'file_exists',
     'path': str(BASE / 'audits/starred-analysis/STARRED-CAPABILITY-ANALYSIS.md'),
     'description': 'Verify starred capability analysis exists'},
    {'type': 'check', 'check_type': 'file_exists',
     'path': str(BASE / 'audits/owned-repo-capability/OWNED-REPO-CAPABILITY-ANALYSIS.md'),
     'description': 'Verify owned repo capability analysis exists'},
    {'type': 'terminal', 'command': 'cd /Users/divinejohns/Documents/Obsidian\\ Vault/worldwidebro-company-registry && python3 -c "import yaml; s=yaml.safe_load(open(\'registry/capital-flow-graph-seed.yaml\')); print(f\'Nodes: {s[\"node_counts\"][\"total\"]}, Edges: {s[\"edge_counts\"][\"total\"]}\')"',
     'description': 'Verify capital flow graph seed has 759 nodes and 2711 edges'},
    {'type': 'terminal', 'command': 'cd /Users/divinejohns/Documents/Obsidian\\ Vault/worldwidebro-company-registry && python3 -c "import yaml; s=yaml.safe_load(open(\'registry/capital-flow-graph-seed.yaml\')); sectors=set(n.get(\'sector\',\'?\') for n in s[\'nodes\'][\'ventures\']); print(f\'Unique sectors in seed: {len(sectors)}\'); [print(f\'  {s}\') for s in sorted(sectors)]"',
     'description': 'Verify sectors in seed are consolidated to 14'},
    {'type': 'check', 'check_type': 'file_exists',
     'path': str(BASE / 'work_os/task_runner.py'),
     'description': 'Verify Work OS task runner exists'},
    {'type': 'check', 'check_type': 'file_exists',
     'path': str(BASE / 'work_os/task-schema.json'),
     'description': 'Verify Work OS task schema exists'},
    {'type': 'terminal', 'command': 'cd /Users/divinejohns/Documents/Obsidian\\ Vault/worldwidebro-company-registry && gh repo view Worldwidebro/worldwidebro-company-registry --json name,description,visibility,updatedAt --jq \'.[].name + " | " + .[].description + " | " + .[].visibility + " | " + .[].updatedAt\'',
     'description': 'Verify GitHub repo is visible and pushed'},
]

t1_criteria = [
    'ventures.yaml contains 742 ventures and parses cleanly',
    'last 5 commits show pushed state on main',
    'all 5 schema files exist (funding-readiness, capital-flow-node, capital-flow-edge, business-taxonomy, task-schema)',
    'capital-flow-graph-seed.yaml exists with 759 nodes',
    'funding-readiness-defaults.yaml exists with 742 venture assessments',
    'financial-analysis.md exists',
    'capital-flow-graph-report.md exists',
    'funding-readiness-report.md exists',
    'starred capability analysis exists',
    'owned repo capability analysis exists',
    'work os task runner exists',
    'work os task schema exists',
    'GitHub repo is visible and pushed with recent commit',
]

write_task(
    'SYSTEM-COMPLETE-CHECK',
    'Verify the Worldwidebro registry system is complete and wired end-to-end',
    'Hermes Agent',
    'Comprehensive system verification: registry counts, schemas, seed data, audit reports, capability analyses, GitHub state, Work OS, sector consolidation. This task confirms the system is in a coherent, committed, and accessible state.',
    'P0',
    'all sectors',
    [
        'registry/ventures.yaml (742 ventures)',
        'registry/capital-flow-graph-seed.yaml (759 nodes, 2711 edges)',
        'registry/funding-readiness-defaults.yaml (742 venture assessments)',
        'schemas/ (5 schema files)',
        'audits/ (7 audit reports)',
        'work_os/ (task runner + schema)',
        'github.com/Worldwidebro/worldwidebro-company-registry',
    ],
    ['registry access', 'gh auth'],
    t1_actions,
    t1_criteria,
    notes='This task should PASS if the system is fully wired. If any criterion fails, that\'s the gap to close.'
)

# ── TASK 2: LT-011-PROD-READY ──
t2_actions = [
    {'type': 'check', 'check_type': 'yaml_parse',
     'path': str(BASE / 'registry/ventures.yaml'),
     'description': 'Find LT-011 in ventures.yaml'},
    {'type': 'terminal', 'command': 'cd /Users/divinejohns/Documents/Obsidian\\ Vault/worldwidebro-company-registry && python3 -c "import yaml; v=yaml.safe_load(open(\'registry/ventures.yaml\')); lt=[x for x in v if x[\'id\'].startswith(\'LT-011\')]; print(yaml.dump(lt[0] if lt else {\'not_found\': True}))"',
     'description': 'Extract LT-011 venture record'},
    {'type': 'check', 'check_type': 'file_exists',
     'path': str(BASE / 'vercel_deployments.csv'),
     'description': 'Verify vercel_deployments.csv exists'},
    {'type': 'terminal', 'command': 'cd /Users/divinejohns/Documents/Obsidian\\ Vault && grep "LT-011\|lt-011\|dispatch-software" vercel_deployments.csv 2>/dev/null | head -5',
     'description': 'Find LT-011 Vercel deployments'},
    {'type': 'check', 'check_type': 'file_exists',
     'path': str(BASE / 'registry/repositories.yaml'),
     'description': 'Verify repositories.yaml exists'},
    {'type': 'terminal', 'command': 'cd /Users/divinejohns/Documents/Obsidian\\ Vault/worldwidebro-company-registry && python3 -c "import yaml; r=yaml.safe_load(open(\'registry/repositories.yaml\')); lt=[x for x in r if \'lt-011\' in x[\'full_name\'].lower() or \'lt_011\' in x[\'full_name\'].lower()]; print(yaml.dump(lt[0] if lt else {\'not_found\': True}))"',
     'description': 'Find LT-011 repository record'},
    {'type': 'terminal', 'command': 'cd /Users/divinejohns/Documents/Obsidian\\ Vault/worldwidebro-company-registry && gh repo view Worldwidebro/lt-011-dispatch-software --json name,description,visibility,verified,stargazersCount,language,primaryLanguage,updatedAt,pushedAt,createdAt --jq \'[.name, .description, .visibility, .language, .primaryLanguage.name, .stargazersCount, .updatedAt, .pushedAt]\'',
     'description': 'Check LT-011 GitHub repo status via gh CLI'},
    {'type': 'terminal', 'command': 'cd /Users/divinejohns/Documents/Obsidian\\ Vault/worldwidebro-company-registry && gh api repos/Worldwidebro/lt-011-dispatch-software --jq \'.[owner.login, name, description, stargazers_count, forks_count, open_issues_count, has_issues, has_downloads, has_wiki, homepage, language, allows_forking, is_template, visibility]\'',
     'description': 'Get detailed LT-011 repo metadata from GitHub API'},
    {'type': 'terminal', 'command': 'cd /Users/divinejohns/Documents/Obsidian\\ Vault/worldwidebro-company-registry && gh api user/starred --paginate -q \'.[].full_name\' 2>/dev/null | grep -i "lt-011\|dispatch-software" | head -5',
     'description': 'Check if LT-011 is in Worldwidebro starred repos'},
    {'type': 'terminal', 'command': 'cd /Users/divinejohns/Documents/Obsidian\\ Vault/worldwidebro-company-registry && python3 -c "import yaml; s=yaml.safe_load(open(\'registry/capital-flow-graph-seed.yaml\')); lt=[n for n in s[\'nodes\'][\'ventures\'] if n[\'venture_registry_id\'].startswith(\'LT-011\')]; print(yaml.dump(lt[0] if lt else {\'not_found\': True}))"',
     'description': 'Check LT-011 in capital flow graph seed'},
    {'type': 'terminal', 'command': 'cd /Users/divinejohns/Documents/Obsidian\\ Vault/worldwidebro-company-registry && python3 -c "import yaml; f=yaml.safe_load(open(\'registry/funding-readiness-defaults.yaml\')); lt=[x for x in f if x[\'venture_id\'].startswith(\'LT-011\')]; print(yaml.dump(lt[0] if lt else {\'not_found\': True}))"',
     'description': 'Check LT-011 funding readiness'},
    {'type': 'check', 'check_type': 'file_exists',
     'path': str(BASE / 'schemas/business-taxonomy.json'),
     'description': 'Verify business taxonomy schema exists'},
    {'type': 'terminal', 'command': 'cd /Users/divinejohns/Documents/Obsidian\\ Vault/worldwidebro-company-registry && python3 -c "import json; t=json.load(open(\'schemas/business-taxonomy.json\')); log=[s for s in t[\'macro_sectors\'] if s[\'id\']==\'logistics-transport\']; print(f\'Logistics subsectors: {len(log[0][\'subsectors\'])}\'); [print(f\'  {s}\') for s in log[0][\'subsectors\']]"',
     'description': 'Verify logistics-transport subsectors available in taxonomy'},
]

t2_criteria = [
    'LT-011 exists in ventures.yaml with sector, status, and Vercel URL',
    'LT-011 has a Vercel production URL in the registry',
    'LT-011 repository exists on GitHub under Worldwidebro/',
    'LT-011 funding readiness is computed in funding-readiness-defaults.yaml',
    'LT-011 has a node in the capital flow graph seed',
    'business taxonomy has logistics-transport subsectors available',
    'LT-011 repo is accessible via gh CLI',
]

write_task(
    'LT-011-PROD-READY',
    'Verify LT-011 Dispatch Software is production-ready: repo exists, deployed, funded, in registry',
    'Hermes Agent',
    'LT-011 Dispatch Software is a P2 logistics-venture in Pre-launch/Building status. This task verifies every layer: registry entry, GitHub repo, Vercel deployment, capital flow graph node, funding readiness, and taxonomy coverage. Answers: is LT-011 ready to go live?',
    'P2',
    'logistics-transport',
    [
        'registry/ventures.yaml',
        'registry/repositories.yaml',
        'vercel_deployments.csv',
        'registry/capital-flow-graph-seed.yaml',
        'registry/funding-readiness-defaults.yaml',
        'schemas/business-taxonomy.json',
        'GitHub: Worldwidebro/lt-011-dispatch-software',
    ],
    ['registry access', 'gh auth', 'Vercel deploy status'],
    t2_actions,
    t2_criteria,
    notes='LT-011 is a P2 venture. If Vercel URL exists and repo is live, it\'s production-ready from a deployment standpoint. Funding readiness and capital flow graph integration show if it\'s ready from a funding standpoint.'
)

# ── TASK 3: REPO-COUNT-VERIFY ──
t3_actions = [
    {'type': 'check', 'check_type': 'yaml_parse',
     'path': str(BASE / 'registry/repositories.yaml'),
     'description': 'Parse repositories.yaml to verify 990 repos load cleanly'},
    {'type': 'terminal', 'command': 'cd /Users/divinejohns/Documents/Obsidian\\ Vault/worldwidebro-company-registry && python3 -c "import yaml; r=yaml.safe_load(open(\'registry/repositories.yaml\')); print(f\'Repos: {len(r)}\')"',
     'description': 'Count repos in registry'},
    {'type': 'terminal', 'command': 'cd /Users/divinejohns/Documents/Obsidian\\ Vault/worldwidebro-company-registry && python3 -c "import yaml; from collections import Counter; r=yaml.safe_load(open(\'registry/repositories.yaml\')); types=Counter(x.get(\'type\',\'?\') for x in r); print(f\'Types:\'); [print(f\'  {t:20} {c:4}\') for t,c in sorted(types.items(), key=lambda x:-x[1])]"',
     'description': 'Show repo type distribution'},
    {'type': 'terminal', 'command': 'cd /Users/divinejohns/Documents/Obsidian\\ Vault/worldwidebro-company-registry && python3 -c "import yaml; from collections import Counter; r=yaml.safe_load(open(\'registry/repositories.yaml\')); langs=Counter(x.get(\'language\',\'?\') for x in r); print(f\'Languages:\'); [print(f\'  {l:20} {c:4}\') for l,c in sorted(langs.items(), key=lambda x:-x[1]) if l != \'?\']"',
     'description': 'Show repo language distribution'},
    {'type': 'terminal', 'command': 'cd /Users/divinejohns/Documents/Obsidian\\ Vault/worldwidebro-company-registry && python3 -c "import yaml; from collections import Counter; r=yaml.safe_load(open(\'registry/repositories.yaml\')); vercel=Counter(bool(x.get(\'production_url\')) for x in r); print(f\'With Vercel: {vercel[True]}, Without: {vercel[False]}\')"',
     'description': 'Count repos with Vercel production URLs'},
    {'type': 'terminal', 'command': 'cd /Users/divinejohns/Documents/Obsidian\\ Vault/worldwidebro-company-registry && python3 -c "import yaml; from collections import Counter; r=yaml.safe_load(open(\'registry/repositories.yaml\')); arch=Counter(x.get(\'status\',\'?\') for x in r); print(f\'Status:\'); [print(f\'  {s:10} {c:4}\') for s,c in sorted(arch.items(), key=lambda x:-x[1])]"',
     'description': 'Show repo status distribution (active/archived/private/public)'},
    {'type': 'terminal', 'command': 'cd /Users/divinejohns/Documents/Obsidian\\ Vault/worldwidebro-company-registry && gh repo list Worldwidebro --limit 100 --json name,isPrivate,isArchived --jq \'[.[] | {name: .name, isPrivate: .isPrivate, isArchived: .isArchived}] | length\'',
     'description': 'Verify GitHub owned repo count from gh CLI'},
    {'type': 'terminal', 'command': 'cd /Users/divinejohns/Documents/Obsidian\\ Vault/worldwidebro-company-registry && gh repo list Worldwidebro --limit 1000 --json name,isArchived --jq \'.[] | select(.isArchived) | .name\' | wc -l',
     'description': 'Count archived repos from GitHub'},
    {'type': 'check', 'check_type': 'file_exists',
     'path': str(BASE / 'audits/owned-repo-capability/OWNED-REPO-CAPABILITY-ANALYSIS.md'),
     'description': 'Verify owned repo capability analysis exists'},
    {'type': 'terminal', 'command': 'cd /Users/divinejohns/Documents/Obsidian\\ Vault/worldwidebro-company-registry && python3 -c "import yaml; s=yaml.safe_load(open(\'registry/capital-flow-graph-seed.yaml\')); print(f\'Seed nodes: {s[\"node_counts\"][\"total\"]}, Seed edges: {s[\"edge_counts\"][\"total\"]}\')"',
     'description': 'Verify capital flow graph seed is intact'},
]

t3_criteria = [
    'repositories.yaml contains 990 repos and parses cleanly',
    'Repo type distribution shows DevOps/Infrastructure (~297), Frontend/UI (~159), Venture Studio (~146)',
    'Repo language distribution populated for at least 346 repos',
    '73 repos have Vercel production URLs',
    'GitHub owned repo count from gh CLI ≈ 890',
    'Owned repo capability analysis exists',
    'Capital flow graph seed has 759 nodes and 2711 edges',
]

write_task(
    'REPO-COUNT-VERIFY',
    'Verify all 990 owned repos are accounted for in the registry with correct counts, types, and Vercel URLs',
    'Hermes Agent',
    'Repository count verification: 890 GitHub owned repos, 990 in registry (890 + 100 starred-ext reference), 73 with Vercel URLs, 116 archived, type/language distributions. Confirms the repository registry is complete and accurate.',
    'P1',
    'all sectors',
    [
        'registry/repositories.yaml (990 repos)',
        'gh CLI authenticated as Worldwidebro',
        'audits/owned-repo-capability/',
    ],
    ['registry access', 'gh auth'],
    t3_actions,
    t3_criteria,
    notes='This task confirms the repository registry matches GitHub reality. If counts diverge, investigate: new repos pushed since last reconciliation, repos deleted, or registry corruption.'
)

# ── Write all tasks ──
print(f"Created 3 sample tasks in {TASKS_DIR}:")
for task_id in ['SYSTEM-COMPLETE-CHECK', 'LT-011-PROD-READY', 'REPO-COUNT-VERIFY']:
    path = TASKS_DIR / f'{task_id}.yaml'
    print(f"  {path}")
print(f"\nRun with: python3 work_os/task_runner.py --task {TASKS_DIR / 'SYSTEM-COMPLETE-CHECK.yaml'}")
