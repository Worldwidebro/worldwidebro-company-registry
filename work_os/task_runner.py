#!/usr/bin/env python3
"""
Work OS Task Execution Engine

Implements the standard task object and execution loop:

  DISCOVERED → PLANNED → READY → EXECUTING → VERIFYING → COMPLETED → MEASURED → LEARNED

Failure branch: EXECUTING → BLOCKED → ESCALATED → REPLANNED → EXECUTING

Usage:
  python3 task_runner.py --task work_os/tasks/<task-file.yaml>

The runner:
  1. Reads the task object
  2. Validates it against the schema
  3. Executes each action via available tools (terminal, file, web, etc.)
  4. Collects evidence
  5. Checks acceptance criteria
  6. Reports: status, evidence, result, measurement, lessons
"""
import argparse
import json
import os
import subprocess
import sys
import yaml
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# ── Paths ──
BASE = Path('/Users/divinejohns/Documents/Obsidian Vault/worldwidebro-company-registry')
TASKS_DIR = BASE / 'work_os' / 'tasks'
EVIDENCE_DIR = BASE / 'work_os' / 'evidence'
REPORT_DIR = BASE / 'work_os' / 'reports'

OUT = sys.stdout  # alias for print

# ── Load task ──
def load_task(path: Path) -> Dict[str, Any]:
    with open(path) as f:
        return yaml.safe_load(f)


# ── Validate task against required fields ──
def validate_task(task: Dict[str, Any]) -> List[str]:
    errors = []
    required = ['id', 'objective', 'owner', 'actions']
    for field in required:
        if field not in task or not task[field]:
            errors.append(f"Missing required field: {field}")
    if 'acceptance_criteria' in task and not isinstance(task['acceptance_criteria'], list):
        errors.append("acceptance_criteria must be a list")
    if 'actions' in task and not isinstance(task['actions'], list):
        errors.append("actions must be a list")
    return errors


# ── Execute a single action ──
def execute_action(action: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute one action and return result + evidence.
    Supported action types: terminal, file_read, file_write, check, web_search, web_extract
    """
    action_type = action.get('type', 'terminal')
    description = action.get('description', '')
    result = {
        'action': description,
        'type': action_type,
        'status': 'pending',
        'output': '',
        'error': None,
        'timestamp': datetime.now(timezone.utc).isoformat(),
    }

    try:
        if action_type == 'terminal':
            cmd = action.get('command', '')
            if not cmd:
                result['status'] = 'failed'
                result['error'] = 'No command specified'
                return result
            proc = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
                timeout=action.get('timeout', 120), cwd=action.get('workdir', BASE)
            )
            result['status'] = 'success' if proc.returncode == 0 else 'failed'
            result['output'] = proc.stdout[:10000]
            if proc.stderr:
                result['output'] += '\n--- stderr ---\n' + proc.stderr[:5000]
            result['returncode'] = proc.returncode

        elif action_type == 'file_read':
            path = action.get('path', '')
            if not path:
                result['status'] = 'failed'
                result['error'] = 'No path specified'
                return result
            full_path = Path(path)
            if not full_path.exists():
                result['status'] = 'failed'
                result['error'] = f"File not found: {path}"
                return result
            limit = action.get('limit', 2000)
            offset = action.get('offset', 1)
            content_lines = []
            with open(full_path) as f:
                for i, line in enumerate(f, 1):
                    if i >= offset and i < offset + limit:
                        content_lines.append(f"{i}|{line.rstrip()}")
            result['status'] = 'success'
            result['output'] = '\n'.join(content_lines)
            result['total_lines'] = sum(1 for _ in open(full_path))

        elif action_type == 'file_write':
            path = action.get('path', '')
            content = action.get('content', '')
            if not path:
                result['status'] = 'failed'
                result['error'] = 'No path specified'
                return result
            full_path = Path(path)
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
            result['status'] = 'success'
            result['output'] = f"Wrote {len(content)} bytes to {path}"

        elif action_type == 'check':
            check_type = action.get('check_type', 'file_exists')
            if check_type == 'file_exists':
                path = action.get('path', '')
                exists = Path(path).exists()
                result['status'] = 'success' if exists else 'failed'
                result['output'] = f"File exists: {exists}"
            elif check_type == 'yaml_parse':
                path = action.get('path', '')
                try:
                    with open(path) as f:
                        data = yaml.safe_load(f)
                    result['status'] = 'success'
                    result['output'] = f"Parsed OK, type={type(data).__name__}"
                    result['data_summary'] = str(data)[:500] if data else 'empty'
                except Exception as e:
                    result['status'] = 'failed'
                    result['error'] = str(e)
            elif check_type == 'grep':
                path = action.get('path', '')
                pattern = action.get('pattern', '')
                try:
                    with open(path) as f:
                        matches = [line.strip() for line in f if pattern in line]
                    result['status'] = 'success'
                    result['output'] = f"Found {len(matches)} matches"
                    result['matches'] = matches[:20]
                except Exception as e:
                    result['status'] = 'failed'
                    result['error'] = str(e)
            elif check_type == 'count':
                path = action.get('path', '')
                try:
                    with open(path) as f:
                        count = sum(1 for _ in f)
                    result['status'] = 'success'
                    result['output'] = f"Line count: {count}"
                except Exception as e:
                    result['status'] = 'failed'
                    result['error'] = str(e)
            else:
                result['status'] = 'failed'
                result['error'] = f"Unknown check_type: {check_type}"

        elif action_type == 'web_search':
            result['status'] = 'skipped'
            result['output'] = 'web_search not available in this context — use Hermes web_search tool directly'

        elif action_type == 'web_extract':
            result['status'] = 'skipped'
            result['output'] = 'web_extract not available in this context — use Hermes web_extract tool directly'

        else:
            result['status'] = 'failed'
            result['error'] = f"Unknown action type: {action_type}"

    except subprocess.TimeoutExpired:
        result['status'] = 'failed'
        result['error'] = 'Command timed out'
    except Exception as e:
        result['status'] = 'failed'
        result['error'] = str(e)

    return result


# ── Evaluate a single acceptance criterion ──
def evaluate_criterion(criterion: str, action_results: List[Dict], task: Dict) -> Dict[str, Any]:
    """
    Evaluate a criterion against action results.
    Heuristics:
    - If criterion mentions 'exists' or 'found' → check if any action succeeded with relevant output
    - If criterion mentions 'status' → check last action result
    - If criterion mentions 'verified' → check if any check action passed
    - Default: look for any successful action whose output contains keywords from criterion
    """
    criterion_lower = criterion.lower()

    for ar in action_results:
        if ar['status'] == 'success':
            output = ar['output'].lower()
            action_desc = ar.get('action', '').lower()

            if ar.get('type') == 'check' and ar['status'] == 'success':
                return {'passed': True, 'evidence': f"Check action succeeded: {ar.get('output', '')[:200]}"}

            if 'exists' in criterion_lower and ar.get('type') == 'file_read' and ar['status'] == 'success':
                return {'passed': True, 'evidence': f"File read successfully: {ar.get('output', '')[:200]}"}

            if 'status' in criterion_lower and ar.get('type') == 'terminal' and ar['status'] == 'success':
                return {'passed': True, 'evidence': f"Command succeeded, exit 0"}

            if 'verified' in criterion_lower and ar.get('type') == 'check' and ar['status'] == 'success':
                return {'passed': True, 'evidence': f"Verification check passed: {ar.get('output', '')[:200]}"}

            # Generic: if output contains key phrases from criterion
            criterion_words = set(criterion_lower.replace(',', '').replace('.', '').split())
            output_words = set(output.replace(',', '').replace('.', '').split())
            overlap = criterion_words & output_words
            if len(overlap) >= 2:
                return {'passed': True, 'evidence': f"Action output contains criterion terms: {overlap}"}

    # All actions succeeded?
    all_success = all(ar['status'] == 'success' for ar in action_results)
    if all_success and action_results:
        return {'passed': True, 'evidence': 'All actions succeeded'}

    return {'passed': False, 'evidence': 'No matching successful action found'}


# ── Run the task ──
def run_task(task: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a task through the full loop.
    Returns the task result with evidence, status, acceptance check.
    """
    task_id = task['id']
    objective = task['objective']
    owner = task.get('owner', 'unassigned')
    print(f"\n{'='*60}\n")
    print(f"TASK: {task_id}\n")
    print(f"OBJECTIVE: {objective}\n")
    print(f"OWNER: {owner}\n")
    print(f"{'='*60}\n\n")

    state = 'DISCOVERED'
    evidence = []
    errors = []

    # ── DISCOVERED → PLANNED ──
    print(f"[DISCOVERED] Task loaded. Validating...\n")
    validation_errors = validate_task(task)
    if validation_errors:
        for err in validation_errors:
            print(f"  VALIDATION ERROR: {err}\n")
        state = 'BLOCKED'
        evidence.append({'phase': 'DISCOVERED', 'status': 'blocked', 'reason': validation_errors})
        return {'task_id': task_id, 'state': state, 'evidence': evidence,
                'result': {'status': 'blocked', 'errors': validation_errors}}

    print(f"  Valid. Planning execution of {len(task['actions'])} actions...\n")
    state = 'PLANNED'
    evidence.append({'phase': 'PLANNED', 'status': 'planned', 'actions_count': len(task['actions'])})

    # ── PLANNED → READY ──
    print(f"[PLANNED] Checking dependencies...\n")
    deps = task.get('dependencies', [])
    dep_status = []
    for dep in deps:
        dep_ok = True
        dep_note = ''
        if dep == 'github access':
            try:
                proc = subprocess.run(['gh', 'auth', 'status'], capture_output=True, text=True, timeout=10)
                dep_ok = proc.returncode == 0
                dep_note = 'gh authenticated' if dep_ok else 'gh not authenticated'
            except Exception:
                dep_ok = False
                dep_note = 'gh check failed'
        elif dep == 'vercel deploy status':
            vercel_path = BASE / 'vercel_deployments.csv'
            dep_ok = vercel_path.exists()
            dep_note = 'vercel_deployments.csv found' if dep_ok else 'vercel_deployments.csv missing'
        elif dep == 'registry access':
            reg_path = BASE / 'registry' / 'ventures.yaml'
            dep_ok = reg_path.exists()
            dep_note = 'registry/ventures.yaml found' if dep_ok else 'registry/ventures.yaml missing'
        else:
            dep_note = f"Dependency '{dep}' not auto-checkable — assume available"
            dep_ok = True
        dep_status.append({'dependency': dep, 'available': dep_ok, 'note': dep_note})
        if not dep_ok:
            print(f"  DEPENDENCY MISSING: {dep} — {dep_note}\n")

    all_deps_ok = all(d['available'] for d in dep_status)
    state = 'READY' if all_deps_ok else 'BLOCKED'
    evidence.append({'phase': 'READY', 'status': 'ready' if all_deps_ok else 'blocked',
                     'dependencies': dep_status})
    if not all_deps_ok:
        print(f"  BLOCKED: missing dependencies\n")
        return {'task_id': task_id, 'state': state, 'evidence': evidence,
                'result': {'status': 'blocked', 'missing_dependencies': [d['dependency'] for d in dep_status if not d['available']]}}

    print(f"  All dependencies available. Ready to execute.\n")
    state = 'EXECUTING'
    evidence.append({'phase': 'EXECUTING', 'status': 'executing', 'started_at': datetime.now(timezone.utc).isoformat()})

    # ── EXECUTING → actions ──
    print(f"\n[EXECUTING] Running {len(task['actions'])} actions...\n\n")
    action_results = []
    for i, action in enumerate(task['actions'], 1):
        action_id = f"{task_id}-action-{i}"
        desc = action.get('description', action.get('type', '?'))
        print(f"  [{i}/{len(task['actions'])}] {desc} ...", end=' ')
        result = execute_action(action)
        action_results.append({'action_id': action_id, **result})
        evidence.append({'phase': 'EXECUTING', 'action': action_id, 'status': result['status'],
                         'output_preview': (result['output'] or '')[:200]})
        if result['status'] == 'success':
            print("✓\n")
        elif result['status'] == 'failed':
            print(f"✗ {result['error']}\n")
            errors.append({'action': action_id, 'error': result['error']})
        elif result['status'] == 'skipped':
            print(f"? skipped\n")
        else:
            print(f"? {result['status']}\n")

    # ── VERIFYING → acceptance criteria ──
    criteria = task.get('acceptance_criteria', [])
    print(f"\n[VERIFYING] Checking {len(criteria)} acceptance criteria...\n\n")
    criteria_results = []
    for j, criterion in enumerate(criteria, 1):
        criterion_id = f"{task_id}-criterion-{j}"
        print(f"  [{j}/{len(criteria)}] {criterion} ...", end=' ')
        cr = evaluate_criterion(criterion, action_results, task)
        criteria_results.append({'criterion_id': criterion_id, 'criterion': criterion,
                                 'passed': cr['passed'], 'evidence': cr['evidence']})
        evidence.append({'phase': 'VERIFYING', 'criterion': criterion_id,
                         'passed': cr['passed'], 'evidence': cr['evidence']})
        if cr['passed']:
            print("✓\n")
        else:
            print(f"✗ — {cr['evidence']}\n")

    all_criteria_passed = all(cr['passed'] for cr in criteria_results)
    criteria_passed_count = sum(cr['passed'] for cr in criteria_results)
    print(f"\n  Acceptance criteria: {criteria_passed_count}/{len(criteria_results)} passed\n")

    if all_criteria_passed:
        state = 'COMPLETED'
        print(f"\n[COMPLETED] All criteria met.\n")
    else:
        state = 'BLOCKED'
        print(f"\n[BLOCKED] {len(criteria_results) - criteria_passed_count} criteria failed.\n")

    evidence.append({'phase': 'VERIFYING', 'status': 'completed' if all_criteria_passed else 'blocked',
                     'criteria_passed': criteria_passed_count, 'criteria_total': len(criteria_results)})

    # ── MEASURED ──
    measurement = {
        'duration_seconds': 0,
        'actions_total': len(action_results),
        'actions_success': sum(1 for ar in action_results if ar['status'] == 'success'),
        'actions_failed': sum(1 for ar in action_results if ar['status'] == 'failed'),
        'actions_skipped': sum(1 for ar in action_results if ar['status'] == 'skipped'),
        'criteria_total': len(criteria_results),
        'criteria_passed': criteria_passed_count,
        'criteria_failed': len(criteria_results) - criteria_passed_count,
        'all_criteria_passed': all_criteria_passed,
    }
    evidence.append({'phase': 'MEASURED', 'measurement': measurement})
    print(f"\n[MEASURED] Actions: {measurement['actions_success']}/{measurement['actions_total']} success | "
              f"Criteria: {criteria_passed_count}/{len(criteria_results)} passed\n")

    state = 'MEASURED'

    # ── LEARNED ──
    lessons = []
    if measurement['actions_success'] > 0:
        lessons.append(f"{measurement['actions_success']}/{measurement['actions_total']} actions succeeded")
    for ar in action_results:
        if ar['status'] == 'failed':
            lessons.append(f"Action '{ar.get('action', '')}' failed: {ar.get('error', '')}")
    for cr in criteria_results:
        if not cr['passed']:
            lessons.append(f"Criterion '{cr['criterion']}' not met")
    if all_criteria_passed:
        lessons.append(f"Task {task_id}: COMPLETED — all {measurement['criteria_total']} criteria met")
    else:
        lessons.append(f"Task {task_id}: BLOCKED — {measurement['criteria_failed']}/{measurement['criteria_total']} criteria failed")

    evidence.append({'phase': 'LEARNED', 'lessons': lessons})
    state = 'LEARNED'
    print(f"\n[LEARNED] Lessons: {len(lessons)} extracted\n")

    # ── Result ──
    result = {
        'task_id': task_id,
        'objective': objective,
        'state': state,
        'status': 'completed' if all_criteria_passed else 'blocked',
        'started_at': evidence[2]['started_at'] if len(evidence) > 2 else None,
        'completed_at': datetime.now(timezone.utc).isoformat(),
        'duration_seconds': measurement['duration_seconds'],
        'actions_total': measurement['actions_total'],
        'actions_success': measurement['actions_success'],
        'actions_failed': measurement['actions_failed'],
        'criteria_total': measurement['criteria_total'],
        'criteria_passed': measurement['criteria_passed'],
        'criteria_failed': measurement['criteria_failed'],
        'action_results': action_results,
        'criteria_results': criteria_results,
        'lessons': lessons,
        'dependencies': dep_status,
    }

    return {'task_id': task_id, 'state': state, 'evidence': evidence, 'result': result}


# ── Save evidence + report ──
def save_result(task_id: str, result: Dict[str, Any], evidence: List[Dict]):
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    ev_path = EVIDENCE_DIR / f'{task_id}.yaml'
    with open(ev_path, 'w') as f:
        yaml.dump({'task_id': task_id, 'evidence': evidence,
                   'result': result, 'completed_at': datetime.now(timezone.utc).isoformat()}, f,
                  default_flow_style=False, sort_keys=False)

    report_path = REPORT_DIR / f'{task_id}.md'
    lines = [
        f"# Task Report: {task_id}",
        "",
        f"**Objective:** {result['objective']}",
        f"**State:** {result['state']}",
        f"**Status:** {result['status']}",
        f"**Started:** {result['started_at']}",
        f"**Completed:** {result['completed_at']}",
        "",
        "## Actions",
        "",
        "| # | Type | Description | Status | Output |",
        "|---|------|-------------|--------|--------|",
    ]
    for ar in result['action_results']:
        preview = (ar.get('output', '') or '')[:80].replace('\n', ' ')
        lines.append(f"| {ar['action_id'].split('-')[-1]} | {ar.get('type', '?')} | "
                     f"{ar.get('action', '?')} | {ar['status']} | {preview} |")
    lines.extend([
        "",
        "## Acceptance Criteria",
        "",
        "| # | Criterion | Passed | Evidence |",
        "|---|-----------|--------|----------|",
    ])
    for cr in result['criteria_results']:
        preview = (cr.get('evidence', '') or '')[:80].replace('\n', ' ')
        lines.append(f"| {cr['criterion_id'].split('-')[-1]} | {cr['criterion']} | "
                     f"{'✓' if cr['passed'] else '✗'} | {preview} |")
    lines.extend([
        "",
        "## Dependencies",
        "",
    ])
    for dep in result.get('dependencies', []):
        lines.append(f"- **{dep['dependency']}**: {'✅' if dep['available'] else '❌'} {dep['note']}")
    lines.extend([
        "",
        "## Lessons",
        "",
    ])
    for lesson in result.get('lessons', []):
        lines.append(f"- {lesson}")
    lines.extend([
        "",
        f"## Evidence",
        "",
        f"Full evidence: `{ev_path}`",
        "",
    ])
    with open(report_path, 'w') as f:
        f.write('\n'.join(lines))

    print(f"\n{'='*60}\n")
    print(f"Evidence saved: {ev_path}\n")
    print(f"Report saved: {report_path}\n")
    print(f"{'='*60}\n")
    return ev_path, report_path


# ── Main ──
def main():
    parser = argparse.ArgumentParser(description='Work OS Task Runner')
    parser.add_argument('--task', '-t', required=True, help='Path to task YAML file')
    parser.add_argument('--evidence-dir', default=str(EVIDENCE_DIR), help='Evidence output dir')
    parser.add_argument('--report-dir', default=str(REPORT_DIR), help='Report output dir')
    args = parser.parse_args()

    evidence_dir_arg = Path(args.evidence_dir)
    report_dir_arg = Path(args.report_dir)
    evidence_dir_arg.mkdir(parents=True, exist_ok=True)
    report_dir_arg.mkdir(parents=True, exist_ok=True)

    task_path = Path(args.task)
    if not task_path.exists():
        print(f"ERROR: Task file not found: {task_path}\n", file=sys.stderr)
        sys.exit(1)

    print(f"Loading task: {task_path}\n", file=sys.stderr)
    task = load_task(task_path)

    result = run_task(task)
    evidence = result['evidence']

    # Use the args-based dirs for saving
    ev_path = evidence_dir_arg / f'{task["id"]}.yaml'
    report_path = report_dir_arg / f'{task["id"]}.md'

    # Save manually with the right paths
    with open(ev_path, 'w') as ef:
        yaml.dump({'task_id': task['id'], 'evidence': evidence,
                   'result': result['result'], 'completed_at': datetime.now(timezone.utc).isoformat()}, ef,
                  default_flow_style=False, sort_keys=False)
    lines = [
        f"# Task Report: {task['id']}",
        "",
        f"**Objective:** {result['result']['objective']}",
        f"**State:** {result['result']['state']}",
        f"**Status:** {result['result']['status']}",
        f"**Started:** {result['result']['started_at']}",
        f"**Completed:** {result['result']['completed_at']}",
        "",
        "## Actions",
        "",
        "| # | Type | Description | Status | Output |",
        "|---|------|-------------|--------|--------|",
    ]
    for ar in result['result']['action_results']:
        preview = (ar.get('output', '') or '')[:80].replace('\n', ' ')
        lines.append(f"| {ar['action_id'].split('-')[-1]} | {ar.get('type', '?')} | "
                     f"{ar.get('action', '?')} | {ar['status']} | {preview} |")
    lines.extend([
        "",
        "## Acceptance Criteria",
        "",
        "| # | Criterion | Passed | Evidence |",
        "|---|-----------|--------|----------|",
    ])
    for cr in result['result']['criteria_results']:
        preview = (cr.get('evidence', '') or '')[:80].replace('\n', ' ')
        lines.append(f"| {cr['criterion_id'].split('-')[-1]} | {cr['criterion']} | "
                     f"{'✓' if cr['passed'] else '✗'} | {preview} |")
    lines.extend([
        "",
        "## Dependencies",
        "",
    ])
    for dep in result['result'].get('dependencies', []):
        lines.append(f"- **{dep['dependency']}**: {'✅' if dep['available'] else '❌'} {dep['note']}")
    lines.extend([
        "",
        "## Lessons",
        "",
    ])
    for lesson in result['result'].get('lessons', []):
        lines.append(f"- {lesson}")
    lines.extend([
        "",
        f"## Evidence",
        "",
        f"Full evidence: `{ev_path}`",
        "",
    ])
    with open(report_path, 'w') as rf:
        rf.write('\n'.join(lines))

    status = result['result']['status']
    print(f"\nFINAL STATUS: {status.upper()}\n", file=sys.stderr)
    print(f"Evidence: {ev_path}\n", file=sys.stderr)
    print(f"Report: {report_path}\n", file=sys.stderr)
    sys.exit(0 if status == 'completed' else 1)


if __name__ == '__main__':
    main()
