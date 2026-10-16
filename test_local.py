import json
import tempfile
import unittest
import sys
import types
from unittest.mock import Mock, patch
from pathlib import Path

from dashboard import generate_dashboard
from legacy_data import normalize_data
from scraper import (safe_cell, save_results, normalize_post_url, username_from_url,
                     caption_from_metadata, should_retry, finalize_run, main)


class LocalTests(unittest.TestCase):
    def test_english_cli_resumes_historical_export(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            root = Path(tmp)
            source = root / 'datos.json'
            historical = {'perfil': {'usuario': 'sample'},
                          'publicaciones': [{'url': 'https://www.instagram.com/p/ABC/', 'descripcion': 'Original caption', 'fecha': None, 'estado': 'extraida_revisar_truncamiento', 'metodo': 'DOM'}],
                          'seguidores': [], 'seguidos': [], 'estados': {}, 'errores': []}
            original = json.dumps(historical)
            source.write_text(original, encoding='utf-8')
            api = types.ModuleType('playwright.sync_api')
            api.sync_playwright = Mock()
            page = Mock()
            context = Mock(pages=[page])
            api.sync_playwright.return_value.__enter__ = Mock(return_value=Mock())
            api.sync_playwright.return_value.__exit__ = Mock(return_value=False)
            api.sync_playwright.return_value.__enter__.return_value.chromium.launch_persistent_context.return_value = context
            arguments = ['scraper.py', '--username', 'sample', '--relationships-only', '--relationship-limit', '100', '--resume', str(source)]
            with patch.dict(sys.modules, {'playwright.sync_api': api}), patch.object(sys, 'argv', arguments), patch('scraper.wait_for_session'), patch('scraper.check_access'), patch('scraper.profile', return_value={'username': 'sample'}), patch('scraper.extract_relationships', return_value=([{'username': 'example', 'url': 'https://www.instagram.com/example/'}], 'limit_reached; partial_sample')) as relationships, patch('scraper.generate_dashboard'):
                main()
            current = json.loads((root / 'data.json').read_text(encoding='utf-8'))
            self.assertEqual(len(current['posts']), 1)
            self.assertEqual(current['posts'][0]['caption'], 'Original caption')
            self.assertEqual(len(current['followers']), 1)
            self.assertEqual(len(current['following']), 1)
            self.assertEqual(relationships.call_args.args[-1], 100)
            self.assertEqual(source.read_text(encoding='utf-8'), original)

    def test_historical_export_compatibility(self):
        historical = {'perfil': {'usuario': 'sample'},
                      'publicaciones': [{'descripcion': 'Texto original', 'estado': 'descripcion_no_detectada'}],
                      'seguidores': [{'usuario': 'example'}], 'seguidos': [],
                      'estados': {'seguidores': 'limite_alcanzado; muestra_parcial'}}
        current = normalize_data(historical)
        self.assertEqual(current['profile']['username'], 'sample')
        self.assertEqual(current['posts'][0]['caption'], 'Texto original')
        self.assertEqual(current['statuses']['followers'], 'limit_reached; partial_sample')
        self.assertIn('perfil', historical)
        self.assertNotIn('profile', historical)

    def test_current_export_takes_priority(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            root = Path(tmp)
            run = root / 'run'
            run.mkdir()
            historical = {'perfil': {'usuario': 'old_marker'}, 'publicaciones': []}
            original = json.dumps(historical)
            (run / 'datos.json').write_text(original, encoding='utf-8')
            html = generate_dashboard(root, root / 'view.html').read_text(encoding='utf-8')
            self.assertIn('old_marker', html)
            save_results({'profile': {'username': 'current_marker'}, 'posts': [], 'followers': [], 'following': []}, run)
            html = generate_dashboard(root, root / 'view.html').read_text(encoding='utf-8')
            self.assertIn('current_marker', html)
            self.assertNotIn('old_marker', html)
            self.assertEqual((run / 'datos.json').read_text(encoding='utf-8'), original)

    def test_disconnected_driver_cleanup(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            data = {'profile': {}, 'posts': [], 'followers': [], 'following': [],
                     'errors': ['KeyboardInterrupt: ']}
            context = Mock()
            context.close.side_effect = RuntimeError('Connection closed while reading from the driver')
            with patch('scraper.generate_dashboard') as generate_view:
                finalize_run(context, data, Path(tmp))
                generate_view.assert_called_once_with(Path(tmp).parent)
            saved = json.loads((Path(tmp) / 'data.json').read_text(encoding='utf-8'))
            self.assertEqual(saved['errors'][0], 'KeyboardInterrupt: ')
            self.assertIn('Connection closed', saved['errors'][1])
            self.assertEqual(saved['summary']['posts'], 0)

    def test_metadata_caption(self):
        self.assertEqual(caption_from_metadata('30 likes, 2 comments - elrubiuswtf on May 1: "Hello: world 🌍\nAnother line"', 'elrubiuswtf'), 'Hello: world 🌍\nAnother line')
        self.assertIsNone(caption_from_metadata('Instagram: "Sign in"', 'elrubiuswtf'))
        self.assertIsNone(caption_from_metadata('someone_else on May 1: "Comment"', 'elrubiuswtf'))
        self.assertIsNone(caption_from_metadata('elrubiuswtf: ""', 'elrubiuswtf'))

    def test_retry_incomplete(self):
        row = {'status': 'caption_not_detected', 'caption': None, 'date': '2026-10-16'}
        self.assertFalse(should_retry(row))
        self.assertTrue(should_retry(row, True))
        self.assertTrue(should_retry({'status': 'error'}))
        self.assertFalse(should_retry({'status': 'extracted', 'caption': 'Text', 'date': '2026-10-16'}, True))

    def test_urls(self):
        self.assertIsNone(username_from_url('https://example.org/someone/'))
        self.assertIsNone(username_from_url('https://instagram.com/accounts/'))
        self.assertEqual(username_from_url('https://instagram.com/someone/'), 'someone')
        self.assertEqual(normalize_post_url('https://instagram.com/someone/reel/Ab_12/?x=1'),
                         'https://www.instagram.com/reel/Ab_12/')
        self.assertIsNone(normalize_post_url('https://example.org/p/123/'))

    def test_formula_csv(self):
        self.assertEqual(safe_cell('  =1+2'), "'  =1+2")
        self.assertEqual(safe_cell('get_text'), 'get_text')

    def test_save_and_dashboard(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            root = Path(tmp)
            data = {'profile': {'username': 'sample', 'bio': '</script><script>alert(1)</script>'},
                     'posts': [], 'followers': [], 'following': []}
            save_results(data, root / 'run')
            self.assertEqual(json.loads((root / 'run/data.json').read_text(encoding='utf-8')), data)
            (root / 'broken').mkdir()
            (root / 'broken/data.json').write_text('{')
            html = generate_dashboard(root, root / 'view.html').read_text(encoding='utf-8')
            self.assertNotIn('</script><script>alert', html)
            self.assertIn('\\u003c/script>', html)
            self.assertTrue((root / 'run/posts.csv').exists())

    def test_empty_results(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as tmp:
            root = Path(tmp)
            html = generate_dashboard(root, root / 'view.html').read_text(encoding='utf-8')
            self.assertIn('const runs=[];', html)


if __name__ == '__main__':
    unittest.main()

