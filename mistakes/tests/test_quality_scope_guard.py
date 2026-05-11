"""범위 보호기 테스트 — 7-부울 술어 분류 로직과 출력 구조를 검증한다."""
from __future__ import annotations

import argparse

import pytest

import scope_guard as sg


class TestClassifyScope:
    """classify_scope 함수의 분류 결과를 테스트한다."""

    # ── 테스트 13: 범위 내 정제 분류 ──
    def test_in_scope_refinement_classification(self) -> None:
        """required_to_satisfy=True + 모든 creep 지표 False → in_scope_refinement."""
        decision, reason = sg.classify_scope(
            required_to_satisfy_acceptance_criteria=True,
            reduces_existing_risk_without_new_behavior=False,
            adds_new_capability=False,
            changes_public_api_or_schema=False,
            changes_architecture_boundary=False,
            touches_files_outside_directive_scope=False,
            changes_user_visible_behavior=False,
        )
        assert decision == sg.IN_SCOPE_REFINEMENT

    # ── 테스트 14: 긍정 조건 없으면 범위 초과 거부 ──
    def test_reject_scope_creep_no_positive(self) -> None:
        """두 긍정 지표 모두 False → reject_scope_creep."""
        decision, reason = sg.classify_scope(
            required_to_satisfy_acceptance_criteria=False,
            reduces_existing_risk_without_new_behavior=False,
            adds_new_capability=True,
            changes_public_api_or_schema=False,
            changes_architecture_boundary=False,
            touches_files_outside_directive_scope=False,
            changes_user_visible_behavior=False,
        )
        assert decision == sg.REJECT_SCOPE_CREEP

    # ── 테스트 15: 긍정 + creep → 사용자 승인 필요 ──
    def test_needs_user_approval_with_creep(self) -> None:
        """required_to_satisfy=True + adds_new_capability=True → needs_user_approval."""
        decision, reason = sg.classify_scope(
            required_to_satisfy_acceptance_criteria=True,
            reduces_existing_risk_without_new_behavior=False,
            adds_new_capability=True,
            changes_public_api_or_schema=False,
            changes_architecture_boundary=False,
            touches_files_outside_directive_scope=False,
            changes_user_visible_behavior=False,
        )
        assert decision == sg.NEEDS_USER_APPROVAL


class TestScopeGuardOutput:
    """build_scope_guard_decision 출력 구조를 검증한다."""

    # ── 테스트 16: 출력에 중첩 'predicates' 키가 없어야 한다 ──
    def test_scope_guard_output_has_no_nested_predicates(self) -> None:
        """출력 딕셔너리의 키가 플랫해야 하며, 'predicates' 같은 중첩 키가 없어야 한다."""
        args = argparse.Namespace(
            repair_id="rp-test-001",
            finding_id="qf-test-001",
            changes_user_visible_behavior=False,
            adds_new_capability=False,
            changes_public_api_or_schema=False,
            changes_architecture_boundary=False,
            touches_files_outside_directive_scope=False,
            required_to_satisfy_acceptance_criteria=True,
            reduces_existing_risk_without_new_behavior=False,
        )
        result = sg.build_scope_guard_decision(
            args,
            decision="in_scope_refinement",
            reason="테스트용 이유",
        )
        # 'predicates'라는 중첩 키가 존재하지 않아야 한다
        assert "predicates" not in result
        # 7개 부울 술어가 최상위 키로 직접 존재해야 한다
        predicate_keys = [
            "changes_user_visible_behavior",
            "adds_new_capability",
            "changes_public_api_or_schema",
            "changes_architecture_boundary",
            "touches_files_outside_directive_scope",
            "required_to_satisfy_acceptance_criteria",
            "reduces_existing_risk_without_new_behavior",
        ]
        for key in predicate_keys:
            assert key in result, f"최상위 키에 '{key}'가 누락됨"
