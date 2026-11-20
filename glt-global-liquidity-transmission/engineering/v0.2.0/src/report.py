#!/usr/bin/env python3
"""Generate safe qualitative GLT report from actual engine results (no invented signals)."""
import argparse,pathlib
from glt import calculate,timestamp
from asset_models import model_status
def render(r):
 rows=[f'# GLT 监测日报（工程测试版） — {r["asof"][:10]}','',f'数据截止：{r["asof"]}','','## 一、综合状态',f'- 数据有效覆盖率：{r["coverage"]:.0%}',f'- 是否允许发布正式综合分：{"是" if r["publishable"] else "否"}',f'- GLT 正式综合评分：{r["composite_score"] if r["composite_score"] is not None else "不发布"}',f'- 状态：{r["state"] or "无法可靠判定"}',f'- 质量提示：{r["quality"]}','','## 二、四层评分','| 层级 | 数据覆盖率 | 正式层级得分 |','|---|---:|---:|']
 for k,name in [('L1','流动性供给'),('L2','金融条件'),('L3','风险偏好'),('L4','实际资金流向')]:
  v=r['layers'][k];rows.append(f'| {name} | {v["coverage"]:.0%} | {v["score"] if v["score"] is not None else "不发布"} |')
 rows+=['','## 三、资产模型（独立）','| 模型 | 评分 | 方向 | 状态 |','|---|---:|---|---|']
 for k,v in model_status().items():rows.append(f'| {k} | 不发布 | 待核实 | {v["status"]} |')
 rows+=['','## 四、未来方向（24小时、7天）','- BTC / 黄金 / 股票：缺乏已验证模型及必要数据，不输出方向。','- 全球资金主流向：待核实。','- 背离警报：暂无足够证据，不能视为不存在风险。','', '## 五、数据质量清单','| 指标 | 状态 | 观测日期 | 来源 |','|---|---|---|---|']
 for v in r['indicators']:rows.append('| '+ ' | '.join([v['indicator_id'],v['status'],v['observation_date'] or 'NA',v['source_url'] or 'NA'])+' |')
 rows+=['','*本文件由真实输入的覆盖率和评分状态生成；不是实时市场研究结论。*']
 return '\n'.join(rows)+'\n'
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parents[1]);p.add_argument('--asof',required=True);a=p.parse_args()
 r=calculate(a.root,timestamp(a.asof));out=a.root/'reports'/('glt_'+r['asof'][:10]+'.md');out.parent.mkdir(exist_ok=True,parents=True);out.write_text(render(r),encoding='utf-8');print(out)
if __name__=='__main__':main()
