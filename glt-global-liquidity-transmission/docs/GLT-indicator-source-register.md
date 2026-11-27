# GLT V1.0 指标与来源登记表

2026-11-24（台湾时间）。指标、权重、目标频率来自现有工程配置。登记表用于第 2 步验收，当前不修改评分口径。来源已识别、已实采、正式口径已验收须分别记录。表内「已实采」表示已有来源证据，披露时点、版本及正式输入状态见待验收栏。

| ID | 权重 | 目标频率 / 单位 | 主来源或待核候选 | 已有证据与待验收口径 |
| --- | ---: | --- | --- | --- |
| reserves | 8 | 周 / 百万美元 | Fed H.4.1，WRESBAL | 已实采；锁定周均及发布时间，周三时点另作对账 |
| tga | 8 | 日 / 百万美元 | 美国财政部 DTS，TGA Closing Balance | 已实采；登记日表披露日及修订，与 H.4.1 周均区分 |
| on_rrp | 5 | 日 / 十亿美元 | NY Fed 操作结果，FRED RRPONTSYD | 已实采；按操作日记录、节假日留缺，与外国官方逆回购区分 |
| fed_assets | 5 | 周 / 百万美元 | Fed H.4.1，WALCL | 已实采；总资产用周三时点，MBS 等分项按各自频率登记 |
| global_usd | 4 | 周 / 综合 | H.4.1 SWPT、NY Fed 互换、BIS 境外美元信贷 | 已有多频资料；缺可回放的同期限跨币种基差和综合映射 |
| dxy | 8 | 日 / 指数 | ICE U.S. Dollar Index | ICE 已核实日频现货收盘定义与数据渠道；未取得持续官方收盘序列；ECB 六币篮子及 DTWEXBGS 仅作研究代理 |
| us_10y_real | 8 | 日 / % | Fed H.15 / FRED DFII10 | 已实采；登记发布时间和历史版本 |
| us_10y_nominal | 4 | 日 / % | Fed H.15 / FRED DGS10 | 已实采；登记发布时间和历史版本 |
| usd_funding | 5 | 日 / 利差 | NY Fed SOFR、Fed IORB；其他利差待验 | 已有同日 SOFR−IORB 基点样本；锁定第二佐证和适用范围 |
| vix | 5 | 日 / 指数 | Cboe / FRED VIXCLS | 已实采；登记收盘时点与来源一致性 |
| hy_spread | 5 | 日 / 百分点 | ICE BofA US HY OAS / FRED BAMLH0A0HYM2 | 已实采；确认源单位及转基点标准，核验披露和使用条款 |
| us_breadth | 4 | 日 / % | 美国交易所上涨与下跌家数，正式入口待选 | 锁定交易所、股票样本、平盘和停牌处理、分母及收盘时间 |
| safe_haven | 3 | 日 / 综合 | 金、日元、瑞郎、国债候选 | 锁定各来源、方向和权重；避免与其他因子重复 |
| global_vol | 3 | 日 / 综合 | 多市场波动率候选 | 锁定市场与指数、时区同步、归一化及缺市处理 |
| btc_flow | 7 | 日 / 美元 | 美国现货 BTC ETF，Farside 汇总及发行人复核 | 已实采；明确逐基金完整口径、发布时间和缺报；源单位百万美元 |
| gold_flow | 6 | 日 / 美元 | 发行人日度净流候选；WGC 周/月数据 | WGC 已核验出版时点；日频尚缺，周/月原样归档，频率变更须走方法版本 |
| us_equity_flow | 6 | 日 / 美元 | 发行人候选；ICI 本土股票 ETF 净发行 | ICI 周频已实采，日频欠缺；源单位百万美元，记录估计及修订 |
| asia_equity_flow | 4 | 日 / 本币 | TWSE、JPX、KRX；港陆官方来源待定 | 台湾日频、日本周频、韩国 KOSPI 日频已实采；定义市场范围、投资者口径及交易日对齐 |
| bond_flow | 2 | 周 / 美元 | ICI 债券 ETF 净发行 | 已实采；锁定应税和市政债范围、源单位百万美元及周报时间 |

第 2 步的验收材料须为每项登记可读的官方入口或固定序列标识、统计对象与范围、原始单位与转换、观察频率、披露规则（时区和可验证的时间精度）、修订政策、来源优先级及缺报处理。每个已锁定来源附至少一条可复核样本，并记录当前值是否符合目标频率。无可验证来源的项继续列为缺口；拟采用不同口径时附方法版本与审批记录。定时链路、历史校准与是否可发布在其他步骤验收。

## 缺报与真实零值

**来源明确报告为 0，就记 0；来源还没报，就留空。** 结构化缺报值使用 `null`。部分基金已报时，已报小计单独展示，完整合计仍留空。补报记录保留其公开披露时间，历史复盘按当时可见的数据计算。

[工程指标配置](../engineering/v0.2.0/config/indicators.csv) · [运行证据](../data/feeds/monitor_status.md) · [资金流快照](../data/feeds/l4_flow_evidence_2026-11-24.json) · [黄金披露档案](../engineering/v0.2.0/research/gold-gt/gold-etf-flow-publications.json) · [美元融资来源核验](../engineering/v0.2.0/research/l1-h41/USD-funding-source-check-2026-11-24.md)

[韩国 KRX 五个交易日研究证据](../data/feeds/krx_kospi_foreign_research_2026-11-27.json) · [ECB 篮子与 GOLD-GT 复验](../engineering/v0.2.0/research/gold-gt/ecb-basket-validation-2026-11-28.md)。两项均不自动进入评分。
