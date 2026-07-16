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

## 2026-07-16: Green-Transition Financial Methodology

Decision: green-transition options are evaluated by deterministic decimal arithmetic over a
configurable annual carbon-tax schedule. Taxable emissions are the non-negative remainder after
the period's coverage rate and free allowance are applied. Carbon-tax savings are the difference
between baseline and transitioned carbon costs. Options are ranked by net present savings after
initial investment and annual operating costs/savings. Legal rates, coverage, allowances, and
their references are request inputs; the engine does not hard-code or forecast regulation.
Initial investment is a time-zero cash flow, while each compliance year's net savings is treated
as an end-of-year cash flow for discounting.
