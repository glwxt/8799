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

## 锁定价格基准后复盘

工程更新引入 `price-three-way-v1`。GLT 方法仍为 V1.0。只对有确定价格序列的预测启用。五档原文保留，计分将“震荡偏多”映射为“偏多”、“震荡偏空”映射为“偏空”。实际收益在含边界的 ±neutral_pct 区间内归为“震荡”。

- 发布前用 `forecast.py predict ... --benchmark benchmark.json` 锁定基准。JSON 必填字段为 `report_id`、`instrument`、`series_id`、`unit`、`price_type`、`calendar`、`session_rule`、`source_url`、`start_at`、`start_value`、`end_at`、`neutral_pct`，以及 `score` 或 `score_missing_reason`。阈值填写百分数，例如 `1.5`。所有时间带 UTC 偏移。按发布时已知交易日历选择到期时点前最后一个符合口径的报价，提前锁定该时点。无合适的期末时点时暂不使用这个协议。
- 到期后用 `forecast.py result --id ID --evaluated-at TIMESTAMP --quote quote.json` 登记结果。JSON 字段为 `observed_at`、`value`、`series_id`、`unit`、`price_type`、`source_url`。程序检查口径与锁定时点，并计算实际方向。报价值和交易日历由提交方核实。
- 用 `review.py` 查看已到期、待到期、待取数及可评分记录。锁定协议单独统计，按标的、序列与周期分组，基准为始终判断“震荡”。旧台账继续读取并单独展示其原口径结果。
- 缺失报价可稍后补录。11 月 19 日首报沿用历史档案，缺少的报价口径及映射继续标记待核实。风险偏好、全球资金方向、生产数据接入和 Muse 调度仍需各自验收。
