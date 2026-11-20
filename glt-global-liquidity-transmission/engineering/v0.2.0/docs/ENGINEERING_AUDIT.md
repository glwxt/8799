# GLT V1.0 audit and engineering improvements (2026-11-20)

## Authoritative inputs
- GitHub glwxt/8799 glt-global-liquidity-transmission/README.md
- GitHub glwxt/8799 glt-global-liquidity-transmission/docs/GLT-methodology.md V1.0 (2026-11-18)
- GitHub historical data/2026-11-19-glt-daily-briefing.md (archive; not independently verified)

## Baseline correction
Previous starter had 16 candidates and used within-layer fractions; source methodology requires 19 indicators and absolute point weights. The engineering implementation uses original 19 indicator definitions.

## Exact method weights
- L1: reserves 8, TGA 8, ON RRP 5, Fed assets 5, global USD 4.
- L2: DXY 8, 10-year real yield 8, 10-year nominal yield 4, USD funding 5.
- L3: VIX 5, HY spread 5, US breadth 4, safe-haven 3, global volatility 3.
- L4: BTC 7, GOLD 6, US equity 6, Asia equity 4, bonds 2.

## What changed / what did not
- Engineering version 0.2.0, formal GLT methodology remains V1.0.
- Fixed absolute-weight handling and intraday lookahead possibility.
- Data completeness/quality checks. Strictness may change historical reprocessing; never edit archived forecasts.
- FRED source identifiers are candidates; their graph endpoints do not attest historical real-time release availability.
- max_age_days engineering defaults are provisional pending release-calendar validation.
- 2026-11-19 archived report has not been independently verified here.
- Repo README explicitly corrects false historical automatic-task IDs; retain that audit trail.

## Important limitations
- No connected live market scores, validated contextual reviews, or scored asset models.
- Asset models await approved factor weights and historical walk-forward calibration.
- Five-way presentation/forecast direction labels differ from repository's earlier suggested three-way forecast labels; track as protocol change, never rewrite archived calls.
- Forecast CLI is append-only by convention but does not prevent offline file tampering; production deployment needs signed snapshots and restricted permissions.
- Historical backtests need as-of data vintages rather than current revised FRED files.
