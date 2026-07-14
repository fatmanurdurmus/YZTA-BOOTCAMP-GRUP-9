from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from carbonpilot.agents.graph import run_carbonpilot_graph
from carbonpilot.calculation.engine import calculate_emissions
from carbonpilot.db.repository import persist_calculation_run
from carbonpilot.db.session import get_db
from carbonpilot.law_rag.retriever import retrieve_default_references
from carbonpilot.reporting.json_report import build_json_report
from carbonpilot.schemas.agent import AgentRunRequest, AgentRunResponse
from carbonpilot.schemas.calculation import CalculationRequest, CalculationResponse

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "carbonpilot-api"}


@router.post("/v1/calculate", response_model=CalculationResponse)
def calculate(request: CalculationRequest) -> CalculationResponse:
    return calculate_emissions(request)


@router.get("/v1/law-rag/sources")
def law_sources() -> dict[str, object]:
    return {"references": [reference.model_dump() for reference in retrieve_default_references()]}


@router.post("/v1/agent/run", response_model=AgentRunResponse)
def run_agent(request: AgentRunRequest, db: Session = Depends(get_db)) -> AgentRunResponse:
    result = run_carbonpilot_graph(request)

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