"""CP-39: Sprint 2 regression suite.

Sprint 2 added PostgreSQL persistence, LangGraph checkpointing, semantic and
episodic memory, and the optimization engine on top of Sprint 1's core.
These tests exist purely to prove that none of that additional wiring
changed the actual, deterministic outputs Sprint 1 shipped and froze:
the calculation engine's numbers and the agent graph's guardrail behaviour.
If any of these ever fail, something in Sprint 2+ silently altered
Sprint 1's frozen core — that is exactly the kind of regression this file
is meant to catch before it reaches the jury.
"""

from carbonpilot.agents import graph as graph_module
from carbonpilot.agents.graph import run_carbonpilot_graph
from carbonpilot.calculation.engine import calculate_emissions
from carbonpilot.schemas.agent import AgentRunRequest
from carbonpilot.schemas.common import EmissionScope

def test_calculation_engine_baseline_is_unchanged(build_demo_calculation_request):
    """The Sprint 1 demo fixture must still produce the exact same numbers
    it did at the end of Sprint 1, regardless of any Sprint 2 persistence
    or memory code added around it.
    """
    response = calculate_emissions(build_demo_calculation_request)
    totals = {summary.scope: summary.total_tco2e for summary in response.scope_summaries}
    
    assert totals[EmissionScope.scope_1] == 20.0
    assert totals[EmissionScope.scope_2] == 20.0
    assert totals[EmissionScope.scope_3] == 5.25
    assert response.total_tco2e == 45.25
    assert response.estimated_cbam_cost_eur == 3620.0

def test_agent_graph_still_completes_successfully_end_to_end(build_demo_calculation_request):
    """A full agent run on the Sprint 1 demo fixture must still complete
    and pass the critic on the first attempt, exactly as it did before
    checkpointing, memory, and optimization were layered on top.
    """
    calculation_request = build_demo_calculation_request
    response = run_carbonpilot_graph(
        AgentRunRequest(
            thread_id="thread-regression-001",
            activity_data=calculation_request.activity_data,
            carbon_price_eur_per_tonne=calculation_request.carbon_price_eur_per_tonne,
        )
    )
    
    assert response["status"] == "completed"
    assert response["critic_passed"] is True
    assert response["calculation"].total_tco2e == 45.25

def test_guardrail_fallback_still_triggers_after_max_retries(
    build_demo_calculation_request, monkeypatch
):
    """The CP-20 loop-limit/fallback guardrail must still engage correctly
    when the critic never passes — this must keep working even though the
    graph now also carries a Postgres checkpointer and episodic/semantic
    memory hooks around it.
    """
    calculation_request = build_demo_calculation_request
    
    def always_fail(calculation, law_references):
        return False, ["forced_failure_for_regression_test"]
        
    monkeypatch.setattr(graph_module, "audit_calculation", always_fail)
    
    response = run_carbonpilot_graph(
        AgentRunRequest(
            thread_id="thread-regression-002",
            activity_data=calculation_request.activity_data,
            carbon_price_eur_per_tonne=calculation_request.carbon_price_eur_per_tonne,
            max_retries=1,
            timeout_seconds=30,
        )
    )
    
    assert response["status"] == "fallback"
    assert response["critic_passed"] is False
    assert any("guardrail_fallback" in message for message in response["messages"])