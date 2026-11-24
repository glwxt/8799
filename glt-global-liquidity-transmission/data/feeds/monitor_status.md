# GLT 运行状态

评分检查截点：2026-11-24T06:56:19+00:00
采集证据时间：2026-11-24T14:55:52.481451+08:00（台湾时间）
FRED：10/10 条成功，状态 OK
评分输入覆盖：23%；可计分覆盖：10%
正式综合分发布条件：未通过

## 各层缺口

| 层级 | 有效输入权重点 | 可计分权重点 | 未通过的指标 |
| --- | ---: | ---: | --- |
| 流动性供给 | 13/30 | 0/30 | reserves（需情境审核）、tga（超出时效）、on_rrp（超出时效）、fed_assets（需情境审核）、global_usd（没有有效输入） |
| 金融条件 | 0/25 | 0/25 | dxy（没有有效输入）、us_10y_real（超出时效）、us_10y_nominal（超出时效）、usd_funding（没有有效输入） |
| 风险偏好 | 10/20 | 10/20 | us_breadth（没有有效输入）、safe_haven（没有有效输入）、global_vol（没有有效输入） |
| 实际资金流向 | 0/25 | 0/25 | btc_flow（没有有效输入）、gold_flow（没有有效输入）、us_equity_flow（没有有效输入）、asia_equity_flow（没有有效输入）、bond_flow（没有有效输入） |

## 已取得的序列

| 序列 | 观测日 | 数值 | 单位 |
| --- | --- | ---: | --- |
| [BAMLH0A0HYM2](https://api.stlouisfed.org/fred/series/observations?series_id=BAMLH0A0HYM2&file_type=json&observation_start=2026-11-03&observation_end=2026-11-24) | 2026-11-20 | 3.76 | Percent |
| [DFII10](https://api.stlouisfed.org/fred/series/observations?series_id=DFII10&file_type=json&observation_start=2026-11-03&observation_end=2026-11-24) | 2026-11-20 | 2.77 | Percent |
| [DGS10](https://api.stlouisfed.org/fred/series/observations?series_id=DGS10&file_type=json&observation_start=2026-11-03&observation_end=2026-11-24) | 2026-11-20 | 4.92 | Percent |
| [IORB](https://api.stlouisfed.org/fred/series/observations?series_id=IORB&file_type=json&observation_start=2026-11-03&observation_end=2026-11-24) | 2026-11-24 | 3.9 | Percent |
| [RRPONTSYD](https://api.stlouisfed.org/fred/series/observations?series_id=RRPONTSYD&file_type=json&observation_start=2026-11-03&observation_end=2026-11-24) | 2026-11-23 | 0.35 | Billions of USD |
| [SOFR](https://api.stlouisfed.org/fred/series/observations?series_id=SOFR&file_type=json&observation_start=2026-11-03&observation_end=2026-11-24) | 2026-11-20 | 3.92 | Percent |
| [SWPT](https://api.stlouisfed.org/fred/series/observations?series_id=SWPT&file_type=json&observation_start=2026-11-03&observation_end=2026-11-24) | 2026-11-18 | 146.0 | Millions of USD |
| [VIXCLS](https://api.stlouisfed.org/fred/series/observations?series_id=VIXCLS&file_type=json&observation_start=2026-11-03&observation_end=2026-11-24) | 2026-11-20 | 35.89 | Percent |
| [WALCL](https://api.stlouisfed.org/fred/series/observations?series_id=WALCL&file_type=json&observation_start=2026-11-03&observation_end=2026-11-24) | 2026-11-18 | 6741452.0 | Millions of USD |
| [WRESBAL](https://api.stlouisfed.org/fred/series/observations?series_id=WRESBAL&file_type=json&observation_start=2026-11-03&observation_end=2026-11-24) | 2026-11-18 | 2979656.0 | Millions of USD |

## 财政部与台湾证交所

采集时间：2026-11-24T14:55:56.126455+08:00（台湾时间）

| 指标 | 观测日 | 数值 | 单位 | 口径 |
| --- | --- | ---: | --- | --- |
| [TGA](https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/dts/operating_cash_balance?filter=record_date%3Agte%3A2026-11-17%2Crecord_date%3Alte%3A2026-11-24&sort=-record_date&page%5Bsize%5D=100) | 2026-11-20 | 880764 | USD millions | Treasury DTS Table I closing balance |
| [TWSE_FOREIGN_NET](https://www.twse.com.tw/rwd/zh/fund/BFI82U?dayDate=20261123&type=day&response=json) | 2026-11-23 | -28947879995 | TWD | 外資及陸資(不含外資自營商) |

## 实际资金流采集证据

采集开始：2026-11-24T06:56:14.068937+00:00（UTC）

| 指标与来源 | 统计日或周末 | 频率 | 净流 | 单位 | 状态 |
| --- | --- | --- | ---: | --- | --- |
| [BTC ETF](https://farside.co.uk/bitcoin-etf-flow-all-data/) | 2026-11-23 | daily | -569.7 | USD millions | 已报齐 12/12 |
| [亚洲股票](https://www.jpx.co.jp/english/markets/statistics-equities/investor-type/vk0khi000002wtoi-att/stock_1_w_20261109_20261113.xlsx) | 2026-11-13 | weekly | -310147409000 | JPY | 已报告 |
| [黄金 ETF](https://www.gold.org/download/file/21413/WMM-23-Nov-2026-AI-reckoning.pdf) | 2026-11-20 | weekly | -2149.0 | USD millions | 来源估计 |

资金流采集异常：ici（HTTPError: HTTP Error 403: Forbidden）。

[采集原始记录与披露时点](l4_scheduled_latest.json)

FRED 采集值为当前版本。正式评分根据已验收的独立输入计算。

[项目步骤与验收状态](../../docs/GLT-delivery-status.md)
