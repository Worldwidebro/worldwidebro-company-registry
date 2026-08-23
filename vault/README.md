# Entity Vault

Human/agent-readable Markdown dossiers, one per registry entity. This is the
narrative layer on top of the machine-readable YAML/JSON in `registry/` and
`schemas/` — not a duplicate of it. A dossier links to its registry record by
ID rather than repeating structured fields.

```
vault/
├── ventures/       one file per registry/ventures.yaml entry, named <id>.md
├── repositories/    one file per registry/repositories.yaml entry, named <id>.md
├── capabilities/    one file per registry/capabilities.yaml entry, named <id>.md
├── platforms/       one file per registry/platforms.yaml entry, named <id>.md
└── decisions/       long-form version of decisions/, cross-linked
```

**Status as of 2026-08-23: scaffolded, not populated.** No dossiers exist yet.
Registry data currently covers 1,767 repository records and a partial venture
set — do not bulk-generate dossiers for all of them from GitHub metadata
alone; that produces the same AI-generated-boilerplate problem the vault
already has elsewhere. Populate incrementally, starting with entities that
have real capability/dependency data.

`capabilities` is no longer empty (DEC-2026-0005, `tag_capabilities.py`) —
818/1,767 repos have ≥1 heuristically-inferred capability tag (627/890 owned,
confidence `name+description`; 191/877 starred, confidence `name-only`).
This is pattern-matching, not a code audit — still not a sufficient basis to
bulk-generate dossiers. `dependencies` remains 0 populated (step 3, not
started).
