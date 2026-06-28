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
