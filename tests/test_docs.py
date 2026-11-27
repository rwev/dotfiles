"""Lint the agent docs: schemas, glossary tokens, anchors, links, and duplication."""
import difflib
from pathlib import Path
import re
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / '.agents'
FENCE = re.compile(r'^```.*?^```', re.M | re.S)
ANCHOR = re.compile(r'<a id="([^"]+)"></a>')
LINK = re.compile(r'\]\(([^)\s]+)\)')
LABEL = re.compile(r'\b([A-Z][A-Za-z]+)(?=\s*[=(])')
SHINGLE = 8
CARDINALS = (
    'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine',
    'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen',
    'seventeen', 'eighteen', 'nineteen',
)


def rel(path, docs=DOCS):
    return Path(path).resolve().relative_to(Path(docs).resolve().parent)


def terms_path(docs=DOCS):
    return Path(docs) / 'references/terms.md'


def after_frontmatter(path):
    text = path.read_text()
    if text.startswith('---\n'):
        return text.split('\n---\n', 1)[1]
    return text


def frontmatter(path):
    text = path.read_text()
    if not text.startswith('---\n'):
        return ''
    return text.split('\n---\n', 1)[0]


def body(path):
    return FENCE.sub('', after_frontmatter(path))


def prose(path):
    return re.sub(r'`[^`\n]+`', '', body(path))


def frontmatter_keys(path):
    text = frontmatter(path)
    return re.findall(r'^([a-z][\w-]*):', text, re.M) if text else []


def headings(path, level='##'):
    return re.findall(rf'^{level} (.+?)\s*$', body(path), re.M)


def slug(heading):
    return re.sub(r'[^\w\- ]', '', heading.lower()).replace(' ', '-')


def section(path, name):
    match = re.search(rf'^## {re.escape(name)}\n(.*?)(?=^## |\Z)', path.read_text(), re.M | re.S)
    return match.group(1) if match else ''


def ticked(text):
    return re.findall(r'`([^`\n]+)`', text)


def resolve(source, target, docs=DOCS):
    if target.startswith('~/.agents/'):
        return Path(docs) / target[len('~/.agents/'):]
    return (source.parent / target).resolve() if target else source


def agents(docs=DOCS):
    return sorted((Path(docs) / 'agents').glob('_my-*.md'))


def skills(docs=DOCS):
    return sorted((Path(docs) / 'skills').glob('my-*/SKILL.md'))


def all_docs(docs=DOCS):
    return sorted(Path(docs).rglob('*.md'))


def glossary_statuses(text):
    return {token for token in ticked(text) if re.fullmatch(r'[A-Z]+(?:_[A-Z]+)*', token)}


def explorer_statuses(terms):
    for sentence in re.split(r'(?<=\.)\s+', section(terms, 'Statuses').strip()):
        if 'explorer uses only' in sentence:
            return {token for token in ticked(sentence) if re.fullmatch(r'[A-Z]+(?:_[A-Z]+)*', token)}
    return set()


def labeled_values(text):
    found = []
    for kind, raw in re.findall(r'`(Status|Verdict):\s*([^`\n]+)`', text):
        value = raw.strip()
        if value:
            found.append((kind, value))
    for line in text.splitlines():
        match = re.fullmatch(r'(Status|Verdict):\s*(.+)', line.strip())
        if not match:
            continue
        for part in match.group(2).split('|'):
            part = part.strip()
            if part and not part.startswith('<'):
                found.append((match.group(1), part))
    return found


def verdict_sets(terms):
    by_role, common = {}, set()
    for row in section(terms, 'Verdicts').splitlines():
        if not row.startswith('|'):
            continue
        cells = [cell.strip() for cell in row.strip('|').split('|')]
        if len(cells) < 2 or set(cells[0]) <= {'-', ' '}:
            continue
        scale = [value for value in ticked(cells[1]) if value != 'Verdict:' and not value.startswith('_my-')]
        role = re.search(r'_my-[\w-]+', cells[0])
        if role:
            by_role.setdefault(role.group(0), set()).update(scale)
        elif scale:
            common.update(scale)
    for values in by_role.values():
        values.update(common)
    union = set()
    for values in by_role.values():
        union |= values
    return by_role, union


def verdicts_for(path, by_role, union):
    if path.parent.name == 'agents' and path.name.startswith('_my-') and path.name.endswith('.md'):
        return by_role.get(path.stem, set())
    return union


def status_errors(docs=DOCS):
    terms = terms_path(docs)
    glossary = terms.read_text()
    statuses = glossary_statuses(glossary)
    subset = explorer_statuses(terms)
    by_role, union = verdict_sets(terms)
    errors = []
    for path in all_docs(docs):
        allowed = verdicts_for(path, by_role, union)
        for kind, value in labeled_values(after_frontmatter(path)):
            where = rel(path, docs)
            if kind == 'Status' and value not in statuses:
                errors.append(f'{where}: `Status: {value}` is not in {rel(terms, docs)}')
            elif kind == 'Status' and path.name == '_my-explorer.md' and value not in subset:
                errors.append(f'{where}: `Status: {value}` is not an explorer status in {rel(terms, docs)}')
            elif kind == 'Verdict' and value not in allowed:
                errors.append(f'{where}: `Verdict: {value}` is not in {rel(terms, docs)}')
    return errors


def role_errors(docs=DOCS):
    terms = terms_path(docs)
    roles = {token for token in ticked(terms.read_text()) if token.startswith('_my-')}
    errors = []
    for path in all_docs(docs):
        found = set(re.findall(r'`(_my-[\w-]+)`', body(path)))
        found.update(re.findall(r'_my-[\w-]+', frontmatter(path)))
        for role in sorted(found - roles):
            errors.append(f'{rel(path, docs)}: role `{role}` is not in {rel(terms, docs)}')
    return errors


def near_miss_errors(docs=DOCS):
    terms = terms_path(docs)
    tokens = set(ticked(terms.read_text()))
    words = tokens - {token for token in tokens if token.startswith('_my-')}
    errors = []
    for path in all_docs(docs):
        for span in set(ticked(body(path))) - tokens:
            close = difflib.get_close_matches(span, words, n=1, cutoff=0.85)
            if close:
                errors.append(f'{rel(path, docs)}: `{span}` is a near-miss of glossary token `{close[0]}`')
    return errors


def token_errors(docs=DOCS):
    return status_errors(docs) + role_errors(docs) + near_miss_errors(docs)


def paren_end(text, open_at):
    depth = 0
    for index in range(open_at, len(text)):
        if text[index] == '(':
            depth += 1
        elif text[index] == ')':
            depth -= 1
            if depth == 0:
                return index
    return len(text)


def colon_region(text, start):
    depth = 0
    for index in range(start, len(text)):
        if text[index] == '(':
            depth += 1
        elif text[index] == ')':
            depth = max(0, depth - 1)
        elif text[index] == '.' and depth == 0:
            return text[start:index]
    return text[start:]


def severity_labels(text):
    labels = []
    for match in re.finditer(r'\bseverity\s*\(', text):
        open_at = match.end() - 1
        labels.extend(LABEL.findall(text[open_at + 1:paren_end(text, open_at)]))
    for match in re.finditer(r'\bseverity:\s*', text):
        labels.extend(LABEL.findall(colon_region(text, match.end())))
    return labels


def severity_errors(docs=DOCS):
    terms = terms_path(docs)
    allowed = set(ticked(section(terms, 'Severities')))
    errors = []
    for path in all_docs(docs):
        text = after_frontmatter(path)
        if path.resolve() == terms.resolve():
            text = re.sub(r'(?ms)^## Severities\n.*?(?=^## |\Z)', '', text)
        for label in severity_labels(text):
            if label not in allowed:
                errors.append(f'{rel(path, docs)}: severity `{label}` is not in {rel(terms, docs)}')
    return errors


def cap_errors(docs=DOCS):
    terms = terms_path(docs)
    rows = re.findall(r'^\| ([\w -]+?) +\| (\d+) +\| \[[^]]*\]\(([^)]+)\)', section(terms, 'Caps'), re.M)
    errors = []
    if not rows:
        return [f'{rel(terms, docs)}: no rows under ## Caps']
    for name, value, link in rows:
        target, _, anchor = link.partition('#')
        match = re.search(
            rf'<a id="{re.escape(anchor)}"></a>(.*?)(?=\n- |\n\n|\Z)',
            resolve(terms, target, docs).read_text(), re.S)
        rule = match.group(1) if match else ''
        number = int(value)
        word = CARDINALS[number] if 0 <= number < len(CARDINALS) else value
        if not re.search(rf'\b(?:{re.escape(value)}|{re.escape(word)})\b', rule, re.I):
            errors.append(f'{rel(terms, docs)}: cap "{name}" = {value}, but rule #{anchor} does not say {value}')
    return errors


def schema_for(glob, docs=DOCS):
    for row in section(terms_path(docs), 'Schemas').splitlines():
        cells = [cell.strip() for cell in row.strip('|').split('|')]
        if len(cells) == 3 and cells[0] == f'`{glob}`':
            return ticked(cells[1]), ticked(cells[2])
    return None


def schema_errors(paths, glob, docs=DOCS):
    pair = schema_for(glob, docs)
    if not pair:
        return [f'{rel(terms_path(docs), docs)}: no ## Schemas row for `{glob}`']
    keys, sections = pair
    errors = []
    for path in paths:
        for found, expected, what in [(frontmatter_keys(path), keys, 'frontmatter keys'),
                                      (headings(path), sections, '## headings')]:
            order = [item.rstrip('?') for item in expected]
            required = [item for item in expected if item in order]
            if not set(found) <= set(order) or sorted(found, key=order.index) != found or \
                    not set(required) <= set(found) or len(found) != len(set(found)):
                errors.append(f'{rel(path, docs)}: {what} {found}; schema is {expected} (? = optional)')
    return errors


def anchor_errors(docs=DOCS):
    seen, errors, fragments = {}, [], set()
    for path in all_docs(docs):
        for link in LINK.findall(prose(path)):
            fragment = link.partition('#')[2]
            if fragment:
                fragments.add(fragment)
    for path in all_docs(docs):
        for anchor in ANCHOR.findall(prose(path)):
            if not re.fullmatch(r'[a-z]+(-[a-z]+)*', anchor):
                errors.append(f'{rel(path, docs)}: anchor "{anchor}" is not kebab-case')
            if anchor in seen:
                errors.append(f'{rel(path, docs)}: anchor "{anchor}" also in {rel(seen[anchor], docs)}')
            seen[anchor] = path
            if anchor not in fragments:
                errors.append(f'{rel(path, docs)}: anchor "{anchor}" has no link; remove it or link to it')
    return errors


def link_errors(docs=DOCS):
    errors = []
    for path in all_docs(docs):
        for link in LINK.findall(prose(path)):
            if re.match(r'[a-z]+:', link):
                continue
            target, _, fragment = link.partition('#')
            dest = resolve(path, target, docs)
            if not dest.is_file():
                errors.append(f'{rel(path, docs)}: link {link} -> missing file')
            elif fragment and fragment not in ANCHOR.findall(prose(dest)) + \
                    [slug(heading) for heading in headings(dest, '#{1,6}')]:
                errors.append(f'{rel(path, docs)}: link {link} -> no heading or anchor "#{fragment}"')
    return errors


def shingles(path):
    words = re.findall(r"[a-z0-9_'-]+", after_frontmatter(path).lower())
    return {' '.join(words[index:index + SHINGLE]) for index in range(len(words) - SHINGLE + 1)}


def duplication_errors(docs=DOCS):
    agent_text = {path: shingles(path) for path in agents(docs)}
    errors = []
    for skill in skills(docs):
        mine = shingles(skill)
        for agent, theirs in agent_text.items():
            for phrase in sorted(mine & theirs)[:1]:
                errors.append(f'{rel(skill, docs)}: shares "{phrase} ..." with {rel(agent, docs)}; '
                              'keep the detail in the agent and point to it')
    return errors


def preamble_errors(docs=DOCS):
    errors = []
    for path in list(agents(docs)) + list(skills(docs)):
        head = re.split(r'(?m)^## ', after_frontmatter(path), maxsplit=1)[0]
        if not head.strip():
            errors.append(f'{rel(path, docs)}: no preamble before the first ## heading')
    return errors


class DocTest(unittest.TestCase):
    def report(self, errors):
        if errors:
            self.fail('\n' + '\n'.join(errors))

    def copy_docs(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        dest = Path(tmp.name) / '.agents'
        shutil.copytree(DOCS, dest)
        return dest

    def assert_one_line(self, errors, *needles):
        self.assertEqual(len(errors), 1, errors)
        self.assertNotIn('\n', errors[0])
        self.assertIn(': ', errors[0])
        for needle in needles:
            self.assertIn(needle, errors[0])


class GlossaryTests(DocTest):
    def test_tokens_in_glossary(self):
        self.report(token_errors() + severity_errors())

    def test_caps_match_rules(self):
        self.report(cap_errors())

    def test_fenced_status_must_be_glossary_token(self):
        docs = self.copy_docs()
        path = docs / 'agents/_my-explorer.md'
        old = 'Status: DONE | NEEDS_CONTEXT'
        text = path.read_text()
        self.assertIn(old, text)
        path.write_text(text.replace(old, 'Status: DONE | BOGUS', 1))
        self.assert_one_line(status_errors(docs), '_my-explorer.md:', 'BOGUS')

    def test_explorer_status_subset(self):
        docs = self.copy_docs()
        path = docs / 'agents/_my-explorer.md'
        path.write_text(path.read_text() + '\n`Status: BLOCKED`\n')
        errors = status_errors(docs)
        self.assert_one_line(errors, '_my-explorer.md:', 'BLOCKED')
        self.assertNotIn('_my-implementer.md', errors[0])

    def test_frontmatter_role_must_be_glossary_token(self):
        docs = self.copy_docs()
        path = docs / 'skills/my-review/SKILL.md'
        old = 'compatibility: Requires native subagents and the _my-reviewer role.'
        text = path.read_text()
        self.assertIn(old, text)
        path.write_text(text.replace(old, 'compatibility: requires the _my-unknown role.', 1))
        self.assert_one_line(role_errors(docs), 'my-review/SKILL.md:', '_my-unknown')

    def test_severity_label_must_be_glossary_token(self):
        docs = self.copy_docs()
        path = docs / 'agents/_my-reviewer.md'
        old = (
            'severity (Critical = breaks in practice or violates the spec;\n'
            'Important = real but not urgent; Minor = nitpick)'
        )
        text = path.read_text()
        self.assertIn(old, text)
        path.write_text(text.replace(old, 'severity (Major = boom)', 1))
        self.assert_one_line(severity_errors(docs), '_my-reviewer.md:', 'Major')

    def test_verdict_must_match_role_scale(self):
        docs = self.copy_docs()
        path = docs / 'agents/_my-reviewer.md'
        path.write_text(path.read_text() + '\n`Verdict: Needs shrinks`\n')
        self.assert_one_line(status_errors(docs), '_my-reviewer.md:', '`Verdict: Needs shrinks`')

    def test_verdict_role_name_is_not_a_value(self):
        docs = self.copy_docs()
        path = docs / 'agents/_my-reviewer.md'
        path.write_text(path.read_text() + '\n`Verdict: _my-reviewer`\n')
        self.assert_one_line(status_errors(docs), '_my-reviewer.md:', '`Verdict: _my-reviewer`')

    def test_cap_value_missing_from_rule(self):
        docs = self.copy_docs()
        terms = docs / 'references/terms.md'
        line = '| fix attempts | 2     | [fix-cap](~/.agents/references/orchestration.md#fix-cap)             |\n'
        row = '| sample | 3 | [fix-cap](~/.agents/references/orchestration.md#fix-cap) |\n'
        text = terms.read_text()
        self.assertIn(line, text)
        terms.write_text(text.replace(line, line + row, 1))
        self.assert_one_line(cap_errors(docs), 'terms.md:', 'sample', '3')

    def test_cap_accepts_cardinal(self):
        docs = self.copy_docs()
        terms = docs / 'references/terms.md'
        line = '| fix attempts | 2     | [fix-cap](~/.agents/references/orchestration.md#fix-cap)             |\n'
        row = '| sample | 3 | [fix-cap](~/.agents/references/orchestration.md#fix-cap) |\n'
        text = terms.read_text()
        self.assertIn(line, text)
        terms.write_text(text.replace(line, line + row, 1))
        rule = docs / 'references/orchestration.md'
        old = 'Do not retry silently.'
        self.assertIn(old, rule.read_text())
        rule.write_text(rule.read_text().replace(old, 'Do not retry silently. three', 1))
        self.assertEqual(cap_errors(docs), [])


class SchemaTests(DocTest):
    def test_agents(self):
        self.report(schema_errors(agents(), '_my-*.md'))

    def test_skills(self):
        self.report(schema_errors(skills(), 'my-*/SKILL.md'))

    def test_duplicate_heading_fails(self):
        docs = self.copy_docs()
        path = docs / 'skills/my-test/SKILL.md'
        path.write_text(path.read_text() + '\n## Process\n\nAgain.\n')
        self.assert_one_line(
            schema_errors(skills(docs), 'my-*/SKILL.md', docs),
            'my-test/SKILL.md:', "['Process', 'Process']")

    def test_duplicate_frontmatter_key_fails(self):
        docs = self.copy_docs()
        path = docs / 'skills/my-test/SKILL.md'
        old = 'name: my-test\n'
        text = path.read_text()
        self.assertIn(old, text)
        path.write_text(text.replace(old, 'name: my-test\nname: extra\n', 1))
        self.assert_one_line(
            schema_errors(skills(docs), 'my-*/SKILL.md', docs),
            'my-test/SKILL.md:', "['name', 'name', 'description']")

    def test_agent_and_skill_need_preamble(self):
        docs = self.copy_docs()
        path = docs / 'skills/my-test/SKILL.md'
        front, sep, _rest = path.read_text().partition('\n---\n')
        path.write_text(front + sep + '\n## Process\n\nDo the work.\n')
        self.assert_one_line(preamble_errors(docs), 'my-test/SKILL.md:', 'no preamble')


class LinkTests(DocTest):
    def test_anchors_unique_and_used(self):
        self.report(anchor_errors())

    def test_links_resolve(self):
        self.report(link_errors())

    def test_anchor_link_fragment_must_match_id(self):
        docs = self.copy_docs()
        path = docs / 'references/orchestration.md'
        old = '# Orchestration\n'
        text = path.read_text()
        self.assertIn(old, text)
        path.write_text(text.replace(old, '# Orchestration\n\n<a id="review"></a>\n', 1))
        self.assert_one_line(anchor_errors(docs), 'orchestration.md:', 'anchor "review"')


class DuplicationTests(DocTest):
    def test_no_rule_text_in_skill_and_agent(self):
        self.report(duplication_errors())

    def test_duplication_includes_fenced_text(self):
        docs = self.copy_docs()
        path = docs / 'skills/my-test/SKILL.md'
        path.write_text(
            path.read_text()
            + '\n```\nUse the supplied requirements, constraints, approval, and relevant findings.\n```\n')
        self.assert_one_line(
            duplication_errors(docs), 'my-test/SKILL.md:', '_my-reviewer.md')


if __name__ == '__main__':
    unittest.main()
