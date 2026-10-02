"""Regression checks for the Stage 1e stylesheet floor (Briefings 096-097 shipped unstyled)."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('validate', Path(__file__).with_name('validate.py'))
validate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate)

ISSUE_CSS = '.known{color:#e2e8f0}\n' + '/* inherited issue rules */\n' * 100
LINK = '<link rel="stylesheet" href="../assets/cyborg-v3-2.css">'


def page(head, body):
    return f'<!doctype html><html><head><title>t</title>{head}</head><body>{body}</body></html>'


def errors(text, number=90):
    report = validate.Report()
    validate.validate_styles(Path('2026-01-01.html'), text, report, number)
    return report.errors


class StylesheetFloorTest(unittest.TestCase):
    def test_styled_issue_passes(self):
        self.assertEqual(errors(page(f'<style>{ISSUE_CSS}</style>{LINK}',
                                     '<p class="known">x</p>')), [])

    def test_missing_embedded_stylesheet_fails(self):
        found = errors(page(LINK, '<p class="known">x</p>'))
        self.assertTrue(any('per-issue embedded stylesheet' in e for e in found))
        self.assertTrue(any('no rule' in e and 'known' in e for e in found))

    def test_shared_link_must_follow_embedded_styles(self):
        found = errors(page(f'{LINK}<style>{ISSUE_CSS}</style>', '<p class="known">x</p>'))
        self.assertTrue(any('must load after' in e for e in found))

    def test_unresolved_class_fails(self):
        found = errors(page(f'<style>{ISSUE_CSS}</style>{LINK}', '<p class="no-such-rule">x</p>'))
        self.assertTrue(any('no-such-rule' in e for e in found))

    def test_schema_era_sections_need_h2(self):
        body = '<section class="s" id="s-ov"><div class="known">Overview</div></section>'
        found = errors(page(f'<style>{ISSUE_CSS}</style>{LINK}', body), number=91)
        self.assertTrue(any('without an <h2>' in e and 'ov' in e for e in found))


if __name__ == '__main__':
    unittest.main()
