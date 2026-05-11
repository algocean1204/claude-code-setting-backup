#!/usr/bin/env python3
"""VerificationDirective JSON 생성기 — 파일 유형별 검증 체인을 DAG로 구성한다."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from shutil import which

DIRECTIVES_DIR = Path.home() / ".claude" / "mistakes" / "registry" / "directives"
DAG_ORDER = ["syntax", "lint", "test", "integration"]

# 확장자 → 검증 체인 원형 정의
_CHECKS: dict[str, list[dict]] = {
    ".py": [
        {"check_id": "py_syntax", "layer": "syntax", "tool": "py_compile",
         "command": "python3 -m py_compile {file}", "description": "Python 문법 검사"},
        {"check_id": "py_lint", "layer": "lint", "tool": "ruff",
         "command": "ruff check {file}", "description": "Python 린트 (ruff)"},
        {"check_id": "py_test", "layer": "test", "tool": "pytest",
         "command": "pytest {file}", "description": "Python 테스트"},
    ],
    ".rs": [
        {"check_id": "rs_syntax", "layer": "syntax", "tool": "cargo",
         "command": "cargo check", "description": "Rust 문법·타입 검사"},
        {"check_id": "rs_test", "layer": "test", "tool": "cargo",
         "command": "cargo test", "description": "Rust 테스트"},
    ],
    ".sh": [
        {"check_id": "sh_syntax", "layer": "syntax", "tool": "bash",
         "command": "bash -n {file}", "description": "셸 문법 검사"},
        {"check_id": "sh_lint", "layer": "lint", "tool": "shellcheck",
         "command": "shellcheck {file}", "description": "셸 린트 (shellcheck)"},
    ],
    ".json": [
        {"check_id": "json_syntax", "layer": "syntax", "tool": "json.tool",
         "command": "python3 -m json.tool {file}", "description": "JSON 문법 검사"},
    ],
    ".md": [
        {"check_id": "md_linecount", "layer": "syntax", "tool": "linecount",
         "command": "wc -l {file}", "description": "Markdown 줄 수 확인 (≤200 권장)"},
    ],
}


def detect_file_checks(files: list[str]) -> list[dict]:
    """파일 유형별 자동 검증 체인을 생성한다."""
    seen: set[str] = set()
    result: list[dict] = []
    for f in files:
        for proto in _CHECKS.get(Path(f).suffix.lower(), []):
            cid = proto["check_id"]
            if cid in seen:
                continue
            # 선택적 도구 가용성 필터
            if proto["tool"] in ("ruff", "shellcheck") and not which(proto["tool"]):
                continue
            seen.add(cid)
            result.append(dict(proto))
    return result


def get_changed_files() -> list[str]:
    """git diff HEAD에서 변경된 파일 목록을 추출한다."""
    try:
        r = subprocess.run(["git", "diff", "--name-only", "HEAD"],
                           capture_output=True, text=True, timeout=10)
        return [l.strip() for l in r.stdout.splitlines() if l.strip()] if r.returncode == 0 else []
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return []


def build_verifier_chain(checks: list[dict]) -> list[dict]:
    """검증 단계를 DAG로 구성한다 (syntax → lint → test → integration)."""
    layer_ids: dict[str, list[str]] = {lay: [] for lay in DAG_ORDER}
    for c in checks:
        lay = c.get("layer", "syntax")
        if lay in layer_ids:
            layer_ids[lay].append(c["check_id"])

    chain: list[dict] = []
    for c in checks:
        lay = c.get("layer", "syntax")
        idx = DAG_ORDER.index(lay) if lay in DAG_ORDER else 0
        deps: list[str] = []
        for prev in DAG_ORDER[:idx]:
            deps.extend(layer_ids.get(prev, []))
        chain.append({**c, "depends_on": deps})

    chain.sort(key=lambda c: (DAG_ORDER.index(c["layer"]) if c["layer"] in DAG_ORDER else 99,
                               c["check_id"]))
    return chain


def create_directive(goal: str, files: list[str], risk_tier: str) -> dict:
    """VerificationDirective JSON을 생성한다."""
    changed = get_changed_files()
    all_files = list(files) + [f for f in changed if f not in files]
    checks = detect_file_checks(all_files)
    return {
        "directive_id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "goal": goal,
        "risk_tier": risk_tier,
        "target_files": files,
        "changed_files_from_git": changed,
        "verifier_chain": build_verifier_chain(checks),
    }


def main() -> None:
    """CLI 진입점."""
    if len(sys.argv) < 2:
        print("사용법: create_verification_directive.py --goal GOAL [--files F1 F2...] "
              "[--risk-tier low|medium|high|critical]", file=sys.stderr)
        sys.exit(1)

    p = argparse.ArgumentParser(description="VerificationDirective JSON을 생성한다.")
    p.add_argument("--goal", required=True, help="검증 목표 요약")
    p.add_argument("--files", nargs="*", default=[], metavar="FILE")
    p.add_argument("--risk-tier", choices=["low", "medium", "high", "critical"],
                   default="medium")
    args = p.parse_args()

    directive = create_directive(args.goal, args.files, args.risk_tier)
    print(json.dumps(directive, ensure_ascii=False, indent=2))

    DIRECTIVES_DIR.mkdir(parents=True, exist_ok=True)
    out = DIRECTIVES_DIR / f"{directive['directive_id']}.json"
    out.write_text(json.dumps(directive, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"# 저장 완료: {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
