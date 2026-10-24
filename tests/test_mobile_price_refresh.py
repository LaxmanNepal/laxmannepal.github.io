"""Regression tests for daily mobile catalogue refresh completeness."""
import importlib.util
import unittest

SPEC = importlib.util.spec_from_file_location("refresh_mobile_prices", "scripts/refresh-mobile-prices.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class MobilePriceRefreshTests(unittest.TestCase):
    def test_partial_store_scrape_does_not_count_as_complete(self):
        previous = [
            {"slug": f"phone-{i}", "prices": [{"store": "Store A", "price": 10000 + i}]}
            for i in range(10)
        ]
        fresh = [
            {"slug": "phone-0", "prices": [{"store": "Store A", "price": 9500}]},
            {"slug": "phone-1", "prices": [{"store": "Store A", "price": 9600}]},
        ]
        health, status = MODULE.assess_source_health(
            fresh, previous, {"Store A": 2}, {}
        )
        self.assertFalse(health["Store A"])
        self.assertEqual(status["Store A"]["status"], "stale")
        self.assertGreater(status["Store A"]["minimum_expected_offers"], 2)

    def test_merge_uses_fresh_prices_and_marks_missing_failed_store_offers_stale(self):
        previous = [{
            "slug": "phone-a", "brand": "Example", "model": "Phone A",
            "prices": [
                {"store": "Store A", "price": 10000, "checked_at": "2026-10-24"},
                {"store": "Store B", "price": 12000, "checked_at": "2026-10-24"},
            ],
        }]
        fresh = [{
            "slug": "phone-a", "brand": "Example", "model": "Phone A",
            "prices": [{"store": "Store A", "price": 9000, "checked_at": "2026-10-25"}],
        }]
        merged = MODULE.merge_previous_catalogue(
            fresh, previous, {"Store A": True, "Store B": False}, "2026-10-25"
        )
        phone = merged[0]
        by_store = {offer["store"]: offer for offer in phone["prices"]}
        self.assertEqual(by_store["Store A"]["price"], 9000)
        self.assertNotIn("stale", by_store["Store A"])
        self.assertEqual(by_store["Store B"]["price"], 12000)
        self.assertTrue(by_store["Store B"]["stale"])
        self.assertEqual(phone["price"], 9000)
        self.assertFalse(phone["price_is_stale"])
        self.assertEqual(phone["fresh_offer_count"], 1)
        self.assertEqual(phone["stale_offer_count"], 1)

    def test_model_with_only_last_known_prices_is_explicitly_stale(self):
        previous = [{
            "slug": "phone-old", "brand": "Example", "model": "Phone Old",
            "price": 14000, "best_store": "Store B",
            "prices": [{"store": "Store B", "price": 14000, "checked_at": "2026-10-20"}],
        }]
        merged = MODULE.merge_previous_catalogue(
            [], previous, {"Store B": False}, "2026-10-25"
        )
        self.assertEqual(len(merged), 1)
        self.assertTrue(merged[0]["price_is_stale"])
        self.assertEqual(merged[0]["price"], 14000)
        self.assertTrue(merged[0]["prices"][0]["stale"])
        self.assertEqual(merged[0]["updated_at"], "2026-10-25") if not previous[0].get("updated_at") else None

    def test_fresh_offers_override_stale_copy_for_same_store(self):
        previous = [{
            "slug": "phone-a", "model": "Phone A",
            "prices": [{"store": "Store A", "price": 11000, "checked_at": "2026-10-24", "stale": True}],
        }]
        fresh = [{
            "slug": "phone-a", "model": "Phone A",
            "prices": [{"store": "Store A", "price": 10000, "checked_at": "2026-10-25"}],
        }]
        merged = MODULE.merge_previous_catalogue(
            fresh, previous, {"Store A": False}, "2026-10-25"
        )
        self.assertEqual(merged[0]["prices"], [{"store": "Store A", "price": 10000, "checked_at": "2026-10-25"}])
        self.assertFalse(merged[0]["price_is_stale"])


if __name__ == "__main__":
    unittest.main()
