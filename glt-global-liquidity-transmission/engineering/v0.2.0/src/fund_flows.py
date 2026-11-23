"""Stage BTC and ICI net-flow evidence for GLT research reports."""

import argparse
import hashlib
import json
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from decimal import Decimal
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

BTC = "https://farside.co.uk/bitcoin-etf-flow-all-data/"
ICI = "https://www.ici.org/research/stats/etf_flows"


class Tables(HTMLParser):
    def __init__(self, raw):
        super().__init__()
        self.tables = []
        self.table = self.row = self.cell = None
        self.depth = 0
        self.feed(raw.decode("utf-8"))

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.depth += 1
            if self.depth == 1:
                self.table = []
        elif self.depth == 1 and tag == "tr":
            self.row = []
        elif self.depth == 1 and self.row is not None and tag in ("td", "th"):
            self.cell = []

    def handle_data(self, data):
        if self.depth == 1 and self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if self.depth == 1 and tag in ("td", "th") and self.cell is not None:
            self.row.append(" ".join("".join(self.cell).split()))
            self.cell = None
        elif self.depth == 1 and tag == "tr" and self.row is not None:
            if self.row:
                self.table.append(self.row)
            self.row = None
        if tag == "table" and self.depth:
            if self.depth == 1:
                self.tables.append(self.table)
                self.table = self.row = self.cell = None
            self.depth -= 1


def amount(cell):
    cell = cell.replace(",", "")
    if cell.startswith("(") and cell.endswith(")"):
        cell = "-" + cell[1:-1]
    value = Decimal(cell)
    if not value.is_finite():
        raise ValueError("Non-finite flow amount")
    return value


def bitcoin(tables, today):
    table = next(t for t in tables if t and t[0][0] == "Date" and t[0][-1] == "Total")
    funds = table[0][1:-1]
    if "IBIT" not in funds or "FBTC" not in funds or len(set(funds)) != len(funds):
        raise ValueError("Unexpected Farside fund headers")
    rows = {}
    for cells in table[1:]:
        try:
            day = datetime.strptime(cells[0], "%d %b %Y").date()
        except ValueError:
            continue
        if day > today:
            continue
        if len(cells) != len(funds) + 2 or day in rows:
            raise ValueError("Malformed or duplicate Farside date row")
        reports = [amount(cell) for cell in cells[1:-1] if cell not in ("", "-", "–", "—")]
        complete = len(reports) == len(funds)
        total = amount(cells[-1]) if complete else None
        if complete and abs(total - sum(reports)) > Decimal("0.05") * (len(funds) + 1):
            raise ValueError("Farside total does not reconcile within rounding tolerance")
        rows[day] = {
            "indicator": "btc_flow", "observation_date": day.isoformat(),
            "frequency": "daily", "unit": "USD millions",
            "value": float(total) if complete else None, "reported_funds": len(reports),
            "expected_funds": len(funds), "status": "complete" if complete else "missing_funds",
            "scope": "US spot bitcoin ETFs covered by Farside",
        }
    latest = max(rows)
    complete_dates = [day for day, row in rows.items() if row["status"] == "complete"]
    selected = {latest}
    if complete_dates:
        selected.add(max(complete_dates))
    return [rows[day] for day in sorted(selected)]


def issuance(tables, today):
    table = next(t for t in tables if {"Domestic", "World", "Bond", "Taxable", "Municipal"}
                 <= {row[0] for row in t})
    labels = {row[0]: row for row in table}
    day = datetime.strptime(table[0][1], "%m/%d/%Y").date()
    if day > today:
        raise ValueError("ICI date is after collection cutoff")
    values = {name: amount(labels[name][1])
              for name in ("Equity", "Domestic", "World", "Bond", "Taxable", "Municipal")}
    if (abs(values["Equity"] - values["Domestic"] - values["World"]) > 2
            or abs(values["Bond"] - values["Taxable"] - values["Municipal"]) > 2):
        raise ValueError("ICI totals do not reconcile within rounding tolerance")
    return issuance_rows(day, values)


def issuance_rows(day, values):
    return [
        {"indicator": key, "observation_date": day.isoformat(),
         "period_start": (day - timedelta(days=6)).isoformat(), "frequency": "weekly",
         "unit": "USD millions", "value": float(values[name]), "status": "estimated",
         "scope": scope}
        for key, name, scope in (
            ("us_equity_flow", "Domestic", "ICI domestic equity ETF estimated net issuance"),
            ("bond_flow", "Bond", "ICI bond ETF estimated net issuance (taxable and municipal)"),
        )
    ]


def workbook_issuance(raw, today):
    import xlrd

    try:
        sheet = xlrd.open_workbook(file_contents=raw).sheet_by_name("Weekly ETF Public Report")
    except xlrd.XLRDError as error:
        raise ValueError("Unexpected ICI workbook") from error
    labels = {(4, 3): "Equity", (5, 5): "Domestic", (5, 7): "World",
              (4, 11): "Bond", (5, 13): "Taxable", (5, 15): "Municipal"}
    if any(sheet.cell_value(*cell) != name for cell, name in labels.items()):
        raise ValueError("Unexpected ICI workbook columns")
    weekly = False
    dates = {}
    for row in range(6, sheet.nrows):
        label = str(sheet.cell_value(row, 0)).strip()
        if label.lower() == "estimated weekly net issuance":
            weekly = True
        if not weekly:
            continue
        try:
            day = datetime.strptime(label, "%m/%d/%Y").date()
        except ValueError:
            continue
        if day <= today:
            dates[day] = row
    day = max(dates)
    values = {name: amount(str(sheet.cell_value(dates[day], col)))
              for (_, col), name in labels.items()}
    if (abs(values["Equity"] - values["Domestic"] - values["World"]) > 2
            or abs(values["Bond"] - values["Taxable"] - values["Municipal"]) > 2):
        raise ValueError("ICI workbook totals do not reconcile")
    return issuance_rows(day, values)


def download(url):
    req = Request(url, headers={"User-Agent": "GLT research evidence collector"})
    with urlopen(req, timeout=18) as response:
        raw = response.read(4_000_001)
    if len(raw) > 4_000_000:
        raise ValueError("Evidence response too large")
    return raw


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--raw-dir", type=Path, required=True)
    args = parser.parse_args()
    args.raw_dir.mkdir(parents=True, exist_ok=True)
    start = datetime.now(timezone.utc)
    today = start.astimezone(ZoneInfo("America/New_York")).date()
    observations, errors = [], {}
    for name, url, parse in (("farside", BTC, bitcoin), ("ici", ICI, issuance)):
        try:
            try:
                raw = download(url)
                (args.raw_dir / f"{name}.html").write_bytes(raw)
                parsed = parse(Tables(raw).tables, today)
            except (OSError, ValueError, StopIteration):
                if name != "ici":
                    raise
                url = f"https://www.ici.org/etf_flows_data_{today.year}.xls"
                raw = download(url)
                (args.raw_dir / "ici.xls").write_bytes(raw)
                parsed = workbook_issuance(raw, today)
            observations.extend(
                dict(row, source_url=url, sha256=hashlib.sha256(raw).hexdigest(),
                     retrieved_at=datetime.now(timezone.utc).isoformat())
                for row in parsed
            )
        except (OSError, ValueError, KeyError, IndexError, StopIteration, ArithmeticError, ImportError) as error:
            errors[name] = f"{type(error).__name__}: {error}"
    result = {
        "schema": "glt-l4-scheduled-evidence-v1", "started_at": start.isoformat(),
        "eligible_for_official_score": False, "observations": observations, "errors": errors,
    }
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Funds-flow evidence: {len(observations)} observations, {len(errors)} source errors")


if __name__ == "__main__":
    main()
