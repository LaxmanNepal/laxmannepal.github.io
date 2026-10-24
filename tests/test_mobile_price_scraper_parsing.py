"""Tests for retailer price parsing and same-page model links."""
import importlib.util
import unittest
from unittest.mock import patch
from bs4 import BeautifulSoup

SPEC = importlib.util.spec_from_file_location("refresh_mobile_prices", "scripts/refresh-mobile-prices.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class RetailerPriceParsingTests(unittest.TestCase):
    def test_parses_nepali_indian_grouped_rupee_amounts(self):
        self.assertEqual(MODULE.money("NRP Rs . 1,27,499"), 127499)
        self.assertEqual(MODULE.money("Rs. 45,999"), 45999)
        self.assertEqual(MODULE.money("NPR 1,19,499"), 119499)

    def test_uses_sale_price_instead_of_crossed_out_price(self):
        row = BeautifulSoup(
            '<tr><td><a href="#iphone-15">iPhone 15 128GB</a></td>'
            '<td><del>NRP Rs . 1,27,499</del><span>NRP Rs . 1,19,499</span></td></tr>',
            "html.parser",
        ).tr
        self.assertEqual(MODULE.current_price(row), 119499)

    def test_same_listing_anchor_keeps_model_name_and_listed_price(self):
        url = "https://store.nationalmobile.com.np/mobile-price-nepal/"
        html = """<table><tbody>
        <tr><td><a href="#iphone-15">iPhone 15 128GB</a></td><td><del>NRP Rs . 1,27,499</del><span>NRP Rs . 1,19,499</span></td></tr>
        <tr><td><a href="#galaxy-s25">Samsung Galaxy S25 12GB/256GB</a></td><td>NRP Rs . 1,09,999</td></tr>
        <tr><td><a href="#redmi-note">Redmi Note 15 8GB/256GB</a></td><td>NRP Rs . 39,999</td></tr>
        </tbody></table>"""
        source = {"store": "National Mobile", "url": url, "kind": "shop"}
        with patch.object(MODULE, "fetch", return_value=BeautifulSoup(html, "html.parser")):
            items = MODULE.parse_listing(source)
        self.assertEqual(len(items), 3)
        iphone = next(item for item in items if "iPhone 15" in item["title"])
        self.assertEqual(iphone["price"], 119499)
        self.assertEqual(iphone["source_url"], url)
        self.assertIn("#iphone-15", iphone["url"])

    def test_uses_current_canonical_retailer_urls(self):
        sources = {item["store"]: item["url"] for item in MODULE.SOURCES}
        self.assertEqual(sources["Oliz Store"], "https://cdn.olizstore.com/collections/phone")
        self.assertEqual(sources["National Mobile"], "https://store.nationalmobile.com.np/mobile-price-nepal/")


if __name__ == "__main__":
    unittest.main()
