# GLT 五项数据缺口补采 · 2026-11-22（台湾时间）

本档记录观测及候选监测口径。权重与正式 V1.0 评分规则沿用原配置。所列代理尚未通过评分校准，缺失项不填零。

| 指标 | 实采或披露证据 | 候选计算及边界 |
| --- | --- | --- |
| 全球美元流动性 | 11 月 18 日美联储央行美元互换余额 146 百万美元；BIS 2026 年第二季度跨境银行美元信贷同比增长 11% | 周频跟踪 SWPT 水平及周变动，季度 BIS 序列提供背景。互换使用增加可能反映融资需求升高，也可能反映政策投放，需结合事件判断；不与 Fed 总资产或 BIS 信贷余额相加。 |
| 美元融资压力 | 11 月 19 日 SOFR 3.91%，IORB 3.90% | 同一观察日的 (SOFR − IORB) × 100 = +1 bp。日频。只覆盖美国境内隔夜有担保融资，全球融资压力仍需 EUR/USD 或 USD/JPY 交叉货币基差。 |
| 美股广度 | 11 月 20 日 Nasdaq 上涨 928 家、下跌 3964 家；NYSE 下跌与上涨之比 3.77∶1 | 日频 Nasdaq 上涨占有涨跌股票 928 ÷ (928 + 3964) = 18.97%。沿用同一交易所、同一统计范围。NYSE 单列交叉核验。 |
| 避险需求 | 11 月 20 日路透报道美国 10 年期收益率下行 10.43 bp、纽约报道时点日元走强、COMEX 12 月黄金期货结算下跌 4.6% | 日频分别观察国债收益率方向、美元兑日元和黄金变动。期货结算与汇率报道时点须保留；本期信号分化，定性记录，不据此推断资金流金额或生成分数。 |
| 全球市场波动 | 11 月 20 日日本 Nikkei 225 VI 33.07（+7.93%，日本时间 15:50）；欧洲 VSTOXX 收盘 28.36（+25.90%） | 日频分列欧洲、日本的隐含波动率，后续分别标准化后再合成；美国 VIX 作为原有独立指标，避免重复计分。当前样本只覆盖欧洲和日本股票期权市场，未覆盖汇率与利率波动。 |

## 数据出处

- [FRED SWPT](https://fred.stlouisfed.org/graph/fredgraph.csv?id=SWPT&cosd=2026-11-12&coed=2026-11-22)、[BIS 2026 Q2](https://www.bis.org/publications/202610-commentary-ibs-gli)。
- [FRED SOFR](https://fred.stlouisfed.org/graph/fredgraph.csv?id=SOFR&cosd=2026-11-12&coed=2026-11-22)、[FRED IORB](https://fred.stlouisfed.org/graph/fredgraph.csv?id=IORB&cosd=2026-11-12&coed=2026-11-22)，均为本次提取所见版本。
- [路透美股收盘](https://www.reuters.com/legal/transactional/wall-st-futures-slip-anthropic-debut-fails-reassure-ai-investors-2026-11-20/)。
- 路透 [全球市场](https://www.reuters.com/world/china/global-markets-global-markets-2026-11-20/)、[汇率](https://www.reuters.com/business/dollar-near-19-month-peak-ai-jitters-sap-risk-appetite-2026-11-20/)、[黄金](https://www.reuters.com/world/india/gold-set-worst-week-eight-months-firm-dollar-fed-hike-bets-weigh-2026-11-20/)。
- [Nikkei 官方](https://indexes.nikkei.co.jp/en/nkave/index/profile?cid=2&idx=nk225vi)、[STOXX 指数定义](https://stoxx.com/index/v2tx/)、[VSTOXX 当日收盘转引](https://www.finanzen.net/index/vstoxx)。

正式输入验收仍需核对原始发布时间、回填同口径历史、验证代理范围与标准化规则，并将来源接入定时采集。避险和跨市场波动本期只形成监测观察。
