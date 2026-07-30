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

// CP-50 protects several endpoints (e.g. /v1/documents/extract) with JWT.
// There is no login screen yet, so until CP-49/50's UI work adds one, the
// dashboard authenticates as a fixed demo identity and caches the token in
// memory for the lifetime of the page. Swap this out once real user login
// exists — nothing else in this file needs to change, only getDemoToken().
let cachedDemoToken: string | null = null;

async function getDemoToken(): Promise<string> {
  if (cachedDemoToken) return cachedDemoToken;

  const response = await fetch(`${API_BASE_URL}/v1/auth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_id: "demo-user",
      organization_id: "demo-org",
      facility_id: "demo-facility",
    }),
  });
  if (!response.ok) throw new Error("Unable to obtain a demo access token");

  const data = (await response.json()) as { access_token: string };
  cachedDemoToken = data.access_token;
  return cachedDemoToken;
}

async function authHeaders(): Promise<Record<string, string>> {
  const token = await getDemoToken();
  return { Authorization: `Bearer ${token}` };
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
  const response = await fetch(`${API_BASE_URL}/v1/documents/extract`, {
    method: "POST",
    headers: await authHeaders(),
    body: form,
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json() as Promise<ExtractionResponse>;
}

export async function calculateEmissions(
  activityData: Record<string, unknown>
): Promise<Record<string, unknown>> {
  const response = await fetch(`${API_BASE_URL}/v1/calculate`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...(await authHeaders()) },
    body: JSON.stringify({ activity_data: activityData, carbon_price_eur_per_tonne: 80 }),
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json() as Promise<Record<string, unknown>>;
}

export async function downloadPdfReport(activityData: Record<string, unknown>): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/v1/reports/pdf`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...(await authHeaders()) },
    body: JSON.stringify({ activity_data: activityData, carbon_price_eur_per_tonne: 80 }),
  });
  if (!response.ok) throw new Error(await response.text());
  return response.blob();
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