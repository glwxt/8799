# 11/28 黄金发行人份额与跨境美元融资来源核验

## 黄金 ETF：同日估算与实际披露分开

[发行人对照](../data/feeds/gold_issuer_creation_research_2026-11-27.json)记录实际下载时点、原档校验值及样本覆盖。11/25，IAU 按份额变化估计净赎回约 3,256 万美元，GLD 估计净创设约 6,352 万美元，方向相反。11/27 IAU 显示份额减少 50 万，按发行人全精度 NAV 估算净赎回约 3,414 万美元；GLD 文件仅到 11/25，11/26 为休市，11/27 留空。11/24 IAU 份额不变，只表示计算值为零，来源未报告实际净流零。GLD 历史档无显式份额列，AUM／NAV 倒算在 11/23 与 SEC 所报相符；其他日不宣称是原始份额披露。不覆盖 [WGC 披露档](../engineering/v0.2.0/research/gold-gt/gold-etf-flow-publications.json)，不纳入正式分。

[GLD 发行人](https://www.spdrgoldshares.com/usa/gld/)通常纽约时间 10:30–10:45、16:00–16:45 更新网页份额，不能等同历史文件或基金净流首次公布。后续可分别保存窗口前最后未更新和窗口后首次见到新值的 UTC 时刻，并保留发行人数据日、文件版本及网页具体字段；只能得到已观测区间，不据此伪造精确首次发布时刻。[WGC 周度数据](https://www.gold.org/goldhub/data/gold-etfs-holdings-and-flows)按其实际期次更新；月度发布周须先核对是否有周更例外。

## 跨境融资：可下载更新的背景序列，不等于同期限基差

[OFR 官方 CSV](https://www.financialresearch.gov/financial-stress-index/data/fsi.csv)实采 6,810 个不重复日期（2000-01-03 至 2026-11-25），Funding 栏是金融压力指数的融资贡献，不是基点；11/25 值 −0.053 指数点。[OFR 文档](https://www.financialresearch.gov/financial-stress-index/)说明约滞后两个营业日。文件 SHA-256：`37388fbfa27335449a52a3c2e7937ca3488aa890ecc6497a9e8ab9a8cc127ef0`。未验证此期首次发布时刻。

与 [EUR/JPY 一年期 CIP 历史对照](../engineering/v0.2.0/research/l2-conditions/funding-cip-comparator-2026-11-28.md)按同观测日取交集（不填补、未回放发布日期），1,075 个日期（2021-02-24 至 2025-06-30）；水平 Pearson 分别 −0.8424、−0.7496，相邻共同观测变化仅 +0.0820、+0.1433。水平关联不等于可替代的日度融资信号；OFR 本身包含多种融资成分，不能反推单一外汇基差，且非独立样本外检验。

[CME FX Link 导出说明](https://www.cmegroup.com/education/articles-and-reports/cme-fx-swap-rate-monitor-user-guide)是候选，需登录，合约到期固定但剩余期限变化，利差不是同期限常数基差。[OFR 论文表 6](https://www.financialresearch.gov/working-papers/files/OFRwp-23-07-transition-to-alternative-reference-rates-in-ofr-financial-stress-index.pdf)列出两年 EUR/USD 与 JPY/USD Datastream 标识 EUUSC2Y、JPUSC2Y；无授权历史下载或首次发布核验，不能当三个月数据。两者不改现有方法及评分。
