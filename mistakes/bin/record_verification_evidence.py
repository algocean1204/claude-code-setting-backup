#!/usr/bin/env python3
"""검증 증거 기록기 — 발견 사항 분류 + 자동 수리 루프 상태 추적 (observe-only)."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

EVIDENCE_DIR = Path.home() / ".claude" / "mistakes" / "registry" / "evidence"
QUEUE_DIR = Path.home() / ".claude" / "mistakes" / "registry" / "queue" / "unresolved"

VALID_CHECK_TYPES = frozenset(["syntax", "test", "lint", "runtime", "manual", "integration"])
VALID_EXECUTORS = frozenset(["system", "model", "hybrid"])

# 키워드 → 분류 매핑 (우선순위 순)
_CLASSIFICATION_RULES: list[tuple[list[str], str]] = [
    (["hallucination", "incomprehensible", "이해불가", "환각"], "MODEL_LIMITATION"),
    (["credential", "permission denied", "service down", "connection refused",
      "인증", "서비스 다운"], "ENVIRONMENT_BLOCKED"),
    (["production data", "security boundary", "타팀", "운영 데이터",
      "보안 경계"], "UNSAFE_TO_FIX"),
    (["api change", "dependency version", "architecture", "breaking change",
      "의존성 버전", "아키텍처"], "NEEDS_USER_DECISION"),
    (["syntax error", "missing import", "lint", "type annotation",
      "문법 오류", "누락된 임포트", "타입 어노테이션"], "AUTO_FIXABLE"),
]


def hash_output(raw_output: str) -> str:
    """원문 출력의 SHA256 해시를 생성한다."""
    return hashlib.sha256(raw_output.encode("utf-8")).hexdigest()


def classify_finding(description: str) -> str:
    """발견 사항을 5가지 분류 중 하나로 분류한다."""
    lower = description.lower()
    for keywords, cls in _CLASSIFICATION_RULES:
        if any(kw in lower for kw in keywords):
            return cls
    return "AUTO_FIXABLE"


def _assign_severity(description: str) -> str:
    """키워드 기반 심각도 결정: error/exception/traceback→P0, warning→P1, fail→P2."""
    lower = description.lower()
    if any(kw in lower for kw in ("error", "exception", "traceback", "오류")):
        return "P0"
    if any(kw in lower for kw in ("warning", "경고")):
        return "P1"
    if any(kw in lower for kw in ("fail", "실패")):
        return "P2"
    return "P1"


def parse_findings(raw_output: str, passed: bool) -> list[dict]:
    """원문 출력에서 오류·경고 행을 발견 사항으로 추출한다."""
    if passed:
        return []
    findings: list[dict] = []
    markers = ["error", "warning", "fail", "오류", "경고", "실패", "exception", "traceback"]
    for line in raw_output.splitlines():
        line = line.strip()
        if not line:
            continue
        if any(m in line.lower() for m in markers):
            findings.append({
                "finding_id": str(uuid.uuid4())[:8],
                "description": line[:300],
                "severity": _assign_severity(line),
                "classification": classify_finding(line),
            })
    return findings


def validate_evidence(evidence: dict) -> list[str]:
    """증거의 유효성을 검증한다. 오류 문자열 목록을 반환한다."""
    errors: list[str] = []
    for field in ("directive_id", "check_id", "check_type", "executor", "raw_output"):
        if not evidence.get(field):
            errors.append(f"필수 필드 누락 또는 빈 값: {field}")
    if evidence.get("check_type") and evidence["check_type"] not in VALID_CHECK_TYPES:
        errors.append(f"유효하지 않은 check_type: {evidence['check_type']}")
    if evidence.get("executor") and evidence["executor"] not in VALID_EXECUTORS:
        errors.append(f"유효하지 않은 executor: {evidence['executor']}")
    if not evidence.get("raw_output", "").strip() and evidence.get("pass"):
        errors.append("raw_output 없이 pass=True는 수상함 — 증거 제공 필요")
    return errors


def check_repair_history(directive_id: str, finding_id: str) -> bool:
    """동일 발견 사항의 수리 이력을 확인한다. 2회 이상이면 True(BLOCKED)."""
    queue_file = QUEUE_DIR / f"{directive_id}.json"
    if not queue_file.exists():
        return False
    try:
        data = json.loads(queue_file.read_text(encoding="utf-8"))
        return data.get("repair_counts", {}).get(finding_id, 0) >= 2
    except (json.JSONDecodeError, OSError):
        return False


def _update_queue(directive_id: str, findings: list[dict]) -> None:
    """미해결 큐에서 발견 사항별 수리 횟수를 증가시킨다."""
    if not findings:
        return
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    queue_file = QUEUE_DIR / f"{directive_id}.json"
    data: dict = {}
    if queue_file.exists():
        try:
            data = json.loads(queue_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            data = {}
    counts: dict[str, int] = data.get("repair_counts", {})
    items: list[dict] = data.get("unresolved", [])
    known_ids = {f["finding_id"] for f in items}
    for finding in findings:
        fid = finding["finding_id"]
        counts[fid] = counts.get(fid, 0) + 1
        status = "BLOCKED" if counts[fid] >= 2 else "OPEN"
        if fid not in known_ids:
            items.append({**finding, "repair_count": counts[fid], "status": status})
        else:
            for item in items:
                if item["finding_id"] == fid:
                    item.update({"repair_count": counts[fid], "status": status})
    data.update({"repair_counts": counts, "unresolved": items,
                 "updated_at": datetime.now(timezone.utc).isoformat()})
    queue_file.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8")


def record(evidence: dict) -> Path:
    """증거를 저장하고 미해결 큐를 갱신한다."""
    target_dir = EVIDENCE_DIR / evidence["directive_id"]
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / f"{evidence['evidence_id']}.json"
    path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _update_queue(evidence["directive_id"], evidence.get("findings", []))
    return path


def main() -> None:
    """CLI 진입점."""
    p = argparse.ArgumentParser(description="검증 증거를 기록하고 발견 사항을 분류한다.")
    p.add_argument("--directive-id", required=True)
    p.add_argument("--check-id", required=True)
    p.add_argument("--check-type", required=True, choices=sorted(VALID_CHECK_TYPES))
    p.add_argument("--executor", required=True, choices=sorted(VALID_EXECUTORS))
    p.add_argument("--raw-output", required=True)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--pass", dest="passed", action="store_true")
    g.add_argument("--fail", dest="passed", action="store_false")
    args = p.parse_args()

    now = datetime.now(timezone.utc).isoformat()
    evidence: dict = {
        "evidence_id": str(uuid.uuid4()), "directive_id": args.directive_id,
        "check_id": args.check_id, "check_type": args.check_type,
        "executor": args.executor, "raw_output": args.raw_output,
        "raw_output_hash": hash_output(args.raw_output), "pass": args.passed,
        "timestamp": now, "duration_ms": 0, "findings": [],
    }

    errors = validate_evidence(evidence)
    if errors:
        for err in errors:
            print(f"검증 오류: {err}", file=sys.stderr)
        sys.exit(1)

    findings = parse_findings(args.raw_output, args.passed)
    # 스키마 외 필드 오염 방지: status는 별도 딕셔너리로 추적한다
    finding_statuses: dict[str, str] = {}
    for f in findings:
        fid = f["finding_id"]
        finding_statuses[fid] = "BLOCKED" if check_repair_history(args.directive_id, fid) else "OPEN"
    evidence["findings"] = findings

    saved = record(evidence)
    blocked = sum(1 for s in finding_statuses.values() if s == "BLOCKED")
    print(json.dumps({
        "evidence_id": evidence["evidence_id"],
        "directive_id": args.directive_id,
        "check_id": args.check_id,
        "pass": args.passed,
        "finding_count": len(findings),
        "blocked_count": blocked,
        "saved_path": str(saved),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
