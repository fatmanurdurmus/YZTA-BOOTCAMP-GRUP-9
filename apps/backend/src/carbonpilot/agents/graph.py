import logging
import time
from typing import Any

from carbonpilot.calculation.engine import calculate_emissions
from carbonpilot.critic.service import audit_calculation
from carbonpilot.law_rag.retriever import retrieve_default_references
from carbonpilot.schemas.agent import AgentRunRequest
from carbonpilot.schemas.calculation import CalculationRequest
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

logger = logging.getLogger(__name__)

_checkpointer: Any = None
_checkpointer_cm: Any = None


def _get_checkpointer() -> Any:
    """CP-33: attach a PostgresSaver checkpointer so agent state survives
    past a single process, keyed by thread_id. If the checkpoint package
    or the database itself is unavailable, this degrades gracefully by
    returning None, and the graph simply compiles without a checkpointer
    (identical to the Sprint 1 behaviour).
    """
    global _checkpointer, _checkpointer_cm
    if _checkpointer is not None:
        return _checkpointer

    try:
        from langgraph.checkpoint.postgres import PostgresSaver

        from carbonpilot.config import get_settings

        settings = get_settings()
        conn_string = settings.database_url.replace("postgresql+psycopg://", "postgresql://")

        # IMPORTANT: keep a reference to the context manager itself at
        # module level, not just the yielded checkpointer. Otherwise the
        # generator gets garbage-collected as soon as this function
        # returns, which closes the underlying psycopg connection even
        # though we're still holding on to the checkpointer object.
        _checkpointer_cm = PostgresSaver.from_conn_string(conn_string)
        checkpointer = _checkpointer_cm.__enter__()

        # Our graph state stores Pydantic models with fields like HttpUrl
        # (e.g. LawReference) which the default ormsgpack encoder cannot
        # pack on its own. pickle_fallback lets JsonPlusSerializer fall
        # back to pickle for any type it doesn't recognize natively.
        #
        # NOTE: from_conn_string() does NOT accept a `serde` kwarg (it
        # only takes conn_string/pipeline) -- passing it there raises a
        # silent TypeError that the except below used to swallow,
        # leaving checkpointing quietly disabled. `serde` is a plain
        # instance attribute (see BaseCheckpointSaver.__init__), so we
        # set it directly on the already-constructed checkpointer.
        checkpointer.serde = JsonPlusSerializer(pickle_fallback=True)
        checkpointer.setup()
        _checkpointer = checkpointer
        return _checkpointer
    except Exception:
        logger.warning(
            "Postgres checkpointer unavailable; agent graph will run "
            "without persistence (falls back to Sprint 1 behaviour).",
            exc_info=True,
        )
        return None


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
        passed, messages = audit_calculation(state["calculation"], state["law_references"])
        state["critic_passed"] = passed

        if "messages" not in state:
            state["messages"] = []
        state["messages"].extend(messages)

        if not passed:
            state["retries"] = state.get("retries", 0) + 1

        return state

    def routing_logic(state: CarbonPilotState) -> str:
        if state.get("critic_passed", False):
            return "approved"

        current_retries = state.get("retries", 0)
        max_allowed = state.get("max_retries", 2)

        if current_retries <= max_allowed:
            state["messages"].append(
                f"Critic audit failed. Self-correction loop triggered (Retry {current_retries}/{max_allowed})."
            )
            return "retry"

        state["messages"].append("Max retries reached without passing critic. Diverting to human_review_required.")
        return "blocked"

    graph = StateGraph(CarbonPilotState)

    graph.add_node("retrieve_law_refs", law_node)
    graph.add_node("calculate_emissions", calculate_node)
    graph.add_node("critic_review", critic_node)

    graph.set_entry_point("retrieve_law_refs")
    graph.add_edge("retrieve_law_refs", "calculate_emissions")
    graph.add_edge("calculate_emissions", "critic_review")

    graph.add_conditional_edges(
        "critic_review",
        routing_logic,
        {
            "approved": END,
            "retry": "calculate_emissions",
            "blocked": END,
        },
    )

    checkpointer = _get_checkpointer()
    return graph.compile(checkpointer=checkpointer)


def _invoke_graph_once(graph: Any, request: AgentRunRequest) -> dict[str, Any]:
    if isinstance(graph, LocalCarbonPilotGraph):
        return graph.invoke({"request": request})

    result = graph.invoke(
        {
            "activity_payload": request.model_dump(mode="json"),
            "max_retries": request.max_retries,
            "retries": 0,
            "messages": [],
        },
        config={
            "recursion_limit": min(500, max(30, 6 * (request.max_retries + 2))),
            "configurable": {"thread_id": request.thread_id},
        },
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
            *result.get("messages", []),
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
    graph = build_carbonpilot_graph()
    start_time = time.monotonic()

    result = _invoke_graph_once(graph, request)

    elapsed_seconds = time.monotonic() - start_time
    if elapsed_seconds > request.timeout_seconds:
        return _build_fallback_response(
            request, result, f"timeout_exceeded_after_{elapsed_seconds:.1f}s"
        )

    if result["critic_passed"]:
        return result

    return _build_fallback_response(request, result, "max_retries_exceeded")