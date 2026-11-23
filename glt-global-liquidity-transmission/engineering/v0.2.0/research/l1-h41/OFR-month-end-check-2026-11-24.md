# OFR 货币基金月末持仓核对

2026-11-24（台湾时间）实采。官方 OFR STFM 接口为 https://data.financialresearch.gov/v1/series/timeseries，查询参数 mnemonic、start_date=2026-09-01、end_date=2026-10-31。以下为美元，缺失保留为空。总持仓为 OFR 投资合计口径。

| OFR 序列 | 2026-09-30 | 2026-10-31 | 变化 |
| --- | ---: | ---: | ---: |
| MMF-MMF_TOT-M 投资总额 | 8396822287018.74 | 8473378242355.38 | +76555955336.64 |
| MMF-MMF_T_TOT-M 美国国债持仓合计 | 3483973546108.55 | 3620456613944.79 | +136483067836.24 |
| MMF-MMF_RP_TOT-M 回购投资总额 | 2871494678859.44 | 2789414202784.37 | -82080476075.07 |
| MMF-MMF_RP_wFR-M 与美联储的回购 | 6113993245.18 | — | — |

美国国债持仓合计包括不同期限的国债。未验证国库券单列。由于美联储对手方序列未返回 10 月值，未计算私人回购（回购合计减与美联储的回购）的月比。行业汇总余额变化无法证明同一基金或同一笔资金的再配置，未使用于日度资金去向或正式评分。此为一次性实采，未接入排程。

[OFR 月末数据说明](https://www.financialresearch.gov/short-term-funding-monitor/datasets/mmf/) · [接口参数](https://www.financialresearch.gov/short-term-funding-monitor/api-specs/api-data-single/)
