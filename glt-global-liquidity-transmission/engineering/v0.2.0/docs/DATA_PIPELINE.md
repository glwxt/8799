# GLT Data Pipeline v0.2.1 — non-scoring ingestion

## What is running
GitHub Actions scheduled collector: `.github/workflows/glt-fred-staging.yml`.
- Scheduled every day at **00:20 UTC / 08:20 Asia/Taipei** and available on manual dispatch.
- Pulls 6 FRED graph CSV series: WRESBAL, WALCL, RRPONTSYD, DFII10, DGS10, BAMLH0A0HYM2.
- Runs project unit tests first and uploads a `glt-fred-staging-...` workflow artifact with timestamped CSV and `manifest.json`.
- Uses read-only GitHub token; does not commit market data, alter official GLT method, or claim a numeric score.
- An artifact is not the same as a published daily report. ChatGPT scheduled daily/weekly reports are separate automations.
- GitHub cron scheduling may be delayed or skipped; check actual Actions execution logs. Setting a workflow is not proof of a successful live download.

## Quality controls
- Each series includes source URL, timestamp of retrieval in UTC, current-vintage marker, SHA-256 content checksum, latest observation date and value, units, source frequency and errors.
- HTTP failure / invalid CSV is logged, other series continue; minimum 4 of 6 successful fetches is required for workflow success.
- `source_availability_ratio` is collector success ratio (max 6 series), **NOT** 19-indicator GLT coverage.
- No raw FRED series is automatically scored or promoted into `data/observations.csv` because source's original publication time, unit conversion and revision vintage still require validation.
- Current graph CSV is unsuitable for historical point-in-time backtesting without ALFRED/release-vintage verification.
- A series latest observation date can legitimately be lagged due to weekends and publication schedules.

## Manual reproduction
```bash
cd glt-global-liquidity-transmission/engineering/v0.2.0
python -m unittest discover -s tests -v
python src/batch_stage.py
python src/glt.py --asof 2026-11-21T08:00:00+08:00
```

## Follow-on engineering gates (not yet complete)
1. Add official release-time/vintage calendars, approved transformations and rolling historical calibration.
2. For TGA/ON RRP and ambiguous macro signals, build documented context review and approvals.
3. Add primary-source ETF subscribe/redeem and exchange foreign-flow collectors, preserving asset/market units.
4. Score independent BTC-GT/GOLD-GT/EQUITY-GT only after formulas and out-of-sample calibration are approved.
5. Add persistent signed/append-only forecast and realized-outcome store (GitHub files alone are editable).
6. End-to-end test from scheduled execution to actual report delivery and GitHub archive, plus failure alerting.

Methodology remains GLT V1.0. No historical forecast is modified.
