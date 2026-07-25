export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export interface HealthResponse { 
  status: string; 
  service: string; 
}

export interface ExtractionResponse { 
  source_filename: string; 
  candidate_activity_data: Record<string, unknown>; 
}

export interface CarbonRiskHotspot {
  id: string;
  category: string;
  source: string;
  riskLevel: "HIGH" | "MEDIUM" | "CRITICAL";
  sharePercentage: number;
  recommendation: string;
}

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) throw new Error("CarbonPilot API is unavailable");
  return response.json() as Promise<HealthResponse>;
}

export async function extractDocument(file: File): Promise<ExtractionResponse> {
  const form = new FormData();
  form.append("file", file);
  form.append("organization_name", "CarbonPilot customer");
  form.append("facility_name", "Uploaded facility");
  form.append("country_code", "TR");
  form.append("reporting_period", "2026-Q1");
  const response = await fetch(`${API_BASE_URL}/v1/documents/extract`, { method: "POST", body: form });
  if (!response.ok) throw new Error(await response.text());
  return response.json() as Promise<ExtractionResponse>;
}

export async function simulateTransitionSliders(payload: Record<string, unknown>): Promise<Record<string, unknown>> {
  const response = await fetch(`${API_BASE_URL}/v1/simulate/transition-slider`, { 
    method: "POST", 
    headers: { "Content-Type": "application/json" }, 
    body: JSON.stringify(payload) 
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json() as Promise<Record<string, unknown>>;
}