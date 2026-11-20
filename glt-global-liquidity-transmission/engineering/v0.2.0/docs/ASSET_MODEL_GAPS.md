# Asset-model activation gaps (GLT V1.0, engineering v0.2.0)

Status: gap analysis, 2026-11-21. `asset_models.py` is a factor contract
only: every model returns `score: None`. This document records, per factor,
what data is actually on file and what is missing. **It proposes no numeric
weights.** Factor weights, direction functions and walk-forward calibration
are Vivi's approval decisions; nothing here pre-approves them.

## BTC-GT (7 points in L4, factor contract has 9 factors)

| factor | data on file |
|---|---|
| global_usd | No verified composite on file. Missing. |
| dxy | Briefing value is a median of several sources (~103.92 on 2026-11-19); no single citable series on file. Missing as a feed. |
| us_10y_real | DFII10 staged (FRED), observation 2026-11-18 2.88%. Available. |
| btc_etf_primary_net_flow | Farside direct read returned 403; 2026-11-18 net outflow $306.5M is via press citation, no citable URL on file. Needs an approved feed. |
| spot_demand | Not tracked in briefings. Missing. |
| funding_rate | Not tracked in briefings. Missing. |
| open_interest | Not tracked in briefings. Missing. |
| liquidations | Not tracked in briefings. Missing. |
| stablecoin_supply | Not tracked in briefings. Missing. |

## GOLD-GT (6 points in L4, 6 factors)

| factor | data on file |
|---|---|
| us_10y_real | DFII10 staged. Available. |
| dxy | Same gap as above. Missing as a feed. |
| gold_etf_primary_flow | GLD holdings level tracked (1,044.12 tonnes, unchanged 2026-11-19); a USD flow is not computed from it. Partial. |
| central_bank_gold_purchases | WGC monthly data, lagged; not in daily briefings. Partial. |
| safe_haven_demand | Context composite; see CONTEXT_REVIEW.md. Procedure exists, no score. |
| physical_gold_demand | WGC quarterly data, lagged. Partial. |

## EQUITY-GT (6 points in L4, 8 factors)

| factor | data on file |
|---|---|
| us_10y_real | DFII10 staged. Available. |
| us_10y_nominal | DGS10 staged. Available. |
| dxy | Same gap as above. Missing as a feed. |
| earnings_forecasts | Not tracked in briefings. Missing. |
| valuation | Not tracked in briefings. Missing. |
| market_breadth | Not tracked as a percentage in briefings (only sector counts). Missing. |
| us_equity_primary_flow | Not tracked in briefings. Missing. |
| regional_foreign_flows | Taiwan foreign flows tracked daily (net sell NT$24.3B on 2026-11-19); HK/CN/JP/KR only partial. Partial. |

## Activation checklist (all must hold before any asset score is published)

1. Approved factor weights per model (Vivi approves; weights sum to the
   model's L4 points and are recorded with a version and date).
2. Approved direction function per factor (how a factor value maps to a
   0-100 contribution), with walk-forward calibration on history.
3. A citable daily feed for every factor, with source URL, published_at
   and retrieved_at recorded per observation (same gates as `glt.py`).
4. The daily briefing keeps publishing its own manual asset scores
   (BTC-GT/GOLD-GT/EQUITY-GT) until this checklist is complete; the
   engine's `None` is not replaced by a partial model.
