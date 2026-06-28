# Jira Workflow

## Project

- Jira project name: CarbonPilot.
- Jira key: CP.
- Issue structure: Epics + Tasks.

## Required Epics

- CP-5 Project Setup & Architecture
- CP-6 Data Ingestion & Validation
- CP-7 Carbon Calculation Engine
- CP-8 Agent Orchestration
- CP-9 Memory & Persistence
- CP-10 Optimization Simulation
- CP-11 Reporting & Audit
- CP-12 Frontend Dashboard
- CP-13 Deployment & Observability

## Sprint 1 Issues

- CP-1 Initialize monorepo structure
- CP-2 Create FastAPI backend skeleton
- CP-3 Create React Vite TypeScript frontend skeleton
- CP-4 Add FastAPI health route and settings stub
- CP-14 Define Pydantic strict schemas
- CP-15 Implement deterministic Scope 1 engine
- CP-16 Implement deterministic Scope 2 engine
- CP-17 Implement deterministic CBAM-focused Scope 3 engine
- CP-18 Create initial Law-RAG stub
- CP-19 Create LangGraph StateGraph skeleton
- CP-20 Add loop limit, timeout, and fallback guardrails
- CP-21 Add pytest backend test structure
- CP-22 Create governance docs and AGENTS.md

## Working Rules

- Do not delete issues.
- Do not transition issues to Done without explicit approval.
- Every meaningful Jira create/update must be summarized to the user.
- Use labels such as `carbonpilot`, `sprint-1`, `backend`, `frontend`, `calculation`, `agent`, `rag`, `testing`, and `governance`.
- Branch and commit names should include CP issue keys when practical.

## Status Meaning

- Backlog: planned but not selected.
- To Do / Selected for Development: selected work not started.
- In Progress: actively being implemented.
- Code Review: ready for review.
- Testing: implemented and under verification.
- Done: only after explicit user approval.
