#!/usr/bin/env python3
"""품질 롤업 생성기 — QualityDirective의 발견 사항·처분을 집계한다. 점수는 관측용."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

DIRECTIVES_DIR = Path.home() / ".claude" / "mistakes" / "registry" / "quality" / "directives"
FINDINGS_DIR = Path.home() / ".claude" / "mistakes" / "registry" / "quality" / "findings"
DISPOSITIONS_DIR = Path.home() / ".claude" / "mistakes" / "registry" / "quality" / "dispositions"
ROLLUPS_DIR = Path.home() / ".claude" / "mistakes" / "registry" / "quality" / "rollups"

DISPOSITION_KEYS = ["upheld", "dismissed", "needs_user", "deferred"]
SEVERITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}


def load_directive(quality_directive_id: str) -> dict | None:
    """QualityDirective를 레지스트리에서 불러온다."""
    path = DIRECTIVES_DIR / f"{quality_directive_id}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def load_findings(quality_directive_id: str) -> list[dict]:
    """해당 디렉티브의 모든 발견 사항을 불러온다."""
    findings_dir = FINDINGS_DIR / quality_directive_id
    if not findings_dir.exists():
        return []
    findings: list[dict] = []
    for json_file in findings_dir.glob("*.json"):
        try:
            findings.append(json.loads(json_file.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            continue
    return findings


def load_disposition(finding_id: str) -> dict | None:
    """발견 사항 ID에 해당하는 처분을 불러온다."""
    path = DISPOSITIONS_DIR / f"{finding_id}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def compute_overall_status(upheld_findings: list[dict]) -> str:
    """전체 상태를 결정한다. 점수는 대시보드용 관측 전용."""
    if not upheld_findings:
        return "clean"
    severities = {f.get("severity") for f in upheld_findings}
    if "P0" in severities or "P1" in severities:
        return "issues"
    return "warnings"


def compute_per_dimension_summary(
    findings: list[dict],
    dispositions: dict[str, dict],
) -> dict[str, dict]:
    """차원별 발견 수와 최고 심각도를 집계한다."""
    summary: dict[str, dict] = {}
    for finding in findings:
        dim = finding.get("dimension", "unknown")
        fid = finding.get("finding_id", "")
        severity = finding.get("severity", "P3")
        disp = dispositions.get(fid, {}).get("disposition")

        if dim not in summary:
            summary[dim] = {"finding_count": 0, "max_severity": None, "dispositions": {}}
        summary[dim]["finding_count"] += 1

        # 최고 심각도 갱신 (P0 > P1 > P2 > P3)
        current_max = summary[dim]["max_severity"]
        if current_max is None or SEVERITY_ORDER.get(severity, 9) < SEVERITY_ORDER.get(current_max, 9):
            summary[dim]["max_severity"] = severity

        # 처분 카운트
        disp_key = disp if disp else "undisposed"
        summary[dim]["dispositions"][disp_key] = summary[dim]["dispositions"].get(disp_key, 0) + 1

    return summary


def build_rollup(
    directive: dict,
    findings: list[dict],
    dispositions: dict[str, dict],
) -> dict:
    """롤업 JSON 객체를 구성한다."""
    quality_directive_id = directive["quality_directive_id"]
    total = len(findings)

    counts: dict[str, int] = {k: 0 for k in DISPOSITION_KEYS}
    counts["undisposed"] = 0
    upheld_findings: list[dict] = []
    unresolved_findings: list[dict] = []

    for finding in findings:
        fid = finding.get("finding_id", "")
        disp = dispositions.get(fid, {}).get("disposition")
        if disp in counts:
            counts[disp] += 1
        else:
            counts["undisposed"] += 1

        if disp == "upheld":
            upheld_findings.append(finding)
        if disp in ("upheld", None):  # upheld + 미처분
            unresolved_findings.append(finding)

    # P0/P1 upheld (관측 전용 — blocking 아님)
    blocking_advisory = [
        f.get("finding_id") for f in upheld_findings
        if f.get("severity") in ("P0", "P1")
    ]

    per_dim = compute_per_dimension_summary(findings, dispositions)
    overall_status = compute_overall_status(upheld_findings)

    return {
        "quality_directive_id": quality_directive_id,
        "task_id": directive.get("task_id"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "observe_only": directive.get("observe_only", True),
        "note": "점수는 관측용. blocking 판정에 사용 금지.",
        "summary": {
            "total_findings": total,
            "upheld_count": counts["upheld"],
            "dismissed_count": counts["dismissed"],
            "needs_user_count": counts["needs_user"],
            "deferred_count": counts["deferred"],
            "undisposed_count": counts["undisposed"],
            "unresolved_count": len(unresolved_findings),
            "blocking_advisory_ids": blocking_advisory,
            "blocking_advisory_note": (
                "P0/P1 upheld 발견 사항 목록 — 관측 전용. "
                "현재 Phase에서 workflow blocking 아님."
            ),
        },
        "overall_status": overall_status,
        "overall_status_note": "clean=upheld 0건|warnings=P2·P3만|issues=P0·P1 존재. 대시보드 전용. Phase Gate blocking 금지.",
        "per_dimension": per_dim,
        "workflow_note": "unresolved_count가 미래 Phase 유일 유효 수치. scores·status는 관측 전용.",
        "dimensions_activated": directive.get("quality_dimensions", []),
    }


def parse_args() -> argparse.Namespace:
    """CLI 인자를 파싱한다."""
    parser = argparse.ArgumentParser(
        description="QualityDirective의 품질 검토 결과를 집계하고 롤업을 저장한다.",
    )
    parser.add_argument("--quality-directive-id", required=True,
                        help="롤업을 생성할 QualityDirective ID")
    return parser.parse_args()


def main() -> None:
    """엔트리포인트."""
    args = parse_args()

    directive = load_directive(args.quality_directive_id)
    if directive is None:
        print(f"[오류] QualityDirective '{args.quality_directive_id}'를 찾을 수 없습니다.", file=sys.stderr)
        sys.exit(1)

    findings = load_findings(args.quality_directive_id)

    # 처분 인덱스: finding_id → disposition dict
    dispositions: dict[str, dict] = {}
    for finding in findings:
        fid = finding.get("finding_id", "")
        disp = load_disposition(fid)
        if disp:
            dispositions[fid] = disp

    rollup = build_rollup(directive, findings, dispositions)

    ROLLUPS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = ROLLUPS_DIR / f"{args.quality_directive_id}.json"
    out_path.write_text(json.dumps(rollup, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(rollup, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
