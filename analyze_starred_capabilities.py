#!/usr/bin/env python3
"""
Three-in-one: 
  1) Classify all 878 starred repos by capability
  2) Identify which are worth integrating vs. just referencing
  3) Map capable repos to Worldwidebro's 17 sectors, pick the most relevant per sector
"""
import json, yaml, re
from collections import Counter, defaultdict
from pathlib import Path

reg = Path('/Users/divinejohns/Documents/Obsidian Vault/worldwidebro-company-registry')
stars = json.loads(Path('/tmp/starred_full.json').read_text())

# ── Venture sectors from registry ──
with open(reg / 'registry/ventures.yaml') as f:
    ventures = yaml.safe_load(f)

sectors = sorted(set(v['sector'] for v in ventures))
print(f"Worldwidebro sectors: {len(sectors)}")
for s in sectors:
    count = sum(1 for v in ventures if v['sector'] == s)
    print(f"  {s:30} {count} ventures")
print()

# Also get venture details per sector for context
sector_ventures = defaultdict(list)
for v in ventures:
    sector_ventures[v['sector']].append(v)

# ── Capability classification ──
def classify(repo):
    name = repo['full_name']
    desc = (repo.get('description') or '').lower()
    topics = [t.lower() for t in (repo.get('topics') or [])]
    lang = (repo.get('language') or '').lower()
    all_text = f"{name} {desc} {' '.join(topics)}"
    caps = []

    ai_kw = ['llm', 'large language model', 'chatgpt', 'openai', 'anthropic', 'claude',
             'gpt-', 'gemini', 'mistral', 'llama', 'gemma', 'deepseek', 'ai model',
             'text generation', 'language model', 'foundation model']
    if any(kw in all_text for kw in ai_kw) or any('ai' in t or 'llm' in t or 'genai' in t or 'generative-ai' in t for t in topics):
        caps.append('AI/LLM/GenAI')
    rag_kw = ['rag', 'retrieval augmented', 'vector database', 'vector db', 'embeddings',
              'semantic search', 'similarity search', 'chromadb', 'pinecone', 'weaviate',
              'qdrant', 'milvus', 'faiss', 'pgvector']
    if any(kw in all_text for kw in rag_kw) or any('rag' in t or 'vector-db' in t or 'embeddings' in t for t in topics):
        caps.append('RAG/Vector DB')
    agent_kw = ['agent', 'agentic', 'autonomous agent', 'ai agent', 'crewai', 'langgraph',
                'autogen', 'flowise', 'dify', 'open Interpreter', 'swe-agent',
                'devin', 'camptocamp', 'agent workflow']
    if any(kw in all_text for kw in agent_kw) or any('agent' in t for t in topics):
        if 'AI/LLM/GenAI' not in caps:
            caps.append('AI/LLM/GenAI')
        caps.append('Agent Frameworks')
    prompt_kw = ['prompt', 'prompt engineering', 'prompt optimization', 'prompt management', 'prompt library']
    if any(kw in all_text for kw in prompt_kw) or any('prompt' in t for t in topics):
        caps.append('Prompt Engineering')
    ft_kw = ['fine-tune', 'fine tuning', 'lora', 'qlora', 'peft', 'sft', 'rlhf',
             'model training', 'model fine', 'adapter', 'huggingface transformers']
    if any(kw in all_text for kw in ft_kw) or any('fine-tuning' in t or 'finetune' in t or 'training' in t for t in topics):
        caps.append('Model Fine-tuning')
    mm_kw = ['image generation', 'image model', 'diffusion', 'stable diffusion', 'midjourney',
             'vision', 'computer vision', 'image recognition', 'image classification',
             'audio', 'speech', 'stt', 'tts', 'whisper', 'sound', 'music generation',
             'video generation', 'video model', 'multimodal']
    if any(kw in all_text for kw in mm_kw) or any('vision' in t or 'audio' in t or 'multimodal' in t or 'image-generation' in t for t in topics):
        caps.append('Multimodal (Vision/Audio)')
    api_kw = ['api', 'rest api', 'graphql', 'grpc', 'microservice', 'server', 'backend',
              'web server', 'http', 'webhook', 'endpoint']
    if any(kw in all_text for kw in api_kw) or any('api' in t or 'backend' in t or 'rest-api' in t for t in topics):
        caps.append('API/Backend Infrastructure')
    fe_kw = ['react', 'vue', 'angular', 'svelte', 'next.js', 'nextjs', 'frontend', 'ui',
             'web app', 'dashboard', 'component', 'typescript', 'css framework',
             'tailwind', 'chakra', 'material-ui']
    if any(kw in all_text for kw in fe_kw) or any('frontend' in t or 'ui' in t or 'react' in t or 'vue' in t for t in topics):
        caps.append('Frontend/UI Frameworks')
    devops_kw = ['ci/cd', 'continuous integration', 'continuous deployment', 'github actions',
                 'action', 'workflow automation', 'pipeline', 'deployment', 'docker',
                 'container', 'kubernetes', 'helm', 'terraform', 'infrastructure as code',
                 'devops', 'automation']
    if any(kw in all_text for kw in devops_kw) or any('devops' in t or 'ci-cd' in t or 'docker' in t or 'kubernetes' in t for t in topics):
        caps.append('DevOps/CI/CD')
    cloud_kw = ['cloud', 'aws', 'azure', 'gcp', 'google cloud', 'serverless', 'lambda',
                'cloudflare', 'vercel', 'netlify', 'firebase', 'cloud function',
                'cloud run', 'ec2', 's3', 'cloud storage']
    if any(kw in all_text for kw in cloud_kw) or any('serverless' in t or 'cloud' in t for t in topics):
        caps.append('Cloud/Serverless')
    db_kw = ['database', 'db', 'postgres', 'postgresql', 'mysql', 'mongodb', 'redis',
             'sqlite', 'sql', 'nosql', 'neo4j', 'graph database', 'document store',
             'key-value', 'storage', 'data store', 'orm']
    if any(kw in all_text for kw in db_kw) or any('database' in t or 'db' in t or 'postgres' in t for t in topics):
        caps.append('Database/Storage')
    obs_kw = ['monitoring', 'observability', 'logging', 'metrics', 'tracing', 'alerting',
              'datadog', 'prometheus', 'grafana', 'sentry', 'log', 'telemetry']
    if any(kw in all_text for kw in obs_kw) or any('monitoring' in t or 'observability' in t or 'logging' in t for t in topics):
        caps.append('Observability/Monitoring')
    cli_kw = ['cli', 'command line', 'terminal', 'developer tool', 'code editor', 'ide',
              'vscode', 'neovim', 'emacs', 'linter', 'formatter', 'build tool',
              'package manager', 'bundler']
    if any(kw in all_text for kw in cli_kw) or any('cli' in t or 'developer-tools' in t or 'command-line' in t for t in topics):
        caps.append('CLI/Dev Tools')
    sdk_kw = ['sdk', 'library', 'package', 'npm', 'pip', 'gem', 'crates', 'maven',
              'gradle', 'composer', 'plugin', 'extension']
    if any(kw in all_text for kw in sdk_kw):
        caps.append('SDK/Library')
    docs_kw = ['documentation', 'docs', 'docgen', 'markdown', 'asciidoc', 'wiki',
               'knowledge base', 'documentation generator']
    if any(kw in all_text for kw in docs_kw) or any('documentation' in t or 'docs' in t or 'wiki' in t for t in topics):
        caps.append('Documentation/Docs')
    test_kw = ['test', 'testing', 'unit test', 'integration test', 'e2e', 'qa',
               'quality assurance', 'mock', 'stub', 'coverage', 'jest', 'pytest',
               'cypress', 'playwright', 'selenium']
    if any(kw in all_text for kw in test_kw) or any('testing' in t or 'test' in t for t in topics):
        caps.append('Testing/Quality')
    sec_kw = ['security', 'auth', 'authentication', 'authorization', 'oauth', 'jwt',
              'encryption', 'cryptography', 'vulnerability', 'penetration', 'scan',
              'audit', 'firewall', 'ddos', 'zero trust']
    if any(kw in all_text for kw in sec_kw) or any('security' in t or 'auth' in t or 'authentication' in t for t in topics):
        caps.append('Security')
    data_kw = ['data pipeline', 'etl', 'data ingestion', 'data processing', 'data lake',
               'data warehouse', 'batch processing', 'stream processing', 'data transformation',
               'apache spark', 'airflow', 'dbt', 'dataloader']
    if any(kw in all_text for kw in data_kw) or any('data-engineering' in t or 'data-pipeline' in t or 'etl' in t for t in topics):
        caps.append('Data Engineering/ETL')
    scrape_kw = ['scraping', 'crawler', 'crawl', 'web scraper', 'scrape', 'spider',
                 'scrapy', 'selenium', 'puppeteer', 'playwright']
    if any(kw in all_text for kw in scrape_kw) or any('scraping' in t or 'crawler' in t or 'web-scraping' in t for t in topics):
        caps.append('Web Scraping/Crawling')
    auth_kw = ['openid', 'sso', 'single sign-on', 'identity provider', 'idp', 'iam',
               'rbac', 'permission', 'role-based']
    if any(kw in all_text for kw in auth_kw):
        caps.append('Auth/Identity')
    pay_kw = ['payment', 'billing', 'subscription', 'stripe', 'paypal', 'revenue',
              'invoicing', 'pricing', 'checkout']
    if any(kw in all_text for kw in pay_kw) or any('payment' in t or 'billing' in t or 'stripe' in t for t in topics):
        caps.append('Payments/Billing')
    comm_kw = ['email', 'smtp', 'sendgrid', 'mailgun', 'sms', 'twilio', 'push notification',
               'notification', 'messaging', 'chat', 'slack', 'discord', 'telegram bot',
               'whatsapp']
    if any(kw in all_text for kw in comm_kw) or any('email' in t or 'sms' in t or 'notification' in t or 'messaging' in t for t in topics):
        caps.append('Email/SMS/Comms')
    search_kw = ['search engine', 'elasticsearch', 'meilisearch', 'typesense',
                 'algolia', 'solr', 'full-text search', 'search']
    if any(kw in all_text for kw in search_kw) or any('search' in t or 'elasticsearch' in t for t in topics):
        caps.append('Search')
    analytics_kw = ['analytics', 'telemetry', 'event tracking', 'usage analytics', 'product analytics',
                    'mixpanel', 'amplitude', 'segment', 'google analytics', 'plausible']
    if any(kw in all_text for kw in analytics_kw) or any('analytics' in t or 'telemetry' in t for t in topics):
        caps.append('Analytics/Telemetry')
    wf_kw = ['workflow', 'orchestration', 'dag', 'state machine', 'pipeline orchestrator',
             'temporal', 'airflow', 'prefect', 'dagster', 'processing pipeline']
    if any(kw in all_text for kw in wf_kw) or any('workflow' in t or 'orchestration' in t for t in topics):
        caps.append('Workflow/Orchestration')
    mq_kw = ['message queue', 'pub-sub', 'kafka', 'rabbitmq', 'sqs', 'pubsub', 'redis pubsub',
             'event bus', 'event streaming', 'async', 'background job']
    if any(kw in all_text for kw in mq_kw) or any('kafka' in t or 'message-queue' in t or 'pubsub' in t for t in topics):
        caps.append('Messaging/Queue')
    os_kw = ['operating system', 'os kernel', 'system call', 'syscall', 'microkernel',
             'unikernel', 'container runtime', 'systemd', 'init system', 'bootloader']
    if any(kw in all_text for kw in os_kw):
        caps.append('Open Source OS/Platform')
    ok_kw = ['open knowledge', 'knowledge graph', 'semantic wiki', 'knowledge base',
             'linked data', 'ontology', 'rdf', 'sparql', 'triples', 'graph db',
             'wiki software', 'confluence alternative']
    if any(kw in all_text for kw in ok_kw) or any('knowledge' in t or 'open-knowledge' in t or 'wiki' in t for t in topics):
        caps.append('Open Knowledge/Wiki')
    edu_kw = ['education', 'learning', 'course', 'tutorial', 'e-learning', 'training',
              'teaching', 'educational', 'curriculum', 'lesson', 'interactive learning',
              'adaptive learning']
    if any(kw in all_text for kw in edu_kw) or any('education' in t or 'learning' in t or 'course' in t for t in topics):
        caps.append('Education/Learning')
    health_kw = ['health', 'medical', 'clinical', 'patient', 'diagnosis', 'medication',
                 'ehr', 'electronic health', 'healthcare', 'hospital', 'telemedicine']
    if any(kw in all_text for kw in health_kw) or any('health' in t or 'medical' in t or 'healthcare' in t for t in topics):
        caps.append('Healthcare/Medical')
    fin_kw = ['finance', 'financial', 'accounting', 'tax', 'banking', 'investment', 'trading',
              'crypto', 'blockchain', 'defi', 'wallet', 'payment processing', 'ledger']
    if any(kw in all_text for kw in fin_kw) or any('finance' in t or 'financial' in t or 'banking' in t or 'crypto' in t for t in topics):
        caps.append('Finance/Fintech')
    ecommerce_kw = ['ecommerce', 'e-commerce', 'shop', 'store', 'cart', 'checkout',
                    'payment gateway', 'product catalog', 'inventory', 'merchant']
    if any(kw in all_text for kw in ecommerce_kw) or any('ecommerce' in t or 'e-commerce' in t or 'shop' in t for t in topics):
        caps.append('E-commerce')
    return caps


print("=== STEP 1: CLASSIFY ALL 878 STARRED REPOS ===")
repos_with_caps = []
for repo in stars:
    caps = classify(repo)
    repos_with_caps.append({
        'full_name': repo['full_name'],
        'description': repo.get('description') or '',
        'language': repo.get('language') or '',
        'stars': repo.get('stargazers_count', 0),
        'forks': repo.get('forks_count', 0),
        'topics': repo.get('topics') or [],
        'license': (repo.get('license') or {}).get('spdx_id', 'none'),
        'last_updated': repo.get('updated_at', ''),
        'capabilities': caps,
    })

cap_counts = Counter()
for r in repos_with_caps:
    for c in r['capabilities']:
        cap_counts[c] += 1

print(f"Total: {len(repos_with_caps)} repos")
print(f"With capabilities: {sum(1 for r in repos_with_caps if r['capabilities'])}")
print(f"Without capabilities: {sum(1 for r in repos_with_caps if not r['capabilities'])}")
print(f"Total capability assignments: {sum(len(r['capabilities']) for r in repos_with_caps)}")
print()

print("Capability distribution:")
for cat, cnt in cap_counts.most_common():
    print(f"  {cat:35} {cnt:4} repos")

# ── STEP 2: INTEGRATE vs REFERENCE scoring ──
print()
print("=== STEP 2: INTEGRATE vs REFERENCE (KEEP/MERGE/FORK/INSTALL/ARCHIVE) ===")

def score_repo(repo):
    """
    Score each starred repo for integration potential.
    KEEP   = worth maintaining a fork/local copy
    MERGE  = core capability worth pulling into an existing project
    FORK   = valuable but needs adaptation to our stack
    INSTALL = install as dependency/tool, don't fork
    ARCHIVE = reference only, no action needed
    """
    name = repo['full_name']
    caps = repo['capabilities']
    stars = repo['stars']
    language = repo['language']
    desc = repo['description']
    topics = repo['topics']

    score = 0
    reasons = []

    # HIGH: large ecosystem, high stars, active
    if stars > 50000:
        score += 3
        reasons.append(f"high-visibility ({stars}★)")
    elif stars > 10000:
        score += 2
        reasons.append(f"well-known ({stars}★)")
    elif stars > 1000:
        score += 1

    # Language alignment with our stack
    if language in ('Python', 'TypeScript', 'Go', 'JavaScript'):
        score += 1
        reasons.append(f"stack-aligned language ({language})")

    # License check
    if repo['license'] in ('MIT', 'Apache-2.0', 'BSD-2-Clause', 'BSD-3-Clause', 'CC0-1.0'):
        score += 1
        reasons.append("permissive license")
    elif repo['license'] in ('AGPL-3.0', 'GPL-3.0', 'GPL-2.0'):
        score -= 1
        reasons.append("copyleft license (review before use)")

    # Capability relevance (topics)
    relevant_topics = ['mcp', 'ai-agents', 'agent', 'agents', 'rag', 'vector-database',
                       'embeddings', 'knowledge-graph', 'agent-skills', 'cli',
                       'developer-tools', 'self-hosted', 'open-source']
    topic_score = sum(1 for t in topics if t.lower() in relevant_topics)
    if topic_score >= 3:
        score += 2
        reasons.append(f"highly relevant topics ({topic_score} matches)")
    elif topic_score >= 1:
        score += 1

    # Capability count — multi-capability repos are higher value
    if len(caps) >= 5:
        score += 2
        reasons.append(f"multi-capability ({len(caps)} areas)")
    elif len(caps) >= 2:
        score += 1

    # MCP-specific — highly relevant to Hermes/IZA
    if any('mcp' in t.lower() for t in topics):
        score += 3
        reasons.append("MCP — directly relevant to Hermes stack")

    # AI agent specific — relevant to LT-011, OPS-001
    if any('agent' in t.lower() or 'ai-agent' in t.lower() for t in topics):
        score += 2
        reasons.append("AI agent — relevant to LT-011/OPS-001")

    # Self-hosted — aligns with our infrastructure model
    if 'self-hosted' in [t.lower() for t in topics]:
        score += 1
        reasons.append("self-hostable")

    # Active maintenance
    updated = repo['last_updated']
    if updated > '2026-06-01':
        score += 1
        reasons.append("recently updated")
    elif updated < '2024-01-01':
        score -= 2
        reasons.append("stale/archived feel")

    # Recommendation
    if score >= 8:
        action = 'KEEP'
        reason = f"High-value external capability ({score} pts): {'; '.join(reasons[:3])}"
    elif score >= 5:
        action = 'MERGE'
        reason = f"Worth integrating into existing project ({score} pts): {'; '.join(reasons[:3])}"
    elif score >= 3:
        action = 'FORK'
        reason = f"Valuable, needs adaptation ({score} pts): {'; '.join(reasons[:3])}"
    elif score >= 1:
        action = 'INSTALL'
        reason = f"Install as dependency, don't fork ({score} pts): {'; '.join(reasons[:3])}"
    else:
        action = 'ARCHIVE'
        reason = f"Reference only ({score} pts): {'; '.join(reasons[:3])}"

    # Override: if it's our own repo (Worldwidebro/ prefix)
    if name.startswith('Worldwidebro/') or name.startswith('Worldwidebro/'):
        action = 'KEEP'
        reason = "Our own repo — maintain"

    return {
        'full_name': name,
        'capabilities': caps,
        'stars': stars,
        'language': language,
        'license': repo['license'],
        'topics': topics,
        'last_updated': updated,
        'score': score,
        'action': action,
        'reason': reason,
    }

scored = [score_repo(r) for r in repos_with_caps]

action_counts = Counter(r['action'] for r in scored)
print(f"Action distribution:")
for action in ['KEEP', 'MERGE', 'FORK', 'INSTALL', 'ARCHIVE']:
    cnt = action_counts.get(action, 0)
    print(f"  {action:10} {cnt:4} repos")

print()
print("KEEP repos (highest value — maintain awareness / possible fork):")
keep = sorted([r for r in scored if r['action'] == 'KEEP'], key=lambda x: -x['score'])
for r in keep[:25]:
    caps_str = ', '.join(r['capabilities'][:5])
    if len(r['capabilities']) > 5:
        caps_str += f' +{len(r["capabilities"])-5} more'
    print(f"  {r['full_name']:50} | {r['stars']:6}★ | {r['language']:12} | [{caps_str}]")
print(f"  ... and {len(keep)-25} more KEEP repos")
print()

print("MERGE repos (integrate into existing projects):")
merge = sorted([r for r in scored if r['action'] == 'MERGE'], key=lambda x: -x['score'])
for r in merge[:15]:
    caps_str = ', '.join(r['capabilities'][:3])
    print(f"  {r['full_name']:50} | {r['stars']:6}★ | {r['language']:12} | [{caps_str}]")
print(f"  ... and {len(merge)-15} more MERGE repos")
print()

print("FORK repos (valuable, adapt to our stack):")
fork = sorted([r for r in scored if r['action'] == 'FORK'], key=lambda x: -x['score'])
for r in fork[:10]:
    caps_str = ', '.join(r['capabilities'][:3])
    print(f"  {r['full_name']:50} | {r['stars']:6}★ | {r['language']:12} | [{caps_str}]")
print(f"  ... and {len(fork)-10} more FORK repos")
print()

print("INSTALL repos (use as dependency/tool):")
install = sorted([r for r in scored if r['action'] == 'INSTALL'], key=lambda x: -x['score'])
for r in install[:10]:
    caps_str = ', '.join(r['capabilities'][:2])
    print(f"  {r['full_name']:50} | {r['stars']:6}★ | {r['language']:12} | [{caps_str}]")
print()

print("ARCHIVE repos (reference only, no action):")
archive = sorted([r for r in scored if r['action'] == 'ARCHIVE'], key=lambda x: x['stars'])
for r in archive[:10]:
    print(f"  {r['full_name']:50} | {r['stars']:6}★ | {r['language']:12} | caps={r['capabilities']}")
print(f"  ... and {len(archive)-10} more ARCHIVE repos")

# ── STEP 3: MAP TO SECTORS ──
print()
print("=== STEP 3: MAP CAPABLE REPOS TO WORLDWIDEBRO SECTORS ===")

# Per-sector capability needs (derived from venture types in each sector)
sector_capability_map = {
    'e-commerce': ['AI/LLM/GenAI', 'Agent Frameworks', 'API/Backend Infrastructure', 'Frontend/UI Frameworks',
                   'Database/Storage', 'Payments/Billing', 'Email/SMS/Comms', 'Search', 'Cloud/Serverless',
                   'Web Scraping/Crawling', 'Analytics/Telemetry'],
    'financial': ['AI/LLM/GenAI', 'API/Backend Infrastructure', 'Database/Storage', 'Security',
                  'Payments/Billing', 'Auth/Identity', 'Finance/Fintech', 'Cloud/Serverless',
                  'DevOps/CI/CD', 'CLI/Dev Tools'],
    'logistics-transport': ['AI/LLM/GenAI', 'Agent Frameworks', 'API/Backend Infrastructure', 'Database/Storage',
                             'CLI/Dev Tools', 'DevOps/CI/CD', 'Messaging/Queue', 'Workflow/Orchestration',
                             'Cloud/Serverless', 'Observability/Monitoring'],
    'software-technology': ['AI/LLM/GenAI', 'Agent Frameworks', 'API/Backend Infrastructure', 'Frontend/UI Frameworks',
                             'DevOps/CI/CD', 'Cloud/Serverless', 'CLI/Dev Tools', 'SDK/Library',
                             'Database/Storage', 'Testing/Quality', 'Security'],
    'beauty-wellness': ['Frontend/UI Frameworks', 'AI/LLM/GenAI', 'API/Backend Infrastructure', 'Database/Storage',
                        'Email/SMS/Comms', 'Payments/Billing', 'Cloud/Serverless'],
    'education-training': ['AI/LLM/GenAI', 'Education/Learning', 'Frontend/UI Frameworks', 'API/Backend Infrastructure',
                           'Database/Storage', 'CLI/Dev Tools', 'Cloud/Serverless'],
    'community': ['AI/LLM/GenAI', 'Frontend/UI Frameworks', 'API/Backend Infrastructure', 'Email/SMS/Comms',
                  'Database/Storage', 'Payments/Billing', 'CLI/Dev Tools'],
    'food-hospitality': ['AI/LLM/GenAI', 'Frontend/UI Frameworks', 'API/Backend Infrastructure', 'Database/Storage',
                          'Payments/Billing', 'Email/SMS/Comms', 'Cloud/Serverless'],
    'fitness-sports': ['AI/LLM/GenAI', 'Frontend/UI Frameworks', 'API/Backend Infrastructure', 'Database/Storage',
                        'Multimodal (Vision/Audio)', 'Payments/Billing', 'Cloud/Serverless'],
    'media-content': ['Multimodal (Vision/Audio)', 'AI/LLM/GenAI', 'Frontend/UI Frameworks', 'API/Backend Infrastructure',
                      'Database/Storage', 'Web Scraping/Crawling', 'Cloud/Serverless'],
    'professional-services': ['AI/LLM/GenAI', 'Frontend/UI Frameworks', 'API/Backend Infrastructure', 'CLI/Dev Tools',
                               'Database/Storage', 'Cloud/Serverless', 'Documentation/Docs'],
    'specialized': ['AI/LLM/GenAI', 'Multimodal (Vision/Audio)', 'API/Backend Infrastructure', 'Frontend/UI Frameworks',
                    'Device/Hardware', 'Cloud/Serverless'],
    'operations': ['AI/LLM/GenAI', 'DevOps/CI/CD', 'Workflow/Orchestration', 'API/Backend Infrastructure',
                   'CLI/Dev Tools', 'Database/Storage', 'Cloud/Serverless', 'Observability/Monitoring',
                   'Messaging/Queue'],
    'emerging': ['AI/LLM/GenAI', 'Agent Frameworks', 'Model Fine-tuning', 'RAG/Vector DB', 'Multimodal (Vision/Audio)',
                 'API/Backend Infrastructure', 'Frontend/UI Frameworks'],
    'construction': ['AI/LLM/GenAI', 'API/Backend Infrastructure', 'Database/Storage', 'Frontend/UI Frameworks',
                     'Docs/Field', 'Payments/Billing', 'Email/SMS/Comms'],
    'real-estate': ['AI/LLM/GenAI', 'Frontend/UI Frameworks', 'API/Backend Infrastructure', 'Database/Storage',
                    'Search', 'Cloud/Serverless', 'Payments/Billing'],
    'technology': ['AI/LLM/GenAI', 'Agent Frameworks', 'API/Backend Infrastructure', 'Cloud/Serverless',
                   'DevOps/CI/CD', 'Database/Storage', 'Frontend/UI Frameworks', 'SDK/Library'],
}

print(f"\nMapping {sum(1 for r in scored if r['capabilities'])} capable repos to {len(sector_capability_map)} sectors...")
print()

for sector, needed_caps in sorted(sector_capability_map.items()):
    sector_ventures_list = sector_ventures.get(sector, [])
    n_ventures = len(sector_ventures_list)
    venture_ids = [v['id'] for v in sector_ventures_list[:5]]
    if len(sector_ventures_list) > 5:
        venture_ids.append(f"... +{len(sector_ventures_list)-5} more")

    # Score each capable repo for this sector
    sector_matches = []
    for r in scored:
        if not r['capabilities']:
            continue
        match_score = 0
        for cap in r['capabilities']:
            if cap in needed_caps:
                match_score += 1
        if match_score >= 1:
            sector_matches.append((r, match_score))

    sector_matches.sort(key=lambda x: (-x[1], -x[0]['stars']))

    print(f"  {sector:25} ({n_ventures} ventures: {', '.join(venture_ids)})")
    print(f"    Capability needs: {', '.join(needed_caps[:5])}{'...' if len(needed_caps)>5 else ''}")
    print(f"    Matching repos: {len(sector_matches)}")
    if sector_matches:
        top = sector_matches[:5]
        for r, ms in top:
            caps_str = ', '.join(r['capabilities'][:4])
            print(f"      [{ms} caps] {r['full_name']:45} | {r['stars']:5}★ | {r['language']:10} | {caps_str}")
        if len(sector_matches) > 5:
            print(f"      ... +{len(sector_matches)-5} more matches")
    print()

# ── WRITE OUTPUT FILES ──
print("=== WRITING OUTPUT FILES ===")
out_dir = reg / 'audits' / 'starred-analysis'
out_dir.mkdir(parents=True, exist_ok=True)

# 1. Full capability classification (JSON)
with open(out_dir / 'starred-capability-classification.json', 'w') as f:
    json.dump(repos_with_caps, f, indent=2)
print(f"  Written: {out_dir / 'starred-capability-classification.json'} ({len(repos_with_caps)} repos)")

# 2. Scored integrate/reference decisions (JSON)
with open(out_dir / 'starred-integration-decisions.json', 'w') as f:
    json.dump(scored, f, indent=2)
print(f"  Written: {out_dir / 'starred-integration-decisions.json'} ({len(scored)} repos)")

# 3. Sector mapping (JSON)
sector_map = {}
for sector, needed_caps in sector_capability_map.items():
    sector_matches = []
    for r in scored:
        if not r['capabilities']:
            continue
        match_score = sum(1 for cap in r['capabilities'] if cap in needed_caps)
        if match_score >= 1:
            sector_matches.append({
                'full_name': r['full_name'],
                'score': match_score,
                'stars': r['stars'],
                'language': r['language'],
                'capabilities': r['capabilities'],
                'action': r['action'],
                'reason': r['reason'],
            })
    sector_matches.sort(key=lambda x: (-x['score'], -x['stars']))
    sector_map[sector] = {
        'needed_capabilities': needed_caps,
        'matching_repos': sector_matches,
        'total_matches': len(sector_matches),
        'top_10': sector_matches[:10],
    }
with open(out_dir / 'sector-capability-mapping.json', 'w') as f:
    json.dump(sector_map, f, indent=2)
print(f"  Written: {out_dir / 'sector-capability-mapping.json'} ({len(sector_map)} sectors)")

# 4. Summary markdown
summary_lines = [
    "# Starred Repos Capability Analysis",
    "",
    f"**Date:** 2026-08-22",
    f"**Source:** GitHub starred repos (user/starred) — 878 repos",
    f"**Prepared for:** Worldwidebro company registry",
    "",
    "## Step 1: Capability Classification",
    "",
    f"- Total starred repos: 878",
    f"- With classified capabilities: {sum(1 for r in repos_with_caps if r['capabilities'])}",
    f"- Without classified capabilities: {sum(1 for r in repos_with_caps if not r['capabilities'])}",
    f"- Total capability assignments: {sum(len(r['capabilities']) for r in repos_with_caps)}",
    "",
    "### Top capability categories:",
    "",
]
for cat, cnt in cap_counts.most_common(10):
    summary_lines.append(f"- **{cat}**: {cnt} repos")

summary_lines += [
    "",
    "## Step 2: Integration vs Reference Decisions",
    "",
    f"- **KEEP** (maintain awareness / possible fork): {action_counts.get('KEEP', 0)} repos",
    f"- **MERGE** (integrate into existing project): {action_counts.get('MERGE', 0)} repos",
    f"- **FORK** (valuable, adapt to stack): {action_counts.get('FORK', 0)} repos",
    f"- **INSTALL** (use as dependency/tool): {action_counts.get('INSTALL', 0)} repos",
    f"- **ARCHIVE** (reference only): {action_counts.get('ARCHIVE', 0)} repos",
    "",
    "### Top KEEP repos (highest value):",
    "",
]
for r in keep[:15]:
    summary_lines.append(f"- `{r['full_name']}` — {r['stars']}★, {r['language']}, [{', '.join(r['capabilities'][:4])}] — {r['reason']}")

summary_lines += [
    "",
    "## Step 3: Sector Capability Mapping",
    "",
    "Each sector lists the most relevant external repos for its capability needs.",
    "",
]
for sector in sorted(sector_capability_map.keys()):
    sm = sector_map[sector]
    summary_lines.append(f"### {sector} ({sm['total_matches']} matching repos)")
    summary_lines.append("")
    summary_lines.append(f"Needed capabilities: {', '.join(sm['needed_capabilities'])}")
    summary_lines.append("")
    for r in sm['top_10']:
        summary_lines.append(f"- `{r['full_name']}` — {r['stars']}★, [{', '.join(r['capabilities'][:4])}] — {r['action']}")
    summary_lines.append("")

summary_lines.append("---")
summary_lines.append("")
summary_lines.append("*Generated by analyze_starred_capabilities.py*")

with open(out_dir / 'STARRED-CAPABILITY-ANALYSIS.md', 'w') as f:
    f.write('\n'.join(summary_lines))
print(f"  Written: {out_dir / 'STARRED-CAPABILITY-ANALYSIS.md'}")

print()
print("=== DONE ===")
print(f"Output directory: {out_dir}")
