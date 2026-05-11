"""품질 발견 사항 기록기 테스트 — 증거 유효성 검사 로직을 검증한다."""
from __future__ import annotations

import pytest

import record_quality_finding as rqf


class TestEvidenceValidation:
    """validate_evidence 함수의 증거 검증 규칙을 테스트한다."""

    # ── 테스트 7: 20자 미만 증거는 거부되어야 한다 ──
    def test_evidence_too_short_rejected(self) -> None:
        """증거가 20자 미만이면 길이 위반 메시지를 반환해야 한다."""
        short_evidence = "짧은 증거"  # 4글자
        violations = rqf.validate_evidence(
            evidence=short_evidence,
            confidence_basis="code_structure_analysis",
            file_path="src/main.py",
            line_start=1,
            line_end=10,
        )
        assert len(violations) >= 1
        # 길이 관련 위반 메시지가 포함되어야 함
        assert any("짧습니다" in v or "20자" in v for v in violations)

    # ── 테스트 8: 모호한 표현이 포함된 증거는 거부되어야 한다 ──
    def test_vague_evidence_rejected(self) -> None:
        """'것 같다' 또는 'probably' 같은 모호한 표현이 있으면 거부해야 한다."""
        # '것 같다' 포함 케이스
        vague_kr = "이 함수는 성능 문제가 있는 것 같다. 루프가 비효율적으로 보인다."
        violations_kr = rqf.validate_evidence(
            evidence=vague_kr,
            confidence_basis="code_structure_analysis",
            file_path="src/main.py",
            line_start=1,
            line_end=20,
        )
        assert any("모호한 표현" in v for v in violations_kr)

        # 'probably' 포함 케이스
        vague_en = "This function probably has a memory leak due to unclosed resources"
        violations_en = rqf.validate_evidence(
            evidence=vague_en,
            confidence_basis="code_structure_analysis",
            file_path="src/main.py",
            line_start=1,
            line_end=20,
        )
        assert any("모호한 표현" in v for v in violations_en)

    # ── 테스트 9: 유효한 증거는 위반 없이 수용되어야 한다 ──
    def test_valid_evidence_accepted(self) -> None:
        """20자 이상의 객관적 증거와 유효한 confidence_basis는 위반 0건이어야 한다."""
        valid_evidence = (
            "함수 process_data()에서 O(n^2) 중첩 루프가 발견됨. "
            "입력 크기 10,000일 때 실행 시간 12.5초 측정."
        )
        violations = rqf.validate_evidence(
            evidence=valid_evidence,
            confidence_basis="measured_metric",
            file_path="src/processor.py",
            line_start=45,
            line_end=67,
        )
        assert violations == []
