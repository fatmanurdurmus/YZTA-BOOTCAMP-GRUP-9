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
