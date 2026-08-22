# worldwidebro-company-registry

Canonical registry for the Worldwidebro portfolio: ventures, repositories, capabilities, platforms, and decisions.

## Structure

```
├── schemas/          # JSON schemas that validate all registry entries
├── registry/         # Empty templates and the decisions.tsv ledger
├── mappings/         # Cross-reference CSVs (venture→opco, venture→sector, repo→venture)
├── audits/           # Repo inventory, schema validation log, sync status
├── decisions/        # Individual DEC-YYYY-NNNN markdown decision records
└── vault/            # Links to Obsidian vault notes for cross-reference
```

## Rules

1. Schemas in `schemas/` are authoritative. All registry entries must validate against them.
2. `registry/decisions.tsv` is the ledger; full decision records live in `decisions/`.
3. The registry references higher-authority systems (Supabase, Vex) by ID — it never duplicates them.
4. `audits/sync-status.md` tracks whether the registry matches GitHub, Vercel, Supabase, ClickUp, and the vault.

## Validation

```bash
pip install pyyaml jsonschema
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

## Registry Maintainer

Divine Johns

## See Also

- `_SYSTEM/REPOSITORY-RULES.md` in the Obsidian vault
- `Worldwidebro/Vex` — portfolio command center
- `Worldwidebro/venture-hub` — venture loop infrastructure
