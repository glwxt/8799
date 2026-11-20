# GLT Engineering v0.2.0 — V1.0 methodology aligned

**Engineering build v0.2.0 only. Official GLT methodology stays V1.0 (2026-11-18).**

Authoritative source: [GLT-methodology.md](../../docs/GLT-methodology.md). This independent engineering implementation is deliberately installed below `engineering/v0.2.0/` to avoid replacing original research documents, archives or Muse task specifications.

## Capabilities
- Original 19 fixed-weight indicators: L1=30, L2=25, L3=20, L4=25 absolute points.
- Point-in-time gates on published_at and retrieved_at, timezone required.
- Missing, stale, uncalibrated, mismatched and context-sensitive readings never receive fabricated scores.
- Per-layer >=80% coverage required before publishing layer; all four layers and total >=80% needed for composite.
- Three independent asset factor *contracts*, not fabricated scores.
- Append-only-by-CLI five-way forecasts and separate outcome records, basic review.
- FRED CSV downloaded into staging only; data not automatically scored.

## Run (Python 3.8+, standard library)
From this directory:

```bash
python -m unittest discover -s tests -v
python src/glt.py --asof 2026-11-20T08:00:00+08:00
python src/audit.py --asof 2026-11-20T08:00:00+08:00
python src/report.py --asof 2026-11-20T08:00:00+08:00
python src/review.py
python src/stage_fred.py --series DFII10
```

## Data contracts
`data/observations.csv`: indicator_id,observation_date,published_at,value,unit,source_url,retrieved_at,revision,transform. Both timestamps need timezone offsets.
`data/calibration.csv`: indicator_id,lookback_start,lookback_end,p05,p95,version,transform. Calibration must predate the observation and match its transform.
`config/indicators.csv`: source definitions, weight points, frequency, and provisional max_age_days.

## Boundaries
This is an **offline prototype**, not a real-time connected monitor or automatically scheduled job. Empty inputs correctly produce 0% source coverage, no GLT score, no asset scores or predictions. The 0% describes this engineering instance, not market conditions.

Do not treat FRED historical graph CSV as release vintage. Context-dependent indicators require a documented review procedure. This build's percentile scaling is provisional. Use `docs/ENGINEERING_AUDIT.md` for limitations and next acceptance tasks.
