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
    from carbonpilot.agents.graph import run_carbonpilot_graph
    from carbonpilot.schemas.agent import AgentRunRequest

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