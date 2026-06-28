import json
from typing import Any

from carbonpilot.calculation.engine import calculate_emissions
from carbonpilot.critic.service import audit_calculation
from carbonpilot.law_rag.retriever import retrieve_default_references
from carbonpilot.schemas.agent import AgentRunRequest
from carbonpilot.schemas.calculation import CalculationRequest


class LocalCarbonPilotGraph:
    """Fallback runner that mirrors the Sprint 1 graph without requiring runtime services."""

    def invoke(self, state: dict[str, Any]) -> dict[str, Any]:
        request: AgentRunRequest = state["request"]
        calculation_request = CalculationRequest(
            activity_data=request.activity_data,
            carbon_price_eur_per_tonne=request.carbon_price_eur_per_tonne,
        )
        law_references = retrieve_default_references()
        calculation = calculate_emissions(calculation_request)
        critic_passed, critic_messages = audit_calculation(calculation, law_references)
        return {
            "thread_id": request.thread_id,
            "status": "completed" if critic_passed else "needs_review",
            "calculation": calculation,
            "law_reference_count": len(law_references),
            "critic_passed": critic_passed,
            "messages": [
                "ingest_document completed",
                "extract_candidate_data skipped: structured input provided",
                "validate_activity_schema completed",
                "retrieve_law_refs completed",
                "calculate_emissions completed",
                *critic_messages,
            ],
        }


def build_carbonpilot_graph() -> Any:
    try:
        from langgraph.graph import END, StateGraph

        from carbonpilot.agents.state import CarbonPilotState
    except ImportError:
        return LocalCarbonPilotGraph()

    def calculate_node(state: CarbonPilotState) -> CarbonPilotState:
        request = AgentRunRequest.model_validate_json(json.dumps(state["activity_payload"]))
        calculation_request = CalculationRequest(
            activity_data=request.activity_data,
            carbon_price_eur_per_tonne=request.carbon_price_eur_per_tonne,
        )
        state["calculation"] = calculate_emissions(calculation_request)
        state["thread_id"] = request.thread_id
        return state

    def law_node(state: CarbonPilotState) -> CarbonPilotState:
        state["law_references"] = retrieve_default_references()
        return state

    def critic_node(state: CarbonPilotState) -> CarbonPilotState:
        passed, messages = audit_calculation(state["calculation"], state["law_references"])
        state["critic_passed"] = passed
        state["messages"] = messages
        return state

    graph = StateGraph(CarbonPilotState)
    graph.add_node("retrieve_law_refs", law_node)
    graph.add_node("calculate_emissions", calculate_node)
    graph.add_node("critic_review", critic_node)
    graph.set_entry_point("retrieve_law_refs")
    graph.add_edge("retrieve_law_refs", "calculate_emissions")
    graph.add_edge("calculate_emissions", "critic_review")
    graph.add_edge("critic_review", END)
    return graph.compile()


def run_carbonpilot_graph(request: AgentRunRequest) -> dict[str, Any]:
    graph = build_carbonpilot_graph()

    if isinstance(graph, LocalCarbonPilotGraph):
        return graph.invoke({"request": request})

    result = graph.invoke(
        {"activity_payload": request.model_dump(mode="json"), "max_retries": request.max_retries},
        config={"recursion_limit": max(5, request.max_retries + 5)},
    )
    calculation = result["calculation"]
    law_references = result["law_references"]
    critic_passed = bool(result["critic_passed"])
    return {
        "thread_id": request.thread_id,
        "status": "completed" if critic_passed else "needs_review",
        "calculation": calculation,
        "law_reference_count": len(law_references),
        "critic_passed": critic_passed,
        "messages": result.get("messages", []),
    }
