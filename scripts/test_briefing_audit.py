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

    def test_source_archive_labels_are_not_leads_but_evidence_survives(self):
        parser = audit.BriefingExtractor()
        parser.feed('<section id="s-gm"><h3>Rates and credit</h3></section>'
                    '<section id="s-sa"><h3>Global markets and financial resilience</h3>'
                    '<p>Reported 25 basis points '
                    '<a href="https://example.org/primary">Primary source</a></p></section>'
                    '<section id="s-te"><h3>Following substantive lead</h3></section>')
        self.assertEqual(parser.headings, ['Rates and credit', 'Following substantive lead'])
        self.assertIn('https://example.org/primary', parser.sources)
        self.assertIn('Reported 25 basis points ', parser.text_parts)

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

    def test_market_history_extends_beyond_novelty_window_without_future_data(self):
        import tempfile
        from datetime import date, timedelta
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            briefings = repo / 'briefings'
            briefings.mkdir()
            target = date(2026, 11, 20)
            for offset in (0, 1, 2, 3, 4, 5, 6, 7, 29):
                day = target - timedelta(days=offset)
                (briefings / f'{day}.html').write_text(
                    '<section id="s-gm"><h2>Global Markets</h2>'
                    f'<h3>Thesis update {offset}</h3><p>Prior assessment.</p>'
                    '<a href="https://example.org/data">Evidence</a></section>'
                    '<section id="s-an"><article class="c anomaly" '
                    'data-anomaly-id="gm-funding"><h3>Funding thesis</h3>'
                    '<p>Next review and contrary evidence.</p></article></section>'
                )
            context = audit.build_context_manifest(repo, target)
            self.assertEqual(len(context['issues']), 4)
            history = context['markets_history']
            self.assertEqual(len(history['recent_issues']), 7)
            self.assertEqual(history['monthly_baseline']['date'], '2026-10-22')
            self.assertNotIn('2026-11-20', [r['date'] for r in history['recent_issues']])
            self.assertEqual(history['recent_issues'][0]['theses'][0]['id'], 'gm-funding')
            self.assertIn('https://example.org/data', history['recent_issues'][0]['sources'])

if __name__ == '__main__':
    unittest.main()
