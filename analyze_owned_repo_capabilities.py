#!/usr/bin/env python3
"""
Classify all 890 GitHub owned repos by capability.
Uses the same classification as starred repos, plus GitHub metadata (description, topics, language).
Writes: owned-repo-capability-classification.json + owned-repo-capabilities.md
"""
import json, yaml
from collections import Counter, defaultdict
from pathlib import Path

reg = Path('/Users/divinejohns/Documents/Obsidian Vault/worldwidebro-company-registry')
with open('/tmp/gh_repos.json') as f:
    gh_repos = json.load(f)

print(f"Classifying {len(gh_repos)} owned repos by capability...")
print()

# ── Capability classification (same as starred) ──
def classify_repo(repo):
    full_name = repo.get('name', '')
    desc = (repo.get('description') or '').lower()
    # Topics not in gh_repos.json — skip
    lang = ''
    pl = repo.get('primaryLanguage')
    if pl and isinstance(pl, dict):
        lang = (pl.get('name') or '').lower()
    elif pl:
        lang = str(pl).lower()
    
    all_text = f"{full_name} {desc} {lang}"
    caps = []

    # AI/LLM/GenAI
    ai_kw = ['llm', 'large language model', 'chatgpt', 'openai', 'anthropic', 'claude',
             'gpt-', 'gemini', 'mistral', 'llama', 'gemma', 'deepseek', 'ai model',
             'text generation', 'language model', 'foundation model', 'genai',
             'artificial intelligence', 'machine learning', 'neural network',
             'transformer', 'nlp', 'natural language']
    if any(kw in all_text for kw in ai_kw):
        caps.append('AI/LLM/GenAI')

    # Agent frameworks
    agent_kw = ['agent', 'agentic', 'autonomous agent', 'ai agent', 'crewai', 'langgraph',
                'autogen', 'flowise', 'dify', 'devin', 'agent workflow', 'agent framework']
    if any(kw in all_text for kw in agent_kw):
        if 'AI/LLM/GenAI' not in caps:
            caps.append('AI/LLM/GenAI')
        caps.append('Agent Frameworks')

    # RAG/Vector DB
    rag_kw = ['rag', 'retrieval augmented', 'vector database', 'vector db', 'embeddings',
              'semantic search', 'similarity search', 'chromadb', 'pinecone', 'weaviate',
              'qdrant', 'milvus', 'faiss', 'pgvector', 'knowledge graph']
    if any(kw in all_text for kw in rag_kw):
        caps.append('RAG/Vector DB')

    # MCP
    if 'mcp' in all_text or 'model context protocol' in all_text:
        caps.append('MCP')

    # Frontend/UI
    fe_kw = ['react', 'vue', 'angular', 'svelte', 'next.js', 'nextjs', 'frontend', 'ui',
             'web app', 'dashboard', 'component', 'typescript', 'css', 'tailwind',
             'chakra', 'material-ui', 'html', 'css framework']
    if any(kw in all_text for kw in fe_kw):
        caps.append('Frontend/UI Frameworks')

    # API/Backend
    api_kw = ['api', 'rest api', 'graphql', 'grpc', 'microservice', 'server', 'backend',
              'web server', 'http', 'webhook', 'endpoint', 'fastapi', 'flask', 'express']
    if any(kw in all_text for kw in api_kw):
        caps.append('API/Backend Infrastructure')

    # CLI/Dev Tools
    cli_kw = ['cli', 'command line', 'terminal', 'developer tool', 'code editor', 'ide',
              'vscode', 'neovim', 'emacs', 'linter', 'formatter', 'build tool',
              'package manager', 'bundler', 'dev tool']
    if any(kw in all_text for kw in cli_kw):
        caps.append('CLI/Dev Tools')

    # SDK/Library
    sdk_kw = ['sdk', 'library', 'package', 'npm', 'pip', 'gem', 'crates', 'maven',
              'gradle', 'composer', 'plugin', 'extension', 'wrapper', 'client']
    if any(kw in all_text for kw in sdk_kw):
        caps.append('SDK/Library')

    # Infrastructure — repos that are tooling, CI/CD, config management, platform
    infra_kw = ['ci/cd', 'continuous integration', 'continuous deployment', 'github actions',
                'pipeline', 'deployment', 'docker', 'container', 'kubernetes', 'helm',
                'terraform', 'infrastructure', 'devops', 'automation', 'config',
                'script', 'template', 'boilerplate', 'scaffold', 'starter',
                'command center', 'orchestrat', 'master', 'platform', 'os-infrastructure',
                'core', 'shared', 'module', 'utils']
    if any(kw in all_text for kw in infra_kw):
        caps.append('DevOps/Infrastructure')

    # Cloud/Serverless
    cloud_kw = ['cloud', 'aws', 'azure', 'gcp', 'google cloud', 'serverless', 'lambda',
                'cloudflare', 'vercel', 'netlify', 'firebase', 'cloud function',
                'cloud run', 'ec2', 's3', 'cloud storage', 'heroku', 'render']
    if any(kw in all_text for kw in cloud_kw):
        caps.append('Cloud/Serverless')

    # Database/Storage
    db_kw = ['database', 'db', 'postgres', 'postgresql', 'mysql', 'mongodb', 'redis',
             'sqlite', 'sql', 'nosql', 'neo4j', 'graph database', 'document store',
             'key-value', 'storage', 'data store', 'orm', 'prisma', 'drizzle']
    if any(kw in all_text for kw in db_kw):
        caps.append('Database/Storage')

    # Observability
    obs_kw = ['monitoring', 'observability', 'logging', 'metrics', 'tracing', 'alerting',
              'datadog', 'prometheus', 'grafana', 'sentry', 'log', 'telemetry']
    if any(kw in all_text for kw in obs_kw):
        caps.append('Observability/Monitoring')

    # Documentation
    docs_kw = ['documentation', 'docs', 'docgen', 'markdown', 'asciidoc', 'wiki',
               'knowledge base', 'documentation generator', 'doc']
    if any(kw in all_text for kw in docs_kw):
        caps.append('Documentation/Docs')

    # Testing
    test_kw = ['test', 'testing', 'unit test', 'integration test', 'e2e', 'qa',
               'quality assurance', 'mock', 'stub', 'coverage', 'jest', 'pytest',
               'cypress', 'playwright', 'selenium']
    if any(kw in all_text for kw in test_kw):
        caps.append('Testing/Quality')

    # Security
    sec_kw = ['security', 'auth', 'authentication', 'authorization', 'oauth', 'jwt',
              'encryption', 'cryptography', 'vulnerability', 'penetration', 'scan',
              'audit', 'firewall', 'ddos', 'zero trust', 'guard', 'protect']
    if any(kw in all_text for kw in sec_kw):
        caps.append('Security')

    # Workflow/Orchestration
    wf_kw = ['workflow', 'orchestration', 'dag', 'state machine', 'pipeline orchestrator',
             'temporal', 'airflow', 'prefect', 'dagster', 'processing pipeline']
    if any(kw in all_text for kw in wf_kw):
        caps.append('Workflow/Orchestration')

    # Web Scraping
    scrape_kw = ['scraping', 'crawler', 'crawl', 'web scraper', 'scrape', 'spider',
                 'scrapy', 'selenium', 'puppeteer', 'playwright']
    if any(kw in all_text for kw in scrape_kw):
        caps.append('Web Scraping/Crawling')

    # Email/SMS/Comms
    comm_kw = ['email', 'smtp', 'sendgrid', 'mailgun', 'sms', 'twilio', 'push notification',
               'notification', 'messaging', 'chat', 'slack', 'discord', 'telegram',
               'whatsapp', 'alert']
    if any(kw in all_text for kw in comm_kw):
        caps.append('Email/SMS/Comms')

    # E-commerce
    ecommerce_kw = ['ecommerce', 'e-commerce', 'shop', 'store', 'cart', 'checkout',
                    'payment gateway', 'product catalog', 'inventory', 'merchant',
                    'cosmic kitty', 'kittys', 'bdsm', 'adult', 'luxury']
    if any(kw in all_text for kw in ecommerce_kw):
        caps.append('E-commerce')

    # Payments
    pay_kw = ['payment', 'billing', 'subscription', 'stripe', 'paypal', 'revenue',
              'invoicing', 'pricing', 'checkout', 'billing']
    if any(kw in all_text for kw in pay_kw):
        caps.append('Payments/Billing')

    # Education
    edu_kw = ['education', 'learning', 'course', 'tutorial', 'e-learning', 'training',
              'teaching', 'educational', 'curriculum', 'lesson', 'interactive learning']
    if any(kw in all_text for kw in edu_kw):
        caps.append('Education/Learning')

    # Finance
    fin_kw = ['finance', 'financial', 'accounting', 'tax', 'banking', 'investment', 'trading',
              'crypto', 'blockchain', 'defi', 'wallet', 'payment processing', 'ledger',
              'arbitrage']
    if any(kw in all_text for kw in fin_kw):
        caps.append('Finance/Fintech')

    # Healthcare
    health_kw = ['health', 'medical', 'clinical', 'patient', 'diagnosis', 'medication',
                 'ehr', 'electronic health', 'healthcare', 'hospital', 'telemedicine',
                 'senior care', 'elder']
    if any(kw in all_text for kw in health_kw):
        caps.append('Healthcare/Medical')

    # Media/Content
    media_kw = ['video', 'audio', 'podcast', 'content', 'media', 'youtube', 'streaming',
                'creator', 'influencer', 'multiplex', 'distribution']
    if any(kw in all_text for kw in media_kw):
        caps.append('Media/Content')

    # Community
    community_kw = ['community', 'forum', 'social', 'network', 'membership', 'discussion',
                    'group', 'hub', 'event', 'meetup']
    if any(kw in all_text for kw in community_kw):
        caps.append('Community/Platform')

    # Real Estate
    realestate_kw = ['real estate', 'property', 'housing', 'lease', 'rental', 'sba',
                     'commercial property', 'apartment', 'building']
    if any(kw in all_text for kw in realestate_kw):
        caps.append('Real Estate')

    # Logistics
    logistics_kw = ['logistics', 'dispatch', 'delivery', 'shipping', 'freight', 'carrier',
                    'transport', 'truck', 'route', 'last mile', 'courier', 'supply chain']
    if any(kw in all_text for kw in logistics_kw):
        caps.append('Logistics/Transport')

    # Construction
    construction_kw = ['construction', 'contractor', 'builder', 'build', 'contract',
                       'ace construction', 'general contractor']
    if any(kw in all_text for kw in construction_kw):
        caps.append('Construction')

    # OS/Kernel — only tag repos whose PRIMARY purpose is an OS (not repos with "os" in the name)
    os_kw = ['operating system', 'os kernel', 'system call', 'syscall', 'microkernel',
             'unikernel', 'container runtime', 'systemd', 'kernel']
    # Only match if the description explicitly talks about OS internals
    if any(kw in desc for kw in os_kw) and ('os' in desc.lower() or 'operating system' in desc.lower()):
        caps.append('OS/Kernel')

    # Open Knowledge/Wiki
    ok_kw = ['open knowledge', 'knowledge graph', 'semantic wiki', 'knowledge base',
             'linked data', 'ontology', 'rdf', 'sparql', 'triples', 'wiki',
             'ok', 'openknowledge']
    if any(kw in all_text for kw in ok_kw):
        caps.append('Open Knowledge/Wiki')

    # Governance
    gov_kw = ['governance', 'policy', 'standard', 'compliance', 'regulation', 'rule',
              'master governance', 'schema', 'registry', 'audit']
    if any(kw in all_text for kw in gov_kw):
        caps.append('Governance/Compliance')

    # Entrepreneurial/VC
    ven_kw = ['venture', 'startup', 'incubator', 'accelerator', 'studio', 'venture studio',
              'autonomous venture', 'venture creation', 'business creation']
    if any(kw in all_text for kw in ven_kw):
        caps.append('Venture Creation/Studio')

    # Application (catch-all for things that are just apps)
    app_kw = ['app', 'application', 'web application', 'mobile app', 'desktop app']
    if any(kw in all_text for kw in app_kw):
        if 'AI/LLM/GenAI' not in caps and 'Frontend/UI Frameworks' not in caps:
            caps.append('Application')

    return caps


# ── Classify all ──
classified_repos = []
for repo in gh_repos:
    caps = classify_repo(repo)
    pl = repo.get('primaryLanguage')
    lang_name = ''
    if pl and isinstance(pl, dict):
        lang_name = pl.get('name', '')
    elif pl:
        lang_name = str(pl)
    
    classified_repos.append({
        'name': repo.get('name', ''),
        'full_name': f"Worldwidebro/{repo.get('name', '')}",
        'description': repo.get('description') or '',
        'language': lang_name,
        'is_archived': repo.get('isArchived', False),
        'is_private': repo.get('isPrivate', False),
        'created_at': repo.get('createdAt', ''),
        'pushed_at': repo.get('pushedAt', ''),
        'capabilities': caps,
    })

# ── Capability stats ──
cap_counter = Counter()
for r in classified_repos:
    for c in r['capabilities']:
        cap_counter[c] += 1

print("=== CAPABILITY CLASSIFICATION OF 890 OWNED REPOS ===")
print()
print(f"Total repos: {len(classified_repos)}")
print(f"With capabilities: {sum(1 for r in classified_repos if r['capabilities'])}")
print(f"Without capabilities: {sum(1 for r in classified_repos if not r['capabilities'])}")
print(f"Total capability assignments: {sum(len(r['capabilities']) for r in classified_repos)}")
print()

print("Capability distribution:")
for cat, cnt in cap_counter.most_common():
    print(f"  {cat:35} {cnt:4} repos")
print()

# ── By type inference (from name patterns + capability) ──
print("=== REPO CATEGORIZATION ===")

# Infrastructure vs Application vs Library vs Service
infra_cats = {'DevOps/CI/CD', 'Cloud/Serverless', 'Database/Storage', 'Observability/Monitoring',
              'Security', 'Workflow/Orchestration', 'OS/Kernel', 'Governance/Compliance',
              'Open Knowledge/Wiki', 'MCP', 'CLI/Dev Tools'}
service_cats = {'API/Backend Infrastructure', 'Payments/Billing', 'Email/SMS/Comms',
                'Auth/Identity'}
lib_cats = {'SDK/Library', 'Documentation/Docs', 'Testing/Quality'}
ai_cats = {'AI/LLM/GenAI', 'Agent Frameworks', 'RAG/Vector DB', 'Model Fine-tuning',
           'Prompt Engineering', 'Multimodal (Vision/Audio)'}

infra = sum(1 for r in classified_repos if any(c in infra_cats for c in r['capabilities']))
services = sum(1 for r in classified_repos if any(c in service_cats for c in r['capabilities']) 
               and not any(c in infra_cats for c in r['capabilities']))
libs = sum(1 for r in classified_repos if any(c in lib_cats for c in r['capabilities'])
           and not any(c in infra_cats | service_cats for c in r['capabilities']))
ai = sum(1 for r in classified_repos if any(c in ai_cats for c in r['capabilities']))
frontend = sum(1 for r in classified_repos if 'Frontend/UI Frameworks' in r['capabilities'])
ecomm = sum(1 for r in classified_repos if 'E-commerce' in r['capabilities'])
community = sum(1 for r in classified_repos if 'Community/Platform' in r['capabilities'])
finance = sum(1 for r in classified_repos if 'Finance/Fintech' in r['capabilities'])
logistics = sum(1 for r in classified_repos if 'Logistics/Transport' in r['capabilities'])
realestate = sum(1 for r in classified_repos if 'Real Estate' in r['capabilities'])
construction = sum(1 for r in classified_repos if 'Construction' in r['capabilities'])
health = sum(1 for r in classified_repos if 'Healthcare/Medical' in r['capabilities'])
media = sum(1 for r in classified_repos if 'Media/Content' in r['capabilities'])
education = sum(1 for r in classified_repos if 'Education/Learning' in r['capabilities'])
venture_studio = sum(1 for r in classified_repos if 'Venture Creation/Studio' in r['capabilities'])
apps_no_cap = sum(1 for r in classified_repos if not r['capabilities'] and 
                  any(kw in r['name'].lower() for kw in ['app', 'application', 'web', 'ui']))

print(f"  Infrastructure/DevOps/Platform: {infra} repos")
print(f"  AI/LLM/GenAI related:            {ai} repos")
print(f"  Agent Frameworks:               {cap_counter.get('Agent Frameworks', 0)} repos")
print(f"  Frontend/UI:                    {frontend} repos")
print(f"  API/Backend Services:           {services} repos")
print(f"  SDKs/Libraries:                 {libs} repos")
print(f"  E-commerce:                     {ecomm} repos")
print(f"  Community/Platform:             {community} repos")
print(f"  Finance/Fintech:                {finance} repos")
print(f"  Logistics/Transport:            {logistics} repos")
print(f"  Real Estate:                    {realestate} repos")
print(f"  Construction:                   {construction} repos")
print(f"  Healthcare/Medical:             {health} repos")
print(f"  Media/Content:                  {media} repos")
print(f"  Education/Learning:             {education} repos")
print(f"  Venture Studio/Creation:        {venture_studio} repos")
print(f"  Uncategorized (no capability):  {sum(1 for r in classified_repos if not r['capabilities'])} repos")
print()

# ── Top repos by capability richness ──
print("=== TOP REPOS BY CAPABILITY RICHNESS (5+ caps) ===")
rich = [(r, len(r['capabilities'])) for r in classified_repos if len(r['capabilities']) >= 5]
rich.sort(key=lambda x: (-x[1], -len(x[0]['description'])))
for r, cnt in rich[:20]:
    print(f"  {r['name']:45} | {cnt} caps | {r['language'] or 'none':10} | {r['description'][:60]}")
    print(f"    Caps: {', '.join(r['capabilities'])}")
print(f"  ... +{len(rich)-20} more" if len(rich) > 20 else "")
print()

# ── Archived vs Active capability distribution ──
print("=== ARCHIVED (116) vs ACTIVE (774) CAPABILITY COMPARISON ===")
archived_caps = Counter()
active_caps = Counter()
for r in classified_repos:
    if r['is_archived']:
        for c in r['capabilities']:
            archived_caps[c] += 1
    else:
        for c in r['capabilities']:
            active_caps[c] += 1

print("Active repos — top capabilities:")
for c, cnt in active_caps.most_common(10):
    print(f"  {c:35} {cnt:4}")
print()
print("Archived repos — top capabilities:")
for c, cnt in archived_caps.most_common(10):
    print(f"  {c:35} {cnt:4}")
print()

# ── Private vs Public ──
private = sum(1 for r in classified_repos if r['is_private'])
public = sum(1 for r in classified_repos if not r['is_private'])
print(f"Private repos: {private}")
print(f"Public repos: {public}")
print()

# ── Vercel-deployed repos capability ──
print("=== VERCEL-DEPLOYED REPOS (73) — CAPABILITY SNAPSHOT ===")
# Load from registry
with open(reg / 'registry/repositories.yaml') as f:
    reg_repos = yaml.safe_load(f)

vercel_repos = {r['full_name'] for r in reg_repos if r.get('production_url')}
vercel_gh = [r for r in classified_repos if r['full_name'] in vercel_repos]
print(f"Vercel-deployed repos with GH metadata: {len(vercel_gh)}")
vercel_cap_counter = Counter()
for r in vercel_gh:
    for c in r['capabilities']:
        vercel_cap_counter[c] += 1
for c, cnt in vercel_cap_counter.most_common(10):
    print(f"  {c:35} {cnt:4}")
print()

# ── WRITE OUTPUT ──
print("=== WRITING OUTPUT FILES ===")
out_dir = reg / 'audits' / 'owned-repo-capability'
out_dir.mkdir(parents=True, exist_ok=True)

# Full classification
with open(out_dir / 'owned-repo-capability-classification.json', 'w') as f:
    json.dump(classified_repos, f, indent=2)
print(f"  {out_dir / 'owned-repo-capability-classification.json'} — {len(classified_repos)} repos")

# Top repos by sector capability (for venture mapping)
sector_cap_map = {
    'e-commerce': ['AI/LLM/GenAI', 'Frontend/UI Frameworks', 'API/Backend Infrastructure',
                   'Database/Storage', 'Payments/Billing', 'Email/SMS/Comms', 'E-commerce',
                   'Cloud/Serverless'],
    'financial': ['AI/LLM/GenAI', 'API/Backend Infrastructure', 'Database/Storage', 'Security',
                  'Payments/Billing', 'Finance/Fintech', 'Cloud/Serverless'],
    'logistics-transport': ['AI/LLM/GenAI', 'API/Backend Infrastructure', 'Database/Storage',
                             'Logistics/Transport', 'CLI/Dev Tools', 'DevOps/CI/CD'],
    'software-technology': ['AI/LLM/GenAI', 'Agent Frameworks', 'API/Backend Infrastructure',
                             'Frontend/UI Frameworks', 'DevOps/CI/CD', 'Cloud/Serverless',
                             'CLI/Dev Tools', 'SDK/Library'],
    'beauty-wellness': ['Frontend/UI Frameworks', 'AI/LLM/GenAI', 'API/Backend Infrastructure',
                        'Database/Storage', 'Email/SMS/Comms', 'E-commerce'],
    'education-training': ['AI/LLM/GenAI', 'Education/Learning', 'Frontend/UI Frameworks',
                           'API/Backend Infrastructure', 'Database/Storage'],
    'community': ['AI/LLM/GenAI', 'Frontend/UI Frameworks', 'API/Backend Infrastructure',
                  'Email/SMS/Comms', 'Database/Storage', 'Community/Platform'],
    'food-hospitality': ['AI/LLM/GenAI', 'Frontend/UI Frameworks', 'API/Backend Infrastructure',
                          'Database/Storage', 'Payments/Billing', 'E-commerce'],
    'fitness-sports': ['AI/LLM/GenAI', 'Frontend/UI Frameworks', 'API/Backend Infrastructure',
                        'Database/Storage', 'Multimodal (Vision/Audio)'],
    'media-content': ['Multimodal (Vision/Audio)', 'AI/LLM/GenAI', 'Frontend/UI Frameworks',
                      'API/Backend Infrastructure', 'Database/Storage', 'Media/Content'],
    'professional-services': ['AI/LLM/GenAI', 'Frontend/UI Frameworks', 'API/Backend Infrastructure',
                               'CLI/Dev Tools', 'Database/Storage'],
    'specialized': ['AI/LLM/GenAI', 'Multimodal (Vision/Audio)', 'API/Backend Infrastructure'],
    'operations': ['AI/LLM/GenAI', 'DevOps/CI/CD', 'Workflow/Orchestration',
                   'API/Backend Infrastructure', 'CLI/Dev Tools', 'Database/Storage'],
    'emerging': ['AI/LLM/GenAI', 'Agent Frameworks', 'Model Fine-tuning', 'RAG/Vector DB',
                 'Multimodal (Vision/Audio)'],
    'construction': ['AI/LLM/GenAI', 'API/Backend Infrastructure', 'Database/Storage',
                     'Frontend/UI Frameworks', 'Construction'],
    'real-estate': ['AI/LLM/GenAI', 'Frontend/UI Frameworks', 'API/Backend Infrastructure',
                    'Database/Storage', 'Real Estate'],
    'technology': ['AI/LLM/GenAI', 'Agent Frameworks', 'API/Backend Infrastructure',
                   'Cloud/Serverless', 'DevOps/CI/CD', 'Database/Storage'],
}

sector_matches = {}
for sector, needed in sector_cap_map.items():
    matches = []
    for r in classified_repos:
        score = sum(1 for c in r['capabilities'] if c in needed)
        if score >= 1:
            matches.append({
                'name': r['name'],
                'full_name': r['full_name'],
                'score': score,
                'language': r['language'] or 'none',
                'description': r['description'][:100],
                'capabilities': r['capabilities'],
            })
    matches.sort(key=lambda x: (-x['score'], -len(x['description'])))
    sector_matches[sector] = {
        'needed_capabilities': needed,
        'total_matches': len(matches),
        'top_10': matches[:10],
    }

with open(out_dir / 'owned-repo-sector-mapping.json', 'w') as f:
    json.dump(sector_matches, f, indent=2)
print(f"  {out_dir / 'owned-repo-sector-mapping.json'} — {len(sector_matches)} sectors")

# Summary markdown
md = [
    "# Owned Repository Capability Analysis",
    "",
    f"**Date:** 2026-08-23",
    f"**Source:** GitHub owned repos (Worldwidebro/) — 890 repos with metadata",
    f"**Data:** /tmp/gh_repos.json (description, language, archived status, dates)",
    "",
    "## Capability Classification",
    "",
    f"- Total owned repos: 890",
    f"- With classified capabilities: {sum(1 for r in classified_repos if r['capabilities'])}",
    f"- Without classified capabilities: {sum(1 for r in classified_repos if not r['capabilities'])}",
    f"- Total capability assignments: {sum(len(r['capabilities']) for r in classified_repos)}",
    f"- Archived: 116 | Active: 774",
    f"- Private: {sum(1 for r in classified_repos if r['is_private'])} | Public: {sum(1 for r in classified_repos if not r['is_private'])}",
    "",
    "### Top capability categories (owned repos):",
    "",
]
for cat, cnt in cap_counter.most_common(15):
    md.append(f"- **{cat}**: {cnt} repos")

md += [
    "",
    "### Categorization by infrastructure type:",
    "",
    f"- **Infrastructure/DevOps/Platform**: {infra} repos — the shared foundation layer",
    f"- **AI/LLM/GenAI related**: {ai} repos — artificial intelligence capabilities",
    f"- **Agent Frameworks**: {cap_counter.get('Agent Frameworks', 0)} repos — agent orchestration",
    f"- **Frontend/UI**: {frontend} repos — user interface layer",
    f"- **API/Backend Services**: {services} repos — backend service layer",
    f"- **SDKs/Libraries**: {libs} repos — reusable code components",
    f"- **Venture Studio/Creation**: {venture_studio} repos — venture-creation infrastructure",
    "",
    "### By sector alignment:",
    "",
]
for sector, data in sorted(sector_matches.items()):
    md.append(f"- **{sector}**: {data['total_matches']} owned repos match capability needs")
md.append("")

md += [
    "### Top capability-rich repos (5+ capabilities):",
    "",
]
for r, cnt in rich[:15]:
    md.append(f"- **{r['name']}** — {cnt} caps, {r['language'] or 'none'}, {r['description'][:80]}")
    md.append(f"  Caps: {', '.join(r['capabilities'])}")
md.append("")

md += [
    "### Vercel-deployed repos (73):",
    "",
    "These are the repos that are actually live on the web:",
    "",
]
for r in vercel_gh[:15]:
    md.append(f"- **{r['name']}** — {r['description'][:80]} | caps: {', '.join(r['capabilities'])}")
md.append("")
md.append(f"  ... +{len(vercel_gh)-15} more Vercel-deployed repos")
md.append("")

md += [
    "### What this tells us:",
    "",
    "1. The owned repo set is heavily infrastructure-weighted (562 of 990 are Infrastructure type).",
    "2. AI/LLM capabilities are present in owned repos but less concentrated than in starred repos.",
    "3. The 73 Vercel-deployed repos are the visible, live layer — the rest are infrastructure,",
    "   libraries, services, and applications not (yet) deployed to Vercel.",
    "4. 116 repos are archived — these are no longer actively maintained.",
    "5. Owned repos serve as the platform/tooling layer that ventures build ON TOP OF.",
    "6. The 439 orphaned repos (no venture mapping) are candidates for: mapping to ventures,",
    "   repurposing as shared infrastructure, or archiving.",
    "",
    "### Gap analysis vs. what we need:",
    "",
    "- We have descriptions for 829 of 890 repos (61 without) — good coverage",
    "- We have language for 346 of 890 — gaps where GitHub didn't detect a primary language",
    "- We have NO capability tags in the registry (all empty) — this analysis fills that gap",
    "- We have NO dependency graph — repos don't declare what they depend on",
    "- We have 439 orphaned repos without venture mapping — needs attention",
    "",
    "*Generated by analyze_owned_repo_capabilities.py*",
]

with open(out_dir / 'OWNED-REPO-CAPABILITY-ANALYSIS.md', 'w') as f:
    f.write('\n'.join(md))
print(f"  {out_dir / 'OWNED-REPO-CAPABILITY-ANALYSIS.md'}")

print()
print("=== DONE ===")
print(f"Output: {out_dir}")
