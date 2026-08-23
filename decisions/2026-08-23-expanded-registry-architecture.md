# Expanded Registry Architecture Decision

**Status:** Accepted
**Date:** 2026-08-23
**Decision ID:** DEC-2026-0004
**Supersedes/extends:** DEC-2026-0003 (registry-architecture.md) — does not replace it, adds to it.

## Context

DEC-2026-0003 (2026-08-22) established `worldwidebro-company-registry` with a
`schemas/registry/mappings/audits/decisions/vault` structure. The 2026-08-22
reconciliation (`audits/reconciliation-summary.yml`) populated
`registry/ventures.yaml` and `registry/repositories.yaml` (1,767 records — 890
owned + 877 starred — 547 matched to a venture) but left `capabilities.yaml`
and `platforms.yaml` as empty templates, and left `vault/` empty.

Reviewing the 343 unmatched owned repos surfaced a concrete need: many
"unclassified" repos (e.g. `civilization-os`, `iza-os-core`, `Vex`,
`avs-omni`) are not ventures at all — they're shared infrastructure platforms
that many ventures depend on. The existing `platform.json` schema only
modeled "distribution channel a single venture reaches customers through"
(App Store, Marketplace...), which doesn't fit this at all — using it as-is
would have conflated two different meanings under one field.

## Decision

Extend, don't replace, the DEC-2026-0003 structure:

1. **Four identities stay four identities.** Venture, Repository, Capability,
   Platform remain separate schemas. `platform.json` now has a `type`
   discriminator (`Shared Infrastructure` vs. distribution-channel types) and
   separate relationship fields (`serves_ventures`/`provides_capabilities` for
   shared infra, `venture` for distribution channels) so the two meanings
   don't collide.
2. **Compound-use scoring is now a first-class field**, not a separate
   system: `repository.json`, `venture.json`, and `platform.json` all gained
   `compound_use_score` (0-100, nullable) and `criticality` (P0-P3, nullable).
   Left null everywhere — scoring requires real dependency data, which does
   not exist yet (0 of 1,767 repository records have `capabilities` or
   `dependencies` populated).
3. **`recommended_action`** added to `repository.json` with the KEEP /
   STANDARDIZE / MERGE / FORK / EXTRACT / RENAME / ARCHIVE / REFERENCE /
   REPLACE / BUILD enum. Left null for every record — per explicit
   instruction, this must be earned by the repository audit, not inferred
   from a name pattern.
4. **Four new mapping files** added as empty CSV templates (matching the
   existing CSV convention in `mappings/`, not the YAML the original proposal
   sketched): `repository-capability.csv`, `repository-repository.csv`
   (dependency graph), `venture-stack.csv`, `portal-repository.csv`.
5. **`vault/` scaffolded** with a README describing the Entity Vault
   Markdown-dossier layer and subfolder structure. Explicitly not bulk-
   generated — dossiers get written once there's real capability/dependency
   data behind them, not from GitHub metadata alone.
6. **`registry/platforms.yaml` populated** with 4 confirmed real entries
   (`IZA-OS` → `iza-os-core`, `CIV-OS` → `civilization-os`, `VEX` → `Vex`,
   `AVS` → `avs-omni`), each sourced from an actual `registry/repositories.yaml`
   record, not invented. Two open items logged inline rather than resolved:
   `civilization-os`'s own README claims "238 repositories" (a fifth
   conflicting portfolio-scale figure); `Avs-Omni-` exists as a likely
   duplicate of `avs-omni`.

## Explicitly deferred (not done in this decision)

- Populating `capabilities.yaml` or any repository's `capabilities`/
  `dependencies` fields — this is the repository audit + capability graph
  phase (steps 2-3 of the agreed order below), a much larger task requiring
  per-repo analysis, not done in bulk here.
- Any `recommended_action` value — none set.
- Any rename, merge, archive, or fork of any repository.
- Resolving the three-way canonical-portfolio-repo conflict (`Vex` vs.
  `worldwidebro-venture-portal` vs. `worldwidebro-company-registry` itself)
  or the fifth venture-count figure (`civilization-os`'s "238 repositories").

## Agreed sequence going forward

```
1. Canonical registry           <- DEC-2026-0003 + this decision (mostly done)
2. Repository audit             <- next
3. Capability + dependency graph
4. Compound-use scoring
5. Portal design (views over one registry)
6. Consolidation plan
7. Rename / migration
```

Explicitly not renaming any of the 889/890 repos before step 6-7.

## Ownership

Registry maintainer: Divine Johns
Review cadence: Weekly during active venture development
