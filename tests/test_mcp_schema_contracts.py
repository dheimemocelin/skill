"""Standards-based fixture checks; optional existing jsonschema, never installed here."""
import inspect
import json
from pathlib import Path
import unittest
try:
    from jsonschema import Draft202012Validator
except ImportError:
    Draft202012Validator = None

ROOT = Path(__file__).resolve().parents[1]
CASES = {c['id']: c for c in json.loads((ROOT / 'examples/behavioral/mcp-schema-fixtures.json').read_text())}


@unittest.skipIf(Draft202012Validator is None, 'jsonschema unavailable: standards validation not executed')
class MCPContractTests(unittest.TestCase):
    def validator(self, name):
        case = CASES[name]
        Draft202012Validator.check_schema(case['schema'])
        return Draft202012Validator(case['schema'])

    def test_valid_schema_and_optional_property(self):
        c = CASES['valid']
        self.assertTrue(self.validator('valid').is_valid(c['input']))
        namespace = {}
        exec(c['implementation'], namespace)
        self.assertEqual(namespace['update'](**c['input']), 'c1')

    def test_required_property_missing_from_instance(self):
        c = CASES['missing_input']
        errors = list(self.validator('missing_input').iter_errors(c['input']))
        self.assertEqual([e.validator for e in errors], ['required'])

    def test_contract_required_not_schema_required(self):
        c = CASES['missing_contract_required']
        self.assertTrue(self.validator('missing_contract_required').is_valid(c['input']))
        self.assertIn('customer_id', c['schema']['properties'])
        self.assertNotIn('customer_id', c['schema'].get('required', []))
        namespace = {}
        exec(c['implementation'], namespace)
        with self.assertRaises(TypeError):
            namespace['update'](**c['input'])

    def test_wrong_type(self):
        c = CASES['wrong_type']
        errors = list(self.validator('wrong_type').iter_errors(c['input']))
        self.assertEqual([e.validator for e in errors], ['type'])

    def test_forbidden_unknown_property(self):
        c = CASES['unknown_property']
        errors = list(self.validator('unknown_property').iter_errors(c['input']))
        self.assertEqual([e.validator for e in errors], ['additionalProperties'])

    def test_schema_implementation_incompatibility(self):
        c = CASES['implementation_mismatch']
        self.assertTrue(self.validator('implementation_mismatch').is_valid(c['input']))
        namespace = {}
        exec(c['implementation'], namespace)
        with self.assertRaises(TypeError):
            inspect.signature(namespace['update']).bind(**c['input'])
