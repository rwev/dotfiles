"""Exercise the Grok statusline script."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class GrokScriptTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='grok-scripts-')
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)
        self.bin = self.path / 'bin'
        self.bin.mkdir()
        for command in ['bash', 'jq', 'cat', 'awk']:
            (self.bin / command).symlink_to(shutil.which(command))
        self.env = {**os.environ, 'PATH': str(self.bin), 'CALLS': str(self.path / 'calls')}
        self.mock('uname', 'printf "Linux\\n"')

    def mock(self, command, body):
        target = self.bin / command
        target.write_text('#!/bin/bash\n' + body + '\n')
        target.chmod(0o755)

    def run_script(self, script, payload):
        data = payload if isinstance(payload, str) else json.dumps(payload)
        result = subprocess.run(['bash', str(ROOT / '.grok' / script)], input=data,
                                env=self.env, cwd=self.path, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, '')
        return result.stdout

    def test_statusline_complete(self):
        self.assertEqual(self.run_script('statusline.sh', {
            'model': {'display_name': 'Grok', 'id': 'unused'}, 'effort': {'level': 'high'},
            'workspace': {'current_dir': '/work/dotfiles', 'branch': 'topic'},
            'context_window': {'used_percentage': 18}, 'cost': {'total_cost_usd': 0.12},
        }), 'Grok · high · dotfiles · topic · 18% ctx · $0.120')

    def test_statusline_missing_fields_do_not_shift(self):
        self.assertEqual(self.run_script('statusline.sh', {
            'effort': {'level': 'high'}, 'workspace': {'branch': 'topic'},
            'context_window': {'used_percentage': 0},
        }), 'high · topic · 0% ctx')
        self.assertEqual(self.run_script('statusline.sh', {
            'model': {'display_name': '', 'id': 'grok-id'}, 'cwd': '/work/project/',
            'cost': {'total_cost_usd': 0},
        }), 'grok-id · project')

    def test_statusline_wrong_type_parents_do_not_shift_valid_fields(self):
        payload = {
            'model': {'display_name': 'Grok'}, 'effort': {'level': 'high'},
            'workspace': {'current_dir': '/work/dotfiles', 'branch': 'topic'},
            'context_window': {'used_percentage': 18}, 'cost': {'total_cost_usd': 0.12},
        }
        expected = {
            'model': 'high · dotfiles · topic · 18% ctx · $0.120',
            'effort': 'Grok · dotfiles · topic · 18% ctx · $0.120',
            'workspace': 'Grok · high · 18% ctx · $0.120',
            'context_window': 'Grok · high · dotfiles · topic · $0.120',
            'cost': 'Grok · high · dotfiles · topic · 18% ctx',
        }
        for parent, output in expected.items():
            for value in [None, True, 12, 'bad', []]:
                with self.subTest(parent=parent, value=value):
                    self.assertEqual(self.run_script('statusline.sh', {**payload, parent: value}),
                                     output)

    def test_statusline_unknown_values_and_malformed_json(self):
        for payload in ['{', '{}', 'null', '[]', 'true', '{"model":true}',
                        '{"effort":[],"workspace":false,"context_window":"bad","cost":1}']:
            with self.subTest(payload=payload):
                self.assertEqual(self.run_script('statusline.sh', payload), '')
        self.assertEqual(self.run_script('statusline.sh', {
            'model': {'display_name': 4}, 'effort': {'level': False},
            'workspace': {'current_dir': [], 'branch': {}},
            'context_window': {'used_percentage': '18'}, 'cost': {'total_cost_usd': '0.12'},
        }), '')

    def test_statusline_ignores_cumulative_usage_and_unavailable_metrics(self):
        self.assertEqual(self.run_script('statusline.sh', {
            'context_window': {'used_percentage': -1, 'session_input_tokens': 10000,
                               'context_window_size': 10},
            'cost': {'total_cost_usd': -1, 'total_lines_added': 10},
            'rate_limits': {'five_hour': {'used_percentage': 20}},
        }), '')
        self.assertEqual(self.run_script('statusline.sh', {
            'cost': {'total_cost_usd': 0.00001},
        }), '$<0.001')

    def test_statusline_control_characters_and_shell_text(self):
        self.assertEqual(self.run_script('statusline.sh', {
            'model': {'display_name': 'Grok\nnext\x1b'},
            'workspace': {'current_dir': '/work/quote \' $HOME `touch sentinel`',
                          'branch': 'topic\tname'},
        }), 'Grok next  · quote \' $HOME `touch sentinel` · topic name')
        self.assertFalse((self.path / 'sentinel').exists())


if __name__ == '__main__':
    unittest.main()
