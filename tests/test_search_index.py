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

    def test_includes_noindex_redirect_and_titleless_html_pages(self):
        private = parse_page('<title>Private</title><meta name="robots" content="noindex,follow">', "private.html")
        redirect = parse_page('<title>Redirecting</title><meta http-equiv="refresh" content="0;url=/new/">', "redirect.html")
        untitled = parse_page('<body><p>Visible content without a title</p></body>', "my-untitled-page.html")
        self.assertEqual(private["url"], "/private.html")
        self.assertEqual(redirect["url"], "/redirect.html")
        self.assertEqual(untitled["title"], "My Untitled Page")
        self.assertIn("Visible content", untitled["content"])

    def test_keeps_each_html_file_even_with_same_canonical_url(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / "a").mkdir(); (root / "b").mkdir()
            canonical = '<link rel="canonical" href="https://laxmannepal.com.np/shared/">'
            (root / "a/page.html").write_text(f'<html><head><title>First page</title>{canonical}</head><body><p>Short</p></body></html>')
            (root / "b/page.html").write_text(f'<html><head><title>Second page</title>{canonical}</head><body><p>More text for search content</p></body></html>')
            (root / "c").mkdir()
            (root / "c/page.htm").write_text('<title>Not an HTML suffix match</title>')
            items = build_index(root)
            self.assertEqual(len(items), 2)
            self.assertEqual({item["url"] for item in items}, {"/a/page.html", "/b/page.html"})

if __name__ == "__main__":
    unittest.main()
