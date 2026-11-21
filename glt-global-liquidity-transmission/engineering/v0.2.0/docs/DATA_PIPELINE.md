# GLT Data Pipeline v0.2.1 — non-scoring ingestion

## What is running
GitHub Actions scheduled collector: `.github/workflows/glt-fred-staging.yml`.
- Scheduled every day at **23:10 UTC (previous calendar day) / 07:10 Asia/Taipei** and available on manual dispatch.
- Pulls 6 FRED graph CSV series: WRESBAL, WALCL, RRPONTSYD, DFII10, DGS10, BAMLH0A0HYM2.
- Runs project unit tests first and uploads a `glt-fred-staging-...` workflow artifact with timestamped CSV and `manifest.json`.
- Uses read-only GitHub token; does not commit market data, alter official GLT method, or claim a numeric score.
- This collection is scheduled ahead of the 08:00 local ChatGPT daily briefing, but actual availability may be delayed and the briefing has no automatic artifact ingestion. An artifact is not the same as a published daily report. ChatGPT scheduled daily/weekly reports are separate automations.
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

## Engineering v0.2.5: stable GitHub evidence feed

A new `src/publish_evidence.py` validates the staged bundle's original CSV SHA-256 checksums, series IDs, source URLs, units and latest values. The workflow commits a metadata-only snapshot to:

- `glt-global-liquidity-transmission/data/feeds/fred_latest.json`
- `glt-global-liquidity-transmission/data/feeds/fred_latest.md`

The snapshot is always tagged `eligible_for_official_glt_score=false` and `source_release_timestamps_verified=false`. Failures may publish `collection_status=DEGRADED` and fail the workflow explicitly. Successful GitHub Actions execution and branch-push permission must be checked in Actions; code merge does not prove runtime success.

**Important:** This new stable path reduces manual retrieval friction but does not automatically pipe GitHub data into ChatGPT automations. Reports must read the feed during execution, compare `data_retrieved_at_taipei` against the report as-of, and independently validate official source releases. The file may be stale if scheduled execution or push failed. No revisions to GLT V1.0 or old predictions.
