#!/usr/bin/env python3
"""QualityDirective 생성기 — 리스크 티어·태스크 프로필 기반으로 품질 검사 차원을 선택한다."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

DIRECTIVES_DIR = Path.home() / ".claude" / "mistakes" / "registry" / "quality" / "directives"

# 5개 핵심 품질 차원
CORE_DIMENSIONS = [
    "requirement_fidelity",
    "maintainability",
    "robustness",
    "security_safety",
    "architecture_fit",
]

# 조건부 품질 차원 → 감지 키워드 매핑
CONDITIONAL_DIMENSIONS: dict[str, list[str]] = {
    "performance": ["performance", "hot path", "resource", "concurrent", "large"],
    "test_quality": ["test", "bug fix", "refactor", "behavior change"],
    "accessibility": ["ui", "tui", "desktop", "web", "frontend"],
    "user_experience": ["ui", "tui", "desktop", "cli", "flow", "ux"],
    "documentation": ["api", "deploy", "public", "user-facing", "breaking"],
}

# 차원 → 루브릭 참조 매핑
RUBRIC_REFS: dict[str, str] = {
    "requirement_fidelity": "rubrics/base.json",
    "maintainability": "rubrics/base.json",
    "robustness": "rubrics/base.json",
    "security_safety": "rubrics/base.json",
    "architecture_fit": "rubrics/base.json",
    "performance": "rubrics/performance.json",
    "test_quality": "rubrics/test_quality.json",
    "accessibility": "rubrics/accessibility.json",
    "user_experience": "rubrics/user_experience.json",
    "documentation": "rubrics/documentation.json",
}


def get_changed_files() -> list[str]:
    """git diff HEAD로 변경된 파일 목록을 가져온다. 에이전트 주장은 신뢰하지 않는다."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True, text=True, check=False,
        )
        staged = subprocess.run(
            ["git", "diff", "--name-only", "--cached"],
            capture_output=True, text=True, check=False,
        )
        files: list[str] = []
        for line in (result.stdout + staged.stdout).splitlines():
            line = line.strip()
            if line:
                files.append(line)
        return list(dict.fromkeys(files))  # 중복 제거 (순서 보존)
    except FileNotFoundError:
        return []  # git 없는 환경에서는 빈 목록 반환


def detect_conditional_dimensions(task_profile: str) -> list[str]:
    """태스크 프로필 문자열에서 조건부 차원을 감지한다."""
    lower = task_profile.lower()
    detected: list[str] = []
    for dim, keywords in CONDITIONAL_DIMENSIONS.items():
        if any(kw in lower for kw in keywords):
            detected.append(dim)
    return detected


def select_dimensions(risk_tier: str, task_profile: str) -> tuple[list[str], list[str]]:
    """리스크 티어와 태스크 프로필에 따라 품질 차원을 선택한다.

    반환: (핵심 차원 목록, 조건부 차원 목록)
    """
    if risk_tier == "low":
        return [], []  # low: 품질 루프 생략
    if risk_tier == "medium":
        return list(CORE_DIMENSIONS), []
    if risk_tier == "high":
        conditional = detect_conditional_dimensions(task_profile)
        return list(CORE_DIMENSIONS), conditional
    if risk_tier == "critical":
        # critical: 5 핵심 + 모든 조건부 차원 활성화
        all_conditional = list(CONDITIONAL_DIMENSIONS.keys())
        return list(CORE_DIMENSIONS), all_conditional
    return list(CORE_DIMENSIONS), []


def build_directive(
    args: argparse.Namespace,
    core_dims: list[str],
    conditional_dims: list[str],
    changed_files: list[str],
) -> dict:
    """QualityDirective JSON 객체를 구성한다."""
    quality_directive_id = f"qd-{uuid.uuid4()}"
    all_dims = core_dims + conditional_dims
    rubric_refs = [RUBRIC_REFS[d] for d in all_dims if d in RUBRIC_REFS]
    return {
        "quality_directive_id": quality_directive_id,
        "verification_directive_id": args.verification_directive_id,
        "task_id": args.task_id,
        "risk_tier": args.risk_tier,
        "task_profile": args.task_profile,
        "acceptance_criteria": args.acceptance_criteria or [],
        "changed_files": changed_files,
        "quality_dimensions": core_dims,
        "conditional_dimensions": conditional_dims,
        "rubric_refs": rubric_refs,
        "evidence_required": True,
        "observe_only": args.observe_only,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def parse_args() -> argparse.Namespace:
    """CLI 인자를 파싱한다."""
    parser = argparse.ArgumentParser(
        description="QualityDirective를 생성하고 레지스트리에 저장한다.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--verification-directive-id", required=True,
                        help="연결할 VerificationDirective ID")
    parser.add_argument("--task-id", required=True,
                        help="태스크 식별자")
    parser.add_argument("--risk-tier", choices=["low", "medium", "high", "critical"],
                        default="medium", help="리스크 티어 (기본: medium)")
    parser.add_argument("--task-profile", required=True,
                        help="태스크 유형 설명 문자열 (조건부 차원 감지에 사용)")
    parser.add_argument("--acceptance-criteria", nargs="*", default=[],
                        help="수용 기준 목록 (복수 가능)")
    parser.add_argument("--observe-only", action="store_true", default=True,
                        help="관측 전용 모드 (기본 활성화, Phase 3.6)")
    return parser.parse_args()


def main() -> None:
    """엔트리포인트."""
    args = parse_args()
    changed_files = get_changed_files()
    core_dims, conditional_dims = select_dimensions(args.risk_tier, args.task_profile)
    directive = build_directive(args, core_dims, conditional_dims, changed_files)

    DIRECTIVES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DIRECTIVES_DIR / f"{directive['quality_directive_id']}.json"
    out_path.write_text(json.dumps(directive, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(directive, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
