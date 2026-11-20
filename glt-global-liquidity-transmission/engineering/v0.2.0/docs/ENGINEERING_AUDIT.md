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

## 2026-11-21 fixes (local run, per Vivi's instruction to fix the checked problems)

- Staging fixed: all 7 FRED series (DFII10, DGS10, BAMLH0A0HYM2, VIXCLS,
  RRPONTSYD, WRESBAL, WALCL) staged via browser fetch on 2026-11-21 00:27 CST
  (windowed 2025-11-01 to 2026-11-20, current vintage), because direct VM
  download stayed unreachable. Key values cross-checked against the verified
  2026-11-19/20 briefings. Staging files are local only, not pushed to GitHub.
- stage_fred.py hardened: timeout 25s to 60s, 3 attempts with exponential
  backoff, VIXCLS added to ALLOWED. Re-test still failed after 3 attempts
  (direct path unreachable); browser-staged files were not overwritten.
- config/indicators.csv: vix fred_id corrected from VIX_CBOE to VIXCLS
  (the FRED series for the CBOE VIX close; 2026-11-19 value 28.44 matches
  the verified briefing).
- data/observations.csv: 8 rows populated from verified briefing values or
  the staged FRED series; 11 indicators remain missing (documented in the
  run log). FRED rows use first-verified time as a conservative
  published_at proxy; exact FRED release timestamps are not on file.
- data/calibration.csv: 7 provisional rows (version provisional-2026-11-21),
  p05/p95 by linear interpolation over the last 252 non-empty daily values
  (52 weekly), lookback_end strictly before observation date. Provisional
  because FRED graph CSV is current vintage, not release vintage, and the
  252-day window is the method default, not yet validated against the
  release calendar.
- docs/CONTEXT_REVIEW.md added: review procedure for the 9 context
  indicators. The engine still returns requires_context_review; reviewed
  judgements are recorded in briefing verify files only, never scored.
- docs/ASSET_MODEL_GAPS.md added: per-factor data availability for
  BTC-GT/GOLD-GT/EQUITY-GT. No weights proposed; activation needs approved
  weights, direction functions, walk-forward calibration and a citable feed
  per factor.
- Forecast protocol decision: engine five-way labels and briefing three-way
  labels coexist; archived calls are never rewritten and were not backfilled
  into the engine forecast ledger (backfilling would falsify created_at).
- Engine re-run (asof 2026-11-21T01:00:00+08:00): unit tests 6/6 pass
  (unittest; pytest is not installed on this machine, so the README's
  pytest command does not run here); coverage 0.18, publishable false,
  composite null; three valid indicators all score 0 (us_10y_real 0/8,
  vix 0/5, hy_spread 0/5); layers L1 0%, L2 32%, L3 50%, L4 0%.
- Still open: the engine is not the daily briefing scorer (11 missing
  indicators, 9 context reviews, unapproved asset weights); calibration
  stays provisional; FRED direct download from this VM stays unreachable.
