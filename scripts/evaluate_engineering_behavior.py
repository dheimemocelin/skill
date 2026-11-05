#!/usr/bin/env python3
"""Real, opt-in paired provider evaluation. No simulated provider results."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys
import subprocess
import tempfile

import run_agent_smoke_tests as smoke

ROOT = Path(__file__).resolve().parents[1]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def final_response(events):
    messages = [e['item'].get('text', '') for e in events
                if e.get('type') == 'item.completed' and e.get('item', {}).get('type') == 'agent_message']
    return messages[-1] if messages else ''


def trace_strings(stdout):
    """Read only the native session of this invocation; not global search hits."""
    events = smoke.event_records('codex', stdout)
    tid = next((e.get('thread_id') for e in events if e.get('type') == 'thread.started'), None)
    if not tid:
        return [], None
    import os
    home = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))
    paths = list((home / 'sessions').rglob(f'*-{tid}.jsonl'))
    if len(paths) != 1:
        return [], tid
    strings = []
    def walk(value):
        if isinstance(value, str):
            strings.append(value)
            try:
                decoded = json.loads(value)
            except ValueError:
                return
            if decoded != value:
                walk(decoded)
        elif isinstance(value, dict):
            for nested in value.values():
                walk(nested)
        elif isinstance(value, list):
            for nested in value:
                walk(nested)
    for line in paths[0].read_text().splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        # Only actual tool outputs establish a read; prompt/assistant text cannot.
        if event.get('type') == 'response_item' and event.get('payload', {}).get('type') in {'function_call_output', 'custom_tool_call_output'}:
            walk(event['payload'].get('output'))
    return strings, tid


def parse_answer(text):
    text = text.strip()
    if text.startswith('```'):
        text = '\n'.join(text.splitlines()[1:-1])
    try:
        return json.loads(text)
    except ValueError:
        return None


def sandbox_blocked(events, native_tool_outputs=()):
    error = 'bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted'
    return any(error in value for value in native_tool_outputs) or any(e.get('type') == 'item.completed'
               and e.get('item', {}).get('type') == 'command_execution'
               and 'bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted' in e['item'].get('aggregated_output', '')
               for e in events)


def mechanical_checks(case, answer, events, unchanged, text):
    completed = any(e.get('type') == 'turn.completed' for e in events)
    commands = [e for e in events if e.get('type') == 'item.completed' and e.get('item', {}).get('type') == 'command_execution']
    checks = {'terminal_event': completed, 'fixture_unchanged': unchanged}
    if case['kind'] == 'negative':
        checks['no_command_execution'] = not commands
        checks['nonempty_answer'] = bool(text.strip())
    elif case['kind'] == 'architecture':
        checks['sync_selected'] = isinstance(answer, dict) and answer.get('choice') == 'sync'
        checks['decision_explained'] = isinstance(answer, dict) and all(answer.get(k) for k in ['rationale', 'revisit_condition', 'tradeoffs'])
    else:
        findings = answer.get('findings', []) if isinstance(answer, dict) else []
        checks['structured_findings'] = bool(findings) and all(isinstance(f, dict) and all(f.get(k) for k in (['file', 'line', 'impact', 'scenario', 'fix'] if case['kind'] == 'security' else ['field', 'impact', 'scenario', 'fix'])) for f in findings)
        if case['kind'] == 'security':
            location = case.get('expected_location', {'file': 'customer.py', 'lines': [2, 3]})
            checks['correct_file_location'] = any(f.get('file') == location['file'] and f.get('line') in location['lines'] for f in findings if isinstance(f, dict))
    return checks


def allowed_fixture_changes(changed, allowed, index_unchanged):
    """Allow declared sources and Python test bytecode, never hidden source/config edits."""
    def permitted(name):
        path = Path(name)
        if name in allowed:
            return True
        source = path.parent.parent / (path.name.split('.', 1)[0] + '.py')
        return path.parent.name == '__pycache__' and path.suffix == '.pyc' and source.as_posix() in allowed
    return index_unchanged and all(permitted(name) for name in changed)


def evaluate(provider, variant, name, case, output, baseline, timeout, baseline_skills=None):
    case_dir = output / provider / variant / name
    case_dir.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix='engos-behavior-') as temporary:
        workspace = Path(temporary)
        smoke.prepare_workspace(provider, smoke.Case(name, None, case['prompt'], case['files'], {}), workspace)
        skill_root = workspace / ('.agents' if provider == 'codex' else '.claude') / 'skills'
        if variant == 'baseline' and baseline_skills:
            shutil.rmtree(skill_root)
            shutil.copytree(baseline_skills, skill_root)
        elif variant == 'baseline':
            shutil.rmtree(skill_root)
            skill_root.mkdir()
            listing = subprocess.run(['git', 'ls-tree', '-r', '--name-only', baseline, 'skills'], cwd=ROOT, capture_output=True, text=True, check=True)
            for relative in listing.stdout.splitlines():
                data = subprocess.run(['git', 'show', f'{baseline}:{relative}'], cwd=ROOT, capture_output=True, check=True).stdout
                dest = skill_root / Path(relative).relative_to('skills')
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(data)
        if case.get('project_guidance'):
            guidance = (ROOT / 'templates/AGENTS.md').read_text() if variant == 'current' else subprocess.run(
                ['git', 'show', f'{baseline}:templates/AGENTS.md'], cwd=ROOT, capture_output=True, text=True, check=True).stdout
            (workspace / 'AGENTS.md').write_text(guidance)
        if 'staged' in case:
            smoke.run(['git', '-c', 'user.name=Evaluation', '-c', 'user.email=evaluation@example.invalid', 'add', 'customer.py'], cwd=workspace)
            smoke.run(['git', '-c', 'user.name=Evaluation', '-c', 'user.email=evaluation@example.invalid', 'commit', '-qm', 'fixture'], cwd=workspace)
            (workspace / 'customer.py').write_text(case['staged'])
            smoke.run(['git', 'add', 'customer.py'], cwd=workspace)
            (workspace / 'customer.py').write_text(case['files']['customer.py'])
        initial = smoke.snapshot(workspace)
        index_before = smoke.run(['git', 'diff', '--cached'], cwd=workspace).stdout
        config_hashes = {str(p.relative_to(workspace)): digest(p.read_bytes()) for p in workspace.rglob('*') if p.is_file() and any(x in p.parts for x in ['skills', 'agents'])}
        bodies = {skill: (skill_root / skill / 'SKILL.md').read_text().split('---', 2)[-1].strip() for skill in smoke.ALL_SKILLS}
        reference = skill_root / case['reference'] if case.get('reference') else None
        reference_body = reference.read_text().strip() if reference and reference.exists() else None
        command, version = smoke.provider_command(provider, workspace, case['prompt'], case.get('read_only', True))
        # Keep the existing configured provider/model. No credentials are copied.
        created, added = smoke.add_smoke_trust_entry(workspace) if provider == 'codex' else (False, False)
        started = datetime.now(timezone.utc).isoformat()
        try:
            result = subprocess.run(command, cwd=workspace, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            (case_dir / 'stdout.jsonl').write_bytes(exc.stdout or b'')
            return {'result': 'blocked', 'reason': 'provider_timeout', 'started': started}
        finally:
            if provider == 'codex':
                smoke.remove_smoke_trust_entry(workspace, created, added)
        (case_dir / 'stdout.jsonl').write_text(result.stdout)
        (case_dir / 'stderr.txt').write_text(result.stderr)
        events = smoke.event_records(provider, result.stdout)
        text = final_response(events) if provider == 'codex' else ''
        (case_dir / 'answer.txt').write_text(text)
        answer = parse_answer(text)
        strings, tid = trace_strings(result.stdout) if provider == 'codex' else ([], None)
        loaded = [s for s, body in bodies.items() if any(body in value for value in strings)]
        ref_loaded = bool(reference_body and any(reference_body in value for value in strings))
        final = smoke.snapshot(workspace)
        changed = sorted(k for k in set(initial) | set(final) if initial.get(k) != final.get(k))
        index_unchanged = index_before == smoke.run(['git', 'diff', '--cached'], cwd=workspace).stdout
        unchanged = not changed and index_unchanged
        validations = []
        for number, code in enumerate(case.get('validations', [])):
            checked = subprocess.run([sys.executable, '-I', '-c', code], cwd=workspace, capture_output=True, text=True, timeout=30)
            (case_dir / f'validation-{number}.txt').write_text(checked.stdout + checked.stderr)
            validations.append({'command': [sys.executable, '-I', '-c', '<versioned fixture assertion>'], 'scope': f'validation {number}', 'exit_code': checked.returncode})
        if case.get('read_only', True):
            checks = mechanical_checks(case, answer, events, unchanged, text)
        else:
            checks = {'terminal_event': any(e.get('type') == 'turn.completed' for e in events),
                      'only_allowed_files_changed': allowed_fixture_changes(changed, case['allowed_changes'], index_unchanged),
                      'independent_validations': bool(validations) and all(v['exit_code'] == 0 for v in validations)}
        usage = smoke.codex_token_usage(result.stdout)

        for relative in set(case['files']) | set(case.get('allowed_changes', [])):
            artifact = workspace / relative
            if artifact.is_file() and artifact.resolve().is_relative_to(workspace.resolve()):
                dest = case_dir / 'artifacts' / relative
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(artifact.read_bytes())
        quota = smoke.provider_quota_blocked(result.stdout, result.stderr)
        infrastructure = sandbox_blocked(events, strings)
        return {'result': 'blocked' if quota or infrastructure else 'mechanical_pass' if result.returncode == 0 and all(checks.values()) else 'failed',
                'block_reason': 'sandbox_unavailable' if infrastructure else 'quota' if quota else None,
                'exit_code': result.returncode, 'version': version, 'thread_id': tid, 'started': started,
                'finished': datetime.now(timezone.utc).isoformat(), 'checks': checks,
                'skills_observed_in_tool_output': loaded, 'reference_observed_in_tool_output': ref_loaded,
                'reference_sha256': digest(reference_body.encode()) if reference_body else None,
                'codex_token_usage': usage, 'usage_basis': 'native_session_counters' if usage else 'unavailable',
                'changed_files': changed, 'index_unchanged': index_unchanged, 'independent_validations': validations,
                'fixture_final_sha256': {k: final.get(k) for k in case['files']},
                'configuration_sha256': config_hashes, 'fixture_initial_sha256': {k: initial[k] for k in case['files']},
                'stdout_sha256': digest(result.stdout.encode()), 'answer': answer, 'answer_text': text,
                'semantic_verdict': 'pending_manual_review', 'limits': 'Mechanical checks are not semantic approval; exact tool output reads establish loading, not causal effectiveness.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--provider', choices=['codex', 'claude', 'all'], default='all')
    parser.add_argument('--execute', action='store_true', help='Authorize real provider calls/quota')
    parser.add_argument('--baseline', default='9a774be')
    parser.add_argument('--case', action='append')
    parser.add_argument('--cases-file', type=Path, default=ROOT / 'examples/behavioral/cases.json')
    parser.add_argument('--baseline-skills', type=Path, help='Complete preserved pre-fix skills tree for a local paired evaluation')
    parser.add_argument('--timeout', type=int, default=180)
    args = parser.parse_args()
    if not args.execute:
        parser.error('Real evaluation requires --execute; no simulated mode exists')
    cases = json.loads(args.cases_file.read_text())
    if args.baseline_skills and {p.parent.name for p in args.baseline_skills.glob('*/SKILL.md')} != set(smoke.ALL_SKILLS):
        parser.error('Baseline snapshot must contain all canonical skills')
    if args.case and set(args.case) - cases.keys():
        parser.error('Unknown case')
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    output = ROOT / '.local-evidence/behavioral' / run_id
    output.mkdir(parents=True)
    summary = {'run_id': run_id, 'baseline': 'local-preserved-snapshot' if args.baseline_skills else args.baseline, 'case_spec_sha256': digest(args.cases_file.read_bytes()), 'providers': {}}
    for provider in (['codex', 'claude'] if args.provider == 'all' else [args.provider]):
        try:
            smoke.provider_command(provider, ROOT, '', True)
        except FileNotFoundError as exc:
            summary['providers'][provider] = {'status': 'not_run', 'reason': str(exc)}
            continue
        if provider != 'codex':
            summary['providers'][provider] = {'status': 'not_run', 'reason': 'This evaluator needs native output extraction for this provider; existing smoke runner supports separate Claude tests.'}
            continue
        outcomes = {}
        summary['providers'][provider] = outcomes
        blocked = False
        for name, case in cases.items():
            if args.case and name not in args.case:
                continue
            outcomes[name] = {}
            for variant in ['baseline', 'current']:
                if blocked:
                    outcomes[name][variant] = {'result': 'not_run', 'reason': 'provider_blocked'}
                    continue
                print(f'Running {provider} {name} {variant}', flush=True)
                result = evaluate(provider, variant, name, case, output, args.baseline, args.timeout, args.baseline_skills)
                outcomes[name][variant] = result
                blocked = result['result'] == 'blocked'
                (output / 'summary.json').write_text(json.dumps(summary, indent=2))
                print(f"{name} {variant}: {result['result']}", flush=True)
    (output / 'summary.json').write_text(json.dumps(summary, indent=2))
    print(f'Evidence: {output}', flush=True)


if __name__ == '__main__':
    main()
