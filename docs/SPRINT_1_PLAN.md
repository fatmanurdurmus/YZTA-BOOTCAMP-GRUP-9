# Sprint 1 Plan

## Dates

19 June 2026 - 5 July 2026

## Goal

Build the foundation that can be tested from the first week: monorepo, API, frontend shell, schemas, deterministic calculation engine, Law-RAG stub, LangGraph skeleton, and pytest coverage.

## Sprint 1 Tasks

- CP-1 Initialize monorepo structure.
- CP-2 Create FastAPI backend skeleton.
- CP-3 Create React Vite TypeScript frontend skeleton.
- CP-14 Define Pydantic strict schemas for activity data, factors, products, calculations, and reports.
- CP-15 Implement deterministic Scope 1 calculation engine.
- CP-16 Implement deterministic Scope 2 calculation engine.
- CP-17 Implement deterministic CBAM-focused Scope 3 engine for steel inputs and upstream logistics.
- CP-18 Create initial Law-RAG knowledge base stub.
- CP-19 Create LangGraph StateGraph orchestration skeleton.
- CP-20 Add loop limit, timeout, and fallback guardrails.
- CP-21 Add pytest backend test structure.
- CP-22 Create governance docs and AGENTS.md.

## Acceptance Criteria

- Backend calculation tests pass locally.
- Calculation engine works without an LLM.
- LLM-like extraction output must be Pydantic-validated before calculation.
- API exposes health and calculation endpoints.
- Frontend dashboard renders sample carbon intelligence views.
- Jira structure reflects epics and Sprint 1 tasks.
