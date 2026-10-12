"""Archive compatibility and prospective Global Markets structural gates."""

import importlib.util
import json
from pathlib import Path
import unittest

from bs4 import BeautifulSoup

spec = importlib.util.spec_from_file_location(
    "validate_markets", Path(__file__).with_name("validate.py"))
validate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate)
REPO = Path(__file__).resolve().parents[1]


class MarketsStructureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Frozen pre-change issue exercises the actual production validator.
        cls.original = (REPO / "briefings/2026-10-08.html").read_text()
        cls.patterns = json.loads((REPO / "concepts/registry.json").read_text())["patterns"]
        cls.number = int(validate.HEADER_RE.search(cls.original).group(1))

    def check_issue(self, text, issue_date):
        report = validate.Report()
        validate.validate_latest({
            "path": REPO / "briefings" / f"{issue_date}.html",
            "date": issue_date, "number": self.number, "html": text,
        }, self.patterns, report)
        return report.errors

    def candidate(self, count=3, deep_dive=True, wrong_order=False):
        soup = BeautifulSoup(self.original, "html.parser")
        markup = '<section class="s" id="s-gm"><h2>Global Markets</h2>'
        for index in range(count):
            markup += (f'<article class="c" data-topic-id="gm-probe-{index}">'
                       f'<h3>Distinct research question {index}</h3>'
                       f'<p><a href="https://example.org/market-{index}">Source</a></p>')
            if index == 0 and deep_dive:
                markup += '<div class="dd-panel"><h4>Mechanism</h4><p>Evidence.</p></div>'
            markup += '</article>'
        markup += '</section>'
        anchor = soup.find(id="s-sc" if wrong_order else "s-ec")
        anchor.insert_after(BeautifulSoup(markup, "html.parser"))
        return str(soup)

    def test_archive_passes_and_new_issue_requires_markets(self):
        self.assertEqual(self.check_issue(self.original, "2026-10-08"), [])
        found = self.check_issue(self.original, "2026-10-11")
        self.assertTrue(any("missing section ids gm" in error for error in found))

    def test_complete_new_section_passes_existing_validator(self):
        self.assertEqual(self.check_issue(self.candidate(), "2026-10-11"), [])

    def test_sparse_or_shallow_section_fails(self):
        found = self.check_issue(self.candidate(count=2), "2026-10-11")
        self.assertTrue(any("lens gm has 2 topics" in error for error in found))
        found = self.check_issue(self.candidate(deep_dive=False), "2026-10-11")
        self.assertTrue(any("Global Markets requires" in error for error in found))

    def test_reading_order_is_enforced(self):
        found = self.check_issue(self.candidate(wrong_order=True), "2026-10-11")
        self.assertTrue(any("canonical reading order" in error for error in found))


if __name__ == "__main__":
    unittest.main()
