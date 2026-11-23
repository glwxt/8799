"""Stage BTC, ICI and JPX net-flow evidence for GLT research reports."""

import argparse
import hashlib
import json
import re
from io import BytesIO
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from decimal import Decimal
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen

BTC = "https://farside.co.uk/bitcoin-etf-flow-all-data/"
ICI = "https://www.ici.org/research/stats/etf_flows"
JPX = "https://www.jpx.co.jp/english/markets/statistics-equities/investor-type/"


class Tables(HTMLParser):
    def __init__(self, raw):
        super().__init__()
        self.tables = []
        self.links = []
        self.table = self.row = self.cell = None
        self.depth = 0
        self.feed(raw.decode("utf-8"))

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)
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


def jpx_workbook(raw, start, end):
    from openpyxl import load_workbook

    book = load_workbook(BytesIO(raw), read_only=True, data_only=True)
    try:
        sheet = next(s for s in book if "Stocks by Investor" in s.title)
        rows = iter(sheet.values)
        headers = [next(rows) for _ in range(7)]
        column = next(i for i, label in enumerate(headers[3])
                      if isinstance(label, str) and "Foreigners" in label)
        if not all(label in str(headers[6][column + i])
                   for i, label in enumerate(("Sales", "Purchases", "Balance"))):
            raise ValueError("JPX foreign investor columns changed")
        if "1,000 yen" not in str(headers[6][2]):
            raise ValueError("JPX source unit changed")
        market = None
        for row in rows:
            if row[1]:
                market = " ".join(str(row[1]).split())
            if not market or "Tokyo & Nagoya Markets" not in market or "Value" not in str(row[2]):
                continue
            sales, purchases, balance = row[column:column + 3]
            if any(v is None or v == "" or v == "-" for v in (sales, purchases, balance)):
                net = None
            else:
                if any(type(v) is not int for v in (sales, purchases, balance)):
                    raise ValueError("Unexpected JPX value cell")
                if purchases - sales != balance:
                    raise ValueError("JPX foreign investor purchases minus sales mismatch")
                net = balance * 1000
            return {
                "indicator": "asia_equity_flow", "observation_date": end.isoformat(),
                "period_start": start.isoformat(), "frequency": "weekly",
                "unit": "JPY", "value": net, "status": "reported" if net is not None else "missing",
                "scope": "JPX Tokyo and Nagoya markets aggregate, foreign investors",
                "market": "Japan", "published_at": None, "index_url": JPX,
            }
    finally:
        book.close()
    raise ValueError("JPX Tokyo and Nagoya value row not found")


def collect_jpx(started_at, raw_dir):
    from zipfile import BadZipFile

    index = download(JPX)
    (raw_dir / "jpx_index.html").write_bytes(index)
    pattern = re.compile(r"/english/markets/statistics-equities/investor-type/"
                         r"[a-zA-Z0-9-]+/stock_1_w_(\d{8})_(\d{8})\.xlsx")
    today = started_at.astimezone(ZoneInfo("Asia/Tokyo")).date()
    candidates = []
    for href in Tables(index).links:
        match = pattern.fullmatch(href)
        if match:
            start, end = (datetime.strptime(part, "%Y%m%d").date() for part in match.groups())
            if start <= end <= today and (end - start).days <= 6:
                candidates.append((end, start, href))
    if not candidates:
        raise ValueError("No dated JPX weekly workbook link")
    end, start, href = max(candidates)
    url = urljoin(JPX, href)
    raw = download(url)
    (raw_dir / "jpx.xlsx").write_bytes(raw)
    try:
        return url, raw, jpx_workbook(raw, start, end)
    except BadZipFile as error:
        raise ValueError("Invalid JPX workbook") from error


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
    try:
        url, raw, observation = collect_jpx(start, args.raw_dir)
        observations.append(dict(observation, source_url=url, sha256=hashlib.sha256(raw).hexdigest(),
                                 retrieved_at=datetime.now(timezone.utc).isoformat()))
    except (OSError, ValueError, KeyError, IndexError, StopIteration, ImportError) as error:
        errors["jpx"] = f"{type(error).__name__}: {error}"
    result = {
        "schema": "glt-l4-scheduled-evidence-v1", "started_at": start.isoformat(),
        "eligible_for_official_score": False, "observations": observations, "errors": errors,
    }
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Funds-flow evidence: {len(observations)} observations, {len(errors)} source errors")


if __name__ == "__main__":
    main()
