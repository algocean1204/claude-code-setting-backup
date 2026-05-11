"""QualityDirective 생성기 테스트 — 핵심 차원, 리스크 티어 분류, 루브릭 참조 검증."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from unittest.mock import patch

import pytest

import create_quality_directive as cqd


# ── 테스트 1: 핵심 차원 목록이 스키마와 일치하는지 확인 ──
class TestCoreDimensions:
    """핵심 품질 차원 상수를 검증한다."""

    def test_core_dimensions_match_schema(self) -> None:
        """CORE_DIMENSIONS가 정확히 5개 핵심 차원을 포함해야 한다."""
        expected = [
            "requirement_fidelity",
            "maintainability",
            "robustness",
            "security_safety",
            "architecture_fit",
        ]
        assert cqd.CORE_DIMENSIONS == expected


# ── 테스트 2~5: 리스크 티어별 차원 선택 ──
class TestSelectDimensions:
    """리스크 티어와 태스크 프로필에 따른 차원 선택 로직을 검증한다."""

    def test_risk_tier_medium_selects_core_only(self) -> None:
        """medium 티어는 핵심 차원만 반환하고 조건부 차원은 비어 있어야 한다."""
        core, conditional = cqd.select_dimensions("medium", "일반 백엔드 작업")
        assert core == cqd.CORE_DIMENSIONS
        assert conditional == []

    def test_risk_tier_high_detects_conditional(self) -> None:
        """high 티어에서 'ui frontend test' 프로필은 핵심 + 관련 조건부 차원을 반환해야 한다."""
        core, conditional = cqd.select_dimensions("high", "ui frontend test")
        assert core == cqd.CORE_DIMENSIONS
        # 'ui'→accessibility, user_experience / 'test'→test_quality
        assert "test_quality" in conditional
        assert "accessibility" in conditional
        assert "user_experience" in conditional

    def test_risk_tier_low_returns_empty(self) -> None:
        """low 티어는 품질 루프를 생략하므로 빈 목록 쌍을 반환해야 한다."""
        core, conditional = cqd.select_dimensions("low", "사소한 오타 수정")
        assert core == []
        assert conditional == []

    def test_risk_tier_critical_all_conditional(self) -> None:
        """critical 티어는 5개 조건부 차원 모두를 반환해야 한다."""
        core, conditional = cqd.select_dimensions("critical", "")
        assert core == cqd.CORE_DIMENSIONS
        expected_conditional = list(cqd.CONDITIONAL_DIMENSIONS.keys())
        assert sorted(conditional) == sorted(expected_conditional)
        assert len(conditional) == 5


# ── 테스트 6: 루브릭 참조가 실제 파일을 가리키는지 확인 ──
class TestRubricRefs:
    """RUBRIC_REFS의 모든 값이 실제 존재하는 루브릭 파일을 참조해야 한다."""

    def test_rubric_refs_point_to_existing_files(self) -> None:
        """루브릭 참조 경로가 registry/quality/ 하위에 실제로 존재해야 한다."""
        registry_base = Path.home() / ".claude" / "mistakes" / "registry" / "quality"
        for dimension, ref_path in cqd.RUBRIC_REFS.items():
            full_path = registry_base / ref_path
            assert full_path.exists(), (
                f"차원 '{dimension}'의 루브릭 참조 '{ref_path}'에 해당하는 "
                f"파일이 존재하지 않음: {full_path}"
            )


# ── 테스트 17: observe_only 기본값이 True인지 확인 ──
class TestObserveOnlyDefault:
    """QualityDirective 출력의 observe_only 기본값을 검증한다."""

    def test_observe_only_default_true(self) -> None:
        """build_directive가 observe_only=True를 기본으로 설정해야 한다."""
        args = argparse.Namespace(
            verification_directive_id="vd-test-001",
            task_id="task-test-001",
            risk_tier="medium",
            task_profile="일반 작업",
            acceptance_criteria=[],
            observe_only=True,
        )
        # git 호출을 회피하기 위해 changed_files를 직접 전달
        directive = cqd.build_directive(
            args,
            core_dims=cqd.CORE_DIMENSIONS,
            conditional_dims=[],
            changed_files=[],
        )
        assert directive["observe_only"] is True
