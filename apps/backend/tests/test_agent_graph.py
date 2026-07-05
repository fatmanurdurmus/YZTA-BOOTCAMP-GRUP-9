from carbonpilot.agents import graph as graph_module
from carbonpilot.agents.graph import run_carbonpilot_graph
from carbonpilot.schemas.agent import AgentRunRequest


def test_agent_graph_runs_with_structured_input(build_demo_calculation_request):
    calculation_request = build_demo_calculation_request

    response = run_carbonpilot_graph(
        AgentRunRequest(
            thread_id="thread-test-001",
            activity_data=calculation_request.activity_data,
            carbon_price_eur_per_tonne=calculation_request.carbon_price_eur_per_tonne,
        )
    )

    assert response["thread_id"] == "thread-test-001"
    assert response["critic_passed"] is True
    assert response["calculation"].total_tco2e == 45.25
    assert response["law_reference_count"] >= 1


def test_fallback_after_max_retries_when_critic_never_passes(
    build_demo_calculation_request, monkeypatch
):
    calculation_request = build_demo_calculation_request

    def always_fail(calculation, law_references):
        return False, ["forced_failure_for_test"]

    monkeypatch.setattr(graph_module, "audit_calculation", always_fail)

    response = run_carbonpilot_graph(
        AgentRunRequest(
            thread_id="thread-test-002",
            activity_data=calculation_request.activity_data,
            carbon_price_eur_per_tonne=calculation_request.carbon_price_eur_per_tonne,
            max_retries=1,
            timeout_seconds=30,
        )
    )

    assert response["status"] == "fallback"
    assert response["critic_passed"] is False
    assert any("guardrail_fallback" in message for message in response["messages"])


def test_timeout_triggers_fallback(build_demo_calculation_request, monkeypatch):
    calculation_request = build_demo_calculation_request

    def always_fail(calculation, law_references):
        return False, ["forced_failure_for_test"]

    monkeypatch.setattr(graph_module, "audit_calculation", always_fail)

    fake_clock = {"value": 0.0}

    def fake_monotonic():
        fake_clock["value"] += 10.0
        return fake_clock["value"]

    monkeypatch.setattr(graph_module.time, "monotonic", fake_monotonic)

    response = run_carbonpilot_graph(
        AgentRunRequest(
            thread_id="thread-test-003",
            activity_data=calculation_request.activity_data,
            carbon_price_eur_per_tonne=calculation_request.carbon_price_eur_per_tonne,
            max_retries=3,
            timeout_seconds=5,
        )
    )

    assert response["status"] == "fallback"
    assert any("timeout_exceeded" in message for message in response["messages"])