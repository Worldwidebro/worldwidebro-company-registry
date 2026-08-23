#!/usr/bin/env python3
"""Enrich the capability inventory from locally available README and code files.

Remote repositories are never fabricated: records without a local clone are
reported as unavailable_for_content_audit, so a later authenticated GitHub pass
can resume them deterministically.
"""

from __future__ import annotations

import csv
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

REGISTRY = Path(__file__).resolve().parent
VAULT = REGISTRY.parent
sys.path.insert(0, str(VAULT))
from apply_capability_taxonomy import SIGNALS, contains, slug  # noqa: E402

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "vendor", "dist", "build", ".next", "coverage"}
CODE_EXTENSIONS = {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".rb", ".php", ".cs", ".sh", ".sql", ".yaml", ".yml", ".json"}
MAX_REPO_BYTES = 80_000
MAX_FILE_BYTES = 15_000


def remote_full_name(repo_dir: Path) -> str | None:
    try:
        config = (repo_dir / ".git/config").read_text(errors="ignore")
    except OSError:
        return None
    origin = re.search(r'\[remote "origin"\][^\[]*?\n\s*url\s*=\s*(\S+)', config, re.S)
    if not origin:
        return None
    url = origin.group(1).removesuffix(".git")
    match = re.search(r"github\.com[/:]([^/]+)/([^/]+)$", url, re.I)
    return f"{match.group(1)}/{match.group(2)}" if match else None


def local_clones() -> dict[str, Path]:
    found = {}
    for root, dirs, _files in os.walk(VAULT):
        has_git = ".git" in dirs
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        if not has_git:
            continue
        repo_dir = Path(root)
        full_name = remote_full_name(repo_dir)
        if full_name:
            found.setdefault(full_name.casefold(), repo_dir)
    return found


def repository_text(repo_dir: Path) -> tuple[str, int, int]:
    """Collect README text plus a bounded amount of first-party code."""
    chunks, readmes, code_files, remaining = [], 0, 0, MAX_REPO_BYTES
    for root, dirs, files in os.walk(repo_dir):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for filename in files:
            path = Path(root) / filename
            is_readme = filename.casefold().startswith("readme")
            if not is_readme and path.suffix.casefold() not in CODE_EXTENSIONS:
                continue
            try:
                if path.stat().st_size > MAX_FILE_BYTES:
                    continue
                text = path.read_text(errors="ignore")
            except OSError:
                continue
            if len(text.encode(errors="ignore")) > remaining:
                continue
            chunks.append(f"\n{path.relative_to(repo_dir)}\n{text}")
            remaining -= len(text.encode(errors="ignore"))
            readmes += int(is_readme)
            code_files += int(not is_readme)
            if remaining <= 0:
                return "\n".join(chunks), readmes, code_files
    return "\n".join(chunks), readmes, code_files


def content_capabilities(text: str) -> list[str]:
    text = text.casefold()
    return sorted({slug(label) for label, signals in SIGNALS.items() if any(contains(text, signal) for signal in signals)})


def main() -> None:
    source = REGISTRY / "audits/repository-capability-taxonomy.csv"
    rows = list(csv.DictReader(source.open()))
    clones = local_clones()
    for row in rows:
        clone = clones.get(row["full_name"].casefold())
        if not clone:
            row.update({"content_audit_status": "unavailable_for_content_audit", "local_clone": "", "readme_files_reviewed": 0, "code_files_reviewed": 0, "content_capabilities": "", "content_confidence": 0.0})
            continue
        text, readmes, code_files = repository_text(clone)
        capabilities = content_capabilities(text)
        confidence = .95 if readmes and code_files else (.85 if code_files else (.80 if readmes else 0.0))
        metadata_caps = set(filter(None, row["taxonomy_capabilities"].split(";"))) - {"unclassified"}
        final_caps = sorted(metadata_caps | set(capabilities)) or ["unclassified"]
        row.update({"content_audit_status": "content_audited", "local_clone": str(clone.relative_to(VAULT)), "readme_files_reviewed": readmes, "code_files_reviewed": code_files, "content_capabilities": ";".join(capabilities), "content_confidence": confidence, "final_taxonomy_capabilities": ";".join(final_caps), "final_confidence": max(float(row["taxonomy_confidence"]), confidence)})
    fields = list(rows[0])
    for directory in (REGISTRY / "audits", VAULT / "audits"):
        target = directory / "repository-capability-taxonomy.csv"
        with target.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader(); writer.writerows(rows)
        content_target = directory / "repository-content-audit.csv"
        with content_target.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader(); writer.writerows(rows)
    summary = {"repositories": len(rows), "content_audited": sum(r["content_audit_status"] == "content_audited" for r in rows), "unavailable_for_content_audit": sum(r["content_audit_status"] != "content_audited" for r in rows), "method": "local README and bounded first-party source scan; no remote retrieval", "next_required_input": "valid GitHub authentication or local clones for unavailable repositories"}
    (REGISTRY / "audits/content-audit-summary.yml").write_text(yaml.safe_dump(summary, sort_keys=False))
    (VAULT / "audits/content-audit-summary.yml").write_text(yaml.safe_dump(summary, sort_keys=False))
    print(yaml.safe_dump(summary, sort_keys=False))


if __name__ == "__main__":
    main()
