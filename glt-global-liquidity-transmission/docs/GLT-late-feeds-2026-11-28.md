# 11/28 迟发与独立来源核验

## 常备隔夜回购：不改阈值的延伸复盘

[纽约联储操作级实采与结果](../data/feeds/nyfed_repo_research_2026-11-27.json)：11/27 两场常规操作中的早场成交合计 **231.50 亿美元**（国债 227.50 亿、机构 MBS 4.00 亿、机构债明确 0），午后场明确 0；同日两场均为 Results，未标演练，逐项和总额一致。11/25 两场常规操作明确 0；11/26 感恩节无记录，不填 0。FRED [国债](https://fred.stlouisfed.org/series/RPONTSYD)／[MBS](https://fred.stlouisfed.org/series/RPONMBSD)／[机构债](https://fred.stlouisfed.org/series/RPONAGYD/)独立对账一致；其更新标示 11/27 19:02 UTC，不当成纽约联储精确首发时刻。另有 [隔夜逆回购](https://fred.stlouisfed.org/series/RRPONTSYD) 3.50 亿美元，方向和工具不同，不与回购合并。

[原验证](../engineering/v0.2.0/research/l2-conditions/funding-repo-validation.md)未改代码、窗口或阈值；先用 Fed IORB 官方 XML 转原格式，重跑旧切点，主要指标与原档一致。新检验的特征有效日为 11/24，同日 SOFR−IORB +4、EFFR−IORB −2 bp，后两个操作日是 11/25、11/27，故不拿 11/27 尚未公布的参考利率补特征。固定阈值（−5、−7 bp）命中；252 日滚动阈值（+7、−1 bp）不报警；持续基准当天仅 200 万美元，也不报警。11/27 金额同时超过 10 亿、50 亿门槛。延伸后 2026 年 224 个样本、5 次主要事件，滚动规则仍零报警；全样本固定规则 34/267，滚动 14/25，持续 16/35。属于锁定规则事后复跑，非已在 11/24 发出的实盘预警。数据不等于跨境融资价格、危机或正式分。

## JPX：假日调整与新鲜度

[JPX 英文原页](https://www.jpx.co.jp/english/markets/statistics-equities/investor-type/)写明通常当地第四个营业日约 15:30 JST 发布。[休市表](https://www.jpx.co.jp/english/corporate/about-jpx/calendar/index.html)显示 11/23 为假日，因此 11/16–20 统计周的预期发布是 11/27 06:30 UTC（台湾 14:30），晚于当日自动采集 04:58 UTC。不能把旧周据此判作解析失败，也不能把预期时刻当首次公开。已读 [JPX 数据档](../data/feeds/asia_equity_research_2026-11-28.json)：外国投资者净卖出 9,230.59 亿日元，东京与名古屋范围。截至本次官方页面最新仍 11/16–20；下一周数据通常 12/03 06:30 UTC 后可查，依实际发布确认。11/30 周报若无更新，注明统计周，不用台湾或其他区域数据替补。
