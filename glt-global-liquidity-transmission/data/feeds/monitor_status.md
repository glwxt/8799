# GLT 运行状态

评分检查截点：2026-11-23T22:47:36+00:00
采集证据时间：2026-11-24T06:47:27.964705+08:00（台湾时间）
FRED：10/10 条成功，状态 OK
评分输入覆盖：48%；可计分覆盖：18%
正式综合分发布条件：未通过

## 各层缺口

| 层级 | 有效输入权重点 | 可计分权重点 | 未通过的指标 |
| --- | ---: | ---: | --- |
| 流动性供给 | 26/30 | 0/30 | reserves（需情境审核）、tga（需情境审核）、on_rrp（需情境审核）、fed_assets（需情境审核）、global_usd（没有有效输入） |
| 金融条件 | 12/25 | 8/25 | dxy（没有有效输入）、us_10y_nominal（需情境审核）、usd_funding（没有有效输入） |
| 风险偏好 | 10/20 | 10/20 | us_breadth（没有有效输入）、safe_haven（没有有效输入）、global_vol（没有有效输入） |
| 实际资金流向 | 0/25 | 0/25 | btc_flow（没有有效输入）、gold_flow（没有有效输入）、us_equity_flow（没有有效输入）、asia_equity_flow（没有有效输入）、bond_flow（没有有效输入） |

## 已取得的序列

| 序列 | 观测日 | 数值 | 单位 |
| --- | --- | ---: | --- |
| [BAMLH0A0HYM2](https://api.stlouisfed.org/fred/series/observations?series_id=BAMLH0A0HYM2&file_type=json&observation_start=2026-11-02&observation_end=2026-11-23) | 2026-11-20 | 3.76 | Percent |
| [DFII10](https://api.stlouisfed.org/fred/series/observations?series_id=DFII10&file_type=json&observation_start=2026-11-02&observation_end=2026-11-23) | 2026-11-20 | 2.77 | Percent |
| [DGS10](https://api.stlouisfed.org/fred/series/observations?series_id=DGS10&file_type=json&observation_start=2026-11-02&observation_end=2026-11-23) | 2026-11-20 | 4.92 | Percent |
| [IORB](https://api.stlouisfed.org/fred/series/observations?series_id=IORB&file_type=json&observation_start=2026-11-02&observation_end=2026-11-23) | 2026-11-23 | 3.9 | Percent |
| [RRPONTSYD](https://api.stlouisfed.org/fred/series/observations?series_id=RRPONTSYD&file_type=json&observation_start=2026-11-02&observation_end=2026-11-23) | 2026-11-23 | 0.35 | Billions of USD |
| [SOFR](https://api.stlouisfed.org/fred/series/observations?series_id=SOFR&file_type=json&observation_start=2026-11-02&observation_end=2026-11-23) | 2026-11-20 | 3.92 | Percent |
| [SWPT](https://api.stlouisfed.org/fred/series/observations?series_id=SWPT&file_type=json&observation_start=2026-11-02&observation_end=2026-11-23) | 2026-11-18 | 146.0 | Millions of USD |
| [VIXCLS](https://api.stlouisfed.org/fred/series/observations?series_id=VIXCLS&file_type=json&observation_start=2026-11-02&observation_end=2026-11-23) | 2026-11-20 | 35.89 | Percent |
| [WALCL](https://api.stlouisfed.org/fred/series/observations?series_id=WALCL&file_type=json&observation_start=2026-11-02&observation_end=2026-11-23) | 2026-11-18 | 6741452.0 | Millions of USD |
| [WRESBAL](https://api.stlouisfed.org/fred/series/observations?series_id=WRESBAL&file_type=json&observation_start=2026-11-02&observation_end=2026-11-23) | 2026-11-18 | 2979656.0 | Millions of USD |

## 财政部与台湾证交所

采集时间：2026-11-24T06:47:31.964458+08:00（台湾时间）

| 指标 | 观测日 | 数值 | 单位 | 口径 |
| --- | --- | ---: | --- | --- |
| [TGA](https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/dts/operating_cash_balance?filter=record_date%3Agte%3A2026-11-17%2Crecord_date%3Alte%3A2026-11-24&sort=-record_date&page%5Bsize%5D=100) | 2026-11-20 | 880764 | USD millions | Treasury DTS Table I closing balance |
| [TWSE_FOREIGN_NET](https://www.twse.com.tw/rwd/zh/fund/BFI82U?dayDate=20261123&type=day&response=json) | 2026-11-23 | -28947879995 | TWD | 外資及陸資(不含外資自營商) |

FRED 采集值为当前版本。正式评分根据已验收的独立输入计算。

[项目步骤与验收状态](../../docs/GLT-delivery-status.md)
