# 11/20 七天预测复盘：11/28 暂存证据

[原始简报](../data/2026-11-20-glt-daily-briefing.md)第 7 节明确以 11/27 收盘核对，其第 8 节提及 11/26，不采用该回顾语句覆盖原预测定义。第 7 节中性区间明标 24 小时，七天没有单独锁定区间。此文件只记证据和方向初判，不改原文，也不计入正式命中率。

| 资产 | 原方向 | 原基准 | 11/27 核对结果 | 正式状态 |
| --- | --- | ---: | --- | --- |
| 标普 500 | 偏空 | 7,175.83 | AP 报 7,297.49，对原基准 +1.6954%，方向初判未命中。其他报价不同；FRED 只到 11/25（7,182.78），故终值未确认。 | 等 FRED 或指数编制方同口径收盘 |
| 黄金 | 偏空 | 3,685.50 USD/oz，COMEX | 初步识别为 GCZ26；CME 当期可读最终公告只到 11/25（GCZ26 3,535.80；GCG27 3,564.60）。11/27 合约进入交割通知期，不能用滚动主力或 GCG27 替代 GCZ26。 | 等 11/27 GCZ26 交易所结算 |
| BTC | 偏空 | 62,851.84 USD | 原文未锁定交易场所与收盘时区或时刻。BTC ETF 部分净流不能作为价格或评分替代。 | 只在能复原原口径时评分；否则记不可判定 |

原文未记录七天置信度，保持未记录。以后应在发报时锁定价格源、产品或合约、收盘时区、截至时刻与独立的七天中性区间；此建议不溯及本期。

核验：[FRED 标普 500](https://fred.stlouisfed.org/data/SP500) · [AP 11/27 报价](https://apnews.com/article/04dab6079cf7f3dfe7285a3cc1f240a2) · [NYSE 交易时间](https://www.nyse.com/trade/hours-calendars) · [CME 黄金合约日历](https://www.cmegroup.com/markets/metals/precious/gold/calendar) · [CME 金属公报](https://www.cmegroup.com/daily_bulletin/current/Section62_Metals_Futures_Products.pdf)。

另据 [Farside](https://farside.co.uk/bitcoin-etf-flow-all-data/)，11/27 查得 5/12 只基金，合计 −41.0 百万美元（已披露小计，非全市场）；7 只缺报留空。最新完整日仍为 11/25，−453.0 百万美元。该行不参与上表命中判定。

## 11/28 后续：黄金终点由 CME 双重核实

[CME 日期结算 JSON](https://www.cmegroup.com/CmeWS/mvc/Settlements/Futures/Settlements/437/FUT?tradeDate=11%2F27%2F2026&pageSize=500&isProtected) 显示交易日 11/27/2026、报告 Final、DEC 26 (GCZ26) 结算 **3,639.60**，FEB 27 (GCG27) 单独为 3,668.50。[CME Clearing 交割通知](https://www.cmegroup.com/delivery_reports/MetalsIssuesAndStopsReport.pdf)的业务日 11/27/2026 也注明 DECEMBER 2026 COMEX 100 GOLD FUTURES 为 3,639.60；书面 (结算日期不同于所示的 12/01/2026 交割日期)。

与原简报锁定的 3,685.50 比较，变动 **-1.2454%**，偏空方向一致。该结论采用同到期月终点和原文基准，未能重新下载基准日 CME 文件，不宣称双端均由交易所复验。原七天窗口无专属中性区间，记为**方向一致**，不导入 24 小时阈值，也不填正式命中率。CME 终点在原早报之后才由本项目核实，不回填历史早报。源哈希：结算 JSON `1789b1c302bafaa70220208144ebbd57d59b2898b249b15581dfd637bbdf1866`；业务日 PDF `96204fb66968cec7119e4dc092446cfa162c1e78dd0f2a3738d1757f037d2aa0`。不将尚未读取的 Metals Bulletin 当证据。
