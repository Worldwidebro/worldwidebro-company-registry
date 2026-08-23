# Sync status

Tracks whether the registry matches the authoritative sources: GitHub, Vercel, Supabase, ClickUp, Obsidian vault.

| Source | Last sync | Status | Notes |
|--------|-----------|--------|-------|
| GitHub | 2026-08-22 | synced | 890 owned repos loaded via `gh repo list Worldwidebro`. All under `Worldwidebro/<slug>` namespace. 547 matched to T7 ventures. |
| Vercel | 2026-08-22 | synced | 88 unique production-ready projects loaded from vercel_deployments.csv. 73 wired into repositories.yaml (production_url field). 58 wired into ventures.yaml (_vercel_url field). 5 focus ventures confirmed: CON-001, LT-005, LT-011, RE-001 have production deploys. |
| T7 Shield | 2026-08-22 | synced | VENTURE-MASTER-REGISTRY.csv (788 ventures) loaded. 50 knowledge_graph duplicate entries (`venture:` prefix) removed. 738 canonical ventures in registry. Caveat: dated 2026-02-23 (~6 months stale). |
| Supabase | — | pending | 19 tables, 9 scripts — listed in venture-hub capabilities but not yet verified against registry. |
| ClickUp | — | pending | Authorization outstanding; 5 spaces only, not 749+ ventures. |
| Obsidian vault | 2026-08-22 | synced | 5 focus ventures (CON-001, LT-005, LT-011, RE-001, OPS-001) cross-referenced. OPS-001 confirmed as T7 Pre-launch with no repo. |

**Post-reconciliation state:**

- ventures.yaml: 742 entries (738 T7 canonical + 4 GH-only with Vercel deploys)
- repositories.yaml: 990 entries (890 owned + 100 starred-ext reference)
- 547 owned repos matched to T7 ventures
- 343 owned repos unmatched (116 archived, 88 platform-infrastructure, 14 platform-with-deploy, 123 other, 1 venture-id-pattern, 1 vercel-match)
- 51 T7 ventures without repos (50 missing mapping, 1 needs build)
- 50 duplicate entries removed (knowledge_graph `venture:` prefix)
- 73 repos with Vercel production URLs
- 877 starred repos (all external/third-party, correctly flagged as External)
- 0 non-Worldwidebro repos in registry

Update this file after each sync run.
