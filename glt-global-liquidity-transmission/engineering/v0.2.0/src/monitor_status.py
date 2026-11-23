"""Render collection evidence and official scoring readiness at the same cutoff."""

import argparse
import json
from pathlib import Path

from readiness import assess

LAYERS = {
    "L1": "流动性供给",
    "L2": "金融条件",
    "L3": "风险偏好",
    "L4": "实际资金流向",
}
ISSUES = {
    "missing": "没有有效输入",
    "stale": "超出时效",
    "uncalibrated": "缺少历史校准",
    "requires_context_review": "需情境审核",
    "calibration_leakage": "校准时间不合格",
    "transform_mismatch": "转换口径不符",
}


def render(feed, report, official=None, flows=None):
    lines = [
        "# GLT 运行状态", "",
        f"评分检查截点：{report['asof']}",
        f"采集证据时间：{feed['data_retrieved_at_taipei']}（台湾时间）",
        f"FRED：{feed['success_count']}/{feed['expected_series']} 条成功，状态 {feed['collection_status']}",
        f"评分输入覆盖：{report['raw_input_coverage']:.0%}；可计分覆盖：{report['score_coverage']:.0%}",
        "正式综合分发布条件：" + ("通过" if report["official_publishable"] else "未通过"),
        "", "## 各层缺口", "",
        "| 层级 | 有效输入权重点 | 可计分权重点 | 未通过的指标 |",
        "| --- | ---: | ---: | --- |",
    ]
    for key, label in LAYERS.items():
        layer = report["layers"][key]
        issues = "、".join(
            f"{row['indicator']}（{ISSUES.get(row['status'], row['status'])}）"
            for row in layer["issues"]
        )
        points = layer["total_points"]
        lines.append(
            f"| {label} | {layer['raw_input_points']}/{points} | "
            f"{layer['scorable_points']}/{points} | {issues or '—'} |"
        )
    lines.extend([
        "", "## 已取得的序列", "",
        "| 序列 | 观测日 | 数值 | 单位 |", "| --- | --- | ---: | --- |",
    ])
    for name, row in sorted(feed["series"].items()):
        lines.append(
            f"| [{name}]({row['source_url']}) | {row['observation_date']} | "
            f"{row['value_current_vintage']} | {row['unit']} |"
        )
    if official is not None:
        lines.extend(["", "## 财政部与台湾证交所", "",
                      f"采集时间：{official['started_at']}（台湾时间）", "",
                      "| 指标 | 观测日 | 数值 | 单位 | 口径 |",
                      "| --- | --- | ---: | --- | --- |"])
        for name, row in sorted(official["observations"].items()):
            lines.append(
                f"| [{name}]({row['source_url']}) | {row['observation_date']} | "
                f"{row['value']} | {row['unit']} | {row['scope']} |"
            )
        if official["errors"]:
            lines.extend(["", "补充采集失败：" + "、".join(sorted(official["errors"])) + "。"])
    if flows is not None:
        lines.extend([
            "", "## 实际资金流采集证据", "",
            f"采集开始：{flows['started_at']}（UTC）",
            "", "| 指标与来源 | 统计日或周末 | 频率 | 净流 | 单位 | 状态 |",
            "| --- | --- | --- | ---: | --- | --- |",
        ])
        flow_names = {"btc_flow": "BTC ETF", "gold_flow": "黄金 ETF", "asia_equity_flow": "亚洲股票",
                      "us_equity_flow": "美股 ETF", "bond_flow": "债券 ETF"}
        for row in flows["observations"]:
            value = row["value"]
            status = {"complete": "已报齐", "missing_funds": "基金缺报", "reported": "已报告",
                      "reported_estimate": "来源估计", "estimated": "来源估计", "missing": "缺报"}.get(
                          row["status"], row["status"])
            if "reported_funds" in row:
                status += f" {row['reported_funds']}/{row['expected_funds']}"
            lines.append(
                f"| [{flow_names.get(row['indicator'], row['indicator'])}]({row['source_url']})"
                f" | {row['observation_date']} | {row['frequency']} | "
                f"{value if value is not None else '缺报'} | {row['unit']} | {status} |"
            )
        if flows["errors"]:
            lines.extend(["", "资金流采集异常：" + "、".join(
                f"{name}（{error}）" for name, error in sorted(flows["errors"].items())
            ) + "。"])
        lines.extend(["", "[采集原始记录与披露时点](l4_scheduled_latest.json)"])
    if feed["errors"]:
        lines.extend(["", "采集失败：" + "、".join(sorted(feed["errors"])) + "。"])
    lines.extend([
        "", "FRED 采集值为当前版本。正式评分根据已验收的独立输入计算。",
        "", "[项目步骤与验收状态](../../docs/GLT-delivery-status.md)",
    ])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--feed", type=Path, required=True)
    parser.add_argument("--official", type=Path)
    parser.add_argument("--flows", type=Path)
    parser.add_argument("--asof", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    feed = json.loads(args.feed.read_text(encoding="utf-8"))
    official = json.loads(args.official.read_text(encoding="utf-8")) if args.official else None
    flows = json.loads(args.flows.read_text(encoding="utf-8")) if args.flows else None
    args.output.write_text(render(feed, assess(args.root, args.asof), official, flows), encoding="utf-8")


if __name__ == "__main__":
    main()
