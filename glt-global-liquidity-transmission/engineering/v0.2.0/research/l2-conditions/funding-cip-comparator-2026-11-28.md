# 跨境美元融资历史对照：2026-11-28

研究用途，不改变 GLT 正式输入、阈值或评分。Du、Keerati、Schreger [2024q4 版](https://cip.jesseschreger.com/data/2024q4)发布的两组 **1 年 OIS `rho_sofr`** 和美国境内隔夜 **SOFR−IORB** 不是同一口径。前者按发行者定义是货币市场 CIP 偏差，不取反、不改称原始可成交交叉货币基差；后者只作为对照。同观测日交集、不进行填补，无时点回放。

下载原文件后运行 [脚本](evaluate_cip_comparator.py) `python evaluate_cip_comparator.py <目录>`（需 pandas、pyarrow）。原始来源、文件名与此次校验值：

- [EUR.parquet](https://cip.jesseschreger.com/data/2024q4/by_currency/EUR.parquet) `a9549c24cf70ac26e447f1465b728947443256fd58a18d4dcc481d2aca2fe1c0`
- [JPY.parquet](https://cip.jesseschreger.com/data/2024q4/by_currency/JPY.parquet) `0513a3ff1aff679c19c8311336b2b0d743fdb1670531e2d2f057308cc70f4005`
- [sofr.json](https://markets.newyorkfed.org/api/rates/secured/sofr/search.json?startDate=2022-01-01&endDate=2026-11-23) `1e521d9e56d5ddfed5ad3aead624d04df32d3f54a8be56910db6a6e74adda101`
- [prates.zip](https://www.federalreserve.gov/datadownload/Output.aspx?filetype=zip&rel=PRates) `27c08fd78e8728c8d4e13bcedcf30795c316949becbb78eccc75ee4d070dfd97`：Fed 政策利率 XML `RESBM_N.D`，含明确 IORB 描述；原 FRED 图表 CSV 返回 503，所以使用央行发布备选。

EUR 与 JPY 单独可用量分别为 1,093 和 1,098，两币精确日期交集 1,080（日历 2021-02-24 至 2025-06-30）；加上境内利差后是 844 个交集（2022-01-04 至 2025-06-30）。EUR 和 JPY 与境内利差的水平 Pearson 分别 +0.3946、−0.0793，连续共同观测间变动的相关分别 −0.0250、+0.0532，接近零。EUR 与 JPY 的共同变动相关 +0.6984，但全交叉样本水平相关 +0.6337、缩到三项共同样本却为 −0.1002，提示时间区间敏感。不是预测检验，也不能判定事件或因果，不用境内利差冒充跨境价格。

[方法页](https://cip.jesseschreger.com/methodology)说明 3m 是年化 FX 远期升贴水、不是 1y OIS 构造，并称 IBOR 与 SOFR 版本理论相同。实际文件有 80 个 EUR 与 800 个 JPY 重叠日数值差异（大于 0.000001 bp；最大 6.73203 与 5.23181 bp），均不晚于 2021-02-23，不视为可用 3m 采购源。1y 数值用作者恒等式复核单位，先按百分点记录，乘 100 为 bp。当前版本覆盖至 2025-06，精确首发时刻无法回放；样本只用于来源核验，实时同期限报价、首发审计和跨期样本外校准仍缺。
