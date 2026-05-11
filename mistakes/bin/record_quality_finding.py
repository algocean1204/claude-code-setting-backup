#!/usr/bin/env python3
"""품질 발견 사항 기록기 — 증거 기반 검증을 통과한 발견 사항만 저장한다."""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

FINDINGS_DIR = Path.home() / ".claude" / "mistakes" / "registry" / "quality" / "findings"

VALID_DIMENSIONS = [
    "requirement_fidelity",
    "maintainability",
    "robustness",
    "security_safety",
    "architecture_fit",
    "performance",
    "test_quality",
    "accessibility",
    "user_experience",
    "documentation",
]

VALID_SEVERITIES = ["P0", "P1", "P2", "P3"]

VALID_CONFIDENCE_BASIS = [
    "measured_metric",
    "tool_output",
    "code_structure_analysis",
    "test_result",
    "artifact_reference",
]

# 증거에서 거부할 모호한 표현 목록 (주관적·추측성 표현)
VAGUE_PHRASES = [
    "보인다", "느낌", "것 같다", "아마", "probably",
    "seems", "looks like", "might be", "복잡해 보임", "좀 이상함",
]


def validate_evidence(evidence: str, confidence_basis: str,
                       file_path: str, line_start: int, line_end: int) -> list[str]:
    """증거 유효성을 검사한다. 위반 사항 목록을 반환한다."""
    violations: list[str] = []

    # 1. 증거 최소 길이 검사
    if len(evidence) < 20:
        violations.append(f"증거(evidence)가 너무 짧습니다 ({len(evidence)}자 < 20자 최소)")

    # 2. 모호한 표현 검사 (주관적 표현 금지)
    lower_ev = evidence.lower()
    found_vague = [p for p in VAGUE_PHRASES if p in lower_ev]
    if found_vague:
        violations.append(f"증거에 모호한 표현 포함: {found_vague}. 객관적·측정 가능한 증거 필요")

    # 3. confidence_basis 유효성 검사
    if confidence_basis not in VALID_CONFIDENCE_BASIS:
        violations.append(f"신뢰 근거(confidence_basis) 무효: '{confidence_basis}'")

    # 4. file_path 공백 검사
    if not file_path or not file_path.strip():
        violations.append("파일 경로(file_path)가 비어 있습니다")

    # 5. 라인 범위 검사
    if line_start > line_end:
        violations.append(f"line_start({line_start}) > line_end({line_end}): 라인 범위 오류")
    if line_start < 1:
        violations.append(f"line_start({line_start}) < 1: 라인 번호는 1 이상이어야 합니다")
    if line_end < 1:
        violations.append(f"line_end({line_end}) < 1: 라인 번호는 1 이상이어야 합니다")

    return violations


def build_finding(args: argparse.Namespace, finding_id: str) -> dict:
    """QualityFinding JSON 객체를 구성한다."""
    return {
        "finding_id": finding_id,
        "quality_directive_id": args.quality_directive_id,
        "dimension": args.dimension,
        "severity": args.severity,
        "file_path": args.file_path,
        "line_start": args.line_start,
        "line_end": args.line_end,
        "evidence": args.evidence,
        "impact": args.impact,
        "proposed_repair": args.proposed_repair,
        "confidence_basis": args.confidence_basis,
        "auto_repair_candidate": args.auto_repair_candidate,
        "created_by": args.created_by,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def parse_args() -> argparse.Namespace:
    """CLI 인자를 파싱한다."""
    parser = argparse.ArgumentParser(
        description="품질 발견 사항을 기록한다. 증거 검증 실패 시 저장하지 않고 종료한다.",
    )
    parser.add_argument("--quality-directive-id", required=True,
                        help="연결할 QualityDirective ID")
    parser.add_argument("--dimension", required=True, choices=VALID_DIMENSIONS,
                        help="품질 차원 (10가지 중 선택)")
    parser.add_argument("--severity", required=True, choices=VALID_SEVERITIES,
                        help="심각도 (P0=최고, P3=낮음)")
    parser.add_argument("--file-path", required=True,
                        help="발견 사항이 위치한 파일 경로")
    parser.add_argument("--line-start", required=True, type=int,
                        help="시작 줄 번호")
    parser.add_argument("--line-end", required=True, type=int,
                        help="종료 줄 번호")
    parser.add_argument("--evidence", required=True,
                        help="객관적 증거 (측정값·도구 출력·코드 구조 분석 등, 최소 20자)")
    parser.add_argument("--impact", required=True,
                        help="영향 범위 설명")
    parser.add_argument("--proposed-repair", required=True,
                        help="제안된 수정 방법")
    parser.add_argument("--confidence-basis", required=True, choices=VALID_CONFIDENCE_BASIS,
                        help="신뢰 근거 유형")
    parser.add_argument("--auto-repair-candidate", action="store_true", default=False,
                        help="자동 수리 후보 여부")
    parser.add_argument("--created-by", required=True,
                        help="기록자 식별자")
    return parser.parse_args()


def main() -> None:
    """엔트리포인트."""
    args = parse_args()

    violations = validate_evidence(
        args.evidence, args.confidence_basis,
        args.file_path, args.line_start, args.line_end,
    )
    if violations:
        for v in violations:
            print(f"[거부] {v}", file=sys.stderr)
        print("증거 검증 실패: 발견 사항이 저장되지 않았습니다.", file=sys.stderr)
        sys.exit(1)

    finding_id = f"qf-{uuid.uuid4()}"
    finding = build_finding(args, finding_id)

    # 디렉터리: findings/{quality_directive_id}/{finding_id}.json
    save_dir = FINDINGS_DIR / args.quality_directive_id
    save_dir.mkdir(parents=True, exist_ok=True)
    out_path = save_dir / f"{finding_id}.json"
    out_path.write_text(json.dumps(finding, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(finding, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
