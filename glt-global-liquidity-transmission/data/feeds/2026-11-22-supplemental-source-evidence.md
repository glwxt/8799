# GLT 补充采集证据 · 2026-11-22（台湾时间）

本次补充采集涉及 7 个指标，证据含单市场、单基金、盘中及周度口径。归档用于来源审核，尚未进入正式评分。

| 指标 | 观测期 | 值与单位 | 口径与来源 |
| --- | --- | --- | --- |
| TGA | 2026-11-19 | 891223 百万美元 | [财政部 DTS](https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/dts/operating_cash_balance?filter=record_date:gte:2026-11-18&sort=-record_date)，取 Closing Balance 行的 open_today_bal 字段；当日 Opening Balance 为 892310，存入 303648、支出 304735，勾稽一致。11/20 尚未在本次查询结果中出现。日频，发布时间待核验。 |
| DXY | 2026-11-20 | 103.86 指数点 | [路透](https://www.reuters.com/business/dollar-near-19-month-peak-ai-jitters-sap-risk-appetite-2026-11-20/)报道时点报价，ICE 收盘待核。 |
| BTC | 2026-11-19 | -582.3 百万美元 | [Farside](https://farside.co.uk/btc/)美国现货 ETF 日净流量。11/20 已报小计 -124.5 百万美元，IBIT 缺报。 |
| 黄金 | 2026-11-19 | 1038.14 吨，较前一日 -5.98 吨 | [GLD 持仓转引](https://www.rutantrade.com/en/spdr)，单基金实物持仓变动，待与发行商历史下载对表。 |
| 美国股票 | 截至 2026-11-11 的一周 | +37058 百万美元 | [ICI](https://www.ici.org/research/stats/etf_flows)11/17 发布的美国本土股票 ETF 周度估计净发行，待补日频口径。 |
| 亚洲股票 | 2026-11-20 | -9510543572 新台币 | [台湾证交所](https://www.twse.com.tw/rwd/zh/fund/BFI82U?dayDate=20261120&type=day&response=json)外资及陆资（不含外资自营商）买卖差额；台湾子项，其他亚洲市场待补。 |
| 债券 | 截至 2026-11-11 的一周 | +11754 百万美元 | [ICI](https://www.ici.org/research/stats/etf_flows)11/17 发布的债券 ETF 周度估计净发行，含应税及市政债 ETF。 |

仍缺同口径序列：全球美元流动性、美元融资压力、美股广度、避险需求、全球市场波动。复合指标须先明确代理变量、频率、合成方式和评分校准。以上记录为实采或披露证据，尚待逐项完成正式输入验收。
