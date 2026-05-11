#!/usr/bin/env python3
"""활성 패턴을 컴파일된 규칙 파일로 변환한다.

active/ 디렉토리의 모든 패턴 JSON을 읽어
compiled/pretool/{surface}.jsonl과 compiled/prompt/context.jsonl로 출력한다.
결정론적: 동일 입력이면 동일 출력을 보장한다.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# 기본 경로
MISTAKES_ROOT = Path.home() / ".claude" / "mistakes"
ACTIVE_DIR = MISTAKES_ROOT / "registry" / "active"
PRETOOL_DIR = MISTAKES_ROOT / "registry" / "compiled" / "pretool"
PROMPT_DIR = MISTAKES_ROOT / "registry" / "compiled" / "prompt"

# 심각도 숫자 매핑
SEVERITY_RANK = {"P0": 0, "P1": 1, "P2": 2}

# pretool surface 목록
PRETOOL_SURFACES = frozenset(["bash", "edit", "write", "agent"])


def load_active_patterns() -> list[dict]:
    """active/ 디렉토리에서 모든 패턴 JSON을 로드한다."""
    if not ACTIVE_DIR.exists():
        return []

    patterns = []
    for f in sorted(ACTIVE_DIR.glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            patterns.append(data)
        except (json.JSONDecodeError, OSError) as e:
            print(f"경고: {f.name} 로드 실패 — {e}", file=sys.stderr)
            continue
    return patterns


def compile_pattern(pattern: dict) -> dict:
    """패턴을 컴파일된 규칙 형식으로 변환한다."""
    detection = pattern.get("detection", {})
    prevention = pattern.get("prevention", {})
    severity = pattern.get("severity", "P2")

    return {
        "pattern_id": pattern.get("id", "unknown"),
        "severity": severity,
        "severity_rank": SEVERITY_RANK.get(severity, 2),
        "action": prevention.get("action", "observe"),
        "message": prevention.get("message", ""),
        "scope": {
            "surfaces": detection.get("surfaces", []),
            "file_patterns": [],
            "phase": None,
        },
        "signals": detection.get("signals", []),
    }


def write_compiled_files(rules_by_surface: dict[str, list[dict]]) -> int:
    """surface별 컴파일된 규칙을 JSONL 파일로 기록한다."""
    total = 0

    # pretool surface 파일 — 항상 모든 surface 파일을 생성 (비어있더라도)
    PRETOOL_DIR.mkdir(parents=True, exist_ok=True)
    for surface in PRETOOL_SURFACES:
        output_file = PRETOOL_DIR / f"{surface}.jsonl"
        rules = rules_by_surface.get(surface, [])
        # 심각도 높은 순으로 정렬 (결정론적)
        rules.sort(key=lambda r: (r["severity_rank"], r["pattern_id"]))

        if rules:
            lines = [json.dumps(r, ensure_ascii=False) for r in rules]
            output_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        else:
            # 빈 파일로 초기화
            output_file.write_text("", encoding="utf-8")
        total += len(rules)

    # context surface 파일
    PROMPT_DIR.mkdir(parents=True, exist_ok=True)
    context_file = PROMPT_DIR / "context.jsonl"
    context_rules = rules_by_surface.get("context", [])
    context_rules.sort(key=lambda r: (r["severity_rank"], r["pattern_id"]))
    if context_rules:
        lines = [json.dumps(r, ensure_ascii=False) for r in context_rules]
        context_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    else:
        context_file.write_text("", encoding="utf-8")
    total += len(context_rules)

    return total


def main() -> None:
    """메인 — 활성 패턴을 읽어 컴파일된 규칙으로 출력한다."""
    patterns = load_active_patterns()

    # surface별 규칙 분류
    rules_by_surface: dict[str, list[dict]] = {}
    for pattern in patterns:
        rule = compile_pattern(pattern)
        surfaces = rule["scope"].get("surfaces", [])

        if not surfaces:
            # surface 미지정 — 모든 pretool surface에 추가
            for s in PRETOOL_SURFACES:
                rules_by_surface.setdefault(s, []).append(rule)
        else:
            for s in surfaces:
                rules_by_surface.setdefault(s, []).append(rule)

    total = write_compiled_files(rules_by_surface)
    print(f"컴파일 완료: {len(patterns)}개 패턴 → {total}개 규칙")


if __name__ == "__main__":
    main()
