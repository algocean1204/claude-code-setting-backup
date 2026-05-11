#!/usr/bin/env python3
"""실수 방지 훅 러너 — PreToolUse 훅에서 호출됨.

stdin으로 도구 입력 JSON을 받아 컴파일된 규칙과 매칭한다.
현재 버전은 observe-only 모드: deny/ask 없이 항상 allow 반환.
200ms 이내 완료를 목표로 한다.
"""
from __future__ import annotations

import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# 기본 경로 설정
MISTAKES_ROOT = Path.home() / ".claude" / "mistakes"
COMPILED_DIR = MISTAKES_ROOT / "registry" / "compiled" / "pretool"
EVENTS_DIR = MISTAKES_ROOT / "registry" / "events"

# 심각도 정렬용 맵
SEVERITY_RANK = {"P0": 0, "P1": 1, "P2": 2}


def load_rules(surface: str) -> list[dict]:
    """지정된 surface의 컴파일된 규칙을 로드한다."""
    rule_file = COMPILED_DIR / f"{surface}.jsonl"
    if not rule_file.exists():
        return []

    rules = []
    content = rule_file.read_text(encoding="utf-8").strip()
    if not content:
        # 빈 파일 — 규칙 없음
        return []

    for line in content.splitlines():
        line = line.strip()
        if line:
            try:
                rules.append(json.loads(line))
            except json.JSONDecodeError:
                # 파싱 실패한 줄은 건너뜀
                continue
    return rules


def match_signal(signal: dict, tool_input: dict) -> bool:
    """단일 시그널 조건이 도구 입력과 매칭되는지 확인한다."""
    field = signal.get("field", "")
    operator = signal.get("operator", "")
    value = signal.get("value", "")

    # 중첩 필드 지원 (예: "command.args")
    target = tool_input
    for part in field.split("."):
        if isinstance(target, dict):
            target = target.get(part, "")
        else:
            target = ""
            break

    target_str = str(target) if target is not None else ""

    if operator == "contains":
        return value in target_str
    elif operator == "equals":
        return target_str == value
    elif operator == "starts_with":
        return target_str.startswith(value)
    elif operator == "ends_with":
        return target_str.endswith(value)
    elif operator == "not_contains":
        return value not in target_str
    elif operator == "matches" or operator == "regex":
        try:
            return bool(re.search(value, target_str))
        except re.error:
            return False
    return False


def match_rule(rule: dict, tool_input: dict) -> bool:
    """규칙의 모든 시그널이 도구 입력과 매칭되는지 확인한다 (AND 조건)."""
    signals = rule.get("signals", [])
    if not signals:
        return False
    return all(match_signal(s, tool_input) for s in signals)


def record_observation(rule: dict, tool_input: dict, surface: str) -> None:
    """매칭된 규칙을 이벤트로 기록한다."""
    EVENTS_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    event_file = EVENTS_DIR / f"{today}.jsonl"

    event = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "session_id": "unknown",
        "pattern_id": rule.get("pattern_id", "unknown"),
        "source": "hook_runner",
        "severity": rule.get("severity", "P2"),
        "surface": surface,
        "tool_input_summary": json.dumps(tool_input, ensure_ascii=False)[:200],
        "outcome": "observed",
    }

    with event_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def determine_surface(tool_input: dict) -> str:
    """도구 입력에서 surface 이름을 추출한다."""
    # tool_name 필드가 있으면 사용
    tool_name = tool_input.get("tool_name", "").lower()
    if tool_name in ("bash", "edit", "write", "agent"):
        return tool_name
    # 기본값: bash (가장 흔한 도구)
    if "command" in tool_input:
        return "bash"
    if "file_path" in tool_input and "old_string" in tool_input:
        return "edit"
    if "file_path" in tool_input and "content" in tool_input:
        return "write"
    return "bash"


def main() -> None:
    """메인 실행 — stdin에서 도구 입력을 읽고 판정을 반환한다."""
    start = time.monotonic()

    # stdin에서 도구 입력 읽기
    raw_input = sys.stdin.read().strip()
    if not raw_input:
        # 입력 없음 — 즉시 허용
        print(json.dumps({"decision": "allow"}))
        return

    try:
        tool_input = json.loads(raw_input)
    except json.JSONDecodeError:
        # JSON 파싱 실패 — 안전하게 허용
        print(json.dumps({"decision": "allow"}))
        return

    surface = determine_surface(tool_input)
    rules = load_rules(surface)

    # 매칭된 규칙 수집 (심각도 높은 순)
    matched = []
    for rule in rules:
        if match_rule(rule, tool_input):
            matched.append(rule)

    matched.sort(key=lambda r: SEVERITY_RANK.get(r.get("severity", "P2"), 2))

    # observe-only 모드: 매칭 결과와 관계없이 항상 allow
    for rule in matched:
        # 200ms 예산 확인 — 초과 시 기록 생략
        elapsed_ms = (time.monotonic() - start) * 1000
        if elapsed_ms > 180:
            break
        record_observation(rule, tool_input, surface)

    # 항상 allow 반환 (Phase 1은 observe-only)
    result = {"decision": "allow"}
    if matched:
        # 정보 제공용: 매칭된 패턴 목록 첨부
        result["observed_patterns"] = [r.get("pattern_id", "unknown") for r in matched]

    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
