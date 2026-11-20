"""Validate locked price benchmarks and calculate reproducible outcomes."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from urllib.parse import urlparse

PROTOCOL = "price-three-way-v1"
DIRECTION_CLASS = {
    "偏多": "偏多",
    "震荡偏多": "偏多",
    "震荡": "震荡",
    "震荡偏空": "偏空",
    "偏空": "偏空",
}


def timestamp(value):
    result = datetime.fromisoformat(value)
    if result.utcoffset() is None:
        raise ValueError("Timestamp must include a UTC offset")
    return result


def number(value):
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError("Expected a finite decimal") from exc
    if not result.is_finite():
        raise ValueError("Expected a finite decimal")
    return result


def required_text(data, key):
    value = data[key]
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be nonempty text")
    return value.strip()


def source(data):
    value = required_text(data, "source_url")
    url = urlparse(value)
    if url.scheme not in {"https", "http"} or not url.hostname:
        raise ValueError("source_url must be an HTTP(S) URL")
    return value


def lock_benchmark(data, asof, horizon, issued_at):
    cutoff = timestamp(asof)
    start = timestamp(data["start_at"])
    end = timestamp(data["end_at"])
    maturity = issued_at.astimezone(timezone.utc) + timedelta(
        hours={"24h": 24, "7d": 168}[horizon]
    )
    if not start <= cutoff <= issued_at < end <= maturity:
        raise ValueError("Benchmark timestamps must satisfy start <= cutoff <= issue < end <= maturity")
    start_value = number(data["start_value"])
    threshold = number(data["neutral_pct"])
    if start_value <= 0 or not 0 < threshold < 100:
        raise ValueError("Expected positive start value and neutral_pct between 0 and 100")
    benchmark = {
        key: required_text(data, key)
        for key in ("series_id", "instrument", "unit", "price_type", "calendar", "session_rule")
    }
    benchmark.update(
        source_url=source(data), start_at=start.isoformat(), end_at=end.isoformat(),
        maturity_at=maturity.isoformat(), start_value=str(start_value),
        neutral_pct=str(threshold),
    )
    return benchmark


def calculate_outcome(forecast, quote, evaluated_at):
    benchmark = forecast["benchmark"]
    observed = timestamp(quote["observed_at"])
    evaluated = timestamp(evaluated_at)
    if evaluated < timestamp(benchmark["maturity_at"]):
        raise ValueError("Forecast horizon has not matured")
    if observed != timestamp(benchmark["end_at"]):
        raise ValueError("Quote timestamp differs from the locked endpoint")
    for key in ("series_id", "unit", "price_type"):
        if required_text(quote, key) != benchmark[key]:
            raise ValueError(f"Quote {key} differs from the locked benchmark")
    end = number(quote["value"])
    if end <= 0:
        raise ValueError("Quote value must be positive")
    start = number(benchmark["start_value"])
    threshold = number(benchmark["neutral_pct"])
    change = (end - start) * 100
    if change > start * threshold:
        direction = "偏多"
    elif change < -start * threshold:
        direction = "偏空"
    else:
        direction = "震荡"
    return {
        "id": forecast["id"], "protocol": PROTOCOL, "observed_direction": direction,
        "expected_direction": DIRECTION_CLASS[forecast["direction"]],
        "exact_match": DIRECTION_CLASS[forecast["direction"]] == direction,
        "evaluated_at": evaluated.isoformat(), "observed_at": observed.isoformat(),
        "value": str(end), "return_pct": str(change / start), "source_url": source(quote),
        "series_id": benchmark["series_id"], "unit": benchmark["unit"],
        "price_type": benchmark["price_type"],
    }
