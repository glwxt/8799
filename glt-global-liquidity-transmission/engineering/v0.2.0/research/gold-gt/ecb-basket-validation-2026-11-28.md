# GOLD-GT：ECB 六货币篮子复验（研究，不是 ICE DXY）

复验日期 2026-11-28（台湾时间）。数据截止 2026-11-20，后续公布报价仅用于数据源完整性核对，不参与回测。没有把研究结果写入任何生产评分表。

## 实采与时点

- [ECB 官方参考汇率](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html)提供公开日频历史。ECB 报价以欧元为基准，用每种外币兑欧元数除以 USD 兑欧元数转成「每美元外币数」，欧元项取 1/USD。用 [ICE 公式与权重](https://www.ice.com/publicdocs/data/ICE_FX_Indexes_Methodology.pdf)几何加权。6 个汇率任一缺报，不算当日，不填零，不前填。固定在 ECB 参考时点，不是 ICE 纽约收盘；实际首次发布时间对历史各行未逐日验证。ICE 现货收盘与 DX 期货杠杆合约是不同对象；[ICE 数据目录](https://developer.ice.com/fixed-income-data-services/catalog/ice-data-indices-currency-indices)列有历史渠道，但本轮未取到可持续公开的官方 ICE 收盘序列。
- 11/27 官方汇率样本：USD 1.0957、JPY 174.81、GBP 0.83504、CAD 1.5608、SEK 11.2080、CHF 0.9157；篮子计算为 103.8707。此数不是 11/27 的 ICE DXY 收盘。最近 20 个 ECB 交易日 CSV 与独立下载的官方 XML 值逐日交叉核对一致；检查了换算方向、Fed 日期解析和重复项。
- 基线使用 [Fed H.10 广义指数](https://www.federalreserve.gov/releases/h10/summary/jrxwtfb_nb.htm)与 [美国财政部 10 年实际收益率](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_real_yield_curve)、[GLD 发行人档案](https://api.spdrgoldshares.com/api/v1/historical-archive?exchange=NYSE&lang=en&product=gld)。Treasury 11/24 值 2.79% 与 [当期仓库 FRED](../../../../data/feeds/fred_latest.json)的同日数值相符；该核对不代表各历史时点版本均已核实。

## 对照结果

所有方案使用完全相同的交易日与目标、月度扩展训练和既定的窗口隔离；实际利率、GLD 估算份额仍至少滞后一交易日。三组分别为广义美元滞后至少 10 个日历日、ECB 篮子同滞后、ECB 篮子最多取前一 GLD 交易日。评价为符号命中及绝对误差（MAE，基点），不是五级预测台账评分，也不是涨跌概率。

| 样本 | 历史均值 | 广义美元 10 日＋利率＋份额 | ECB 10 日＋利率＋份额 | ECB 前一交易日＋利率＋份额 |
| --- | --- | --- | --- | --- |
| 1 日，1,983 个 | 80.53 / 54.16% | 80.68 / 52.14% | 80.67 / 52.14% | 80.68 / 52.24% |
| 5 日，1,979 个 | 182.18 / 56.75% | 183.22 / 55.84% | 183.09 / 56.44% | 183.86 / 53.46% |
| 5 日，不重叠 396 个 | 182.58 / 56.31% | 183.87 / 56.06% | 183.88 / 57.32% | 185.10 / 53.79% |

较新的 ECB 数据没有改善这套模型。固定滞后组在少数切片方向命中较高，但五日不重叠误差仍大于历史均值，不能据此启用。GOLD-GT 正式分保持未发布，L2 的 DXY 8 点仍不计。下一轮用带披露时点的多基金实际净流作独立增量检验，不把 GLD 单基金估算或 ECB 篮子冒充正式数据。

## 复现

下载 [ECB 完整 ZIP](https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip)为 `ecb.zip`、上方 Fed H.10 HTML 为 `broad.htm`、发行人 Excel 为 `gld.xlsx`；按年下载财政部 2016–2026 年“Daily Treasury Par Real Yield Curve Rates”CSV 为 `real_YYYY.csv`。例如 [2026 年 CSV](https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/2026/all?type=daily_treasury_real_yield_curve&field_tdr_date_value=2026&page&_format=csv)，逐年替换 URL 两处年份。运行 `python evaluate_ecb_basket.py <数据目录> --cutoff 2026-11-20`。本次档案均为可获取的当前版本，历史修订不可回放，结果只供研究。ECB ZIP SHA-256 为 `5100374d7fe6f8cd5dd552f077341d41578464ad4d33a7a6d8d0cf02c0950ab4`；H.10 HTML 为 `cf984da3edea454a5827aa4df479e2e51ed7baa1ee1058fb2dbc205e60db3c08`；GLD XLSX 为 `4e04cec2c1efbfee26a746960c2128b56d86f2b21e2a47b92b362c851bc28279`。完整回测输出包括不带份额的模型与 2024 年以来子样本。
