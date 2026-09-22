"""Regression checks for mandatory anomaly carry-forward versus fresh leads."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('briefing_audit', Path(__file__).with_name('briefing-audit.py'))
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

class ContinuityExtractionTest(unittest.TestCase):
    def test_carried_anomaly_preserves_evidence_without_becoming_a_lead(self):
        parser = audit.BriefingExtractor()
        parser.feed('<article class="c"><h3>Fresh lens lead</h3></article>'
                    '<article class="c anomaly" data-anomaly-id="stable-id">'
                    '<h3>Carried watch</h3><p>Claim 17 million '
                    '<a href="https://example.org/evidence">evidence</a></p></article>'
                    '<article class="c"><h3>Following lens lead</h3></article>')
        self.assertEqual(parser.headings, ['Fresh lens lead', 'Following lens lead'])
        self.assertIn('Claim 17 million ', parser.text_parts)
        self.assertIn('https://example.org/evidence', parser.sources)

    def test_actual_repeated_lens_lead_still_fails(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / '2026-09-22.html'
            p.write_text('<article class="c"><h3>Repeated substantive lead</h3>'
                         '<a href="https://example.org/source">source</a></article>')
            context = {'issues': [{'date': '2026-09-21',
                'lead_titles': ['Repeated substantive lead'],
                'normalized_lead_titles': ['repeated substantive lead']} ]}
            result = audit.audit_candidate(p, context)
            self.assertFalse(result['ok'])
            self.assertTrue(any('Repeated lead title' in e for e in result['errors']))

if __name__ == '__main__':
    unittest.main()
