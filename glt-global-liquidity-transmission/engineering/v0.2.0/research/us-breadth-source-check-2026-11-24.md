# 美股市场广度来源与分母试验

2026-11-24（台湾时间）。用路透同一报道口径的 Nasdaq 上涨、下跌家数试算上涨占比：上涨家数 ÷（上涨＋下跌家数）。未包含持平或无涨跌记录的证券；不能与 Nasdaq Trader 的总成交证券数混作分母。

| 美国交易日 | 上涨 | 下跌 | 上涨占比 | 来源 |
| --- | ---: | ---: | ---: | --- |
| 2026-11-20 | 928 | 3964 | 18.97% | [路透当日收盘报道](https://www.reuters.com/legal/transactional/wall-st-futures-slip-anthropic-debut-fails-reassure-ai-investors-2026-11-20/) |
| 2026-11-23 | 4088 | 1035 | 79.80% | [路透当日收盘报道](https://www.reuters.com/business/wall-street-futures-rebound-after-rough-week-ai-linked-shares-2026-11-23/) |

这是单市场、二手报道的可复核样本。Nasdaq Trader 公开日表已核对，其列示成交证券总数、成交量和成交笔数，未提供可直接复现该分子的涨跌拆分。正式 us_breadth 仍需锁定交易所或稳定的可授权且可回放的来源，确认证券范围、持平规则、交易所覆盖和原始披露时间。未写入评分输入。

[Nasdaq Trader 日表](https://nasdaqtrader.com/Trader.aspx?id=DailyMarketSummary)

## 11/28 补录：感恩节周的可比交易日

| 美国交易日 | 上涨 | 下跌 | 上涨占比 | 来源 |
| --- | ---: | ---: | ---: | --- |
| 2026-11-24 | 2376 | 2548 | 48.25% | [路透报道](https://www.marketscreener.com/news/nasdaq-s-p-500-slip-following-monday-s-nvidia-fueled-rally-ce7851dbdc88f423) |
| 2026-11-25 | 2902 | 2009 | 59.09% | [路透报道](https://www.reuters.com/business/nasdaq-futures-slide-over-2-fresh-us-tariff-concerns-inflation-data-focus-2026-11-25/) |
| 2026-11-27 | 3677 | 1135 | 76.41% | [路透报道](https://www.reuters.com/business/wall-st-futures-surge-investors-return-holiday-2026-11-27/) |

加上上表已有的 11/23，四个实际交易日中三日上涨家数占多数；11/25 即使 Nasdaq 综合指数下跌，上涨家数仍占 59.09%，显示成分权重与证券计数不同。11/26 [交易所休市](https://www.nyse.com/trade/hours-calendars)，不记零。11/27 路透另报 NYSE 涨跌家数比例 3.25:1，只作为方向交叉核对，不与 Nasdaq 家数相加。路透是二手统计来源，部分直链本次未能打开，另以授权转载或公开媒体核查报道计数。没有锁定分母证券范围及首次发布时间，不算正式权重。
