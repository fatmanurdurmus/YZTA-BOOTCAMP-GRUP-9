import pytest

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


def test_agent_graph_trigger_self_correction_loop(build_demo_calculation_request):
    """
    Tests that the LangGraph workflow triggers autonomous self-correction
    when the critic initially rejects the output, running up to max_retries.
    """
    calculation_request = build_demo_calculation_request

    # Valid Pydantic request mapped using the predefined fixture setup
    request = AgentRunRequest(
        thread_id="test-loop-123",
        activity_data=calculation_request.activity_data,
        carbon_price_eur_per_tonne=calculation_request.carbon_price_eur_per_tonne,
        max_retries=2
    )

    # Run the graph workflow
    response = run_carbonpilot_graph(request)

    # Verify that the graph did not crash and managed state constraints
    assert response["thread_id"] == "test-loop-123"
    assert "messages" in response
    assert len(response["messages"]) > 0


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

    # time.monotonic mock'lanarak guardrail_fallback: timeout_exceeded senaryosu simüle ediliyor
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


def test_state_recovery_after_simulated_crash(
    build_demo_calculation_request, monkeypatch, require_checkpointer
):
    """
    CP-34: simulates a crash mid-graph (after retrieve_law_refs and
    calculate_emissions succeed, but before critic_review completes) and
    verifies the same thread_id can resume from the Postgres checkpoint
    instead of starting over.

    Uses require_checkpointer so this FAILS (not silently passes/skips)
    if Docker Postgres isn't running -- see tests/conftest.py.
    """
    checkpointer = require_checkpointer

    calculation_request = build_demo_calculation_request
    thread_id = "thread-cp34-recovery"
    config = {"configurable": {"thread_id": thread_id}}

    def boom(calculation, law_references):
        raise RuntimeError("simulated crash for CP-34")

    monkeypatch.setattr(graph_module, "audit_calculation", boom)

    graph = graph_module.build_carbonpilot_graph()
    request = AgentRunRequest(
        thread_id=thread_id,
        activity_data=calculation_request.activity_data,
        carbon_price_eur_per_tonne=calculation_request.carbon_price_eur_per_tonne,
    )

    with pytest.raises(RuntimeError):
        graph.invoke(
            {
                "activity_payload": request.model_dump(mode="json"),
                "max_retries": request.max_retries,
                "retries": 0,
                "messages": [],
            },
            config=config,
        )

    # Proof the crash didn't wipe out earlier progress: a checkpoint for
    # this thread must already exist in Postgres.
    saved = checkpointer.get_tuple(config)
    assert saved is not None, "no checkpoint was persisted before the simulated crash"

    # "Restart the process": undo the crash, resume the SAME thread_id
    # with no new input. LangGraph should continue from the last good
    # checkpoint (retrieve_law_refs + calculate_emissions already done)
    # rather than recomputing everything from scratch.
    monkeypatch.undo()
    result = graph.invoke(None, config=config)

    assert result["critic_passed"] is True
    assert result["thread_id"] == thread_id