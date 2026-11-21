# GLT data readiness vs official scoring coverage (v0.2.4)

## Found problem
A single `coverage` number obscures two different facts: source entries are available and the entries can support a defensible numeric score. The official GLT 80% release gate concerns usable weighted indicators, not merely the number of downloaded source files.

## New read-only report
`python src/readiness.py --asof 2026-11-20T08:00:00+08:00`

The script explicitly separates:
- `raw_input_coverage`: indicator weights for which timestamped, within-freshness-window input values have reached the local observations CSV. This **does not** mean the source claim, vintage or publication instant is externally verified.
- `score_coverage`: points meeting actual scoring prerequisites. Context-dependent signals under official V1.0 do not count unless a formally approved method exists.
- `official_publishable`: unchanged engine permission, governed by both global and per-layer score-quality release gates.
- `issues`: reasons for not scoring each indicator (missing, stale, context review needed, calibration missing, etc.).

Downloaded CSV entries in GitHub Actions `staging/runs/` never count as observation input without a separately audited promotion step. Data availability for only 6 FRED series is not a percentage of the 19-item GLT framework.

### Important
This is a **diagnostic**, not a formal methodological change. GLT V1.0 methods, archived forecasts and scoring thresholds remain untouched. The source audit and historical release-vintage calibration are still incomplete.

The new metric is useful for identifying whether today's blocker is *data acquisition*, *contextual interpretation*, or *score calibration*, without falsely claiming a market score.
