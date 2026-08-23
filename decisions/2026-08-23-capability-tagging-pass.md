# Capability Tagging Pass (Heuristic, Portfolio-Wide)

**Status:** Accepted
**Date:** 2026-08-23
**Decision ID:** DEC-2026-0005
**Extends:** DEC-2026-0004 (expanded-registry-architecture.md), step 2/3 of the agreed sequence.

## Context

`registry/repositories.yaml` had 0 of 1,767 records with a populated
`capabilities` field, and `registry/capabilities.yaml` was an empty template.
The user asked for capabilities across all 1,767 repos, grounded in real
source files rather than fabrication.

Located the real source data behind `reconcile_company_registry.py`:
- `/tmp/gh_repos.json` — 890 owned repos, fields `name`, `description`,
  `primaryLanguage`, `isArchived`, `createdAt`, `pushedAt`. 829/890 (93%) have
  a non-empty description.
- `/tmp/starred_repos.txt` — 877 starred repos as `owner/name` only. No
  description field exists for starred repos anywhere in the source data.

This is a hard data-quality asymmetry, not a processing gap: owned-repo tags
can be grounded in real descriptive text; starred-repo tags can only ever be
grounded in the repo name.

## Decision

Built `tag_capabilities.py` (mirrors the `reconcile_company_registry.py`
convention — a reproducible script, not a one-off edit) that:

1. Defines a fixed 34-capability taxonomy across 7 categories (matches the
   existing `Product/Infrastructure/Operations/Data/AI/Integration/Compliance`
   enum in `capability.json`).
2. Matches whole-word keywords against `name + description + language` for
   owned repos, `name` only for starred repos.
3. Writes matched capability IDs into each repo's `capabilities` field in
   `registry/repositories.yaml`.
4. Writes one entry per matched capability into `registry/capabilities.yaml`
   with `status: Proposed` and a new `provenance: inferred` field (added to
   `schemas/capability.json`) — explicitly not claiming `Live` maturity,
   which would require real audit evidence per DEC-2026-0004's
   `recommended_action` discipline.
5. Writes every repo-capability edge to `mappings/repository-capability.csv`
   with a `confidence` column (`name+description` / `name+language` /
   `name-only`) so no consumer of this data can mistake a starred-repo guess
   for an owned-repo grounded tag.

**Caught and fixed one false-positive during this pass:** "civilization" was
initially in the `venture-governance` keyword list and matched 546 repos —
not because they're governance-related, but because 443/890 owned repo
descriptions share an auto-generated `"Civilization OS — <name>"` boilerplate
prefix. Removed `civilization` from the taxonomy; kept the rest of each
description (the substantive part after the prefix), which is real per-repo
content and tags correctly against other keywords.

**Side finding, logged not resolved:** two of those boilerplate descriptions
cite yet more conflicting portfolio-scale figures — `"...for 749 ventures"`
(x2) and `"...shared governance for all 835 repos"` — additional data points
for the already-open venture/repo-count conflict tracked in memory
(`project_civilization_os_scale.md`) and `CLAUDE.md`'s "still-open" sections.
Not resolved here; flagged only.

## Results

- 818 / 1,767 repos (46%) received ≥1 capability tag.
  - Owned: 627 / 890 (70%) — real description-grounded.
  - Starred: 191 / 877 (22%) — name-only, lower confidence by construction.
- 33 / 34 taxonomy capabilities matched at least one repo (`healthcare` was
  the only unmatched capability).
- 1,176 total repo-capability edges.
- Largest capabilities: `ai-ml` (399 repos, spot-checked as genuine — this
  portfolio is heavily AI-branded), `automation-orchestration` (149),
  `venture-governance` (82, post-fix).

## What this is NOT

- Not a code-level audit. No repository's actual source was read. This is
  text pattern-matching against name/description/language only.
- Not a claim that untagged repos (949 of 1,767) lack capabilities — many
  are starred repos with no description to match against, or owned repos
  whose description didn't hit the fixed taxonomy.
- Not a `recommended_action` input on its own — per DEC-2026-0004, that
  still requires real audit evidence.

## Next steps (per the agreed sequence)

1. **Repository audit (step 2)** — for the highest-value unmatched/ambiguous
   owned repos, do a real per-repo pass (open the repo, read the README) to
   convert `inferred` capability tags into `audited` ones and fill in the 263
   owned repos this pass missed entirely.
2. **Compound-use scoring (step 4)** — now unblocked for a first pass:
   `compound_use_score` can be approximated as `count of ventures whose repos
   share a capability`, using the 1,176 edges just written, once repo→venture
   mapping (547 matched) is joined against `mappings/repository-capability.csv`.
3. **Starred-repo capability enrichment** — the 686 untagged starred repos are
   the weakest-signal part of the dataset; consider pulling real descriptions
   for them (a second `gh repo view` pass) before trusting starred-repo
   compound-use numbers at all — per DEC-2026-0004, starred repos are
   candidates, not owned assets, so this is lower priority than owned-repo
   coverage.
