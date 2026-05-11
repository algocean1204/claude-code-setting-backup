#!/usr/bin/env python3
"""발견 사항 처분 기록기 — upheld/dismissed/needs_user/deferred 중 하나로 결정한다."""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

FINDINGS_DIR = Path.home() / ".claude" / "mistakes" / "registry" / "quality" / "findings"
DISPOSITIONS_DIR = Path.home() / ".claude" / "mistakes" / "registry" / "quality" / "dispositions"

VALID_DISPOSITIONS = ["upheld", "dismissed", "needs_user", "deferred"]

# P0/P1 dismiss 시 evidence 최소 길이
P01_DISMISS_MIN_EVIDENCE_LEN = 10


def find_finding(finding_id: str) -> dict | None:
    """레지스트리에서 finding_id에 해당하는 발견 사항을 탐색한다."""
    if not FINDINGS_DIR.exists():
        return None
    for json_file in FINDINGS_DIR.rglob("*.json"):
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
            if data.get("finding_id") == finding_id:
                return data
        except (json.JSONDecodeError, OSError):
            continue
    return None


def validate_disposition(
    finding: dict,
    disposition: str,
    evidence: str,
    reason: str,
) -> list[str]:
    """처분 결정 유효성을 검사한다. 위반 사항 목록을 반환한다."""
    violations: list[str] = []
    severity = finding.get("severity", "")

    # disposition_reason 최소 길이 검사 (스키마 minLength: 10)
    if len(reason.strip()) < 10:
        violations.append(
            f"처분 이유(disposition_reason)가 너무 짧습니다 "
            f"(최소 10자, 현재: {len(reason.strip())}자)"
        )

    # P0/P1 dismiss 시 evidence 필수
    if disposition == "dismissed" and severity in ("P0", "P1"):
        if not evidence or len(evidence.strip()) < P01_DISMISS_MIN_EVIDENCE_LEN:
            violations.append(
                f"P0/P1 finding을 dismiss하려면 evidence 필수 "
                f"(최소 {P01_DISMISS_MIN_EVIDENCE_LEN}자, 현재: {len(evidence.strip())}자)"
            )
    return violations


def build_disposition(args: argparse.Namespace, finding: dict) -> dict:
    """FindingDisposition JSON 객체를 구성한다."""
    disposition_id = f"fd-{uuid.uuid4()}"

    # upheld이고 수리가 코드 변경을 수반하면 재검증 필요
    auto_requires_reverification = False
    if args.disposition == "upheld":
        proposed_repair = finding.get("proposed_repair", "")
        # 코드 변경을 암시하는 키워드가 있으면 재검증 플래그 설정
        change_keywords = ["수정", "변경", "추가", "삭제", "refactor", "fix", "change", "remove", "add"]
        if any(kw in proposed_repair.lower() for kw in change_keywords):
            auto_requires_reverification = True

    requires_reverification = args.requires_reverification or auto_requires_reverification

    return {
        "disposition_id": disposition_id,
        "finding_id": args.finding_id,
        "disposition": args.disposition,
        "disposition_reason": args.reason,
        "disposition_evidence": args.evidence,
        "decided_by": args.decided_by,
        "decided_at": datetime.now(timezone.utc).isoformat(),
        "requires_phase_3_5_reverification": requires_reverification,
    }


def parse_args() -> argparse.Namespace:
    """CLI 인자를 파싱한다."""
    parser = argparse.ArgumentParser(
        description="품질 발견 사항의 처분을 기록한다.",
    )
    parser.add_argument("--finding-id", required=True,
                        help="처분할 발견 사항 ID")
    parser.add_argument("--disposition", required=True, choices=VALID_DISPOSITIONS,
                        help="처분 결정 (upheld/dismissed/needs_user/deferred)")
    parser.add_argument("--reason", required=True,
                        help="처분 이유")
    parser.add_argument("--evidence", default="",
                        help="처분 근거 증거 (P0/P1 dismiss 시 필수, 최소 10자)")
    parser.add_argument("--decided-by", required=True,
                        help="결정자 식별자")
    parser.add_argument("--requires-reverification", action="store_true", default=False,
                        help="Phase 3.5 재검증 필요 여부 (upheld 시 자동 설정 가능)")
    return parser.parse_args()


def main() -> None:
    """엔트리포인트."""
    args = parse_args()

    # 발견 사항 존재 확인
    finding = find_finding(args.finding_id)
    if finding is None:
        print(f"[오류] finding_id='{args.finding_id}'를 레지스트리에서 찾을 수 없습니다.", file=sys.stderr)
        sys.exit(1)

    # 처분 유효성 검사
    violations = validate_disposition(finding, args.disposition, args.evidence, args.reason)
    if violations:
        for v in violations:
            print(f"[거부] {v}", file=sys.stderr)
        sys.exit(1)

    disposition = build_disposition(args, finding)

    DISPOSITIONS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DISPOSITIONS_DIR / f"{args.finding_id}.json"
    out_path.write_text(json.dumps(disposition, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(disposition, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
