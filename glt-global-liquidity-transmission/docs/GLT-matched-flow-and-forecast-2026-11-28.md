# 11 月 28 日同日资金流与到期端点复核

台湾时间 11:57 截点。以下结果用于研究复核。

## 亚洲分市场同日对照

把三个已归档的市场／通道按交易日期取交集，避免将 JPX 上周周值与本周日值配对。KRX 各日买减卖以及五日区间对账通过。沪深南向分别重算买减卖，五日均与档案中双通道合计一致。

| 共同交易日 | TWSE 外资及陆资，TWD | KOSPI 外资合计，KRW | 沪深南向，亿 HKD |
| --- | ---: | ---: | ---: |
| 2026-11-24 | -50,389,912,492 | 804,600,939,411 | 62.04 |
| 2026-11-25 | -123,654,798,153 | -1,819,260,861,839 | 64.34 |
| 2026-11-26 | -49,181,133,625 | -88,557,881,055 | -213.51 |
| 2026-11-27 | -29,628,066,640 | 1,162,455,778,869 | 45.87 |
| 四日各自合计 | -252,853,910,910 | 59,237,975,386 | -41.26 |

四日中，台湾与韩国净流同向 2 日，三者同向 1 日。各市场按本币单列。11/23 缺进入本次对照的台湾逐元记录，四日合计不能代表全周。各源首发时间及地区覆盖仍待验收，区域总分为空。

[TWSE 11/24](https://www.twse.com.tw/rwd/zh/fund/BFI82U?dayDate=20261124&response=html&type=day) · [TWSE 11/25](../data/feeds/twse_foreign_research_2026-11-25.json) · [TWSE 11/26](../data/feeds/twse_foreign_research_2026-11-26.json) · [TWSE 11/27](../data/feeds/asia_equity_research_2026-11-28.json) · [KRX](../data/feeds/krx_kospi_foreign_research_2026-11-27.json) · [沪深南向](../data/feeds/hk_southbound_research_2026-11-27.json)

## 七天预测与资金流复查

11/20 期锁定 11/27 收盘。AP 与 YCharts 均显示标普 500 收于 7,297.49，较锁定基准 7,175.83 上升 1.6954%，与原偏空方向相反。增加第二个收盘证据，正式命中率仍待指数编制方或 FRED 确认收盘，以及厘清七天中性区间缺失时的既有评分规则。COMEX 公报尚未核实 11/27 GCZ26 的同合约结算，BTC 原始交易场所与收盘口径仍未锁定。两项留空，保存上轮暂存记录。

[11/20 原预测](../data/2026-11-20-glt-daily-briefing.md) · [上轮暂存](GLT-7d-review-2026-11-20-provisional-2026-11-28.md) · [AP](https://apnews.com/article/04dab6079cf7f3dfe7285a3cc1f240a2) · [YCharts](https://ycharts.com/indices/%5ESPX/level) · [FRED](https://fred.stlouisfed.org/data/SP500)

Farside 11/27 仍为 11/12，BTCO 实报零，IBIT 一栏为缺值。表中 -61.8 百万美元等于已报基金小计，完整总额为空。ICI 官方索引仍列 11/24 专报，截至 11/18。两个来源均未新增版本档。GLI 原文、Muse 回执和早报截点前采集的连续验收仍待取得。

[Farside](https://farside.co.uk/bitcoin-etf-flow-all-data/) · [ICI 官方索引](https://www.ici.org/research/statistics/etfs/weekly-estimated-etf-net-issuance) · [采集时效验收](GLT-collection-timing-2026-11-28.md)

## 补录：五个共同交易日（台湾时间 12 点后核验）

保留前面四日的历史截点，新增 [TWSE 11/23 原表](https://www.twse.com.tw/rwd/zh/fund/BFI82U?dayDate=20261123&response=html&type=day) 同口径外资及陆资行（不含外资自营商），买入 484,813,745,109、卖出 513,761,625,104，相减与原表 −28,947,879,995 TWD 一致；原表 HTML SHA-256：`a9ccb979733736e490a6747aad23e8d000b039ac1c660c231593af179e476643`。另两市场 11/23 分别为 KOSPI −256,460,868,182 KRW、沪深南向 −96.28 亿 HKD。

| 11/23–27 各自五个共同交易日 | 净流 |
| --- | ---: |
| TWSE 外资及陆资 | −281,801,790,905 TWD |
| KOSPI 外资合计 | −197,222,892,796 KRW |
| 沪深南向 | −137.54 亿 HKD |

台湾与韩国同向 3/5，三者同向 2/5。韩国四日小计为正，但补足周一后全周为负；三个不同市场、交易范围和币种只单列，不求区域合计或正式分。

[发行人 11/27 全精度数据](../data/feeds/etf_issuer_creation_research_2026-11-27.json)核实假期后相邻交易日份额变化。按当日发行人 NAV 估算，IVV 净创设约 +5.8511 亿美元，ITOT +1.8302 亿美元，NOBL 份额未变、估计为零但不是来源披露现金净流为零。IBIT 份额减少 972 万，估计净赎回约 3.2853 亿美元；Farside 截至复核仍缺 IBIT，11/12 小计 −6,180 万美元，完整总额仍为空。两个口径不拼接，现金与实物比例、首次公布时间均未知，也不据此回填历史价格或命中记录。
