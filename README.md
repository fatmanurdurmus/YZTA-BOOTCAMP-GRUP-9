# CarbonPilot AI

CarbonPilot AI is an agentic CBAM/SKDM compliance and carbon cost intelligence platform for industrial exporters. The MVP focuses on demir-celik exporters and provides deterministic Scope 1, Scope 2, and CBAM-focused Scope 3 calculations with audit-ready evidence.

## Product Vision

Industrial exporters need reliable carbon accounting before CBAM/SKDM costs become operational and financial risk. CarbonPilot AI ingests ERP logs, invoices, shipment documents, or structured activity data; validates carbon-relevant parameters; calculates emissions with deterministic Python code; retrieves legal/factor references with Law-RAG; audits the output with a Critic Agent; and prepares PDF/JSON-ready reports.

## Tech Stack

- Backend: Python, FastAPI, Pydantic v2, SQLAlchemy/Alembic-ready structure.
- Agent orchestration: LangGraph StateGraph with guarded loops and checkpoint-ready state.
- Database: PostgreSQL with pgvector.
- Frontend: React, Vite, TypeScript, Tailwind CSS, Recharts.
- Tests: pytest for backend, Vitest/Playwright-ready frontend structure.
- Observability: LangSmith-first configuration.

## Repository Structure

```text
apps/
  backend/        FastAPI, schemas, deterministic calculation engine, agent graph stubs
  frontend/       React + Vite dashboard
docs/             Product, architecture, roadmap, Jira workflow, methodology
infra/            Docker Compose and database bootstrap assets
packages/         Shared schema notes for future generated contracts
ProjectManagement Bootcamp sprint artifacts
```

## Local Backend

```bash
cd apps/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m pytest
uvicorn carbonpilot.main:app --reload
```

## Local Frontend

```bash
cd apps/frontend
npm install
npm run dev
```

## Safety Rules

- Do not push, force push, merge PRs, deploy, delete remote resources, or mark Jira issues Done without explicit approval.
- Emission calculations are deterministic Python code, never free-form LLM reasoning.
- LLM outputs must be schema-validated before entering the database, calculation engine, or reporting pipeline.

## Sprint 1 Goal

Sprint 1 establishes the monorepo, backend/frontend skeletons, strict schemas, Scope 1/2/CBAM-focused Scope 3 calculation engine, Law-RAG stub, LangGraph skeleton, guardrails, and pytest structure.
