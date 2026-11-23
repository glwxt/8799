# GLT L2 两项情境指标的取数与验证

2026-11-24（台湾时间）。研究证据，未接入正式评分。观测窗口从 2022-01-01 至 2026-11-23。原始文件哈希、共同观测日期和统计结果见 [results.json](results.json)。

## 境内美元融资压力

从纽约联储直接取得有抵押 SOFR 和无抵押 EFFR，以同一有效日与 Fed IORB 对齐。11 月 20 日配对得到 SOFR−IORB +2 基点、EFFR−IORB −2 基点；11 月 23 日缺完整同日数据，暂留空。用 2022–2024 年 748 个共同日分别确定第 95 百分位（−5、−7 基点），冻结阈值后检查 2025–2026 年 471 个共同日，两个利差同时严格超过阈值达 265 日（56.3%）。阈值跨期稳定性不及作为异常压力信号的需要。本次未用两个美国境内利差替代跨境基差，也未把区间上尾解释为市场危机。历史文件为当前版本，逐日首发时间及修订未全部核验。纽约联储存在当日重发机制。

## 名义长端利率 4 个权重点

同日将 DGS10 拆为 DFII10 实际利率与 T10YIE 通胀盈亏平衡利率。1,221 个共同观测日的加总差最大为 0 基点。11 月 20 日相较 11 月 19 日，名义 −12 基点 = 实际 −11 基点 + 盈亏平衡 −1 基点。T10YIE 是从相关收益率推导的结果，这项对账只验证日期、单位与拆分一致性，不能独立验证经济原因。现行 L2 已有实际利率因子；名义利率不得重复给这 −11 基点赋分。拟先验证非实际利率部分及其他背景证据能否提供增量，仍需样本外方向校准和方法审批。

## 复跑来源

下载为同一目录，执行 `python evaluate.py <目录> --cutoff 2026-11-23`。

- `sofr.json` [纽约联储 SOFR](https://markets.newyorkfed.org/api/rates/secured/sofr/search.json?startDate=2022-01-01&endDate=2026-11-23)
- `effr.json` [纽约联储 EFFR](https://markets.newyorkfed.org/api/rates/unsecured/effr/search.json?startDate=2022-01-01&endDate=2026-11-23)
- `iorb.csv` [FRED IORB](https://fred.stlouisfed.org/graph/fredgraph.csv?id=IORB&cosd=2022-01-01&coed=2026-11-23)
- `DGS10.csv`、`DFII10.csv`、`T10YIE.csv`：同上 FRED 查询，替换 id。
- [纽约联储参考利率披露和修订说明](https://www.newyorkfed.org/markets/reference-rates/additional-information-about-reference-rates)
