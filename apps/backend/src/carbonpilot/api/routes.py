from fastapi import APIRouter

from carbonpilot.agents.graph import run_carbonpilot_graph
from carbonpilot.calculation.engine import calculate_emissions
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
def run_agent(request: AgentRunRequest) -> AgentRunResponse:
    result = run_carbonpilot_graph(request)
    return AgentRunResponse(**result)


@router.post("/v1/reports/json")
def create_json_report(request: CalculationRequest) -> dict[str, object]:
    calculation = calculate_emissions(request)
    references = retrieve_default_references()
    return build_json_report(calculation, references)
