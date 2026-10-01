"""Run the installer only in isolated homes. Python is a test dependency only."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
import json
import tomllib
import shutil

ROOT = Path(__file__).resolve().parents[1]


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="agents-install-")
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name) / "home with ' quotes $ and `ticks`"
        self.home.mkdir()
        self.env = {k: v for k, v in os.environ.items() if k not in {
            'CLAUDE_CONFIG_DIR', 'CODEX_HOME', 'COPILOT_HOME', 'XDG_CONFIG_HOME',
            'GEMINI_CLI_HOME', 'XDG_DATA_HOME'}}
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
        self.assertEqual(len(list((self.home / '.agents/skills').iterdir())), 12)
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
        self.assertEqual(len(list((self.home / '.agents/skills').glob('my-*'))), 12)
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
            self.assertEqual(len(list(root.iterdir())), 12)
            self.assertEqual({p.name for p in root.iterdir()},
                             {p.name for p in (ROOT / '.agents/skills').iterdir()})


if __name__ == '__main__':
    unittest.main()
