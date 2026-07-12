CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS organizations (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS facilities (
  id UUID PRIMARY KEY,
  organization_id UUID NOT NULL REFERENCES organizations(id),
  name TEXT NOT NULL,
  country_code CHAR(2) NOT NULL,
  sector TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS emission_factors (
  id UUID PRIMARY KEY,
  scope TEXT NOT NULL,
  category TEXT NOT NULL,
  unit TEXT NOT NULL,
  factor_value NUMERIC NOT NULL,
  source_name TEXT NOT NULL,
  source_url TEXT,
  valid_from DATE,
  valid_to DATE,
  quality TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS law_chunks (
  id UUID PRIMARY KEY,
  title TEXT NOT NULL,
  jurisdiction TEXT NOT NULL,
  source_url TEXT NOT NULL,
  chunk_text TEXT NOT NULL,
  embedding vector(1536)
);

CREATE TABLE IF NOT EXISTS documents (
  id UUID PRIMARY KEY,
  facility_id UUID NOT NULL REFERENCES facilities(id),
  file_name TEXT NOT NULL,
  document_type TEXT NOT NULL,
  uploaded_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS activity_records (
  id UUID PRIMARY KEY,
  facility_id UUID NOT NULL REFERENCES facilities(id),
  document_id UUID REFERENCES documents(id),
  activity_type TEXT NOT NULL,
  activity_name TEXT NOT NULL,
  reporting_period TEXT NOT NULL,
  amount NUMERIC,
  unit TEXT,
  emission_factor_id UUID REFERENCES emission_factors(id),
  input_reference TEXT NOT NULL,
  raw_payload JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS calculation_runs (
  id UUID PRIMARY KEY,
  facility_id UUID NOT NULL REFERENCES facilities(id),
  thread_id TEXT NOT NULL,
  status TEXT NOT NULL,
  total_tco2e NUMERIC,
  critic_passed BOOLEAN,
  requested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS reports (
  id UUID PRIMARY KEY,
  calculation_run_id UUID NOT NULL REFERENCES calculation_runs(id),
  format TEXT NOT NULL,
  file_path TEXT,
  generated_at TIMESTAMPTZ NOT NULL DEFAULT now()git branch
);