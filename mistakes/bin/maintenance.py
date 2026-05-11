#!/usr/bin/env python3
"""패턴 통계 갱신 및 유지보수 작업.

- 이벤트 로그에서 pattern_stats.json 갱신
- 60일 무발생 패턴 강등 후보 표시
- 90일 + 낮은 심각도 패턴 은퇴 제안
- 90일 이상 된 이벤트 로그 gzip 압축
"""
from __future__ import annotations

import gzip
import json
import shutil
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

# 기본 경로
MISTAKES_ROOT = Path.home() / ".claude" / "mistakes"
EVENTS_DIR = MISTAKES_ROOT / "registry" / "events"
ACTIVE_DIR = MISTAKES_ROOT / "registry" / "active"
STATS_FILE = MISTAKES_ROOT / "registry" / "stats" / "pattern_stats.json"

# 임계값 상수
DEMOTION_DAYS = 60   # 강등 후보 임계일
RETIREMENT_DAYS = 90  # 은퇴 제안 임계일
ROTATION_DAYS = 90    # 이벤트 로그 압축 임계일


def load_stats() -> dict:
    """현재 pattern_stats.json을 로드한다."""
    if not STATS_FILE.exists():
        return {}
    try:
        return json.loads(STATS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save_stats(stats: dict) -> None:
    """pattern_stats.json을 저장한다."""
    STATS_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATS_FILE.write_text(
        json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def collect_events_since(cutoff: datetime) -> list[dict]:
    """cutoff 이후의 모든 이벤트를 수집한다."""
    events = []
    if not EVENTS_DIR.exists():
        return events

    for f in sorted(EVENTS_DIR.glob("*.jsonl")):
        # 파일명에서 날짜 추출 (2026-05-11.jsonl)
        try:
            file_date = datetime.strptime(f.stem, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            continue

        if file_date < cutoff - timedelta(days=1):
            # 날짜 범위 밖 — 건너뜀
            continue

        content = f.read_text(encoding="utf-8").strip()
        if not content:
            continue

        for line in content.splitlines():
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return events


def update_stats() -> dict:
    """30일 이내 이벤트를 기반으로 통계를 갱신한다."""
    now = datetime.now(timezone.utc)
    cutoff_30d = now - timedelta(days=30)
    events = collect_events_since(cutoff_30d)

    stats: dict[str, dict] = {}

    # 패턴별 집계
    pattern_events: dict[str, list[dict]] = defaultdict(list)
    for ev in events:
        pid = ev.get("pattern_id", "unknown")
        pattern_events[pid].append(ev)

    for pid, evts in pattern_events.items():
        sessions = set(ev.get("session_id", "") for ev in evts)
        last_ts = max(ev.get("ts", "") for ev in evts)

        stats[pid] = {
            "occurrences_30d": len(evts),
            "distinct_sessions_30d": len(sessions),
            "last_seen": last_ts,
            "prevented_count": sum(
                1 for ev in evts if ev.get("outcome") in ("blocked", "warned")
            ),
            "escaped_count": sum(
                1 for ev in evts if ev.get("outcome") == "escaped"
            ),
        }

    return stats


def flag_demotion_candidates(stats: dict) -> list[str]:
    """60일 무발생 패턴을 강등 후보로 표시한다."""
    now = datetime.now(timezone.utc)
    candidates = []

    if not ACTIVE_DIR.exists():
        return candidates

    for f in sorted(ACTIVE_DIR.glob("*.json")):
        try:
            pattern = json.loads(f.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        pid = pattern.get("id", "")
        pattern_stat = stats.get(pid, {})
        last_seen_str = pattern_stat.get("last_seen")

        if last_seen_str:
            try:
                last_seen = datetime.fromisoformat(last_seen_str)
                days_since = (now - last_seen).days
            except ValueError:
                days_since = DEMOTION_DAYS + 1
        else:
            # 한 번도 발생하지 않음 — 강등 후보
            days_since = DEMOTION_DAYS + 1

        if days_since >= DEMOTION_DAYS:
            candidates.append(pid)
            severity = pattern.get("severity", "P2")
            # 90일 + P2 → 은퇴 제안
            if days_since >= RETIREMENT_DAYS and severity == "P2":
                print(f"은퇴 제안: {pid} ({days_since}일 무발생, P2)")
            else:
                print(f"강등 후보: {pid} ({days_since}일 무발생)")

    return candidates


def rotate_old_events() -> int:
    """90일 이상 된 이벤트 로그를 gzip 압축한다."""
    if not EVENTS_DIR.exists():
        return 0

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=ROTATION_DAYS)
    compressed = 0

    for f in sorted(EVENTS_DIR.glob("*.jsonl")):
        # 이미 압축된 파일은 건너뜀
        if f.suffix == ".gz":
            continue

        try:
            file_date = datetime.strptime(f.stem, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            continue

        if file_date < cutoff:
            gz_path = f.with_suffix(".jsonl.gz")
            with f.open("rb") as f_in, gzip.open(gz_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
            f.unlink()
            compressed += 1
            print(f"압축 완료: {f.name} → {gz_path.name}")

    return compressed


def main() -> None:
    """메인 — 통계 갱신, 강등 후보 표시, 이벤트 로테이션을 수행한다."""
    stats = update_stats()
    save_stats(stats)
    print(f"통계 갱신: {len(stats)}개 패턴")
    candidates = flag_demotion_candidates(stats)
    if not candidates:
        print("강등 후보 없음")
    compressed = rotate_old_events()
    if compressed:
        print(f"로테이션: {compressed}개 압축")

if __name__ == "__main__":
    main()
