"""Run the installer only in isolated homes. Python is a test dependency only."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
import json
import tomllib
import shutil
import shlex

ROOT = Path(__file__).resolve().parents[1]
GROK_DEFAULTS = {
    'models': {'default_reasoning_effort': 'high'},
    'memory': {'enabled': False},
    'memory_v2': {'enabled': False},
    'ui': {'screen_mode': 'fullscreen', 'theme': 'dark',
           'permission_mode': 'always-approve', 'max_thoughts_width': 120,
           'yolo': True, 'compact_mode': True, 'show_timeline': True,
           'page_flip_on_send': False, 'show_thinking_blocks': True,
           'status_line': {'type': 'command', 'command': '~/.grok/statusline.sh'}},
    'toolset': {'ask_user_question': {'timeout_secs': 600}},
    'subagents': {'enabled': True},
    'features': {'active_agent_messages': True, 'subagent_model_inheritance': True},
    'sandbox': {'profile': 'workspace'},
    'compat': {'claude': {'agents': False}},
    'permission': {'deny': [
        'Read(**/.env)', 'Read(**/.env.*)', 'Read(secrets/**)',
        'Read(**/*.pem)', 'Read(**/*.key)', 'Read(**/id_rsa)',
        'Read(**/id_ed25519)', 'Read(**/credentials.json)',
        'Read(**/.ssh/**)', 'Read(**/.aws/credentials)',
    ]},
}


def grok_defaults_with(overrides):
    defaults = json.loads(json.dumps(GROK_DEFAULTS))

    def merge(base, local):
        for key, value in local.items():
            if isinstance(value, dict) and isinstance(base.get(key), dict):
                merge(base[key], value)
            else:
                base[key] = value

    merge(defaults, overrides)
    return defaults


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="agents-install-")
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name) / "home with ' quotes $ and `ticks`"
        self.home.mkdir()
        self.env = {k: v for k, v in os.environ.items() if k not in {
            'CLAUDE_CONFIG_DIR', 'CODEX_HOME', 'COPILOT_HOME', 'XDG_CONFIG_HOME',
            'GEMINI_CLI_HOME', 'GROK_HOME', 'XDG_DATA_HOME'}}
        self.env['HOME'] = str(self.home)
        self.root = ROOT

    def install(self, *args, ok=True):
        result = subprocess.run(['bash', str(self.root / 'install.sh'), '--agents-only', *args],
                                env=self.env, capture_output=True, text=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result

    def snapshot(self):
        return {str(p.relative_to(self.home)): ('link', os.readlink(p)) if p.is_symlink()
                else ('dir',) if p.is_dir() else ('file', p.read_bytes())
                for p in self.home.rglob('*')}

    def test_clean_and_idempotent(self):
        self.install()
        self.assertEqual(len(list((self.home / '.agents/skills').iterdir())), 13)
        for path in ['.claude/CLAUDE.md', '.codex/AGENTS.md',
                     '.config/opencode/AGENTS.md', '.copilot/copilot-instructions.md']:
            text = (self.home / path).read_text()
            self.assertIn('Global rules', text)
            self.assertNotIn('\nname:', text)
            self.assertEqual(text.count('## Address'), 0 if path.startswith(('.claude', '.config')) else 1)
        for harness, suffix in [('.claude', '.md'), ('.codex', '.toml'),
                                 ('.config/opencode', '.md'), ('.copilot', '.agent.md')]:
            for role in ['implementer', 'reviewer', 'security-reviewer']:
                path = self.home / harness / 'agents' / ('_my-' + role + suffix)
                self.assertIn('## Process', path.read_text())
                if suffix == '.toml':
                    agent = tomllib.loads(path.read_text())
                    self.assertTrue(agent['developer_instructions'])
        before = self.snapshot()
        self.install()
        self.assertEqual(before, self.snapshot())
        self.assertFalse((self.home / '.zshrc').exists())
        self.assertFalse((self.home / '.grok').exists())
        self.assertFalse((self.home / '.copilot/config.json').exists())
        self.assertEqual(json.loads((self.home / '.claude/settings.json').read_text()),
                         json.loads((ROOT / '.claude/settings.json').read_text()))
        self.assertEqual(json.loads((self.home / '.config/opencode/opencode.json').read_text()),
                         json.loads((ROOT / '.opencode/opencode.json').read_text()))
        self.assertEqual((self.home / '.codex/config.toml').read_text(),
                         (ROOT / '.codex/config.toml').read_text())

    def test_targets_and_bad_args(self):
        for arg in ['--bogus', '--tools=', '--tools=bad', '--tools=claude,', '--tools=universal,codex']:
            self.install(arg, ok=False)
            self.assertEqual(self.snapshot(), {})
        self.install('--tools=universal')
        self.assertTrue((self.home / '.agents/exports/default.md').exists())
        self.assertFalse((self.home / '.codex').exists())
        self.install('--tools=gemini,amp')
        self.assertIn('## Address', (self.home / '.gemini/GEMINI.md').read_text())
        self.assertIn('Unsupported', (self.home / '.config/amp/AGENTS.md').read_text())
        self.assertFalse((self.home / '.claude').exists())

    def test_dry_run(self):
        self.install('--dry-run')
        self.assertEqual(self.snapshot(), {})
        self.install()
        before = self.snapshot()
        self.install('--dry-run', '--tools=gemini,amp')
        self.assertEqual(before, self.snapshot())

    def test_custom_homes(self):
        for key, folder in [('CLAUDE_CONFIG_DIR', 'claude'), ('CODEX_HOME', 'codex'),
                            ('COPILOT_HOME', 'copilot'), ('XDG_CONFIG_HOME', 'config'),
                            ('GEMINI_CLI_HOME', 'gemini-root')]:
            self.env[key] = str(self.home / folder)
        self.install('--tools=claude,codex,opencode,copilot,gemini,amp')
        for path in ['claude/CLAUDE.md', 'codex/AGENTS.md', 'copilot/copilot-instructions.md',
                     'config/opencode/AGENTS.md', 'config/amp/AGENTS.md', 'gemini-root/.gemini/GEMINI.md']:
            self.assertTrue((self.home / path).is_file(), path)
        settings = json.loads((self.home / 'claude/settings.json').read_text())
        result = subprocess.run(['bash', '-c', "printf '%s' " + settings['statusLine']['command']], capture_output=True, text=True)
        self.assertEqual(result.stdout, str(self.home / 'claude/statusline.sh'))
        self.assertEqual(result.stderr, '')
        self.assertTrue((self.home / 'gemini-root/.gemini/skills/my-test/SKILL.md').is_file())

    def test_grok_opt_in_and_idempotent(self):
        self.install('--tools=grok')
        grok = self.home / '.grok'
        instructions = (grok / 'AGENTS.md').read_text()
        self.assertIn('Global rules', instructions)
        self.assertEqual(instructions.count('## Address'), 1)
        self.assertNotIn('Unsupported workflows', instructions)
        self.assertIn('Supply the full diff and test results', instructions)
        self.assertIn('cannot run git or tests', instructions)
        self.assertEqual(tomllib.loads((grok / 'config.toml').read_text()),
                         GROK_DEFAULTS)
        read_tools = {'read_file', 'grep', 'list_dir', 'todo_write'}
        for role in ['implementer', 'reviewer', 'security-reviewer']:
            name = '_my-' + role
            text = (grok / 'agents' / (name + '.md')).read_text()
            _, header, body = text.split('---', 2)
            metadata = dict(line.split(': ', 1) for line in header.strip().splitlines())
            self.assertEqual(metadata['name'], name)
            expected_tools = {
                'implementer': read_tools | {'search_replace', 'run_terminal_cmd'},
                'reviewer': read_tools,
                'security-reviewer': read_tools | {'web_search'},
            }[role]
            self.assertEqual(set(metadata['tools'].split(', ')), expected_tools)
            if role != 'implementer':
                self.assertEqual(set(metadata['disallowedTools'].split(', ')), {'search_tool', 'use_tool'})
                self.assertEqual(metadata['mcpInheritance'], 'none')
                self.assertIn('full diff and test results', metadata['description'])
                self.assertIn('cannot run git or tests', body)
                self.assertIn('request the missing context', body)
            shared_body = (ROOT / '.agents/agents' / (name + '.md')).read_text().split('---', 2)[2]
            self.assertTrue(body.endswith(shared_body.lstrip('\n')))
        self.assertEqual(len(list((self.home / '.agents/skills').iterdir())), 13)
        self.assertFalse((grok / 'skills').exists())
        self.assertTrue((grok / 'statusline.sh').is_symlink())
        self.assertEqual((grok / 'statusline.sh').resolve(), ROOT / '.grok' / 'statusline.sh')
        self.assertTrue(os.access(grok / 'statusline.sh', os.X_OK))
        self.assertFalse((grok / 'notify.sh').exists())
        self.assertFalse((grok / 'hooks' / 'notifications.json').exists())
        self.assertFalse((self.home / '.claude').exists())
        before = self.snapshot()
        self.install('--tools=grok')
        self.assertEqual(before, self.snapshot())

    def test_grok_custom_home(self):
        grok = self.home / 'custom grok'
        self.env['GROK_HOME'] = str(grok)
        self.install('--tools=grok')
        self.assertTrue((grok / 'AGENTS.md').is_file())
        self.assertTrue((grok / 'agents/_my-reviewer.md').is_file())
        self.assertTrue((grok / 'config.toml').is_file())
        self.assertFalse((grok / '.grok').exists())
        self.assertFalse((grok / 'skills').exists())
        self.assertFalse((self.home / '.grok').exists())
        self.assertTrue((self.home / '.agents/skills/my-test/SKILL.md').is_file())

    def test_grok_custom_home_statusline_command_is_shell_safe(self):
        grok = self.home / "custom grok ' $dollars `ticks`"
        self.env['GROK_HOME'] = str(grok)
        for initial in [None, '[ui.status_line]\ntype = "command"\n']:
            with self.subTest(initial=initial):
                if initial is not None:
                    (grok / 'config.toml').write_text(initial)
                self.install('--tools=grok')
                config = tomllib.loads((grok / 'config.toml').read_text())
                command = config['ui']['status_line']['command']
                self.assertEqual(shlex.split(command), [str(grok / 'statusline.sh')])
                payload = json.dumps({'model': {'display_name': 'safe model'}})
                result = subprocess.run(['sh', '-c', command], input=payload, env=self.env,
                                        capture_output=True, text=True)
                self.assertEqual((result.returncode, result.stdout, result.stderr),
                                 (0, 'safe model', ''))
                before = self.snapshot()
                self.install('--tools=grok')
                self.assertEqual(before, self.snapshot())
        (grok / 'config.toml').write_text('[ui.status_line]\ntype = "builtin"\ncommand = "local command"\n')
        self.install('--tools=grok')
        self.assertEqual(tomllib.loads((grok / 'config.toml').read_text())['ui']['status_line'],
                         {'type': 'builtin', 'command': 'local command'})

    def test_grok_preserves_custom_notification_hook_and_external_target(self):
        grok = self.home / '.grok'
        hooks = grok / 'hooks'
        hooks.mkdir(parents=True)
        external = self.home / 'external-hook.json'
        content = '{"hooks":{"Notification":[]}}\n'
        external.write_text(content)
        destination = hooks / 'notifications.json'
        destination.symlink_to(external)
        (hooks / 'custom.json').write_text(content)
        notify = grok / 'notify.sh'
        notify.symlink_to(self.home / 'absent-notify.sh')
        self.install('--tools=grok')
        self.assertTrue(destination.is_symlink())
        self.assertEqual(os.readlink(destination), str(external))
        self.assertEqual(external.read_text(), content)
        self.assertEqual((hooks / 'custom.json').read_text(), content)
        self.assertFalse(notify.exists())

        managed = '{"hooks":{"Notification":[{"hooks":[{"type":"command","command":"../notify.sh"}]}]}}\n'
        destination.unlink()
        destination.write_text(managed)
        notify.symlink_to(self.home / 'absent-notify.sh')
        self.install('--tools=grok')
        self.assertFalse(destination.exists())
        self.assertFalse(notify.exists())
        self.assertEqual((hooks / 'custom.json').read_text(), content)
        self.assertEqual(external.read_text(), content)

        kept = '{"hooks":{"Stop":[{"hooks":[{"type":"command","command":"keep.sh"}]}]}}\n'
        destination.write_text(kept)
        notify.write_text('#!/bin/sh\nexit 0\n')
        self.install('--tools=grok')
        self.assertEqual(destination.read_text(), kept)
        self.assertTrue(notify.is_file())
        self.assertFalse(notify.is_symlink())
        self.assertEqual((hooks / 'custom.json').read_text(), content)
        before = self.snapshot()
        self.install('--tools=grok')
        self.assertEqual(before, self.snapshot())

    def test_grok_unknown_hook_directory_link_is_not_written_through(self):
        grok = self.home / '.grok'
        grok.mkdir()
        outside = self.home / 'outside'
        outside.mkdir()
        (outside / 'sentinel').write_text('untouched\n')
        (outside / 'notifications.json').write_text(
            '{"hooks":{"Notification":[{"hooks":[{"type":"command","command":"../notify.sh"}]}]}}\n')
        (grok / 'hooks').symlink_to(outside)
        self.install('--tools=grok')
        self.assertEqual({p.name for p in outside.iterdir()}, {'sentinel', 'notifications.json'})
        self.assertEqual((outside / 'sentinel').read_text(), 'untouched\n')
        self.assertTrue((grok / 'hooks').is_symlink())

    def test_grok_dry_run(self):
        self.install('--tools=grok', '--dry-run')
        self.assertEqual(self.snapshot(), {})
        self.install('--tools=grok')
        before = self.snapshot()
        self.install('--tools=grok', '--dry-run')
        self.assertEqual(before, self.snapshot())

    def test_grok_preserves_local_instructions_config_and_runtime(self):
        grok = self.home / '.grok'
        grok.mkdir()
        (grok / 'AGENTS.md').write_text('existing Grok instructions\n')
        (grok / 'AGENTS.local.md').write_text('local Grok instructions\n')
        runtime = {}
        for path in ['auth.json', 'sessions/session.json', 'cache/data', 'agents/custom.md',
                     'skills/custom/SKILL.md', 'hooks/custom.json']:
            target = grok / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text('placeholder local content\n')
            runtime[target] = target.read_bytes()
        config = 'model = "local-choice"\n[compat.claude]\nagents = true\nskills = false\n'
        (grok / 'config.toml').write_text(config)
        self.install('--tools=claude,grok')
        self.assertEqual(tomllib.loads((grok / 'config.toml').read_text()),
                         grok_defaults_with(tomllib.loads(config)))
        instructions = (grok / 'AGENTS.md').read_text()
        self.assertIn('existing Grok instructions', instructions)
        self.assertIn('local Grok instructions', instructions)
        self.assertEqual((grok / 'AGENTS.md.bak').read_text(), 'existing Grok instructions\n')
        for path, content in runtime.items():
            self.assertEqual(path.read_bytes(), content)
        before = self.snapshot()
        self.install('--tools=claude,grok')
        self.assertEqual(before, self.snapshot())

    def test_grok_adds_only_missing_defaults(self):
        grok = self.home / '.grok'
        grok.mkdir()
        config = 'model = "local-choice"\n[compat.claude]\nskills = false\nhooks = true\n[ui]\ntheme = "local"\n'
        (grok / 'config.toml').write_text(config)
        self.install('--tools=grok')
        expected = grok_defaults_with(tomllib.loads(config))
        self.assertEqual(tomllib.loads((grok / 'config.toml').read_text()), expected)
        before = self.snapshot()
        self.install('--tools=grok')
        self.assertEqual(before, self.snapshot())

    def test_grok_preserves_all_local_runtime_defaults(self):
        grok = self.home / '.grok'
        grok.mkdir()
        config = '\n'.join([
            'model = "local-choice"',
            '[models]', 'default_reasoning_effort = "low"',
            '[memory]', 'enabled = true', '[memory_v2]', 'enabled = true',
            '[ui]', 'screen_mode = "minimal"', 'theme = "local"',
            'permission_mode = "ask"', 'max_thoughts_width = 80', 'yolo = false',
            'compact_mode = false', 'show_timeline = false',
            'page_flip_on_send = true', 'show_thinking_blocks = false',
            '[ui.status_line]', 'type = "disabled"', 'command = "local-script"',
            '[toolset.ask_user_question]', 'timeout_secs = 120',
            '[subagents]', 'enabled = false',
            '[features]', 'active_agent_messages = false',
            'subagent_model_inheritance = false',
            '[sandbox]', 'profile = "read-only"',
            '[compat.claude]', 'agents = true',
            '[permission]', 'deny = [', '  "Read(local/**)",', ']', '',
        ])
        (grok / 'config.toml').write_text(config)
        self.install('--tools=grok')
        self.assertEqual((grok / 'config.toml').read_text(), config)
        before = self.snapshot()
        self.install('--tools=grok')
        self.assertEqual(before, self.snapshot())

    def test_grok_multiline_deny_insertion(self):
        grok = self.home / '.grok'
        grok.mkdir()
        config = '[permission]\nallow = ["Bash(cargo test *)"]\n[ui]\ntheme = "local"\n'
        (grok / 'config.toml').write_text(config)
        self.install('--tools=grok')
        self.assertEqual(tomllib.loads((grok / 'config.toml').read_text()),
                         grok_defaults_with(tomllib.loads(config)))
        before = self.snapshot()
        self.install('--tools=grok')
        self.assertEqual(before, self.snapshot())

    def test_grok_preserves_alternate_runtime_syntax(self):
        grok = self.home / '.grok'
        grok.mkdir()
        configs = [
            'ui = { theme = "local" }\n',
            'ui.theme = "local"\n',
            '["ui"]\ntheme = "local"\n',
            '[ui]\n"\\u0074heme" = "local"\n',
            '[toolset]\nask_user_question = { timeout_secs = 120 }\n',
            '[toolset]\nask_user_question.timeout_secs = 120\n',
            'toolset.ask_user_question = { timeout_secs = 120 }\n',
            'memory = false\n',
            '[toolset]\nask_user_question = false\n',
            'note = """\n[ui]\ntheme = "local"\n"""\n',
            'note = """unterminated\n[ui]\n',
            '[ui\ntheme = "local"\n',
        ]
        for config in configs:
            with self.subTest(config=config):
                (grok / 'config.toml').write_text(config)
                self.install('--tools=grok')
                self.assertEqual((grok / 'config.toml').read_text(), config)
                before = self.snapshot()
                self.install('--tools=grok')
                self.assertEqual(before, self.snapshot())

    def test_grok_preserves_multiline_strings_inside_arrays(self):
        grok = self.home / '.grok'
        grok.mkdir()
        config = grok / 'config.toml'
        external = self.home / 'external.toml'
        for delimiter in ['"""', "'" * 3]:
            for linked in [False, True]:
                with self.subTest(delimiter=delimiter, linked=linked):
                    original = ('[custom]\nnotes = [' + delimiter +
                                '\n[ui]\n[other]\nkeep this text\n' + delimiter + ']\n').encode()
                    if config.exists() or config.is_symlink():
                        config.unlink()
                    if linked:
                        external.write_bytes(original)
                        config.symlink_to(external)
                    else:
                        config.write_bytes(original)
                    self.install('--tools=grok')
                    self.assertEqual(config.read_bytes(), original)
                    self.assertEqual(config.is_symlink(), linked)
                    self.assertEqual(list(grok.glob('config.toml.bak*')), [])
                    if linked:
                        self.assertEqual(external.read_bytes(), original)
                    before = self.snapshot()
                    self.install('--tools=grok')
                    self.assertEqual(before, self.snapshot())

    def test_toml_default_preserves_literal_paths(self):
        config = self.home / 'config.toml'
        config.write_text('[ui]\ntheme = "local"\n')
        literal_path = str(self.home / r'folder\name')
        line = 'command = ' + json.dumps(literal_path)
        result = subprocess.run([
            'bash', '-c',
            'source "$1"; codex_insert_default "$2" ui "$3"',
            'test-default', str(ROOT / 'install/agent-config.sh'), str(config), line,
        ], env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(tomllib.loads(result.stdout),
                         {'ui': {'theme': 'local', 'command': literal_path}})
        self.assertEqual(config.read_text(), '[ui]\ntheme = "local"\n')

    def test_grok_shell_aliases(self):
        aliases = '\n'.join(line for line in (ROOT / '.zshrc').read_text().splitlines()
                            if line.startswith('alias gr'))
        result = subprocess.run(['zsh', '-f', '-c', aliases + '\nalias grk grkc grkr'],
                                env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), [
            "grk='grok --always-approve'",
            "grkc='grok --continue --always-approve'",
            "grkr='grok --resume --always-approve'",
        ])

    def test_grok_preserves_alternate_compat_syntax(self):
        grok = self.home / '.grok'
        grok.mkdir()
        for config in ['compat.claude.agents = true\n',
                       '"compat".claude.agents = true\n',
                       '[compat]\nclaude = { agents = true, skills = false }\n',
                       '["compat"."claude"]\nagents = true\n',
                       '["\\u0063ompat".claude]\nagents = true\n',
                       '"\\u0063ompat".claude.agents = true\n',
                       'compat."\\u0063laude".agents = true\n',
                       '[compat.claude]\n"\\u0061gents" = true\n',
                       '[compat.claude]\n"agents" = true\n']:
            with self.subTest(config=config):
                (grok / 'config.toml').write_text(config)
                self.install('--tools=grok')
                self.assertEqual((grok / 'config.toml').read_text(), config)
                self.assertEqual(tomllib.loads(config)['compat']['claude']['agents'], True)
                before = self.snapshot()
                self.install('--tools=grok')
                self.assertEqual(before, self.snapshot())

    def test_grok_escaped_config_names_preserve_symlink(self):
        grok = self.home / '.grok'
        grok.mkdir()
        external = self.home / 'external.toml'
        original = '["\\u0063ompat".claude]\nagents = true\n'
        external.write_text(original)
        config = grok / 'config.toml'
        config.symlink_to(external)
        self.install('--tools=grok')
        self.assertTrue(config.is_symlink())
        self.assertEqual(external.read_text(), original)
        self.assertEqual(config.read_text(), original)
        self.assertEqual(list(grok.glob('config.toml.bak*')), [])
        before = self.snapshot()
        self.install('--tools=grok')
        self.assertEqual(before, self.snapshot())

    def test_grok_config_symlink_preserves_external_content(self):
        grok = self.home / '.grok'
        grok.mkdir()
        external = self.home / 'external.toml'
        original = 'model = "local-choice"\n[compat.claude]\nskills = false\n'
        external.write_text(original)
        config = grok / 'config.toml'
        config.symlink_to(external)
        self.install('--tools=grok')
        self.assertEqual(external.read_text(), original)
        self.assertFalse(config.is_symlink())
        self.assertTrue((grok / 'config.toml.bak').is_symlink())
        self.assertEqual(tomllib.loads(config.read_text())['compat']['claude'],
                         {'skills': False, 'agents': False})
        original = config.read_text().replace('agents = false', 'agents = true')
        external.write_text(original)
        config.unlink()
        config.symlink_to(external)
        self.install('--tools=grok')
        self.assertTrue(config.is_symlink())
        self.assertEqual(external.read_text(), original)

    def test_grok_unknown_directory_links_are_not_written_through(self):
        outside = self.home / 'outside'
        outside.mkdir()
        (outside / 'sentinel').write_text('untouched\n')
        grok = self.home / '.grok'
        grok.symlink_to(outside)
        result = self.install('--tools=grok', ok=False)
        self.assertIn('Refusing to write through directory symlink', result.stderr)
        self.assertEqual({p.name for p in outside.iterdir()}, {'sentinel'})
        grok.unlink()
        grok.mkdir()
        (grok / 'agents').symlink_to(outside)
        result = self.install('--tools=grok', ok=False)
        self.assertIn('Refusing to write through directory symlink', result.stderr)
        self.assertEqual({p.name for p in outside.iterdir()}, {'sentinel'})
        self.assertEqual((outside / 'sentinel').read_text(), 'untouched\n')

    @unittest.skipUnless(shutil.which('grok'), 'Grok CLI is not installed')
    def test_grok_native_discovery(self):
        cwd = Path(self.tmp.name) / 'project'
        cwd.mkdir()
        for custom in [False, True]:
            with self.subTest(custom_home=custom):
                if custom:
                    self.env['GROK_HOME'] = str(self.home / 'custom grok')
                self.install('--tools=claude,grok')
                env = {k: v for k, v in self.env.items() if not k.startswith('GROK_')}
                if custom:
                    env['GROK_HOME'] = self.env['GROK_HOME']
                for env_override in [False, True]:
                    if env_override:
                        env['GROK_CLAUDE_AGENTS_ENABLED'] = 'false'
                    command = [shutil.which('grok'), 'inspect', '--json']
                    result = subprocess.run(command, env=env, cwd=cwd,
                                            capture_output=True, text=True, timeout=30)
                    if result.returncode != 0:
                        self.assertEqual(result.stderr,
                                         'error: this sandbox could not enforce its deny list on Linux: '
                                         'bwrap exec failed: No such file or directory (os error 2). '
                                         'Install bubblewrap with `apt install -y bubblewrap`. '
                                         'Refusing to start with denied paths unprotected.\n')
                        self.assertEqual(result.stdout, '')
                        # Check discovery only after verifying fail-closed sandbox startup.
                        command[1:1] = ['--sandbox', 'off']
                        result = subprocess.run(command, env=env, cwd=cwd,
                                                capture_output=True, text=True, timeout=30)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    report = json.loads(result.stdout)
                    self.assertTrue({'_my-implementer', '_my-reviewer', '_my-security-reviewer'} <=
                                    {agent['name'] for agent in report['agents']})
                    self.assertTrue({p.name for p in (ROOT / '.agents/skills').iterdir()} <=
                                    {skill['name'] for skill in report['skills']})
                    active = [entry for entry in report['projectInstructions'] if not entry.get('disabled')]
                    paths = [entry['path'] for entry in active]
                    grok = Path(self.env.get('GROK_HOME', self.home / '.grok'))
                    self.assertEqual(tomllib.loads((grok / 'config.toml').read_text())['sandbox'],
                                     {'profile': 'workspace'})
                    self.assertGreaterEqual(report['permissions']['loaded'],
                                            len(GROK_DEFAULTS['permission']['deny']))
                    self.assertEqual(report['permissions']['skipped'], [])
                    hooks = [hook for hook in report.get('hooks', []) if hook['event'] == 'notification']
                    self.assertEqual(hooks, [])
                    self.assertIn(str(grok / 'config.toml') + ' (config)',
                                  report['permissions']['sources'])
                    self.assertIn(str(grok / 'AGENTS.md'), paths)
                    self.assertNotIn(str(self.home / '.claude/CLAUDE.md'), paths)
                    instructions = '\n'.join(Path(path).read_text() for path in paths)
                    self.assertEqual(instructions.count('# Global rules'), 1)
                    self.assertEqual(instructions.count('## Address'), 1)

    def test_overrides_and_migration(self):
        codex = self.home / '.codex'
        codex.mkdir()
        (codex / 'AGENTS.md').write_text('old custom\n')
        (codex / 'AGENTS.local.md').write_text('local custom\n')
        (codex / 'AGENTS.md.bak').write_text('prior backup\n')
        (codex / 'config.toml').write_text('model = "custom"\ndefault_permissions = "custom"\n')
        opencode = self.home / '.config/opencode'
        opencode.mkdir(parents=True)
        (opencode / 'opencode.json').write_text(json.dumps({'instructions': [
            '~/.claude/output-styles/my-humble-servant.md', 'extra.md'], 'model': 'custom'}))
        claude = self.home / '.claude'
        claude.mkdir()
        (claude / 'settings.local.json').write_text(json.dumps({'model': 'custom', 'permissions': {'deny': ['local']}}))
        (claude / 'skills').symlink_to(ROOT / '.claude/skills')
        (claude / 'agents').symlink_to(ROOT / '.claude/agents')
        (claude / 'output-styles').symlink_to(ROOT / '.claude/output-styles')
        self.install()
        self.assertTrue((claude / 'skills').is_dir())
        self.assertFalse((claude / 'skills').is_symlink())
        text = (codex / 'AGENTS.md').read_text()
        self.assertIn('old custom', text)
        self.assertIn('local custom', text)
        self.assertEqual((codex / 'AGENTS.md.bak').read_text(), 'prior backup\n')
        self.assertIn('model = "custom"', (codex / 'config.toml').read_text())
        self.assertNotIn('sandbox_mode', (codex / 'config.toml').read_text())
        settings = json.loads((claude / 'settings.json').read_text())
        self.assertEqual(settings['permissions']['deny'], ['local'])
        settings = json.loads((opencode / 'opencode.json').read_text())
        self.assertEqual(settings['instructions'], ['~/.agents/personas/my-humble-servant.md', 'extra.md'])
        before = self.snapshot()
        self.install()
        self.assertEqual(before, self.snapshot())

    def test_unmanaged_links_and_invalid_json(self):
        external = self.home / 'external'
        external.mkdir()
        (external / 'rules').write_text('external rules\n')
        (external / 'settings').write_text('{bad json')
        claude = self.home / '.claude'
        claude.mkdir()
        (claude / 'CLAUDE.md').symlink_to(external / 'rules')
        (claude / 'settings.json').symlink_to(external / 'settings')
        (claude / 'settings.local.json').write_text('{also bad')
        (claude / 'skills').symlink_to(external)
        before = {p.name: p.read_bytes() for p in external.iterdir()}
        self.install(ok=False)
        self.assertEqual(before, {p.name: p.read_bytes() for p in external.iterdir()})
        (claude / 'skills').unlink()
        self.install()
        self.assertEqual(before, {p.name: p.read_bytes() for p in external.iterdir()})
        self.assertIn('external rules', (claude / 'CLAUDE.md').read_text())
        self.assertTrue(list(claude.glob('settings.local.json.bak*')))
        self.assertTrue(any(p.is_symlink() for p in claude.glob('CLAUDE.md.bak*')))
        self.assertIsInstance(json.loads((claude / 'settings.json').read_text()), dict)

    def test_legacy_unrelated_children(self):
        fixture = Path(self.tmp.name) / 'repo'
        fixture.mkdir()
        shutil.copytree(ROOT / 'install', fixture / 'install')
        for folder in ['.agents', '.codex', '.opencode/templates', '.claude/templates', '.copilot']:
            shutil.copytree(ROOT / folder, fixture / folder)
        for path in ['install.sh', '.claude/settings.json', '.claude/statusline.sh', '.opencode/opencode.json']:
            target = fixture / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / path, target)
        self.root = fixture
        for harness, folder in [('.claude', 'skills'), ('.claude', 'agents'),
                                ('.claude', 'output-styles'), ('.opencode', 'agents')]:
            legacy = fixture / harness / folder
            legacy.mkdir(parents=True, exist_ok=True)
            if folder == 'skills':
                entry = legacy / 'synced/runtime.txt'
                entry.parent.mkdir()
                entry.write_text('runtime skill')
            else:
                (legacy / 'custom.md').write_text('custom runtime')
            dest = self.home / ('.config/opencode' if harness == '.opencode' else harness) / folder
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.symlink_to(legacy)
        self.install()
        self.assertEqual((self.home / '.claude/skills/synced/runtime.txt').read_text(), 'runtime skill')
        for path in ['.claude/agents', '.claude/output-styles', '.config/opencode/agents']:
            self.assertEqual((self.home / path / 'custom.md').read_text(), 'custom runtime')
        self.assertEqual((fixture / '.claude/skills/synced/runtime.txt').read_text(), 'runtime skill')
        before = self.snapshot()
        self.install()
        self.assertEqual(before, self.snapshot())

    def test_failed_generated_render_keeps_existing_output(self):
        fixture = Path(self.tmp.name) / 'repo'
        fixture.mkdir()
        shutil.copytree(ROOT / 'install', fixture / 'install')
        shutil.copytree(ROOT / '.agents', fixture / '.agents')
        shutil.copy2(ROOT / 'install.sh', fixture / 'install.sh')
        (fixture / '.agents/personas/my-humble-servant.md').unlink()
        self.root = fixture
        export = self.home / '.agents/exports/default.md'
        export.parent.mkdir(parents=True)
        export.write_text('custom export\n')

        self.install('--tools=universal', ok=False)
        self.assertEqual(export.read_text(), 'custom export\n')
        self.assertEqual(list(export.parent.glob('default.md.bak*')), [])
        self.assertEqual(list(export.parent.glob('default.md.tmp.*')), [])

    def test_failed_json_render_keeps_existing_output(self):
        fixture = Path(self.tmp.name) / 'repo'
        fixture.mkdir()
        shutil.copytree(ROOT / 'install', fixture / 'install')
        shutil.copytree(ROOT / '.agents', fixture / '.agents')
        (fixture / '.claude').mkdir()
        (fixture / '.claude/settings.json').write_text('{bad json')
        shutil.copy2(ROOT / 'install.sh', fixture / 'install.sh')
        self.root = fixture
        settings = self.home / '.claude/settings.json'
        settings.parent.mkdir()
        settings.write_text('custom settings\n')

        self.install('--tools=claude', ok=False)
        self.assertEqual(settings.read_text(), 'custom settings\n')
        self.assertEqual(list(settings.parent.glob('settings.json.bak*')), [])
        self.assertEqual(list(settings.parent.glob('settings.json.tmp.*')), [])

    def test_invalid_tracked_json_source_keeps_existing_output(self):
        fixture = Path(self.tmp.name) / 'repo'
        fixture.mkdir()
        shutil.copytree(ROOT / 'install', fixture / 'install')
        shutil.copytree(ROOT / '.agents', fixture / '.agents')
        (fixture / '.claude').mkdir()
        shutil.copy2(ROOT / 'install.sh', fixture / 'install.sh')
        self.root = fixture
        settings = self.home / '.claude/settings.json'
        settings.parent.mkdir()
        settings.write_text('{"custom":true}\n')
        (settings.parent / 'settings.local.json').write_text('{}\n')

        for content in ['null', '[]', '{}\n{}']:
            with self.subTest(content=content):
                (fixture / '.claude/settings.json').write_text(content)
                self.install('--tools=claude', ok=False)
                self.assertEqual(settings.read_text(), '{"custom":true}\n')
                self.assertEqual(list(settings.parent.glob('settings.json.bak*')), [])
                self.assertEqual(list(settings.parent.glob('settings.json.tmp.*')), [])
                self.assertEqual(list(settings.parent.glob('settings.json.base.*')), [])

    def test_opencode_standalone_local_migration(self):
        directory = self.home / '.config/opencode'
        directory.mkdir(parents=True)
        local = directory / 'opencode.local.json'
        local.write_text(json.dumps({'instructions': ['extra.md', '~/.claude/output-styles/my-humble-servant.md'],
                                     'permission': {'read': {'custom': 'allow'}}, 'model': 'keep'}))
        self.install('--tools=opencode')
        self.assertEqual(json.loads(local.read_text())['instructions'],
                         ['extra.md', '~/.agents/personas/my-humble-servant.md'])
        config = json.loads((directory / 'opencode.json').read_text())
        self.assertEqual(config['model'], 'keep')
        self.assertEqual(config['permission']['read']['custom'], 'allow')
        self.assertFalse((self.home / '.claude').exists())
        before = self.snapshot()
        self.install('--tools=opencode')
        self.assertEqual(before, self.snapshot())

    def test_unmanaged_config_and_agent_links(self):
        outside = self.home / 'outside'
        outside.mkdir()
        (outside / 'config.toml').write_text('model = "custom"\n')
        (outside / 'agent.toml').write_text('name = "custom"\n')
        directory = self.home / '.codex'
        (directory / 'agents').mkdir(parents=True)
        (directory / 'config.toml').symlink_to(outside / 'config.toml')
        (directory / 'agents/_my-reviewer.toml').symlink_to(outside / 'agent.toml')
        (directory / 'agents/_my-reviewer.toml.bak').write_text('previous')
        self.install('--tools=codex')
        self.assertEqual((outside / 'config.toml').read_text(), 'model = "custom"\n')
        self.assertEqual((outside / 'agent.toml').read_text(), 'name = "custom"\n')
        self.assertTrue((directory / 'agents/_my-reviewer.toml.bak.1').is_symlink())
        config = tomllib.loads((directory / 'config.toml').read_text())
        self.assertEqual(config['model'], 'custom')
        for role in ['reviewer', 'security-reviewer']:
            config = tomllib.loads((directory / f'agents/_my-{role}.toml').read_text())
            self.assertEqual(config['sandbox_mode'], 'read-only')

    def test_codex_defaults_insert_into_existing_sections(self):
        directory = self.home / '.codex'
        directory.mkdir()
        config_file = directory / 'config.toml'
        config_file.write_text('model = "custom"\ndefault_permissions = "custom"\n\n'
                               '[features]\ncustom = true\n\n[tui]\ntheme = "custom"\n')
        self.install('--tools=codex')
        config = tomllib.loads(config_file.read_text())
        self.assertEqual(config['model'], 'custom')
        self.assertNotIn('sandbox_mode', config)
        self.assertEqual(config['features'], {'custom': True, 'memories': False})
        self.assertEqual(config['tui']['theme'], 'custom')
        self.assertEqual(config['tui']['alternate_screen'], 'always')
        before = config_file.read_text()
        self.install('--tools=codex')
        self.assertEqual(config_file.read_text(), before)

    def test_codex_defaults_respect_commented_section_headers(self):
        directory = self.home / '.codex'
        directory.mkdir()
        config_file = directory / 'config.toml'
        config_file.write_text('model = "custom"\ndefault_permissions = "custom"\n\n'
                               '[features] # keep this note\ncustom = true\n\n'
                               '[tui] # another note\ntheme = "custom"\n')

        self.install('--tools=codex')
        text = config_file.read_text()
        config = tomllib.loads(text)
        self.assertEqual(text.count('[features]'), 1)
        self.assertEqual(text.count('[tui]'), 1)
        self.assertEqual(config['features'], {'custom': True, 'memories': False})
        self.assertEqual(config['tui']['theme'], 'custom')
        self.assertEqual(config['tui']['alternate_screen'], 'always')
        self.assertEqual(config['default_permissions'], 'custom')
        self.assertNotIn('sandbox_mode', config)
        self.install('--tools=codex')
        self.assertEqual(config_file.read_text(), text)

    def test_shared_references_link_preserves_existing_directory(self):
        references = self.home / '.agents/references'
        references.mkdir(parents=True)
        (references / 'progress.md').write_text('custom\n')
        self.install('--tools=universal')
        self.assertTrue(references.is_symlink())
        self.assertEqual(os.readlink(references), str(ROOT / '.agents/references'))
        self.assertTrue((references / 'progress.md').is_file())
        self.assertEqual((self.home / '.agents/references.bak/progress.md').read_text(), 'custom\n')
        before = self.snapshot()
        self.install('--tools=universal')
        self.assertEqual(before, self.snapshot())

    def test_harness_agent_metadata(self):
        self.install('--tools=claude,opencode,copilot,grok')

        def frontmatter(path):
            header = path.read_text().split('---', 2)[1]
            fields = dict(line.split(': ', 1) for line in header.strip().splitlines()
                          if ': ' in line and not line.startswith(' '))
            return fields, header

        for role in ['implementer', 'reviewer', 'security-reviewer']:
            name = '_my-' + role
            canonical = frontmatter(ROOT / '.agents/agents' / (name + '.md'))[0]['description']
            claude = frontmatter(self.home / '.claude/agents' / (name + '.md'))[0]
            copilot = frontmatter(self.home / '.copilot/agents' / (name + '.agent.md'))[0]
            opencode, opencode_header = frontmatter(self.home / '.config/opencode/agents' / (name + '.md'))
            for fields in [claude, copilot, opencode]:
                self.assertEqual(fields['description'], canonical)
            claude_tools = set(claude['tools'].split(', '))
            copilot_tools = set(json.loads(copilot['tools']))
            self.assertNotIn('TodoWrite', claude_tools)
            self.assertEqual({'WebFetch', 'WebSearch'} <= claude_tools, role == 'security-reviewer')
            self.assertEqual('web' in copilot_tools, role == 'security-reviewer')
            self.assertIn('\n  task: deny\n', opencode_header)
        grok = frontmatter(self.home / '.grok/agents/_my-implementer.md')[0]
        self.assertEqual(grok['description'],
                         frontmatter(ROOT / '.agents/agents/_my-implementer.md')[0]['description'])

    def test_json_with_existing_local_is_backed_up(self):
        directory = self.home / '.claude'
        directory.mkdir()
        (directory / 'settings.json').write_text('{"model":"old model","custom":true}')
        (directory / 'settings.local.json').write_text('{"model":"override"}')
        (directory / 'settings.json.bak').write_text('prior backup')
        self.install('--tools=claude')
        self.assertEqual((directory / 'settings.json.bak').read_text(), 'prior backup')
        self.assertEqual(json.loads((directory / 'settings.json.bak.1').read_text())['custom'], True)
        self.assertEqual(json.loads((directory / 'settings.json').read_text())['model'], 'override')
        before = self.snapshot()
        self.install('--tools=claude')
        self.assertEqual(before, self.snapshot())

    def test_generated_rules_not_imported_and_local_command_wins(self):
        directory = self.home / '.claude'
        directory.mkdir()
        (directory / 'settings.local.json').write_text('{"statusLine":{"command":"custom-command"}}')
        self.install('--tools=claude,codex,copilot')
        settings = json.loads((directory / 'settings.json').read_text())
        self.assertEqual(settings['statusLine']['command'], 'custom-command')
        self.assertFalse((directory / 'CLAUDE.local.md').exists())
        self.assertFalse((self.home / '.codex/AGENTS.local.md').exists())
        self.install('--tools=claude,codex,copilot')
        self.assertFalse((self.home / '.codex/AGENTS.local.md').exists())
        for source in (ROOT / '.agents/skills').glob('my-*/SKILL.md'):
            text = source.read_text()
            self.assertIn('name: ' + source.parent.name, text)
            self.assertIn('description:', text)
        for skill in ['my-build', 'my-plan', 'my-security']:
            text = (self.home / f'.agents/skills/{skill}/SKILL.md').read_text()
            self.assertIn('Unsupported:', text)
        for tool in ['.claude', '.opencode']:
            for directory in ['agents', 'output-styles']:
                self.assertEqual(list((ROOT / tool / directory).glob('_my-*.md')), [])
        self.assertFalse((ROOT / '.claude/output-styles/my-humble-servant.md').exists())
        for role in ['implementer', 'reviewer', 'security-reviewer']:
            text = (self.home / f'.copilot/agents/_my-{role}.agent.md').read_text()
            self.assertIn('include-custom-instructions: true', text)
            self.assertIn('tools:', text)
            self.assertIn('"execute"', text)

    def test_invalid_json_document_shapes(self):
        directory = self.home / '.claude'
        directory.mkdir()
        local = directory / 'settings.local.json'
        for content in ['[]', 'null', '{}\n{"model":"unexpected"}']:
            local.write_text(content)
            self.install('--tools=claude')
            self.assertEqual(json.loads(local.read_text()), {})
            self.assertTrue(any(p.read_text() == content for p in directory.glob('settings.local.json.bak*')))
            self.assertEqual(json.loads((directory / 'settings.json').read_text())['model'], 'opusplan')

    def test_unknown_parent_directory_link_is_not_followed(self):
        outside = self.home / 'outside'
        outside.mkdir()
        (outside / 'untouched').write_text('keep')
        (self.home / '.config').symlink_to(outside)
        self.install('--tools=opencode', ok=False)
        self.assertEqual(list(outside.iterdir()), [outside / 'untouched'])
        self.assertEqual((outside / 'untouched').read_text(), 'keep')

    def test_full_dry_run_respects_targets(self):
        self.env['SHELL'] = '/bin/zsh'
        result = subprocess.run(['bash', str(self.root / 'install.sh'), '--dry-run', '--tools=universal'],
                                env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.snapshot(), {})
        self.assertNotIn(str(self.home / '.codex'), result.stdout)
        self.assertNotIn(str(self.home / '.claude'), result.stdout)
        self.assertIn(str(self.home / '.agents'), result.stdout)

    def test_full_dry_run_without_zsh(self):
        commands = Path(self.tmp.name) / 'commands'
        commands.mkdir()
        for name in ['apt-get', 'basename', 'dirname', 'jq']:
            (commands / name).symlink_to('/usr/bin/true' if name == 'apt-get' else shutil.which(name))
        self.env['PATH'] = str(commands)
        self.env['SHELL'] = '/bin/bash'
        result = subprocess.run(['/bin/bash', str(self.root / 'install.sh'), '--dry-run', '--tools=universal'],
                                env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Changing default shell to zsh', result.stdout)
        self.assertIn('Dry run complete.', result.stdout)
        self.assertEqual(self.snapshot(), {})

    def test_optional_homebrew_failures_warn(self):
        commands = Path(self.tmp.name) / 'commands'
        commands.mkdir()
        (commands / 'dirname').symlink_to('/usr/bin/dirname')
        brew = commands / 'brew'
        brew.write_text('#!/bin/sh\nexit 42\n')
        brew.chmod(0o755)
        self.env['PATH'] = str(commands)
        result = subprocess.run(['/bin/bash', '-c',
                                 'source "$1" --agents-only; select_package_manager; install_pretty_print_tools',
                                 'bash', str(ROOT / 'install.sh')], env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Failed to install bat', result.stdout)
        self.assertIn('Failed to install glow', result.stdout)

    def test_required_homebrew_failure_is_fatal(self):
        commands = Path(self.tmp.name) / 'commands'
        commands.mkdir()
        (commands / 'dirname').symlink_to('/usr/bin/dirname')
        brew = commands / 'brew'
        brew.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$CALLS"\nexit 42\n')
        brew.chmod(0o755)
        calls = Path(self.tmp.name) / 'calls'
        self.env['PATH'] = str(commands)
        self.env['CALLS'] = str(calls)
        result = subprocess.run(['/bin/bash', '-c',
                                 'source "$1" --agents-only; select_package_manager; install_packages',
                                 'bash', str(ROOT / 'install.sh')], env=self.env, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('brew install failed', result.stderr)
        self.assertEqual(calls.read_text(), 'install zsh fzf git jq\n')

    def test_glow_snap_fallback_with_apt(self):
        commands = Path(self.tmp.name) / 'commands'
        commands.mkdir()
        (commands / 'dirname').symlink_to('/usr/bin/dirname')
        for name in ['apt-get', 'bat', 'snap']:
            (commands / name).symlink_to('/usr/bin/true')
        brew = commands / 'brew'
        brew.write_text('#!/bin/sh\nexit 42\n')
        brew.chmod(0o755)
        sudo = commands / 'sudo'
        sudo.write_text('#!/bin/sh\nprintf "%s\\n" "$*" >> "$CALLS"\n')
        sudo.chmod(0o755)
        calls = Path(self.tmp.name) / 'calls'
        self.env['PATH'] = str(commands)
        self.env['CALLS'] = str(calls)
        result = subprocess.run(['/bin/bash', '-c',
                                 'source "$1" --agents-only; select_package_manager; install_pretty_print_tools',
                                 'bash', str(ROOT / 'install.sh')], env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(calls.read_text(), 'snap install glow\n')
        self.assertNotIn('[warn]', result.stdout)

    def test_runtime_and_unrelated_skills_untouched(self):
        files = {}
        for path in ['.claude/.credentials.json', '.codex/auth.json', '.copilot/config.json',
                     '.agents/skills/unrelated/SKILL.md', '.agents/other/content.txt']:
            target = self.home / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text('placeholder runtime content')
            files[target] = target.read_bytes()
        own_skill = self.home / '.agents/skills/my-test'
        own_skill.mkdir()
        (own_skill / 'SKILL.md').write_text('custom same-name skill')
        self.install()
        for target, content in files.items():
            self.assertEqual(target.read_bytes(), content)
        self.assertEqual((self.home / '.agents/backups/skills/my-test.bak/SKILL.md').read_text(),
                         'custom same-name skill')
        self.assertTrue(own_skill.is_symlink())
        self.assertEqual(len(list((self.home / '.agents/skills').glob('my-*'))), 13)
        self.assertFalse(any(p.name.endswith('.bak') for p in (self.home / '.agents/skills').iterdir()))

    def test_dry_run_legacy_directory_migration(self):
        directory = self.home / '.claude'
        directory.mkdir()
        for folder in ['skills', 'agents', 'output-styles']:
            (directory / folder).symlink_to(ROOT / '.claude' / folder)
        opencode = self.home / '.config/opencode'
        opencode.mkdir(parents=True)
        (opencode / 'agents').symlink_to(ROOT / '.opencode/agents')
        before = self.snapshot()
        self.install('--dry-run')
        self.assertEqual(before, self.snapshot())

    def test_conflicting_claude_skill_link_backup_not_discovered(self):
        outside = self.home / 'outside'
        outside.mkdir()
        (outside / 'SKILL.md').write_text('custom same-name skill')
        directory = self.home / '.claude/skills'
        directory.mkdir(parents=True)
        (directory / 'my-test').symlink_to(outside)
        self.install('--tools=claude')
        backups = self.home / '.agents/backups/skills'
        backup = backups / 'my-test.bak'
        self.assertTrue(backup.is_symlink())
        self.assertEqual((backup / 'SKILL.md').read_text(), 'custom same-name skill')
        self.assertEqual((outside / 'SKILL.md').read_text(), 'custom same-name skill')
        for root in [directory, self.home / '.agents/skills']:
            self.assertEqual(len(list(root.iterdir())), 13)
            self.assertEqual({p.name for p in root.iterdir()},
                             {p.name for p in (ROOT / '.agents/skills').iterdir()})


if __name__ == '__main__':
    unittest.main()
