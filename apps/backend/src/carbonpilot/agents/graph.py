import json
import time
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
    """
    Builds the production-ready LangGraph StateGraph with autonomous self-correction loops.
    Falls back to LocalCarbonPilotGraph if LangGraph core libraries are unavailable.
    """
    try:
        from langgraph.graph import END, StateGraph
        from carbonpilot.agents.state import CarbonPilotState
    except ImportError:
        return LocalCarbonPilotGraph()

    # --- Node Definitions ---
    def law_node(state: CarbonPilotState) -> CarbonPilotState:
        state["law_references"] = retrieve_default_references()
        if "messages" not in state or not state["messages"]:
            state["messages"] = []
        state["messages"].append("retrieve_law_refs completed")
        return state

    def calculate_node(state: CarbonPilotState) -> CarbonPilotState:
        payload = state["activity_payload"]
        request = AgentRunRequest.model_validate(payload)
        
        calculation_request = CalculationRequest(
            activity_data=request.activity_data,
            carbon_price_eur_per_tonne=request.carbon_price_eur_per_tonne,
        )
        state["calculation"] = calculate_emissions(calculation_request)
        state["thread_id"] = request.thread_id
        
        if "messages" not in state:
            state["messages"] = []
        state["messages"].append("calculate_emissions completed")
        return state

    def critic_node(state: CarbonPilotState) -> CarbonPilotState:
        if "retries" not in state:
            state["retries"] = 0
            
        passed, messages = audit_calculation(state["calculation"], state["law_references"])
        state["critic_passed"] = passed
        
        if "messages" not in state:
            state["messages"] = []
        state["messages"].extend(messages)
        return state

    # --- Conditional Router Edge (CP-20 Guardrail Implementation) ---
    def routing_logic(state: CarbonPilotState) -> str:
        """Evaluates critic outcome and applies self-correction loops or fallback to avoid token loops."""
        if state.get("critic_passed", False):
            return "approved"
            
        current_retries = state.get("retries", 0)
        max_allowed = state.get("max_retries", 2)
        
        if current_retries < max_allowed:
            state["retries"] = current_retries + 1
            state["messages"].append(f"Critic audit failed. Self-correction loop triggered (Retry {state['retries']}/{max_allowed}).")
            return "retry"
            
        state["messages"].append("Max retries reached without passing critic. Diverting to human_review_required.")
        return "blocked"

    # --- Graph Structural Layout ---
    graph = StateGraph(CarbonPilotState)
    
    graph.add_node("retrieve_law_refs", law_node)
    graph.add_node("calculate_emissions", calculate_node)
    graph.add_node("critic_review", critic_node)
    
    graph.set_entry_point("retrieve_law_refs")
    graph.add_edge("retrieve_law_refs", "calculate_emissions")
    graph.add_edge("calculate_emissions", "critic_review")
    
    # Binding conditional logic to the critic outcome
    graph.add_conditional_edges(
        "critic_review",
        routing_logic,
        {
            "approved": END,
            "retry": "calculate_emissions",  
            "blocked": END                  
        }
    )
    
    return graph.compile()


def _invoke_graph_once(graph: Any, request: AgentRunRequest) -> dict[str, Any]:
    if isinstance(graph, LocalCarbonPilotGraph):
        return graph.invoke({"request": request})

    # Execute inside real runtime graph configuration
    result = graph.invoke(
        {
            "activity_payload": request.model_dump(mode="json"), 
            "max_retries": request.max_retries,
            "retries": 0,
            "messages": []
        },
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
        "messages": [
            "ingest_document completed",
            "extract_candidate_data skipped: structured input provided",
            "validate_activity_schema completed",
            *result.get("messages", [])
        ],
    }


def _build_fallback_response(
    request: AgentRunRequest, last_result: dict[str, Any], reason: str
) -> dict[str, Any]:
    return {
        "thread_id": request.thread_id,
        "status": "fallback",
        "calculation": last_result["calculation"],
        "law_reference_count": last_result["law_reference_count"],
        "critic_passed": False,
        "messages": [*last_result["messages"], f"guardrail_fallback: {reason}"],
    }


def run_carbonpilot_graph(request: AgentRunRequest) -> dict[str, Any]:
    """Runs the graph with CP-20 guardrails.

    - loop limit: at most `request.max_retries` retries after the first attempt
    - timeout: aborts and falls back once `request.timeout_seconds` is exceeded
    - fallback: if the critic never passes, returns a 'fallback' status carrying
      the last known calculation instead of looping forever
    """
    graph = build_carbonpilot_graph()
    start_time = time.monotonic()
    last_result: dict[str, Any] | None = None

    for _attempt in range(1, request.max_retries + 2):
        if last_result is not None:
            elapsed_seconds = time.monotonic() - start_time
            if elapsed_seconds > request.timeout_seconds:
                return _build_fallback_response(
                    request, last_result, f"timeout_exceeded_after_{elapsed_seconds:.1f}s"
                )

        last_result = _invoke_graph_once(graph, request)

        if last_result["critic_passed"]:
            return last_result

    return _build_fallback_response(request, last_result, "max_retries_exceeded")