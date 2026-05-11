#!/usr/bin/env python3
"""실수 이벤트 기록기 — 이벤트를 JSONL 파일에 추가한다.

인자 또는 stdin으로 이벤트 JSON을 받아 날짜별 JSONL 파일에 기록한다.
이벤트 스키마의 필수 필드를 기본 검증한다.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# 기본 경로
EVENTS_DIR = Path.home() / ".claude" / "mistakes" / "registry" / "events"

# 필수 필드 목록 (스키마 기반)
REQUIRED_FIELDS = frozenset(
    ["ts", "session_id", "pattern_id", "source", "severity", "surface", "outcome"]
)

# 유효 값 검증용 상수
VALID_SEVERITIES = frozenset(["P0", "P1", "P2"])
VALID_OUTCOMES = frozenset(["blocked", "warned", "observed", "escaped"])


def validate_event(event: dict) -> list[str]:
    """이벤트 딕셔너리의 필수 필드를 검증한다. 오류 목록을 반환한다."""
    errors = []

    # 필수 필드 존재 여부 확인
    missing = REQUIRED_FIELDS - set(event.keys())
    if missing:
        errors.append(f"필수 필드 누락: {', '.join(sorted(missing))}")

    # 열거형 값 검증
    severity = event.get("severity")
    if severity and severity not in VALID_SEVERITIES:
        errors.append(f"유효하지 않은 severity: {severity}")

    outcome = event.get("outcome")
    if outcome and outcome not in VALID_OUTCOMES:
        errors.append(f"유효하지 않은 outcome: {outcome}")

    return errors


def record(event: dict) -> Path:
    """이벤트를 날짜별 JSONL 파일에 기록하고 파일 경로를 반환한다."""
    EVENTS_DIR.mkdir(parents=True, exist_ok=True)

    # 타임스탬프에서 날짜 추출, 없으면 현재 UTC 날짜 사용
    ts = event.get("ts", "")
    try:
        date_str = ts[:10]  # "2026-05-11T..." → "2026-05-11"
        # 날짜 형식 검증
        datetime.strptime(date_str, "%Y-%m-%d")
    except (ValueError, IndexError):
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    event_file = EVENTS_DIR / f"{date_str}.jsonl"

    # JSONL 한 줄 추가
    with event_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    return event_file


def main() -> None:
    """메인 — 인자 또는 stdin에서 이벤트 JSON을 읽어 기록한다."""
    # 인자가 있으면 인자에서, 없으면 stdin에서 읽기
    if len(sys.argv) > 1:
        raw = " ".join(sys.argv[1:])
    else:
        raw = sys.stdin.read().strip()

    if not raw:
        print("오류: 이벤트 JSON이 제공되지 않음", file=sys.stderr)
        sys.exit(1)

    try:
        event = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"오류: JSON 파싱 실패 — {e}", file=sys.stderr)
        sys.exit(1)

    # 기본 검증
    errors = validate_event(event)
    if errors:
        for err in errors:
            print(f"검증 오류: {err}", file=sys.stderr)
        sys.exit(1)

    # 기록
    path = record(event)
    print(f"기록 완료: {path}")


if __name__ == "__main__":
    main()
