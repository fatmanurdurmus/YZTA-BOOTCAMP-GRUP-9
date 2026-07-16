from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from carbonpilot.agents.graph import run_carbonpilot_graph
from carbonpilot.calculation.engine import calculate_emissions
from carbonpilot.db.repository import get_episodic_history, persist_calculation_run
from carbonpilot.db.session import get_db
from carbonpilot.law_rag.retriever import retrieve_default_references, semantic_search
from carbonpilot.law_rag.seed import seed_law_chunks
from carbonpilot.reporting.json_report import build_json_report
from carbonpilot.schemas.agent import AgentRunRequest, AgentRunResponse
from carbonpilot.schemas.calculation import CalculationRequest, CalculationResponse
from carbonpilot.schemas.optimization import OptimizationRequest, OptimizationResponse
from carbonpilot.schemas.simulation import SliderSimulationRequest, SliderSimulationResponse
from carbonpilot.simulation.service import optimize_green_transition, simulate_transition_sliders

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "carbonpilot-api"}


@router.post("/v1/calculate", response_model=CalculationResponse)
def calculate(request: CalculationRequest) -> CalculationResponse:
    return calculate_emissions(request)


@router.post("/v1/optimize/green-transition", response_model=OptimizationResponse)
def optimize_transition(request: OptimizationRequest) -> OptimizationResponse:
    return optimize_green_transition(request)


@router.post("/v1/simulate/transition-slider", response_model=SliderSimulationResponse)
def simulate_transition_slider(
    request: SliderSimulationRequest,
) -> SliderSimulationResponse:
    return simulate_transition_sliders(request)


@router.get("/v1/law-rag/sources")
def law_sources() -> dict[str, object]:
    return {"references": [reference.model_dump() for reference in retrieve_default_references()]}


@router.post("/v1/law-rag/seed")
def seed_law_rag(db: Session = Depends(get_db)) -> dict[str, object]:
    """CP-35: seeds the curated CBAM/SKDM law chunks (with embeddings) into
    Postgres. Safe to call repeatedly — already-seeded titles are skipped.
    """
    inserted = seed_law_chunks(db)
    return {"inserted": inserted}


@router.get("/v1/law-rag/search")
def search_law_rag(query: str, top_k: int = 3, db: Session = Depends(get_db)) -> dict[str, object]:
    """CP-35: semantic memory search over indexed CBAM/SKDM law chunks."""
    references = semantic_search(db, query, top_k=top_k)
    return {"references": [reference.model_dump() for reference in references]}

@router.get("/v1/memory/episodic")
def episodic_memory(
    organization_name: str, facility_name: str, limit: int = 5, db: Session = Depends(get_db)
) -> dict[str, object]:
    """CP-36: episodic memory — recent calculation runs for a facility."""
    runs = get_episodic_history(db, organization_name, facility_name, limit=limit)
    return {
        "runs": [
            {
                "thread_id": run.thread_id,
                "status": run.status,
                "total_tco2e": float(run.total_tco2e) if run.total_tco2e is not None else None,
                "critic_passed": run.critic_passed,
                "requested_at": run.requested_at.isoformat() if run.requested_at else None,
            }
            for run in runs
        ]
    }


@router.post("/v1/agent/run", response_model=AgentRunResponse)
def run_agent(request: AgentRunRequest, db: Session = Depends(get_db)) -> AgentRunResponse:
    result = run_carbonpilot_graph(request)

    # CP-36: episodic memory recall — look at this facility's past runs
    # *before* persisting the current one, so "past" never includes itself.
    # A lookup failure must never break the API response, so it's isolated.
    try:
        past_runs = get_episodic_history(
            db,
            request.activity_data.facility.organization_name,
            request.activity_data.facility.facility_name,
            limit=3,
        )
        if past_runs:
            result["messages"] = [
                *result.get("messages", []),
                f"episodic_memory: found {len(past_runs)} prior run(s) for this facility; "
                f"most recent status={past_runs[0].status}, critic_passed={past_runs[0].critic_passed}",
            ]
    except Exception:
        db.rollback()

    # CP-32: persist the outcome so it survives past this single request.
    # A persistence failure must never break the API response the user
    # already computed correctly, so it is isolated in its own try/except.
    try:
        persist_calculation_run(
            db=db,
            activity_data=request.activity_data,
            thread_id=result["thread_id"],
            status=result["status"],
            critic_passed=result["critic_passed"],
            calculation=result.get("calculation"),
        )
    except Exception:
        db.rollback()

    return AgentRunResponse(**result)


@router.post("/v1/reports/json")
def create_json_report(request: CalculationRequest) -> dict[str, object]:
    calculation = calculate_emissions(request)
    law_references = retrieve_default_references()

    # Synchronized parameter signatures safely with keyword arguments (CP-11)
    report_data = build_json_report(
        calculation=calculation,
        law_references=law_references
    )
    return report_data
