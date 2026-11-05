"""Tests of evaluation mechanics; these never count as provider evidence."""
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import evaluate_engineering_behavior as evaluation
import run_agent_smoke_tests as smoke


class BehavioralEvaluationTests(unittest.TestCase):
    def test_codex_path_discovery_uses_actual_executable(self):
        with patch.object(smoke, 'CODEX_JS', None), patch.object(smoke.shutil, 'which', return_value='/fixture/codex'), patch.object(smoke, 'run') as run:
            run.return_value.stdout = 'codex-cli fixture'
            command, _ = smoke.provider_command('codex', Path('/tmp'), 'review', True)
            self.assertEqual(command[0], '/fixture/codex')
            self.assertEqual(command[command.index('--sandbox') + 1], 'read-only')

    def test_final_answer_excludes_command_output(self):
        events = [{'type': 'item.completed', 'item': {'type': 'command_execution', 'text': 'fake answer'}},
                  {'type': 'item.completed', 'item': {'type': 'agent_message', 'text': '{"choice":"sync"}'}}]
        self.assertEqual(json.loads(evaluation.final_response(events)), {'choice': 'sync'})

    def test_failed_terminal_and_modified_fixture_cannot_pass(self):
        case = {'kind': 'architecture'}
        checks = evaluation.mechanical_checks(case, {'choice': 'queue'}, [], False, '')
        self.assertFalse(checks['terminal_event'])
        self.assertFalse(checks['fixture_unchanged'])
        self.assertFalse(checks['sync_selected'])

    def test_negative_case_rejects_tool_execution(self):
        events = [{'type': 'turn.completed'}, {'type': 'item.completed', 'item': {'type': 'command_execution'}}]
        checks = evaluation.mechanical_checks({'kind': 'negative'}, None, events, True, 'MCP explanation')
        self.assertFalse(checks['no_command_execution'])

    def test_sandbox_block_requires_native_command_output(self):
        error = 'bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted'
        self.assertTrue(evaluation.sandbox_blocked([], [error]))
        self.assertFalse(evaluation.sandbox_blocked([{'type': 'item.completed', 'item': {'type': 'agent_message', 'text': error}}]))
        self.assertTrue(evaluation.sandbox_blocked([{'type': 'item.completed', 'item': {'type': 'command_execution', 'aggregated_output': error}}]))

    def test_final_message_is_not_prefixed_with_progress(self):
        events = [{'type': 'item.completed', 'item': {'type': 'agent_message', 'text': 'Working...'}},
                  {'type': 'item.completed', 'item': {'type': 'agent_message', 'text': '{"choice":"sync"}'}}]
        self.assertEqual(evaluation.parse_answer(evaluation.final_response(events)), {'choice': 'sync'})

    def test_native_trace_decodes_nested_json_output_not_assistant_claims(self):
        import tempfile
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sessions = root / 'sessions'
            sessions.mkdir()
            tool = {'type': 'response_item', 'payload': {'type': 'custom_tool_call_output', 'output': [{'text': json.dumps({'output': 'exact reference body'})}]}}
            claim = {'type': 'response_item', 'payload': {'type': 'message', 'content': 'assistant claim'}}
            (sessions / 'trace-fixture.jsonl').write_text(json.dumps(tool) + '\n' + json.dumps(claim))
            with patch.dict('os.environ', {'CODEX_HOME': str(root)}):
                strings, _ = evaluation.trace_strings('{"type":"thread.started","thread_id":"fixture"}')
            self.assertIn('exact reference body', strings)
            self.assertNotIn('assistant claim', strings)

    def test_fixture_changes_allow_test_bytecode_but_not_unrelated_edits(self):
        self.assertTrue(evaluation.allowed_fixture_changes(['subtotal.py', '__pycache__/subtotal.cpython-312.pyc'], ['subtotal.py'], True))
        self.assertFalse(evaluation.allowed_fixture_changes(['.codex/config.toml'], ['subtotal.py'], True))
        self.assertFalse(evaluation.allowed_fixture_changes(['.codex/__pycache__/config.cpython-312.pyc'], ['subtotal.py'], True))
        self.assertFalse(evaluation.allowed_fixture_changes(['__pycache__/payload.py'], [], True))
        self.assertFalse(evaluation.allowed_fixture_changes(['subtotal.py'], ['subtotal.py'], False))

    def test_review_location_uses_case_contract(self):
        case = {'kind': 'security', 'expected_location': {'file': 'auth.py', 'lines': [1, 2]}}
        answer = {'findings': [{'file': 'auth.py', 'line': 2, 'impact': 'tenant leak', 'scenario': 'other tenant', 'fix': 'check tenant'}]}
        checks = evaluation.mechanical_checks(case, answer, [{'type': 'turn.completed'}], True, '')
        self.assertTrue(checks['correct_file_location'])
