"""Regression tests for mobile-price validation and daily history consistency."""
import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("validate_mobile_prices", "scripts/validate-mobile-prices.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class MobilePriceValidationTests(unittest.TestCase):
    def test_rejects_suspicious_low_iphone_offer_without_peer_reference(self):
        phone = {"model": "iPhone 15", "brand": "Apple", "prices": [{"store": "Example", "price": 12749}]}
        changed, removed = MODULE.repair_phone(phone)
        self.assertEqual((changed, removed), (0, 1))
        self.assertEqual(phone["prices"], [])

    def test_corrects_tenfold_iphone_error_when_peer_offer_supports_it(self):
        phone = {"model": "iPhone 15", "brand": "Apple", "prices": [
            {"store": "Example A", "price": 12749},
            {"store": "Example B", "price": 127499},
        ]}
        changed, removed = MODULE.repair_phone(phone)
        self.assertEqual(changed, 1)
        self.assertEqual(removed, 0)
        self.assertIn(127499, [offer["price"] for offer in phone["prices"]])

    def test_metadata_counts_only_valid_numeric_offers_and_stores(self):
        data = {}
        phones = [{"prices": [
            {"store": "A", "price": 10000},
            {"store": "B", "price": None},
            {"store": "A", "price": 0},
            {"store": "", "price": 12000},
        ]}]
        MODULE.refresh_metadata(data, phones)
        self.assertEqual(data["price_count"], 1)
        self.assertEqual(data["store_count"], 1)
        self.assertEqual(data["variant_count"], 1)

    def test_validated_catalogue_replaces_todays_history_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            history_path = Path(directory) / "history.json"
            today = datetime.now(timezone.utc).date().isoformat()
            history_path.write_text(json.dumps({
                "updated_at": None,
                "days": [{"date": today, "phones": [{"slug": "iphone-15", "model": "iPhone 15",
                          "best_price": 12749, "best_store": "Bad source",
                          "offers": [{"store": "Bad source", "price": 12749}]}]}]
            }), encoding="utf-8")
            phones = [{"slug": "iphone-15", "model": "iPhone 15", "prices": [
                {"store": "Verified source", "price": 127499}
            ]}]
            count = MODULE.sync_today_history(phones, history_path=history_path)
            saved = json.loads(history_path.read_text(encoding="utf-8"))
            today_entry = next(day for day in saved["days"] if day["date"] == today)
            self.assertEqual(count, 1)
            self.assertEqual(today_entry["phones"][0]["best_price"], 127499)
            self.assertEqual(today_entry["phones"][0]["best_store"], "Verified source")
            self.assertEqual(phones[0]["history"][-1]["price"], 127499)


if __name__ == "__main__":
    unittest.main()
