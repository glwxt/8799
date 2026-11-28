# GLT 早报采集延迟：定位与补采验收

以下均为台湾时间。计划主采集 07:10，工作流配置 23:10 UTC 正确。执行开始取自 GitHub runner 日志首行，写回取自 `HEAD -> main` 成功日志（时间截断到秒）。

| 日期 | Runner 开始 | 写回 main | 开始到写回 | 运行 |
| --- | ---: | ---: | ---: | --- |
| 11/24 | 14:55:48 | 14:56:20 | 31 秒 | [Actions](https://github.com/glwxt/8799/actions/runs/45344094938) |
| 11/25 | 13:24:11 | 13:24:35 | 24 秒 | [Actions](https://github.com/glwxt/8799/actions/runs/45553319780) |
| 11/26 | 12:58:00 | 12:58:39 | 39 秒 | [Actions](https://github.com/glwxt/8799/actions/runs/45758493004) |
| 11/27 | 12:57:48 | 12:58:10 | 22 秒 | [Actions](https://github.com/glwxt/8799/actions/runs/45942937067) |

已识别工作流开始前的延迟约 5 小时 48 分至 7 小时 46 分。尚未区分 GitHub 定时事件生成延迟与 runner 排队，不归因于 GitHub 特定内部原因。11/24 曾有早间证据，表中只对账对应的定时运行，不用下午文件代替早间报告所见版本。

[部署提交](https://github.com/glwxt/8799/commit/e18293b7807040d644aed7ceb0b3464fc3ac3aaf)：保留 07:10 主采集，新增 07:37 同平台补采。补采开始后从 main 读取最新 FRED 文件，仅在当日 07:10 起已经有有效时间戳、状态 OK、10/10 成功且无失败时跳过，其他情况实际补采。主采集和手动触发照旧。YAML 检查和 9 个本地分支测试通过。此提交用 skip CI 防止部署时人为写入一批凌晨证据，定时路径需实跑。

验收须记录计划、runner 实际开始、GitHub 写回、早报实际截止时间；检查早报截点前可见版本确实是当天 07:10 以后采集、10/10 且状态 OK。最新文件事后被覆盖时，回读各提交；Actions 成功不能替代数据核验。同平台第二条 cron 不是独立备援，遇到主、备用均晚到时，应改用独立调度器调用已支持的 workflow_dispatch，并用仓库文件读回确认。保留早报的定性降级与既有正式评分门槛。

## 11/28 早报：H.4.1 新鲜度验收对照

美联储[日历](https://www.federalreserve.gov/newsevents/2026-november.htm)列示感恩节后 H.4.1 改为美东 11/27 16:30（台湾 11/28 05:30）。已交叉读取 11/27 [原始公报](https://www.federalreserve.gov/releases/h41/current/default.htm)与 FRED 表。下列新值在主采集计划前已查到：这是公开可见的下界证据，不等于精确首发时间。各值单位为百万美元。

| 序列 | 11/25 新值 | 11/18 前一期 | 公报口径 |
| --- | ---: | ---: | --- |
| [WRESBAL](https://fred.stlouisfed.org/data/WRESBAL) | 2,963,667 | 2,979,656 | 表 1 周均准备金，非周三的 2,928,659 |
| [WALCL](https://fred.stlouisfed.org/data/WALCL) | 6,732,044 | 6,741,452 | 表 5 周三总资产 |
| [SWPT](https://fred.stlouisfed.org/data/SWPT) | 145 | 146 | 表 5 周三中央银行流动性互换 |

主采集计划前，仓库快照仍为 11/27 台湾时间 12:57 的前一期值，属运行前基线，不是故障。待早报截点当时可见的提交出来后，分别核验采集是否在截点前写回、上述三项是否匹配新一期。事后补发不改变早报截点；10/10 不自动证明取到最新期，也不改变正式评分资格。

### 第一天：08:08 现场记录

11/28 08:08:17（00:08:17 UTC）两次计划时间均已过去，main 尚无当天证据写回：[当时可见的快照](https://github.com/glwxt/8799/blob/f593f28e5af1b86fe46d1139ef46e54c72789bc5/glt-global-liquidity-transmission/data/feeds/fred_latest.json)仍为 11/27 台湾时间 12:57:50、10/10、H.4.1 截至 11/18。11/28 报告及其实际截点尚未确认，暂不能判定两次是否均错过报告；若实际截点不晚于此次记录，即可确认当天截点前未写回。记录时未主动触发补采，以保留计划路径的真实验收结果。

另核对到 07:37 的条件只检查 FRED；触发跳过时也会跳过 Treasury、TWSE、资金流和运维报告。不能以 FRED 成功证明其他采集齐全。独立调度验收应分别对账这些产物，不要求低频源每天发布新期，只检查采集尝试、来源的合理新鲜度和提交截点。

### 第一天验收结果：08:23 截点未写回

[11/28 原始早报](https://chatgpt.com/c/6b0066ec-a1ec-83ee-b623-7f8b094343a6?messageId=1116fc95-b88d-414f-9c80-a37e09a9a8c6)声明截点 08:23（00:23 UTC），本期仅在 ChatGPT 发布。报告第 7 节与[早报前仓库快照](https://github.com/glwxt/8799/blob/12b29139c549b1fabaf7bab0f2621ea0af2dbd33/glt-global-liquidity-transmission/data/feeds/fred_latest.json)均仍显示 11/27 12:57:50 批次。**07:10 和 07:37 均未在早报实际截点前写回，首日不通过。** 09:03 后复查仍为旧批次。两项定时运行的开始和写回时间尚未证实，不把“截点前未交付”表述为“工作流失败”或“从未运行”。早报可以独立核对原始 H.4.1，但并不改变本次采集验收。继续 11/29、11/30 比较。

下期日报已加入分日期来源登记表与 Fed/TWSE/JPX/KRX/南向研究档案回查，仍需下一期实际报告验收。11/28 原报保留。覆盖变化更正：11/26 [评分器](https://github.com/glwxt/8799/blob/2b3c95193c1b34d3a620d76b933c7aa38832e326/glt-global-liquidity-transmission/data/feeds/monitor_status.md)及 11/27 [评分器](https://github.com/glwxt/8799/blob/a97cf0c03c0aaaed9ffa6cdf20cc26217aa10eb2/glt-global-liquidity-transmission/data/feeds/monitor_status.md)均将 VIX 判为陈旧；导致 5%→0% 的是高收益债利差：评分台账观察期为 11/19，年龄从 7 到 8 天，超过 7 天上限。原始采集表另有 11/24 值，但不是同一评分台账。正式分继续不发。另核对 [DGS10](https://fred.stlouisfed.org/data/DGS10) 和 [DFII10](https://fred.stlouisfed.org/data/DFII10)：11/25 同日分别 4.85% 和 2.73%，均较 11/24 低 6 个基点；差值仍为 2.12 个百分点。不同日期不配对。

### 独立调度升级：待可用执行主机

曾用于讨论 GLM 的东京 Ubuntu 主机仅是候选，目前未确认可用或接入。连接器未提供直接触发接口。建议在一个已批准、持续在线且独立于 GitHub cron 的环境中，用仅限本仓库 Actions 写权限的凭据调用 [workflow_dispatch](https://docs.github.com/en/rest/actions/workflows#create-a-workflow-dispatch-event)，固定工作流 `glt-fred-staging.yml` 和 `main`。可先做低风险手动验证：在验收窗口外触发一次，记录请求时间、返回的运行链接（若有）、runner 启动及落库；成功后再配置定时。建议先在原 07:10 主采集后验证是否已有当日 OK 10/10，且同批次的官方与 L4 产物均更新；任一缺失才触发，单日最多一次；不得将触发回执当成数据通过。外部调度绕过的是 GitHub 定时事件，依然依赖 GitHub runner。暂不更改现有两个计划或正式评分。不要把凭据交给聊天或写入仓库。
