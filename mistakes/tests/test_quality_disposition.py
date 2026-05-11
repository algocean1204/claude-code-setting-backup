"""발견 사항 처분 기록기 테스트 — P0/P1 보호, 이유 최소 길이, 재검증 플래그를 검증한다."""
from __future__ import annotations

import argparse

import pytest

import dispose_finding as df


# ── 공통 헬퍼: 가짜 발견 사항 생성 ──
def _make_finding(severity: str = "P0", proposed_repair: str = "") -> dict:
    """테스트용 발견 사항 딕셔너리를 생성한다."""
    return {
        "finding_id": "qf-test-001",
        "quality_directive_id": "qd-test-001",
        "dimension": "robustness",
        "severity": severity,
        "file_path": "src/core.py",
        "line_start": 10,
        "line_end": 25,
        "evidence": "NULL 포인터 역참조가 발생할 수 있는 분기가 존재함 (정적 분석 결과)",
        "impact": "런타임 크래시 유발 가능",
        "proposed_repair": proposed_repair,
        "confidence_basis": "tool_output",
        "auto_repair_candidate": False,
        "created_by": "quality-judge",
    }


class TestDispositionValidation:
    """validate_disposition 함수의 처분 규칙을 테스트한다."""

    # ── 테스트 10: P0 dismiss 시 증거 없으면 거부 ──
    def test_p0_dismiss_without_evidence_rejected(self) -> None:
        """P0 발견을 dismiss할 때 evidence가 비어 있으면 위반을 반환해야 한다."""
        finding = _make_finding(severity="P0")
        violations = df.validate_disposition(
            finding=finding,
            disposition="dismissed",
            evidence="",
            reason="충분히 검토 후 안전한 것으로 판단됨",
        )
        assert len(violations) >= 1
        assert any("P0/P1" in v and "evidence" in v for v in violations)

    # ── 테스트 11: 처분 이유가 10자 미만이면 거부 ──
    def test_disposition_reason_too_short_rejected(self) -> None:
        """처분 이유(reason)가 10자 미만이면 위반을 반환해야 한다."""
        finding = _make_finding(severity="P2")
        violations = df.validate_disposition(
            finding=finding,
            disposition="upheld",
            evidence="상세한 증거",
            reason="짧음",  # 2자 — 10자 미만
        )
        assert len(violations) >= 1
        assert any("처분 이유" in v or "10자" in v for v in violations)

    # ── 테스트 12: upheld + 수리에 '수정' 키워드 → 재검증 필요 ──
    def test_upheld_with_repair_keywords_sets_reverification(self) -> None:
        """upheld 처분이고 proposed_repair에 '수정'이 포함되면 재검증 플래그가 True여야 한다."""
        finding = _make_finding(
            severity="P1",
            proposed_repair="NULL 체크를 추가하고 분기를 수정해야 합니다",
        )
        args = argparse.Namespace(
            finding_id="qf-test-001",
            disposition="upheld",
            reason="정적 분석 결과 확인됨. 수리가 필요한 것으로 판정함.",
            evidence="도구 출력에서 NULL 역참조 경로 확인",
            decided_by="quality-judge",
            requires_reverification=False,
        )
        result = df.build_disposition(args, finding)
        assert result["requires_phase_3_5_reverification"] is True
