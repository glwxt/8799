# GLT 11 月 27 日取数与验收

截点为台湾时间 11:21。以下补取供研究复核。

- **BTC ETF**。11/25 行情日的资金流由 11/26 12:58 已报 11/12 只、小计 -123.3 百万美元，补齐至 12/12 只、净流 -453.0 百万美元。逐基金相加等于总额，差额 -329.7 与完整表 IBIT 行相符。保留原批次哈希及空总额，完整表精确首发时刻未知。[披露顺序](../data/feeds/btc_flow_disclosure_2026-11-25.json) · [Farside](https://farside.co.uk/bitcoin-etf-flow-all-data/)
- **台湾**。11/26 官方两种交易范围的外资及陆资买卖总额不同，分别以买减卖重算均得净卖出 49,181,133,625 新台币。外资自营商的零为来源实报。两种范围分别留档，亚洲总量仍空。[两表对账](../data/feeds/twse_foreign_research_2026-11-26.json)
- **黄金**。WGC 11/23 报告第 19 页明确显示 11/20 周 AUM 完成率 62.2%，80 只基金报齐，121 只未报齐。补档后八周有 AUM 完成率，以研究用 70% 分组，两组各有 3/4 周美国样本与全球估计同向。11/09 和 11/16 两份 PDF 的文本层未提取到覆盖率，仍待目视复核。[WGC PDF](https://www.gold.org/download/file/21413/WMM-23-Nov-2026-AI-reckoning.pdf) · [周度档案](../engineering/v0.2.0/research/gold-gt/gold-etf-flow-publications.json)
- **ICI 与采集**。ETF 专报仍为 11/24 版，截至 11/18。11/26 自动取数于 12:58 落库，ICI 仍返回 403。验收需下一统计周官方专报及自动归档回执。JPX 官方说明一般为一周第 4 个营业日日本时间约 15:30 更新。11/23 休市后，本周按该规则应于 11/27 台湾时间约 14:30 更新，仍需核对实际公开的工作簿和时刻。[ICI](https://www.ici.org/research/stats/etf_flows) · [JPX](https://www.jpx.co.jp/english/markets/statistics-equities/investor-type/index.html) · [运行状态](../data/feeds/monitor_status.md)
- **预测时窗**。11/20 原始日报七天窗口明定用 11/27 收盘。标普 500 于美国东部时间 11/27 13:00、台湾时间 11/28 02:00 收盘，本轮尚未到期。黄金与 BTC 同样等待原记录指定的 11/27 结算或收盘证据。11/25 期标普 24 小时为 11/26 休市窗口，留空。GLI 第三期原文及 Muse 读回证据仍待取得。[原始预测](../data/2026-11-20-glt-daily-briefing.md) · [NYSE](https://www.nyse.com/trade/hours-calendars)
