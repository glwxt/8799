# 空间同步任务

空间：Muse 空间「GLT全球流动性传导监测」，slug `gltquan-qiu-liu-dong-xing-chuan-dao-jian-ce`，独立空间，不并入「金融简报和GLI监控」。

| 同步 | 任务 ID（Muse 内） | 运行时间 | 动作 |
| --- | --- | --- | --- |
| 每日同步 | `glt-daily-sync` | 每天约 09:27 | `refreshDaily` |
| 每周同步 | `glt-weekly-sync` | 每周一约 09:27 | `refreshWeekly` |

同步必须跑在对应报告生成之后（生成约 08:11，同步约 09:27），否则空间会显示旧报告。空间本身是 Muse 里的 fullstack 空间，源码由 Muse 托管，不能导出，本仓库只存规格、任务说明与报告档案。
