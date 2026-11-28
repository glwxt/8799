"""ICI official route selection and missing data behavior."""
import sys
import unittest
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.error import HTTPError
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import fund_flows as f


def fixture(week, equity=53322, muni=-482):
    pairs = [("Equity", equity + 21478), ("Domestic", equity), ("World", 21478),
             ("Bond", 1741), ("Taxable", 2223), ("Municipal", muni)]
    return (f"<table><tr><th></th><th>{week}</th></tr>"
            + "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in pairs)
            + "</table>").encode()


def blocked(url):
    return HTTPError(url, 403, "Forbidden", None, None)


class IciRoutesTest(unittest.TestCase):
    def collect(self, replies, today=date(2026, 11, 28)):
        def dl(url):
            if url in replies:
                return replies[url]
            raise blocked(url)
        with TemporaryDirectory() as d, patch.object(f, "download", side_effect=dl):
            return f.collect_ici(today, Path(d))

    def test_alias_after_primary_block(self):
        result, errors = self.collect({f.ICI_GLOBAL: fixture("11/18/2026")})
        self.assertEqual(result[1], f.ICI_GLOBAL)
        self.assertEqual([r["value"] for r in result[3]], [53322, 1741])
        self.assertIn(f.ICI, errors)

    def test_wait_for_current_week_if_old_source_returns(self):
        result, _ = self.collect({f.ICI: fixture("11/18/2026"),
                                  f.ICI_GLOBAL: fixture("11/25/2026")})
        self.assertEqual(result[0], "2026-11-25")
        self.assertEqual(result[1], f.ICI_GLOBAL)

    def test_stale_routes_conflict(self):
        result, errors = self.collect({f.ICI: fixture("11/18/2026"),
                                       f.ICI_GLOBAL: fixture("11/18/2026", equity=53000)})
        self.assertIsNone(result)
        self.assertIn("same_period_check", errors)

    def test_bad_reconciliation_and_blocked_are_not_zero(self):
        result, errors = self.collect({f.ICI: fixture("11/18/2026", muni=-400)})
        self.assertIsNone(result)
        self.assertEqual(len(errors), 4)
        self.assertIn("reconcile", errors[f.ICI])

    def test_stable_primary_does_not_probe_alias(self):
        result, errors = self.collect({f.ICI: fixture("11/18/2026")}, date(2026, 11, 27))
        self.assertEqual(result[1], f.ICI)
        self.assertFalse(errors)
