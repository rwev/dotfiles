"""Lint the agent docs: schemas, glossary tokens, anchors, links, and duplication."""
import difflib
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / '.agents'
TERMS = DOCS / 'references/terms.md'
FENCE = re.compile(r'^```.*?^```', re.M | re.S)
ANCHOR = re.compile(r'<a id="([^"]+)"></a>')
LINK = re.compile(r'\]\(([^)\s]+)\)')
SHINGLE = 8


def body(path):
    text = path.read_text()
    if text.startswith('---\n'):
        text = text.split('\n---\n', 1)[1]
    return FENCE.sub('', text)


def prose(path):
    return re.sub(r'`[^`\n]+`', '', body(path))


def frontmatter_keys(path):
    text = path.read_text()
    if not text.startswith('---\n'):
        return []
    return re.findall(r'^([a-z][\w-]*):', text.split('\n---\n', 1)[0], re.M)


def headings(path, level='##'):
    return re.findall(rf'^{level} (.+?)\s*$', body(path), re.M)


def slug(heading):
    return re.sub(r'[^\w\- ]', '', heading.lower()).replace(' ', '-')


def section(path, name):
    match = re.search(rf'^## {re.escape(name)}\n(.*?)(?=^## |\Z)', path.read_text(), re.M | re.S)
    return match.group(1) if match else ''


def ticked(text):
    return re.findall(r'`([^`\n]+)`', text)


def resolve(source, target):
    if target.startswith('~/.agents/'):
        return DOCS / target[len('~/.agents/'):]
    return (source.parent / target).resolve() if target else source


def agents():
    return sorted((DOCS / 'agents').glob('_my-*.md'))


def skills():
    return sorted((DOCS / 'skills').glob('my-*/SKILL.md'))


def all_docs():
    return sorted(DOCS.rglob('*.md'))


def rel(path):
    return path.relative_to(ROOT)


class DocTest(unittest.TestCase):
    def report(self, errors):
        if errors:
            self.fail('\n' + '\n'.join(errors))


class GlossaryTests(DocTest):
    def test_tokens_in_glossary(self):
        tokens = set(ticked(TERMS.read_text()))
        statuses = {t for t in tokens if re.fullmatch(r'[A-Z]+(_[A-Z]+)*', t)}
        verdicts = set(ticked(section(TERMS, 'Verdicts')))
        roles = {t for t in tokens if t.startswith('_my-')}
        words = tokens - roles
        errors = []
        for path in all_docs():
            text = body(path)
            for kind, allowed in [('Status', statuses), ('Verdict', verdicts)]:
                for value in re.findall(rf'`{kind}: ([^`|]+?)`', text):
                    if value.strip() not in allowed:
                        errors.append(f'{rel(path)}: `{kind}: {value}` is not in {rel(TERMS)}')
            for span in set(ticked(text)) - tokens:
                close = difflib.get_close_matches(span, words, n=1, cutoff=0.85)
                if close:
                    errors.append(f'{rel(path)}: `{span}` is a near-miss of glossary token `{close[0]}`')
            for role in set(re.findall(r'`(_my-[\w-]+)`', text)) - roles:
                errors.append(f'{rel(path)}: role `{role}` is not in {rel(TERMS)}')
            for word in re.findall(r'\b(?:Major|Blocker|Trivial|Severe)\b', text):
                errors.append(f'{rel(path)}: severity `{word}` is not in {rel(TERMS)}; use Critical, Important, or Minor')
        self.report(errors)

    def test_caps_match_rules(self):
        words = {'2': 'two', '5': 'five'}
        rows = re.findall(r'^\| ([\w -]+?) +\| (\d+) +\| \[[^]]*\]\(([^)]+)\)', section(TERMS, 'Caps'), re.M)
        self.assertTrue(rows, f'{rel(TERMS)}: no rows under ## Caps')
        errors = []
        for name, value, link in rows:
            target, _, anchor = link.partition('#')
            match = re.search(rf'<a id="{anchor}"></a>(.*?)(?=\n- |\n\n|\Z)', resolve(TERMS, target).read_text(), re.S)
            rule = match.group(1) if match else ''
            if not re.search(rf'\b({value}|{words.get(value, value)})\b', rule, re.I):
                errors.append(f'{rel(TERMS)}: cap "{name}" = {value}, but rule #{anchor} does not say {value}')
        self.report(errors)


class SchemaTests(DocTest):
    def schema(self, glob):
        for row in section(TERMS, 'Schemas').splitlines():
            cells = [c.strip() for c in row.strip('|').split('|')]
            if len(cells) == 3 and cells[0] == f'`{glob}`':
                return ticked(cells[1]), ticked(cells[2])
        self.fail(f'{rel(TERMS)}: no ## Schemas row for `{glob}`')

    def check(self, paths, glob):
        keys, sections = self.schema(glob)
        errors = []
        for path in paths:
            for found, expected, what in [(frontmatter_keys(path), keys, 'frontmatter keys'),
                                          (headings(path), sections, '## headings')]:
                order = [e.rstrip('?') for e in expected]
                required = [e for e in expected if e in order]
                if not set(found) <= set(order) or sorted(found, key=order.index) != found or \
                        not set(required) <= set(found):
                    errors.append(f'{rel(path)}: {what} {found}; schema is {expected} (? = optional)')
        self.report(errors)

    def test_agents(self):
        self.check(agents(), '_my-*.md')

    def test_skills(self):
        self.check(skills(), 'my-*/SKILL.md')


class LinkTests(DocTest):
    def test_anchors_unique_and_used(self):
        seen, errors = {}, []
        links = ' '.join(LINK.findall(' '.join(prose(p) for p in all_docs())))
        for path in all_docs():
            for anchor in ANCHOR.findall(prose(path)):
                if not re.fullmatch(r'[a-z]+(-[a-z]+)*', anchor):
                    errors.append(f'{rel(path)}: anchor "{anchor}" is not kebab-case')
                if anchor in seen:
                    errors.append(f'{rel(path)}: anchor "{anchor}" also in {rel(seen[anchor])}')
                seen[anchor] = path
                if f'#{anchor}' not in links:
                    errors.append(f'{rel(path)}: anchor "{anchor}" has no link; remove it or link to it')
        self.report(errors)

    def test_links_resolve(self):
        errors = []
        for path in all_docs():
            for link in LINK.findall(prose(path)):
                if re.match(r'[a-z]+:', link):
                    continue
                target, _, fragment = link.partition('#')
                dest = resolve(path, target)
                if not dest.is_file():
                    errors.append(f'{rel(path)}: link {link} -> missing file')
                elif fragment and fragment not in ANCHOR.findall(prose(dest)) + \
                        [slug(h) for h in headings(dest, '#{1,6}')]:
                    errors.append(f'{rel(path)}: link {link} -> no heading or anchor "#{fragment}"')
        self.report(errors)


class DuplicationTests(DocTest):
    def shingles(self, path):
        words = re.findall(r"[a-z0-9_'-]+", body(path).lower())
        return {' '.join(words[i:i + SHINGLE]) for i in range(len(words) - SHINGLE + 1)}

    def test_no_rule_text_in_skill_and_agent(self):
        agent_text = {path: self.shingles(path) for path in agents()}
        errors = []
        for skill in skills():
            mine = self.shingles(skill)
            for agent, theirs in agent_text.items():
                for phrase in sorted(mine & theirs)[:1]:
                    errors.append(f'{rel(skill)} and {rel(agent)} share "{phrase} ..."; '
                                  'keep the detail in the agent and point to it')
        self.report(errors)


if __name__ == '__main__':
    unittest.main()
