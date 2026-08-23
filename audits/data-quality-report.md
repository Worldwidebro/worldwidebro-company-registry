# Registry Data Quality Report
# Generated: 2026-08-22
# Sources: T7 Shield (788), GitHub owned (890), GitHub starred (877), Vercel (88)

## Confidence Overview

| Tier | Confidence | Count | What it means |
|------|-----------|-------|---------------|
| HIGH | Direct evidence, no inference | ~650 | T7 venture identity, GH repo ownership, Vercel deploys, GH archived flag |
| MEDIUM | Derived from keywords/heuristics | ~730 | Sector classification, repo type, repo Active/Maintenance status, GH-only venture sectors |
| LOW | Translated from stale source or unknown | ~673 | Pre-launch status (622), unknown sectors (52), ventures without repos (101), GH-only sectors |
| NONE | Not yet populated | all | Capabilities, agents, projects, KPIs, risks, decisions (all empty) |

---

## HIGH Confidence Records (~650)

### T7 venture identity (687, source=venture_registry)
- Venture ID, name, sector are directly from the canonical registry.
- **Caveat:** T7 snapshot dated 2026-02-23 — 6 months stale.
- Ventures created after Feb 2026 (CON-001, RE-001) are NOT in T7.
- Confidence on ID/name/sector: HIGH.
- Confidence on status: MEDIUM (translated from T7 status, not verified against current reality).

### GitHub repo ownership (890, all)
- All 890 repos confirmed owned by Worldwidebro via `gh api`.
- All 890 are under `Worldwidebro/<slug>` namespace.
- Zero repos under any other owner.
- Confidence: HIGH.

### GitHub repo → T7 venture match (547)
- Matched by repo slug appearing in T7 registry's `repository_url`.
- Slug collision is extremely unlikely — these are the same repos.
- Confidence: HIGH.

### Vercel production deployment (73 repos)
- Matched by repo slug appearing in Vercel project name + state=READY + target=production.
- These 73 repos have a live production URL.
- Confidence: HIGH.

### GitHub archived flag (116 repos)
- Direct `isArchived` flag from GitHub API.
- Confidence: HIGH.

### Starred external repos (100 in repositories.yaml, 870 total)
- These are third-party repos we've starred — correctly flagged as External.
- Confidence on their status=External: HIGH.
- Confidence on their relevance to ventures: NONE (not yet assessed).

---

## MEDIUM Confidence Records (~730)

### GH-only venture sector classification (6 ventures)
- Sector assigned from description/name keyword matching.
- Example: `con-001-ace-construction` → sector=construction (correct).
- Example: `re-001-worldwidebro-holdings` → sector=real-estate (plausible but unverified).
- These 6 had no T7 record → heuristic filling.
- Confidence: MEDIUM. Correct for most, but some may be wrong.

### Repo type classification (990 repos)
- Classified into Application/Service/Library/Infrastructure/Prototype/Data from description keywords.
- 562 classified as Infrastructure — this is likely over-classified.
- Many repos with generic descriptions default to Infrastructure.
- Confidence: MEDIUM. The classification is directional, not definitive.

### Repo Active vs Maintenance status (774 Active, rest Maintenance)
- `Active` if pushed within 6 months; `Maintenance` if older.
- 6-month threshold is arbitrary.
- Some repos pushed 5 months ago may be inactive in reality.
- Confidence: MEDIUM.

### Venture status translation (622 Pre-launch)
- T7 status "planned" or "new" translated to "Pre-launch".
- This is a schema translation, not a state update.
- A venture marked "planned" in Feb 2026 may be "Building" or "Live" now.
- Confidence: LOW-MEDIUM. The translation is correct per the schema, but the underlying data is stale.

---

## LOW Confidence Records (~673)

### Ventures without repos (101)
- Pure T7 registry entries with no GitHub repo, no URL, no code.
- Confidence on their EXISTENCE: HIGH (T7 is canonical).
- Confidence on their CURRENT STATE: LOW.
- 50 are "missing mapping" — T7 source=correlation_map, no repo URL.
- 51 are "needs build" — planned ventures with no code yet.
- These need manual review to determine: still active? built elsewhere? abandoned?

### Unknown sectors (52 ventures)
- T7 entries with sector="unknown" that we kept as-is.
- No keyword in name/description to classify.
- Confidence: LOW/NONE. Needs manual classification.

### GH-only venture statuses (6)
- `con-001-ace-construction`: status=Live because it has Vercel deploy. HIGH confidence on Live, MEDIUM on sector.
- `re-001-worldwidebro-holdings`: status=Live because it has Vercel deploy. HIGH on Live, MEDIUM on sector.
- `lt-011-dispatch-software`: this is actually in T7 (LT-011-Dispatch-Software) — should use T7 data, not GH-only path. See OPS-001 fix below.
- `arbitrage-nexus`: status=Live, sector=software-technology. MEDIUM both.
- `ec-111-miss-toys`, `ec-112-cosmic-kitty`: status=Live, sector=e-commerce. MEDIUM both.
- `OS-001-MATHEMATICAL-OS-REGISTRY`: status=Building, sector=unknown. LOW.

---

## NONE Confidence (Not Yet Populated)

All of these fields are empty across all 794 ventures:

- capabilities (array)
- agents (array)
- projects (array)
- kpis (array)
- risks (array)
- decisions (array)
- customers (string)
- revenue (number)
- costs (number)

This is expected — the first pass establishes venture/repo identity. The next pass (capability extraction + compound scoring) populates these.

---

## Namespace Question: Are everything under Worldwidebro/?

**YES — fully consistent.**

| Source | Namespace | Count | Non-Worldwidebro |
|--------|-----------|-------|-----------------|
| GitHub owned repos | Worldwidebro/<slug> | 890 | 0 |
| T7 registry repo URLs | github.com/Worldwidebro/<slug> | 687 | 0 |
| T7 registry repos with non-github URL | various | 50 | N/A (no GitHub URL) |
| Starred repos | external (not Worldwidebro) | 877 | 877 (all third-party) |
| Generated repositories.yaml | Worldwidebro/<slug> | 990 | 0 |

**No repos need renaming.** Every owned repo is already `Worldwidebro/<name>`. The T7 registry URLs all point to `github.com/Worldwidebro/`. The starred repos are correctly flagged as external.

---

## OPS-001 Data Quality Issue

OPS-001 has a known problem in the current registry:

```
OPS-001                    | Process Automation Suite | operations | Pre-launch | source=correlation_map | repo=EMPTY
venture:OPS-001           | Process Automation Suite | unknown    | Pre-launch | source=knowledge_graph | repo=EMPTY
OPS-001-Fractional-CTO-Agency | Fractional Cto Agency | operations | Pre-launch | source=venture_registry | repo=ops-001-fractional-cto-agency
```

- `OPS-001` from T7 (correlation_map source) has no repo URL.
- `venture:OPS-001` from T7 (knowledge_graph source) is a duplicate with sector=unknown.
- `OPS-001-Fractional-CTO-Agency` is a separate T7 venture (also in operations).

The GH-only path added `process-automation-suite` as a separate venture — but T7 already has OPS-001 with that exact name. The GH-only entry should have been recognized as a match to T7 OPS-001.

**Fix needed:** Deduplicate OPS-001. Use the T7 `OPS-001` record (operations sector, source=correlation_map) and note that the GH repo `process-automation-suite` is the repo for it (GH slug doesn't match T7's repo URL format).

---

## Data Quality Summary

| Metric | Value | Assessment |
|--------|-------|------------|
| YAML integrity | PASS | All files parse, no duplicate IDs, no empty required fields |
| Namespace consistency | PASS | All 990 repos are Worldwidebro/ |
| Venture identity coverage | 788/788 T7 + 6 GH-only | GOOD — only CON-001 and RE-001 are post-T7 |
| Sector coverage | 742/794 classified, 52 unknown | ACCEPTABLE — 6.5% need manual classification |
| Status freshness | T7 is 6 months stale | CONCERN — 622 Pre-launch may be stale |
| Repo → venture mapping | 547 matched, 343 unmatched | GOOD — 61% of owned repos mapped to ventures |
| Production visibility | 73 repos with Vercel URLs | ACCEPTABLE — 8% of owned repos have known deploys |
| Empty capability fields | All 794 ventures | EXPECTED — next pass |
| OPS-001 deduplication | NOT DONE | BUG — needs fix |

---

## Recommended Next Actions (by confidence priority)

1. **FIX OPS-001** — merge the duplicate entries, wire `process-automation-suite` as the repo.
2. **CLASSIFY 52 unknown sectors** — manual or better heuristic.
3. **VERIFY 622 Pre-launch ventures** — sample check against current reality (GitHub activity, Vercel deploys, T7 name matches).
4. **POPULATE capabilities** — extract from repo descriptions, READMEs, topics.
5. **ASSESS 870 starred external repos** — which are actually useful as capability references?
6. **REFRESH T7 snapshot** — if a newer version exists on T7 Shield.

