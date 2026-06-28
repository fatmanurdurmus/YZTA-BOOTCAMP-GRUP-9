# Architecture Decisions

## 2026-06-28: Product Name

Decision: use CarbonPilot AI as the active product name. CarbonChain remains a historical name from early project documents.

## 2026-06-28: Frontend

Decision: use React + Vite + TypeScript instead of Next.js for Sprint 1. This keeps the demo surface fast and simple while remaining Vercel-ready.

## 2026-06-28: Emission Calculation Boundary

Decision: emission calculations must be deterministic Python code and tested with pytest. LLMs may extract candidate values or explain evidence but may not freely calculate final emissions.

## 2026-06-28: Scope 3 MVP Definition

Decision: implement CBAM-focused Scope 3 for the demir-celik demo: purchased inputs, supplier factors, and upstream logistics. Full GHG 15-category Scope 3 remains a later expansion.

## 2026-06-28: AI Provider

Decision: Gemini-first for LLM tasks, but provider adapters should remain possible. Structured outputs and schema validation are mandatory at LLM boundaries.

## 2026-06-28: Observability

Decision: use LangSmith first for tracing and debugging LangGraph runs, behind environment configuration.
