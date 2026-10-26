import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from generate_search_index import build_index, parse_page

class SearchIndexTests(unittest.TestCase):
    def test_extracts_content_and_ignores_navigation_and_scripts(self):
        source = """<!doctype html><html><head><title>Excel Formula Guide</title>
        <meta name="description" content="Learn Excel formulas">
        <link rel="canonical" href="https://laxmannepal.com.np/guides/excel/"></head>
        <body><header>Ignore common navigation</header><nav>Never index this</nav>
        <main><h1>Excel formulas for beginners</h1><h2>VLOOKUP and SUM</h2>
        <p>Use formulas to organize spreadsheets.</p><script>secretInjectedTerm</script></main>
        <footer>Footer boilerplate</footer></body></html>"""
        item = parse_page(source, "guides/excel/index.html")
        self.assertEqual(item["url"], "/guides/excel/")
        self.assertIn("vlookup", item["headings"].lower())
        self.assertIn("spreadsheets", item["content"].lower())
        self.assertNotIn("never index", item["content"].lower())
        self.assertNotIn("secretInjectedTerm", item["content"])

    def test_skips_noindex_and_redirect_pages(self):
        self.assertIsNone(parse_page('<title>Private</title><meta name="robots" content="noindex,follow">', "private.html"))
        self.assertIsNone(parse_page('<title>Redirecting</title><meta http-equiv="refresh" content="0;url=/new/">', "redirect.html"))

    def test_rejects_external_canonical_and_keeps_local_path(self):
        item = parse_page('<title>Local Guide</title><link rel="canonical" href="https://example.org/elsewhere/"><body><p>Text</p></body>', "guides/local.html")
        self.assertEqual(item["url"], "/guides/local.html")

    def test_deduplicates_canonical_urls(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / "a").mkdir(); (root / "b").mkdir()
            (root / "a/index.html").write_text('<html><head><title>First page</title><link rel="canonical" href="https://laxmannepal.com.np/shared/"></head><body><p>Short</p></body></html>')
            (root / "b/index.html").write_text('<html><head><title>More useful shared page</title><link rel="canonical" href="https://laxmannepal.com.np/shared/"></head><body><p>More text for search content</p></body></html>')
            items = build_index(root)
            self.assertEqual(len(items), 1)
            self.assertEqual(items[0]["url"], "/shared/")
            self.assertEqual(items[0]["title"], "More useful shared page")

if __name__ == "__main__":
    unittest.main()
