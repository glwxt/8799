# GLT Forecast Ledger V2 (engineering v0.2.3)

## Why this extension exists
Earlier `src/forecast.py` saved model, horizon, direction and confidence, but not the actual timestamped baseline price or neutral/strong move bands. This prevents reproducible five-level directional accuracy calculations. Do **not** change historical records, or retroactively manufacture missing price baselines.

`src/forecast_v2.py` is a **new independent ledger format**, not an in-place edit or method V1.1.

## Pre-registered forecast protocol
- `model`: BTC-GT, GOLD-GT or EQUITY-GT (asset-specific). `asset` names the exact price instrument, e.g. BTCUSD or XAUUSD.
- `asof`: forecast issuance instant, mandatory UTC offset.
- `baseline-at`: price observation time; must be no later than as-of. Source URL must support the benchmark. Price source availability at as-of MUST be independently verified; the CLI alone cannot establish this.
- `baseline-price`: positive observed price with instrument-specific units.
- `neutral-pct`: first pre-registered absolute return threshold. `strong-pct`: second, strictly larger threshold; these are fixed before outcome, not optimized in hindsight.
- `horizon`: 24h or 7d. Result cannot be recorded before the time horizon ends.
- `direction`: 偏多 / 震荡偏多 / 震荡 / 震荡偏空 / 偏空. The realized move falls into five bins: return lower than -strong => 偏空; (-strong,-neutral) => 震荡偏空; [-neutral,+neutral] => 震荡; (neutral,strong] => 震荡偏多; above strong => 偏多. Negative strong boundary belongs to 震荡偏空.
- `confidence`: 0..1 confidence tag, NOT price-up probability; calibration requires later empirical tests.
- `rationale`: factual basis and invalidation triggers.
- `observed-at`: result price timestamp, at or after exact horizon deadline and within +96h (to allow non-24h stock sessions). If no genuinely comparable result is available, DO NOT score it; provide a missing-reason externally.
- `source`: public evidence for outcome price.

One JSON file per forecast / one per realized outcome, written with OS exclusive-create; this prevents accidental duplicate writes but does **not** make records tamper-proof. Production needs hash-linked records, restricted permissions, off-repository backup and verified publication times.

## Usage
```bash
python src/forecast_v2.py predict --model BTC-GT --asset BTCUSD \
 --horizon 24h --direction 震荡偏多 --asof 2026-11-20T08:00:00+08:00 \
 --baseline-at 2026-11-20T07:00:00+08:00 --baseline-price 100 \
 --baseline-source https://example.org/price --neutral-pct 1 --strong-pct 3 \
 --confidence 0.55 --rationale "Test-only example, not a real prediction"
python src/forecast_v2.py review
```

The command above uses *illustrative fake prices* only for CLI documentation; never publish them as a market report.

## Limits and comparisons
- Report five-way exact accuracy by asset/horizon only at >=30 realized outcomes, with per-direction totals; sample size alone does not establish statistical validity.
- Compare against neutral-only and price-momentum baselines once independently captured.
- A correct direction is not a justified trade recommendation.
- **Neither this ledger nor current GitHub Actions staging automatically publishes forecasts**; all prediction records must be accompanied by verified source snapshots and published report references.
- Historical `data/2026-11-19-glt-daily-briefing.md` remains unchanged.
