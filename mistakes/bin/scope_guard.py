#!/usr/bin/env python3
"""범위 보호기 — 제안된 수리의 범위를 7개 부울 술어로 분류한다. 모델 판단 없음."""
from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

SCOPE_GUARD_DIR = Path.home() / ".claude" / "mistakes" / "registry" / "quality" / "scope-guard"

# 분류 결과 상수 (스키마 enum: 소문자)
IN_SCOPE_REFINEMENT = "in_scope_refinement"
REJECT_SCOPE_CREEP = "reject_scope_creep"
NEEDS_USER_APPROVAL = "needs_user_approval"


def classify_scope(
    required_to_satisfy_acceptance_criteria: bool,
    reduces_existing_risk_without_new_behavior: bool,
    adds_new_capability: bool,
    changes_public_api_or_schema: bool,
    changes_architecture_boundary: bool,
    touches_files_outside_directive_scope: bool,
    changes_user_visible_behavior: bool,
) -> tuple[str, str]:
    """7개 부울 술어를 기반으로 범위를 순수하게 분류한다. 모델 판단 없음.

    반환: (decision, reason)
    """
    positive = required_to_satisfy_acceptance_criteria or reduces_existing_risk_without_new_behavior
    creep_indicators = [
        adds_new_capability,
        changes_public_api_or_schema,
        changes_architecture_boundary,
        touches_files_outside_directive_scope,
    ]
    # IN_SCOPE_REFINEMENT: 긍정 조건 충족 + 모든 creep 지표 false
    if (
        positive
        and not adds_new_capability
        and not changes_public_api_or_schema
        and not changes_architecture_boundary
        and not touches_files_outside_directive_scope
    ):
        return IN_SCOPE_REFINEMENT, (
            "수용 기준 충족 또는 기존 리스크 감소에 해당하며, "
            "신규 기능·API 변경·아키텍처 경계 침범·범위 외 파일 수정 없음"
        )

    # REJECT_SCOPE_CREEP: 긍정 조건 없음 (수용 기준도 아니고 리스크 감소도 아님)
    if not positive:
        return REJECT_SCOPE_CREEP, (
            "수용 기준을 충족하지 않고 기존 리스크를 감소시키지도 않음. "
            "범위 초과 수리로 거부됨"
        )

    # NEEDS_USER_APPROVAL: 긍정 조건 충족하지만 creep 지표 하나 이상 true
    creep_details: list[str] = []
    if adds_new_capability:
        creep_details.append("신규 기능 추가")
    if changes_user_visible_behavior:
        creep_details.append("사용자 가시적 동작 변경")
    if changes_public_api_or_schema:
        creep_details.append("공개 API·스키마 변경")
    if changes_architecture_boundary:
        creep_details.append("아키텍처 경계 변경")
    if touches_files_outside_directive_scope:
        creep_details.append("디렉티브 범위 외 파일 수정")

    reason = f"긍정 조건 충족하나 다음 항목으로 사용자 승인 필요: {', '.join(creep_details)}"
    return NEEDS_USER_APPROVAL, reason


def build_scope_guard_decision(args: argparse.Namespace, decision: str, reason: str) -> dict:
    """ScopeGuardDecision JSON 객체를 구성한다."""
    return {
        "scope_guard_id": f"sg-{uuid.uuid4()}",
        "repair_id": args.repair_id,
        "finding_id": args.finding_id,
        "changes_user_visible_behavior": args.changes_user_visible_behavior,
        "adds_new_capability": args.adds_new_capability,
        "changes_public_api_or_schema": args.changes_public_api_or_schema,
        "changes_architecture_boundary": args.changes_architecture_boundary,
        "touches_files_outside_directive_scope": args.touches_files_outside_directive_scope,
        "required_to_satisfy_acceptance_criteria": args.required_to_satisfy_acceptance_criteria,
        "reduces_existing_risk_without_new_behavior": args.reduces_existing_risk_without_new_behavior,
        "decision": decision,
        "reason": reason,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def parse_args() -> argparse.Namespace:
    """CLI 인자를 파싱한다."""
    parser = argparse.ArgumentParser(
        description="제안된 수리의 범위를 7개 부울 술어로 분류한다.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "분류 결과:\n"
            "  in_scope_refinement  — 범위 내 정제 (즉시 진행 가능)\n"
            "  reject_scope_creep   — 범위 초과 거부\n"
            "  needs_user_approval  — 사용자 승인 필요\n"
        ),
    )
    parser.add_argument("--repair-id", required=True, help="수리 식별자")
    parser.add_argument("--finding-id", required=True, help="연결된 발견 사항 ID")
    parser.add_argument("--changes-user-visible-behavior", action="store_true", default=False,
                        help="사용자 가시적 동작이 변경되는가")
    parser.add_argument("--adds-new-capability", action="store_true", default=False,
                        help="신규 기능·역할을 추가하는가")
    parser.add_argument("--changes-public-api-or-schema", action="store_true", default=False,
                        help="공개 API 또는 DB 스키마를 변경하는가")
    parser.add_argument("--changes-architecture-boundary", action="store_true", default=False,
                        help="아키텍처 경계(모듈·레이어)를 변경하는가")
    parser.add_argument("--touches-files-outside-directive-scope", action="store_true", default=False,
                        help="디렉티브 범위 외 파일을 수정하는가")
    parser.add_argument("--required-to-satisfy-acceptance-criteria", action="store_true", default=False,
                        help="수용 기준 충족에 필수인가")
    parser.add_argument("--reduces-existing-risk-without-new-behavior", action="store_true", default=False,
                        help="신규 동작 없이 기존 리스크만 감소시키는가")
    parser.add_argument("--reason", required=True, help="범위 판단 이유 (사람이 제공)")
    return parser.parse_args()


def main() -> None:
    """엔트리포인트."""
    args = parse_args()

    decision_val, reason_val = classify_scope(
        required_to_satisfy_acceptance_criteria=args.required_to_satisfy_acceptance_criteria,
        reduces_existing_risk_without_new_behavior=args.reduces_existing_risk_without_new_behavior,
        adds_new_capability=args.adds_new_capability,
        changes_public_api_or_schema=args.changes_public_api_or_schema,
        changes_architecture_boundary=args.changes_architecture_boundary,
        touches_files_outside_directive_scope=args.touches_files_outside_directive_scope,
        changes_user_visible_behavior=args.changes_user_visible_behavior,
    )

    decision = build_scope_guard_decision(args, decision_val, reason_val)

    SCOPE_GUARD_DIR.mkdir(parents=True, exist_ok=True)
    out_path = SCOPE_GUARD_DIR / f"{args.repair_id}.json"
    out_path.write_text(json.dumps(decision, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(decision, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
