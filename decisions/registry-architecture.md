# Registry Architecture Decision

**Status:** Accepted
**Date:** 2026-08-22
**Decision ID:** DEC-2026-0003

## Context

The Worldwidebro portfolio lacks a single authoritative registry that ties ventures, repositories, capabilities, platforms, and decisions together. Existing data is scattered across GitHub, Vercel, Supabase, ClickUp, and the Obsidian vault.

## Decision

We adopt `worldwidebro-company-registry` as the canonical registry repository with the following structure:

```
worldwidebro-company-registry/
├── schemas/
│   ├── venture.json
│   ├── repository.json
│   ├── capability.json
│   ├── platform.json
│   └── decision.json
├── registry/
│   ├── ventures.yaml
│   ├── repositories.yaml
│   ├── capabilities.yaml
│   ├── platforms.yaml
│   └── decisions.tsv
├── mappings/
│   ├── venture-to-opco.csv
│   ├── venture-to-sector.csv
│   └── repo-to-venture.csv
├── audits/
│   ├── repo-inventory.csv
│   ├── schema-validation.log
│   └── sync-status.md
├── decisions/
│   └── (individual DEC-YYYY-NNNN markdown records)
└── vault/
    └── (links to Obsidian notes for cross-reference)
```

## Rules

1. **Schemas are authoritative.** All registry entries must validate against the JSON schemas in `schemas/`.
2. **Registry files are the source of truth for the vault.** GitHub is the system of record; the vault mirrors via links.
3. **Decisions get unique IDs.** DEC-YYYY-NNNN format. One record per decision in `registry/decisions.tsv` plus a full markdown version in `decisions/`.
4. **Audit is recurring.** `audits/repo-inventory.csv` is regenerated from GitHub API on a schedule; `schema-validation.log` records validation runs.
5. **No duplication.** If information already exists in a higher-authority system (Supabase operational data, Vex portfolio registry), the registry references it via ID rather than copying it.

## Validation

Registry YAML/JSON entries can be validated with:

```bash
# Using Python + jsonschema
python -c "
import json, yaml, glob, jsonschema
schemas = {p.stem: json.loads(open(p).read()) for p in glob.glob('schemas/*.json')}
for f in glob.glob('registry/*.yaml'):
    data = yaml.safe_load(open(f))
    if isinstance(data, list):
        for item in data:
            if item.get('id'):
                schema_name = f.split('/')[-1].replace('.yaml','')
                jsonschema.validate(item, schemas[schema_name])
    print(f'OK: {f}')
"
```

## Ownership

Registry maintainer: Divine Johns
Review cadence: Weekly during active venture development
