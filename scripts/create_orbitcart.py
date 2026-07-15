#!/usr/bin/env python3
"""Create the deterministic OrbitCart demo repository with genuine Git history."""

from __future__ import annotations

import os
import shutil
import subprocess
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / ".data" / "orbitcart"


def run(*args: str, env: dict[str, str] | None = None) -> None:
    subprocess.run(args, cwd=TARGET, env=env, check=True, capture_output=True, text=True)


def write(path: str, content: str) -> None:
    destination = TARGET / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")


def commit(subject: str, body: str, date: str) -> None:
    run("git", "add", ".")
    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_NAME": "OrbitCart Engineering",
            "GIT_AUTHOR_EMAIL": "engineering@orbitcart.demo",
            "GIT_COMMITTER_NAME": "OrbitCart Engineering",
            "GIT_COMMITTER_EMAIL": "engineering@orbitcart.demo",
            "GIT_AUTHOR_DATE": date,
            "GIT_COMMITTER_DATE": date,
        }
    )
    run("git", "commit", "-m", subject, "-m", body, env=env)


def build() -> None:
    if TARGET.exists():
        shutil.rmtree(TARGET)
    TARGET.mkdir(parents=True)
    run("git", "init", "-b", "main")

    write(
        "README.md",
        """
        # OrbitCart

        A deliberately small checkout service used to demonstrate how engineering
        decisions accumulate over time. Prices are represented as integer cents.
        """,
    )
    write(
        "orbitcart/pricing.py",
        """
        def subtotal(items):
            return sum(item["price_cents"] * item.get("quantity", 1) for item in items)
        """,
    )
    write(
        "orbitcart/checkout.py",
        """
        from .pricing import subtotal

        def checkout(items):
            return {"subtotal_cents": subtotal(items), "total_cents": subtotal(items)}
        """,
    )
    write("orbitcart/__init__.py", "from .checkout import checkout")
    commit(
        "feat(checkout): launch the first pricing flow",
        "Summary: Added a minimal checkout calculation based on product prices.\n\nWhy: OrbitCart needed a reliable baseline before promotions and payment processing.\n\nRisk: Pricing rules are intentionally simple and do not yet support discounts.",
        "2026-01-08T09:30:00+00:00",
    )

    write(
        "orbitcart/discounts.py",
        """
        DISCOUNTS = {"WELCOME10": 10, "SAVE20": 20}

        def apply_discount(amount_cents, code):
            percent = DISCOUNTS.get(code, 0)
            return amount_cents - (amount_cents * percent // 100)
        """,
    )
    write(
        "orbitcart/checkout.py",
        """
        from .discounts import apply_discount
        from .pricing import subtotal

        def checkout(items, discount_codes=None):
            total = subtotal(items)
            for code in discount_codes or []:
                total = apply_discount(total, code)
            return {"subtotal_cents": subtotal(items), "total_cents": total}
        """,
    )
    commit(
        "feat(discounts): support promotional codes at checkout",
        "Summary: Added percentage discount codes and allowed checkout to apply a list of codes.\n\nWhy: Marketing needed launch promotions for new customers.\n\nRisk: Multiple codes can currently be combined without a policy check.",
        "2026-01-19T11:15:00+00:00",
    )

    write(
        "history/issues/OC-17.md",
        """
        # OC-17 — Duplicate promotion can be applied twice

        A customer can submit WELCOME10 more than once and receive both reductions.
        Expected: each promotion code should affect an order at most once.
        """,
    )
    commit(
        "bug(checkout): document duplicate discount incident OC-17",
        "Summary: Recorded a production report showing the same promotion being applied twice.\n\nWhy: The original discount loop trusted the incoming list and had no uniqueness rule.\n\nRisk: Orders can be undercharged when clients resend a code.",
        "2026-02-02T14:20:00+00:00",
    )

    write(
        "orbitcart/checkout.py",
        """
        from .discounts import apply_discount
        from .pricing import subtotal

        def checkout(items, discount_codes=None):
            total = subtotal(items)
            unique_codes = list(dict.fromkeys(discount_codes or []))
            for code in unique_codes:
                total = apply_discount(total, code)
            return {"subtotal_cents": subtotal(items), "total_cents": total}
        """,
    )
    commit(
        "fix(discounts): reject duplicate promotion applications",
        "Summary: Deduplicated promotion codes before calculating the order total.\n\nWhy: This closes OC-17 with a narrow validation guard.\n\nRisk: Promotion policy remains embedded in checkout and may become difficult to extend.",
        "2026-02-03T10:05:00+00:00",
    )

    write(
        "history/issues/OC-31.md",
        """
        # OC-31 — Promotion expires early for western timezones

        Campaign expiry is evaluated using the server date rather than the customer's
        timezone. Users near midnight can lose a valid discount several hours early.
        """,
    )
    commit(
        "bug(promotions): capture timezone expiry failure OC-31",
        "Summary: Documented promotion expiry differences between server time and customer time.\n\nWhy: Date handling was added informally as campaigns became more complex.\n\nRisk: Valid promotions can be rejected around midnight.",
        "2026-02-26T18:40:00+00:00",
    )

    write(
        "orbitcart/pricing.py",
        """
        from datetime import datetime, timezone
        from .discounts import apply_discount

        def subtotal(items):
            return sum(item["price_cents"] * item.get("quantity", 1) for item in items)

        def calculate_total(items, discount_codes=None, now=None):
            now = now or datetime.now(timezone.utc)
            total = subtotal(items)
            for code in dict.fromkeys(discount_codes or []):
                total = apply_discount(total, code)
            return total
        """,
    )
    write(
        "orbitcart/checkout.py",
        """
        from .pricing import calculate_total, subtotal

        def checkout(items, discount_codes=None, now=None):
            return {
                "subtotal_cents": subtotal(items),
                "total_cents": calculate_total(items, discount_codes, now),
            }
        """,
    )
    commit(
        "refactor(pricing): centralize totals and promotion rules",
        "Summary: Moved discount calculation into a single pricing module and made time an explicit input.\n\nWhy: Fixing OC-31 safely required one consistent location for pricing decisions.\n\nRisk: The pricing module is now a critical dependency for every checkout.",
        "2026-03-04T08:50:00+00:00",
    )

    write(
        "history/issues/OC-44.md",
        """
        # OC-44 — Checkout latency spike

        Large carts repeatedly calculate the same product totals. P95 checkout latency
        increased after promotion rules moved into the central pricing path.
        """,
    )
    commit(
        "perf(checkout): record repeated pricing latency OC-44",
        "Summary: Captured evidence that repeated pricing calculations slowed large carts.\n\nWhy: Centralization made correctness clearer but placed more work on the checkout path.\n\nRisk: Checkout abandonment may increase if latency continues to rise.",
        "2026-03-23T16:10:00+00:00",
    )

    write(
        "orbitcart/cache.py",
        """
        _prices = {}

        def get(product_id):
            return _prices.get(product_id)

        def put(product_id, price_cents):
            _prices[product_id] = price_cents

        def clear():
            _prices.clear()
        """,
    )
    write(
        "orbitcart/pricing.py",
        """
        from datetime import datetime, timezone
        from . import cache
        from .discounts import apply_discount

        def item_price(item):
            cached = cache.get(item["id"])
            if cached is not None:
                return cached
            cache.put(item["id"], item["price_cents"])
            return item["price_cents"]

        def subtotal(items):
            return sum(item_price(item) * item.get("quantity", 1) for item in items)

        def calculate_total(items, discount_codes=None, now=None):
            now = now or datetime.now(timezone.utc)
            total = subtotal(items)
            for code in dict.fromkeys(discount_codes or []):
                total = apply_discount(total, code)
            return total
        """,
    )
    commit(
        "perf(pricing): cache product prices during checkout",
        "Summary: Added an in-memory price cache to avoid repeated product lookups.\n\nWhy: This directly addresses the latency reported in OC-44.\n\nRisk: Cached prices have no invalidation path when catalog prices change.",
        "2026-03-27T12:35:00+00:00",
    )

    write(
        "history/issues/OC-52.md",
        """
        # OC-52 — Checkout displays an outdated product price

        After the catalog changes a price, checkout can continue charging the previous
        value until the service restarts. First observed after the pricing cache release.
        """,
    )
    commit(
        "bug(pricing): report stale checkout prices OC-52",
        "Summary: Recorded that checkout can retain an old price after a catalog update.\n\nWhy: The new cache stores prices indefinitely and never observes catalog changes.\n\nRisk: Customers may be overcharged or undercharged.",
        "2026-04-01T07:45:00+00:00",
    )

    write(
        "orbitcart/pricing.py",
        """
        from datetime import datetime, timezone
        from .discounts import apply_discount

        def subtotal(items):
            return sum(item["price_cents"] * item.get("quantity", 1) for item in items)

        def calculate_total(items, discount_codes=None, now=None):
            now = now or datetime.now(timezone.utc)
            total = subtotal(items)
            for code in dict.fromkeys(discount_codes or []):
                total = apply_discount(total, code)
            return total
        """,
    )
    commit(
        "revert(pricing): disable unsafe price cache",
        "Summary: Removed cache reads from pricing while preserving the module for follow-up work.\n\nWhy: Correct totals are more important than the latency improvement.\n\nRisk: OC-44 performance symptoms may return until a safe design ships.",
        "2026-04-01T13:25:00+00:00",
    )

    write(
        "orbitcart/cache.py",
        """
        _prices = {}

        def get(product_id, version):
            return _prices.get((product_id, version))

        def put(product_id, version, price_cents):
            _prices[(product_id, version)] = price_cents

        def invalidate(product_id):
            for key in [key for key in _prices if key[0] == product_id]:
                del _prices[key]

        def clear():
            _prices.clear()
        """,
    )
    write(
        "orbitcart/pricing.py",
        """
        from datetime import datetime, timezone
        from . import cache
        from .discounts import apply_discount

        def item_price(item):
            version = item.get("price_version", 1)
            cached = cache.get(item["id"], version)
            if cached is not None:
                return cached
            cache.put(item["id"], version, item["price_cents"])
            return item["price_cents"]

        def subtotal(items):
            return sum(item_price(item) * item.get("quantity", 1) for item in items)

        def calculate_total(items, discount_codes=None, now=None):
            now = now or datetime.now(timezone.utc)
            total = subtotal(items)
            for code in dict.fromkeys(discount_codes or []):
                total = apply_discount(total, code)
            return total
        """,
    )
    commit(
        "fix(cache): key prices by catalog version",
        "Summary: Reintroduced caching with catalog versions and an explicit invalidation function.\n\nWhy: Versioned keys preserve the OC-44 speedup without retaining obsolete prices.\n\nRisk: Catalog callers must increment the version whenever a product price changes.",
        "2026-04-09T09:55:00+00:00",
    )

    write(
        "tests/test_pricing.py",
        """
        import unittest
        from orbitcart import cache
        from orbitcart.pricing import item_price

        class PricingCacheTests(unittest.TestCase):
            def setUp(self):
                cache.clear()

            def test_new_version_never_reuses_old_price(self):
                old = {"id": "sku-1", "price_cents": 1000, "price_version": 1}
                new = {"id": "sku-1", "price_cents": 800, "price_version": 2}
                self.assertEqual(item_price(old), 1000)
                self.assertEqual(item_price(new), 800)

        if __name__ == "__main__":
            unittest.main()
        """,
    )
    commit(
        "test(pricing): prevent stale price regression",
        "Summary: Added a regression test proving a new catalog version cannot reuse an old cached price.\n\nWhy: OC-52 needs executable evidence that the corrected behavior remains safe.\n\nRisk: Cache performance under production load still requires monitoring.",
        "2026-04-10T15:30:00+00:00",
    )

    print(f"Created OrbitCart with 12 commits at {TARGET}")


if __name__ == "__main__":
    build()
