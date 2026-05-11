#!/usr/bin/env python3
"""피드백 메모리 파일을 실수 방지 패턴 후보로 변환한다.

~/.claude/projects/*/memory/feedback_*.md 파일을 스캔하여
registry/candidates/에 JSON 파일로 변환한다.
원본 메모리 파일은 변경하지 않는다.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

# 기본 경로
CLAUDE_DIR = Path.home() / ".claude"
MISTAKES_ROOT = CLAUDE_DIR / "mistakes"
CANDIDATES_DIR = MISTAKES_ROOT / "registry" / "candidates"
REPORTS_DIR = MISTAKES_ROOT / "reports"

# 카테고리 매핑 — 키워드 → 분류
CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "scope_control": ["workaround", "우회", "bypass"],
    "verification": ["verification", "검증", "validate"],
    "runtime_resource": ["pytest", "resource", "자원", "zombie"],
    "architecture": ["skeleton", "design", "설계", "architecture"],
    "data_integrity": ["data", "integrity", "무결성"],
    "security": ["security", "보안", "credential"],
    "performance": ["performance", "성능", "optimization"],
    "ux_consistency": ["ux", "ui", "consistency", "background"],
    "delegation": ["delegation", "위임", "agent"],
}

# 기본 카테고리
DEFAULT_CATEGORY = "code_quality"

TODAY = date.today().isoformat()


def detect_category(name: str, body: str) -> str:
    """파일 이름과 본문에서 카테고리를 추론한다."""
    combined = (name + " " + body).lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in combined:
                return category
    return DEFAULT_CATEGORY


def sanitize_id(name: str) -> str:
    """파일 이름을 ID에 사용할 수 있는 문자열로 변환한다."""
    # feedback_ 접두사와 .md 확장자 제거
    slug = name.replace("feedback_", "").replace(".md", "")
    # 영숫자, 밑줄, 하이픈만 유지
    slug = re.sub(r"[^a-zA-Z0-9_\-]", "_", slug)
    return slug.strip("_").lower()


def parse_memory_file(path: Path) -> dict:
    """메모리 파일의 frontmatter와 본문을 파싱한다."""
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()

    frontmatter: dict[str, str] = {}
    body_start = 0

    # YAML frontmatter 파싱 (--- 블록)
    if lines and lines[0].strip() == "---":
        for i, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                body_start = i + 1
                break
            # 단순 key: value 파싱
            if ":" in line:
                key, _, value = line.partition(":")
                frontmatter[key.strip()] = value.strip()

    body = "\n".join(lines[body_start:]).strip()

    return {
        "name": frontmatter.get("name", path.stem),
        "description": frontmatter.get("description", ""),
        "type": frontmatter.get("type", ""),
        "body": body,
    }


def create_candidate(parsed: dict, category: str, source_path: Path) -> dict:
    """파싱된 메모리 데이터를 후보 패턴 JSON으로 변환한다."""
    slug = sanitize_id(source_path.stem)
    pid = f"{category}.{slug}"
    body = parsed["body"][:500] if parsed["body"] else "내용 없음"
    desc = parsed["description"] or parsed["name"]
    empty_stats = {"occurrences_30d": 0, "distinct_sessions_30d": 0, "last_seen": None,
                   "false_positive_rate": None, "escape_rate": None, "prevented_count": 0}
    return {
        "id": pid, "category": category, "severity": "P2", "status": "candidate",
        "title": desc, "failure_mode": body,
        "detection": {"surfaces": [], "signals": [], "signal_type": "pending_review",
                      "precision": "unknown", "cost": "unknown"},
        "prevention": {"action": "observe",
                       "message": "imported from feedback memory — needs curation"},
        "solution": {"canonical_fix": body, "verification": []},
        "stats": empty_stats,
        "promotion": {"state": "candidate", "target": "pending_review",
                      "reason": "자동 import — 큐레이션 팀 리뷰 필요"},
        "provenance": {"original_memory": str(source_path.relative_to(CLAUDE_DIR)),
                       "created": TODAY, "last_modified": TODAY,
                       "created_by": "import_feedback_memories.py"},
    }


def find_feedback_files() -> list[Path]:
    """모든 피드백 메모리 파일을 검색한다."""
    files = []

    # 프로젝트별 메모리 디렉토리
    projects_dir = CLAUDE_DIR / "projects"
    if projects_dir.exists():
        for memory_dir in projects_dir.glob("*/memory"):
            files.extend(sorted(memory_dir.glob("feedback_*.md")))

    # 전역 메모리 디렉토리
    global_memory = CLAUDE_DIR / "memory"
    if global_memory.exists():
        files.extend(sorted(global_memory.glob("feedback_*.md")))

    return files


def generate_report(results: list[dict], dry_run: bool) -> str:
    """import 리포트를 생성한다."""
    mode = "dry-run (미적용)" if dry_run else "live"
    lines = [f"# Feedback Memory Import Report\n", f"실행: {TODAY} | 모드: {mode}\n"]
    if not results:
        return "\n".join(lines) + "\nimport 대상 없음\n"
    lines.append(f"총 {len(results)}개\n")
    lines.append("| 원본 | 패턴 ID | 카테고리 | 상태 |")
    lines.append("|---|---|---|---|")
    for r in results:
        lines.append(f"| {r['source']} | {r['pattern_id']} | {r['category']} | {r['status']} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    """메인 — 피드백 메모리 파일을 스캔하고 후보 패턴으로 변환한다."""
    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("=== DRY RUN 모드 (파일 생성 없음) ===\n")

    files = find_feedback_files()
    if not files:
        print("import 대상 피드백 메모리 파일 없음")
        return

    print(f"{len(files)}개 피드백 메모리 파일 발견\n")

    results = []
    CANDIDATES_DIR.mkdir(parents=True, exist_ok=True)
    for f in files:
        parsed = parse_memory_file(f)
        cat = detect_category(parsed["name"], parsed["body"])
        cand = create_candidate(parsed, cat, f)
        r = {"source": str(f.relative_to(CLAUDE_DIR)), "pattern_id": cand["id"],
             "category": cat, "status": "생성 예정" if dry_run else "생성 완료"}
        if not dry_run:
            out = CANDIDATES_DIR / f"{cand['id']}.json"
            if out.exists():
                r["status"] = "이미 존재 (건너뜀)"
            else:
                out.write_text(json.dumps(cand, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                print(f"  생성: {cand['id']}")
        else:
            print(f"  [DRY] {cand['id']} <- {f.name} ({cat})")
        results.append(r)
    report = generate_report(results, dry_run)
    if not dry_run:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        (REPORTS_DIR / "import-report.md").write_text(report, encoding="utf-8")
        print(f"\n리포트 저장: {REPORTS_DIR / 'import-report.md'}")
    else:
        print(f"\n{report}")


if __name__ == "__main__":
    main()
