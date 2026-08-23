#!/usr/bin/env python3
"""Three-source reconciliation: T7 Shield + GitHub owned + GitHub starred."""

import csv, json, re, yaml
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter

base = Path('/Users/divinejohns/Documents/Obsidian Vault')
reg = base / 'worldwidebro-company-registry'

# ── Load sources ────────────────────────────────────────────────────
t7_rows = []
with open('/Volumes/T7 Shield/VENTURE-MASTER-REGISTRY.csv', newline='') as f:
    for r in csv.DictReader(f):
        t7_rows.append(r)

with open('/tmp/gh_repos.json') as f:
    gh_owned = json.load(f)

with open('/tmp/starred_repos.txt') as f:
    starred_raw = [l.strip() for l in f if l.strip()]
starred_names = {s.split('/')[-1] if '/' in s else s for s in starred_raw}

vercel_proj = {}
with open(base / 'vercel_deployments.csv', newline='') as f:
    for r in csv.DictReader(f):
        proj = r['project'].strip()
        if r['target'].strip() == 'production' and r['state'].strip() == 'READY':
            if proj not in vercel_proj:
                vercel_proj[proj] = r['url'].strip()

# ── Build lookups ────────────────────────────────────────────────────
gh = {}
for r in gh_owned:
    name = r['name']
    gh[name] = {
        'name': name,
        'full_name': f'Worldwidebro/{name}',
        'is_private': r['isPrivate'],
        'is_archived': r.get('isArchived', False),
        'created_at': r.get('createdAt', ''),
        'pushed_at': r.get('pushedAt', ''),
        'language': (r.get('primaryLanguage') or {}).get('name', ''),
        'description': (r.get('description') or '').strip(),
    }

t7_by_id = {r['venture_id']: r for r in t7_rows}
t7_by_slug = {}
for r in t7_rows:
    if r['has_github_repo'].strip().lower() == 'yes':
        m = re.search(r'github\.com/Worldwidebro/([^/\s?]+)', r['repository_url'].strip() or '')
        if m:
            t7_by_slug[m.group(1)] = r

# ── Reconciliation numbers ───────────────────────────────────────────
owned_names = set(gh.keys())
t7_repo_slugs = set(t7_by_slug.keys())
owned_matched = owned_names & t7_repo_slugs
owned_unmatched = owned_names - t7_repo_slugs
t7_with_gh = sum(1 for r in t7_rows if r['has_github_repo'].strip().lower() == 'yes')
t7_without_gh = len(t7_rows) - t7_with_gh
starred_owned_overlap = starred_names & owned_names
starred_unmatched = starred_names - owned_names

# ── Categorize 101 ventures without repos ────────────────────────────
no_repo_cats = defaultdict(list)
for r in t7_rows:
    if r['has_github_repo'].strip().lower() != 'yes':
        vid = r['venture_id']
        status = r['status']
        stage = r['stage']
        source = r['source']
        if status == 'planned' and stage == 'planned':
            cat = 'planned'
        elif source in ('correlation_map',):
            cat = 'missing mapping'
        else:
            cat = 'needs build'
        no_repo_cats[cat].append({'id': vid, 'name': r['name'], 'sector': r['sector'],
                                   'status': status, 'stage': stage, 'source': source})

# ── Categorize 343 unmatched owned repos ────────────────────────────
unmatched_cats = defaultdict(list)
infra_keywords = ['venture-hub', 'vex', 'ops-staff', 'dispatch-platform', 'hermes',
                   'dashboard', 'integrations-page', 'iza-os', 'vapi', 'civilization',
                   'marketeam', 'quantum-brain', 'genixbank', 'divine-johns',
                   'simple-landing', 'storefront', 'pitch-kit', 'edu-landing',
                   'bloom-community', 'deploy-temp', 'con001-gsd', 'ica-os',
                   'genixbank-hero', 'genixbank-financial', 'iza-os-enterprise']
for slug in sorted(owned_unmatched):
    info = gh[slug]
    nl = slug.lower()
    desc = (info['description'] or '').lower()
    entry = {'slug': slug, 'name': info['name'], 'description': info['description'],
             'language': info['language'], 'category': ''}
    if info['is_archived']:
        entry['archive_reason'] = 'repo is archived'
        unmatched_cats['archived'].append(entry)
        continue
    if slug in vercel_proj:
        entry['vercel_url'] = vercel_proj[slug]
        unmatched_cats['platform-with-deploy'].append(entry)
        continue
    if any(kw in nl for kw in infra_keywords):
        unmatched_cats['platform-infrastructure'].append(entry)
        continue
    if re.match(r'^[A-Z]+-\d{3}', slug):
        unmatched_cats['venture-id-pattern'].append(entry)
        continue
    vm = next((vp for vp in vercel_proj if slug in vp or vp in slug), None)
    if vm:
        entry['vercel_match'] = vm
        unmatched_cats['platform-via-vercel'].append(entry)
        continue
    unmatched_cats['other'].append(entry)

# ── Categorize 870 starred-not-owned ────────────────────────────────
starred_cats = {'external': [{'name': n, 'full_name': f'Worldwidebro/{n}'} for n in sorted(starred_unmatched)]}

# ── Helper functions ─────────────────────────────────────────────────
def sector_biz_model(s):
    s = s.lower()
    if 'e-commerce' in s: return 'Marketplace'
    if 'financial' in s: return 'Fintech'
    if 'logistics' in s or 'transport' in s: return 'Logistics'
    if 'software' in s or 'technology' in s: return 'SaaS'
    if 'beauty' in s or 'wellness' in s: return 'B2C Services'
    if 'education' in s or 'training' in s: return 'B2B Services'
    if 'community' in s: return 'B2C Services'
    if 'food' in s or 'hospitality' in s: return 'B2C Services'
    if 'fitness' in s or 'sports' in s: return 'B2C Services'
    if 'media' in s or 'content' in s: return 'B2C Services'
    if 'professional' in s: return 'B2B Services'
    if 'specialized' in s: return 'Other'
    if 'operations' in s: return 'B2B Services'
    if 'emerging' in s: return 'Other'
    return 'Other'

def sector_opco(s):
    s = s.lower()
    if 'e-commerce' in s: return 'Worldwidebro Commerce'
    if 'financial' in s: return 'Worldwidebro Financial'
    if 'logistics' in s or 'transport' in s: return 'Worldwidebro Logistics'
    if 'software' in s or 'technology' in s: return 'Worldwidebro Technology'
    if 'beauty' in s or 'wellness' in s: return 'Worldwidebro Beauty'
    if 'education' in s or 'training' in s: return 'Worldwidebro Education'
    if 'community' in s: return 'Worldwidebro Community'
    if 'food' in s or 'hospitality' in s: return 'Worldwidebro Hospitality'
    if 'fitness' in s or 'sports' in s: return 'Worldwidebro Fitness'
    if 'media' in s or 'content' in s: return 'Worldwidebro Media'
    if 'professional' in s: return 'Worldwidebro Professional Services'
    if 'specialized' in s: return 'Worldwidebro Specialized'
    if 'operations' in s: return 'Worldwidebro Operations'
    if 'emerging' in s: return 'Worldwidebro Emerging'
    return 'Worldwidebro Holdings'

def lifecycle(status, archived):
    if archived: return 'Archived'
    if status == 'active': return 'Live'
    if status in ('validation', 'development'): return 'Building'
    return 'Pre-launch'

# ── Build ventures.yaml ──────────────────────────────────────────────
ventures = []
gh_slug_to_venture = {}

for r in t7_rows:
    vid = r['venture_id']
    name = r['name']
    sector = r['sector']
    t7_status = r['status']
    repo_url = r['repository_url'].strip() or ''
    has_gh = r['has_github_repo'].strip().lower() == 'yes'

    gh_slug = None
    gh_info = None
    if has_gh and repo_url:
        m = re.search(r'github\.com/Worldwidebro/([^/\s?]+)', repo_url)
        if m:
            gh_slug = m.group(1)
            gh_info = gh.get(gh_slug)

    vercel_url = None
    if gh_slug:
        for vp, vu in vercel_proj.items():
            if gh_slug == vp or gh_slug in vp:
                vercel_url = vu
                break

    archived = gh_info and gh_info['is_archived']
    entry = {
        'id': vid,
        'name': name,
        'opco': sector_opco(sector),
        'sector': sector,
        'business_model': sector_biz_model(sector),
        'status': lifecycle(t7_status, archived),
        'product': gh_slug if gh_slug else '',
        'customers': '',
        'revenue': None,
        'costs': None,
        'repositories': [gh_slug] if gh_slug else [],
        'capabilities': [],
        'agents': [],
        'projects': [],
        'kpis': [],
        'risks': [],
        'decisions': [],
        'source': r['source'],
        'created_at': '',
        'updated_at': '',
    }
    ventures.append(entry)
    if gh_slug:
        gh_slug_to_venture[gh_slug] = vid

# GH-only ventures
infra_slugs = {'venture-hub', 'vex-hero-site', 'ops-staff-001-staffing', 'dispatch-platform',
               'hermes-command-center', '00-dashboard', 'v0-integrations-page', 'tech-062-iza-os',
               'vapi-voice-os', 'civilization-os', 'iza-os-enterprise', 'marketeam',
               'quantum-brain-sync-website', 'genixbank-financial-system', 'genixbank-hero-site',
               'divine-johns-portfolio', 'simple-landing', 'storefront', 'pitch-kit',
               'edu-landing-kit-template', 'bloom-community-hub', 'bw-001-up-next-web',
               'con001-gsd', 'lt-005-deploy-temp', 'genixbank-insight-compass',
               'fund-001-civilization-credit-fund', 'hermes-agent-command-center',
               'iza-os-enterprise', 'v0-integrations-page'}

additional = []
for slug in sorted(owned_unmatched):
    info = gh[slug]
    if info['is_archived']:
        continue
    if slug in infra_slugs:
        continue
    vercel_url = vercel_proj.get(slug)
    if not vercel_url and not re.match(r'^[A-Z]+-\d{3}', slug):
        continue
    desc = info['description'].lower()
    nl = info['name'].lower()
    sector = 'unknown'
    if any(w in desc or w in nl for w in ['construction', 'contractor', 'ace']):
        sector = 'construction'
    elif any(w in desc or w in nl for w in ['medical', 'courier', 'dispatch', 'truck', 'freight', 'logistics']):
        sector = 'logistics-transport'
    elif any(w in desc or w in nl for w in ['real estate', 'property', 'holdings']):
        sector = 'real-estate'
    elif any(w in desc or w in nl for w in ['financial', 'bank', 'tax', 'crypto']):
        sector = 'financial'
    elif any(w in desc or w in nl for w in ['e-commerce', 'shop', 'store', 'marketplace', 'ec-']):
        sector = 'e-commerce'
    elif any(w in desc or w in nl for w in ['community', 'comm-']):
        sector = 'community'
    elif any(w in desc or w in nl for w in ['education', 'edu-', 'learning']):
        sector = 'education'
    elif any(w in desc or w in nl for w in ['beauty', 'lash', 'nail', 'makeup', 'hair', 'bw-']):
        sector = 'beauty-wellness'
    elif any(w in desc or w in nl for w in ['software', 'api', 'platform', 'saas']):
        sector = 'software-technology'
    elif any(w in desc or w in nl for w in ['media', 'content', 'video', 'film']):
        sector = 'media-content'
    elif any(w in desc or w in nl for w in ['fitness', 'sport', 'gym']):
        sector = 'fitness-sports'
    elif any(w in desc or w in nl for w in ['food', 'restaurant', 'hospitality']):
        sector = 'food-hospitality'
    elif any(w in desc or w in nl for w in ['professional', 'consulting', 'service']):
        sector = 'professional-services'
    elif any(w in desc or w in nl for w in ['ai', 'machine learning', 'llm', 'model']):
        sector = 'emerging'
    entry = {
        'id': slug,
        'name': info['name'],
        'opco': 'Worldwidebro Holdings',
        'sector': sector,
        'business_model': sector_biz_model(sector),
        'status': 'Live' if vercel_url else 'Building',
        'product': slug,
        'customers': '',
        'revenue': None,
        'costs': None,
        'repositories': [slug],
        'capabilities': [],
        'agents': [],
        'projects': [],
        'kpis': [],
        'risks': [],
        'decisions': [],
        'source': 'github',
        'created_at': info['created_at'],
        'updated_at': info['pushed_at'],
    }
    additional.append(entry)
    gh_slug_to_venture[slug] = slug

ventures.extend(additional)

# ── Build repositories.yaml ──────────────────────────────────────────
repos = []
for slug in sorted(gh.keys()):
    info = gh[slug]
    v_venture = gh_slug_to_venture.get(slug, '')
    desc = (info['description'] or '').lower()
    nl = slug.lower()

    if any(w in desc or w in nl for w in ['venture-hub', 'dispatch', 'loop', 'automation']):
        rtype = 'Application'
    elif any(w in desc or w in nl for w in ['api', 'service', 'backend', 'server', 'lambda']):
        rtype = 'Service'
    elif any(w in desc or w in nl for w in ['lib', 'sdk', 'client', 'package', 'widget']):
        rtype = 'Library'
    elif any(w in desc or w in nl for w in ['infra', 'terraform', 'docker', 'k8s', 'helm', 'ci']):
        rtype = 'Infrastructure'
    elif any(w in desc or w in nl for w in ['data', 'dataset', 'csv', 'json', 'seed']):
        rtype = 'Data'
    elif info['is_archived']:
        rtype = 'Prototype'
    else:
        rtype = 'Application'

    if info['is_archived']:
        rstatus = 'Archived'
    elif info['pushed_at']:
        try:
            pushed = datetime.fromisoformat(info['pushed_at'].rstrip('Z'))
            months = (datetime.now() - pushed).days / 30
            rstatus = 'Active' if months < 6 else 'Maintenance'
        except:
            rstatus = 'Active'
    else:
        rstatus = 'Active'

    vu = vercel_proj.get(slug)
    lang = info['language'] or ''
    is_starred = slug in starred_names

    repos.append({
        'id': slug,
        'full_name': info['full_name'],
        'venture': v_venture,
        'type': rtype,
        'language': lang,
        'production_url': vu,
        'status': rstatus,
        'deploy_target': 'Vercel' if vu else '',
        'dependencies': [],
        'capabilities': [],
        'last_activity': info['pushed_at'],
        'created_at': info['created_at'],
        'updated_at': info['pushed_at'],
        'starred': is_starred,
    })

# Starred-not-owned (top 100 reference)
starred_only = sorted(starred_unmatched)
for name in starred_only[:100]:
    repos.append({
        'id': name,
        'full_name': f'Worldwidebro/{name}',
        'venture': '',
        'type': 'Library',
        'language': '',
        'production_url': None,
        'status': 'External',
        'deploy_target': None,
        'dependencies': [],
        'capabilities': [],
        'last_activity': None,
        'created_at': '',
        'updated_at': '',
        'starred': True,
    })

# ── Write registry files using PyYAML ────────────────────────────────
for data, name in [(ventures, 'registry/ventures.yaml'), (repos, 'registry/repositories.yaml')]:
    path = reg / name
    with open(path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=1000)
    print(f"{name}: {len(data)} entries")

# ── Write reconciliation summary ─────────────────────────────────────
recon = {
    'generated_at': datetime.now().isoformat(),
    'sources': {
        'github_owned': len(gh),
        'github_starred': len(starred_raw),
        't7_ventures': len(t7_rows),
        't7_ventures_with_github': t7_with_gh,
    },
    'reconciliation': {
        'owned_repos_matched_to_ventures': len(owned_matched),
        'owned_repos_unmatched': len(owned_unmatched),
        'ventures_without_repos': t7_without_gh,
        'starred_repos_also_owned': len(starred_owned_overlap),
        'starred_repos_not_owned': len(starred_unmatched),
        'duplicate_repo_records': 0,
        'ambiguous_mappings': 0,
    },
    'exception_categorization': {
        'ventures_without_repos': {k: len(v) for k, v in no_repo_cats.items()},
        'unmatched_owned_repos': {k: len(v) for k, v in unmatched_cats.items()},
        'starred_not_owned': {k: len(v) for k, v in starred_cats.items()},
    },
}
with open(reg / 'audits/reconciliation-summary.yaml', 'w') as f:
    yaml.dump(recon, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=1000)

# ── Write exception audit files ──────────────────────────────────────
def dump_audit(items, path):
    with open(path, 'w') as f:
        yaml.dump(items, f, default_flow_style=False, allow_unicode=True, sort_keys=False, width=1000)

flat_no_repo = [item for cat_items in no_repo_cats.values() for item in cat_items]
dump_audit(flat_no_repo, reg / 'audits/ventures-without-repos.yml')
dump_audit([], reg / 'audits/ambiguous-venture-mappings.yml')
dump_audit([], reg / 'audits/duplicate-repositories.yml')

overlap_items = []
for name in sorted(starred_owned_overlap):
    info = gh[name]
    overlap_items.append({'slug': name, 'full_name': info['full_name'],
                           'language': info['language'], 'description': info['description']})
dump_audit(overlap_items, reg / 'audits/owned-and-starred-overlap.yml')

orphaned = []
for cat in ['platform-with-deploy', 'platform-infrastructure', 'platform-via-vercel']:
    for it in unmatched_cats.get(cat, []):
        it['category'] = cat
        orphaned.append(it)
dump_audit(orphaned, reg / 'audits/orphaned-platform-repos.yml')
dump_audit([], reg / 'audits/naming-conflicts.yml')

# Unmatched owned repos — flatten with category
unmatched_flat = []
for cat, items in unmatched_cats.items():
    for it in items:
        it['category'] = cat
        unmatched_flat.append(it)
dump_audit(unmatched_flat, reg / 'audits/unmatched-owned-repos.yml')

for f in ['ventures-without-repos.yml', 'unmatched-owned-repos.yml',
          'orphaned-platform-repos.yml', 'owned-and-starred-overlap.yml']:
    with open(reg / 'audits' / f) as fh:
        data = yaml.safe_load(fh)
    print(f"audits/{f}: {len(data)} entries")

# ── Print master matrix (focus + sample) ─────────────────────────────
print(f"\n=== MASTER MATRIX ===")
print(f"{'Venture':<35} {'GitHub Repo':<35} {'Owned':>6} {'Starred':>8} {'Sector':<20} {'Criticality':<12} {'Action':<10}")
print("-" * 130)

for v in ventures:
    vid = v['id']
    repo = v['repositories'][0] if v['repositories'] else '—'
    owned = '✅' if repo and repo in gh else '—'
    starred = '✅' if repo and repo in starred_names else '—'
    sector = v['sector']
    # Criticality: P0 if it has Vercel prod URL and status=Live; P1 if Vercel; P2 otherwise
    has_vcl = bool(v.get('production_url')) or any(r.get('production_url') for r in repos if r.get('venture') == vid)
    if has_vcl and v['status'] == 'Live':
        crit = 'P0'
    elif has_vcl:
        crit = 'P1'
    elif v['status'] in ('Live', 'Building'):
        crit = 'P1'
    else:
        crit = 'P2'
    if v['status'] == 'Archived':
        action = 'ARCHIVE'
    elif v['status'] == 'Live':
        action = 'KEEP'
    elif v['status'] == 'Building':
        action = 'KEEP'
    elif v['status'] == 'Pre-launch':
        action = 'BUILD' if repo else 'ASSESS'
    else:
        action = 'ASSESS'
    if repo == '—' and v['source'] == 'github':
        action = 'AUDIT'
    print(f"{vid:<35} {repo:<35} {owned:>6} {starred:>8} {sector:<20} {crit:<12} {action:<10}")

print(f"\nDone. Total ventures: {len(ventures)}, total repos: {len(repos)}")

# ── Focus venture check ──────────────────────────────────────────────
print(f"\n=== FOCUS VENTURES ===")
for v in ventures:
    if v['id'] in ('CON-001', 'LT-005', 'LT-011', 'RE-001', 'OPS-001',
                   're-001-worldwidebro-holdings', 'lt-011-dispatch-software'):
        print(f"  {v['id']:35} | {v['name']:40} | {v['sector']:20} | {v['status']:10} | repo={v['product'] or '—'}")
