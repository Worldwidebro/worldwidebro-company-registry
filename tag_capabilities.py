#!/usr/bin/env python3
"""Heuristic capability tagging pass over registry/repositories.yaml.

This is NOT a code-level audit. It pattern-matches repository name +
description (+ language, for owned repos) against a fixed keyword taxonomy.
Owned repos (890) have real descriptions from /tmp/gh_repos.json (93% non-empty).
Starred repos (877) have name-only signal from /tmp/starred_repos.txt — no
description exists for them anywhere, so their tags are lower confidence by
construction, not by omission.

Every repository-capability edge this script writes gets an explicit
`confidence` value (name+description | name+language | name-only) in
mappings/repository-capability.csv so nothing here masquerades as verified.
Capability records are written with status=Proposed and provenance=inferred
in registry/capabilities.yaml — maturity (Live/Deprecated) is left for the
real per-repo audit (step 2 of the agreed sequence), not claimed here.
"""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
OWNED_SOURCE = Path("/tmp/gh_repos.json")
REPOS_YAML = ROOT / "registry" / "repositories.yaml"
CAPABILITIES_YAML = ROOT / "registry" / "capabilities.yaml"
MAPPING_CSV = ROOT / "mappings" / "repository-capability.csv"
SNAPSHOT_DATE = "2026-08-23"

# id: (name, category, [keywords])
# Keywords are matched as whole words against "id + description + language"
# lowercased with hyphens/underscores/slashes turned into spaces.
TAXONOMY: dict[str, tuple[str, str, list[str]]] = {
    "ai-ml": ("AI / ML Models", "AI", ["ai", "ml", "llm", "gpt", "model", "neural", "embedding", "transformer", "diffusion", "claude", "gemini", "openai", "anthropic"]),
    "agent-systems": ("Agent Systems", "AI", ["agent", "agentic", "autonomous", "multiagent", "swarm"]),
    "search-retrieval": ("Search & Retrieval", "Data", ["search", "retrieval", "rag", "elastic", "vector", "index", "embedding"]),
    "image-vision": ("Image / Vision", "AI", ["image", "vision", "ocr", "photo", "screenshot"]),
    "voice-audio": ("Voice & Audio", "Product", ["voice", "audio", "speech", "tts", "stt", "whisper", "podcast"]),
    "video-media": ("Video & Media", "Product", ["video", "media", "stream", "ffmpeg", "youtube"]),
    "automation-orchestration": ("Automation & Orchestration", "Operations", ["automation", "automate", "orchestration", "orchestrator", "workflow", "pipeline", "dispatch", "cron", "scheduler"]),
    "api-integration": ("API & Integration", "Integration", ["api", "sdk", "integration", "connector", "webhook", "mcp"]),
    "authentication-identity": ("Authentication & Identity", "Infrastructure", ["auth", "oauth", "sso", "identity", "login", "jwt"]),
    "payments-billing": ("Payments & Billing", "Product", ["payment", "billing", "stripe", "invoice", "checkout", "subscription"]),
    "data-analytics": ("Data & Analytics", "Data", ["analytics", "dashboard", "metrics", "report", "reporting", "bi"]),
    "database-storage": ("Database & Storage", "Data", ["database", "postgres", "mysql", "supabase", "storage", "sql", "sqlite", "mongodb", "redis"]),
    "frontend-ui": ("Frontend / UI", "Product", ["frontend", "react", "vue", "next", "website", "landing", "webapp", "ui"]),
    "backend-service": ("Backend Service", "Infrastructure", ["backend", "server", "microservice", "fastapi", "express", "django", "flask"]),
    "mobile-app": ("Mobile App", "Product", ["mobile", "ios", "android", "flutter", "react-native"]),
    "devops-infra": ("DevOps & Infrastructure", "Infrastructure", ["devops", "docker", "kubernetes", "k8s", "terraform", "deploy", "deployment", "infra", "infrastructure", "ci", "cd"]),
    "security-compliance": ("Security & Compliance", "Compliance", ["security", "compliance", "vulnerability", "encrypt", "secrets", "pentest", "audit"]),
    "cms-content": ("CMS & Content", "Product", ["cms", "content", "blog", "publish", "editor", "markdown"]),
    "e-commerce": ("E-Commerce", "Product", ["ecommerce", "shop", "store", "cart", "marketplace"]),
    "crm-sales": ("CRM & Sales", "Product", ["crm", "sales", "lead", "outreach"]),
    "messaging-communication": ("Messaging & Communication", "Integration", ["chat", "message", "slack", "discord", "telegram", "email", "sms", "notification"]),
    "knowledge-graph": ("Knowledge Graph & Notes", "Data", ["knowledge", "graph", "obsidian", "vault", "wiki", "notes", "zettelkasten"]),
    "game-development": ("Game Development", "Product", ["game", "unity", "unreal", "godot", "roblox"]),
    "blockchain-web3": ("Blockchain / Web3", "Product", ["blockchain", "web3", "crypto", "nft", "solidity", "defi"]),
    "education-learning": ("Education & Learning", "Product", ["education", "learning", "course", "tutor", "quiz", "study"]),
    "healthcare": ("Healthcare", "Product", ["health", "medical", "clinical", "patient", "hipaa"]),
    "finance-fintech": ("Finance & Fintech", "Product", ["finance", "fintech", "trading", "invest", "portfolio", "quant", "tax"]),
    "real-estate": ("Real Estate", "Product", ["realestate", "property", "listing", "realtor"]),
    "legal-compliance": ("Legal & Compliance", "Compliance", ["legal", "contract", "law"]),
    "hr-recruiting": ("HR & Recruiting", "Operations", ["recruit", "hiring", "resume", "talent"]),
    "marketing-growth": ("Marketing & Growth", "Product", ["marketing", "growth", "seo", "campaign", "ads"]),
    "developer-tools": ("Developer Tools", "Infrastructure", ["cli", "toolkit", "template", "boilerplate", "starter", "generator", "framework", "sdk"]),
    "venture-governance": ("Venture Governance & Registry", "Operations", ["governance", "registry", "empire", "portfolio"]),
    # NOTE: "civilization" deliberately excluded — 443/890 owned repo descriptions
    # share a "Civilization OS — <name>" boilerplate prefix (portfolio branding,
    # not a functional signal), which made this capability falsely dominant.
    "monitoring-observability": ("Monitoring & Observability", "Infrastructure", ["monitor", "observability", "logging", "telemetry", "tracing"]),
}

WORD_RE_CACHE: dict[str, re.Pattern] = {}


def word_pattern(keyword: str) -> re.Pattern:
    if keyword not in WORD_RE_CACHE:
        WORD_RE_CACHE[keyword] = re.compile(rf"\b{re.escape(keyword)}\b")
    return WORD_RE_CACHE[keyword]


def normalize(text: str) -> str:
    return re.sub(r"[-_/.]", " ", text.lower())


def match_capabilities(text: str) -> list[str]:
    norm = normalize(text)
    hits = []
    for cap_id, (_name, _cat, keywords) in TAXONOMY.items():
        for kw in keywords:
            if word_pattern(kw).search(norm):
                hits.append(cap_id)
                break
    return hits


def main() -> None:
    owned_raw = json.loads(OWNED_SOURCE.read_text())
    owned_by_name = {repo["name"]: repo for repo in owned_raw}

    repos = yaml.safe_load(REPOS_YAML.read_text())

    cap_repos: dict[str, list[str]] = defaultdict(list)
    mapping_rows: list[tuple[str, str, str, str]] = []
    tagged, untagged_owned, untagged_starred = 0, 0, 0

    for repo in repos:
        repo_id = repo["id"]
        if repo["starred"]:
            text = repo_id
            confidence = "name-only"
        else:
            src = owned_by_name.get(repo_id, {})
            desc = src.get("description") or ""
            lang = (src.get("primaryLanguage") or {}).get("name", "") if src.get("primaryLanguage") else ""
            text = f"{repo_id} {desc} {lang}"
            confidence = "name+description" if desc else "name+language" if lang else "name-only"

        hits = match_capabilities(text)
        repo["capabilities"] = sorted(hits)
        if hits:
            tagged += 1
            for cap_id in hits:
                cap_repos[cap_id].append(repo_id)
                mapping_rows.append((repo_id, cap_id, "provides", confidence))
        else:
            if repo["starred"]:
                untagged_starred += 1
            else:
                untagged_owned += 1

    REPOS_YAML.write_text(yaml.safe_dump(repos, sort_keys=False, allow_unicode=True, width=1000))

    capabilities = []
    for cap_id, (name, category, _kw) in TAXONOMY.items():
        repo_list = sorted(set(cap_repos.get(cap_id, [])))
        capabilities.append({
            "id": cap_id,
            "name": name,
            "description": f"Repositories whose name/description/language match the '{name}' keyword set (heuristic, not code-audited).",
            "category": category,
            "owners": [],
            "repositories": repo_list,
            "status": "Proposed",
            "provenance": "inferred",
            "created_at": f"{SNAPSHOT_DATE}T00:00:00Z",
            "updated_at": f"{SNAPSHOT_DATE}T00:00:00Z",
        })
    # Keep only capabilities that actually matched at least one repo.
    capabilities = [c for c in capabilities if c["repositories"]]
    CAPABILITIES_YAML.write_text(yaml.safe_dump(capabilities, sort_keys=False, allow_unicode=True, width=1000))

    with MAPPING_CSV.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["repo_id", "capability_id", "relation", "confidence"])
        for row in mapping_rows:
            writer.writerow(row)

    print(f"Repos tagged with >=1 capability: {tagged} / {len(repos)}")
    print(f"Owned repos with zero capability matches: {untagged_owned}")
    print(f"Starred repos with zero capability matches: {untagged_starred}")
    print(f"Capabilities with >=1 repo: {len(capabilities)} / {len(TAXONOMY)}")
    print(f"Total repo-capability edges: {len(mapping_rows)}")


if __name__ == "__main__":
    main()
