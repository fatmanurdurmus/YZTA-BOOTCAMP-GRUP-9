# AGENTS.md

## Project Purpose

CarbonPilot AI is an agentic CBAM/SKDM compliance and carbon cost intelligence platform for industrial exporters, starting with a demir-celik MVP. The platform ingests operational documents and structured activity data, validates carbon-relevant parameters, calculates Scope 1, Scope 2, and CBAM-focused Scope 3 emissions, audits the result, and produces PDF/JSON-ready compliance outputs.

## Required Stack

- Backend: Python, FastAPI, Pydantic v2 strict schemas.
- Agent orchestration: LangGraph StateGraph with loop, timeout, and checkpoint guardrails.
- Database: PostgreSQL with pgvector for semantic memory.
- Frontend: React, Vite, TypeScript, Tailwind CSS, shadcn/ui-style components.
- Charts: Recharts unless a stronger reason is documented.
- Tests: pytest for backend, Vitest/Playwright for frontend where useful.
- Observability: LangSmith first, behind environment-based configuration.

## Coding Standards

- Keep deterministic business logic separate from LLM/agent logic.
- Prefer small modules with explicit schemas and typed function boundaries.
- Do not let free-form LLM text enter the database, calculation engine, or reports.
- Every LLM output must be parsed and validated through Pydantic strict models first.
- Emission calculations must be deterministic, source-aware, and covered by tests.
- Every calculation result must retain audit evidence: input reference, factor source, formula, and scope.
- Keep generated or external data source assumptions in docs/DECISIONS.md.

## Testing Requirements

- Run backend tests before reporting calculation or schema work complete.
- Scope 1, Scope 2, and Scope 3 calculations require unit tests for normal, zero, invalid, and edge inputs.
- Agent graph changes require tests for loop limits, timeout behavior, retry/fallback behavior, and checkpoint resume where implemented.
- Reporting changes require JSON schema validation and source-reference checks.

## Jira Rules

- Jira project: CarbonPilot AI / CP.
- Use Epics + Tasks unless the Jira project adds Story types later.
- Mention Jira issue keys in branch and commit names when possible.
- Summarize every meaningful Jira create/update to the user.
- Do not delete Jira issues.
- Do not mark Jira issues as Done without explicit user approval.

## Git and Release Safety

- Do not push to GitHub.
- Do not force push.
- Do not merge pull requests.
- Do not deploy anything.
- Do not delete remote resources.
- Prepare commits locally only if the user asks.

## Documentation Maintenance

- Update docs/DECISIONS.md whenever architecture, stack, methodology, data source, or compliance assumptions change.
- Update this AGENTS.md when an operating rule changes.
- Keep README.md and docs/SPRINT_1_PLAN.md aligned with the current Sprint 1 scope.
