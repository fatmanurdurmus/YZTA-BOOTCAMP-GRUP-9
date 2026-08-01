import { useState } from "react";
import { 
  Activity, 
  AlertTriangle, 
  Factory, 
  FileCheck2, 
  Flame, 
  RefreshCw, 
  ShieldCheck, 
  TrendingUp, 
  UploadCloud, 
  Zap 
} from "lucide-react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

import { LandingScreen } from "./components/LandingScreen";

import { StatCard } from "./components/StatCard";
import { 
  CarbonRiskHotspot, 
  calculateEmissions,
  downloadPdfReport,
  extractDocument, 
  getHealth, 
  simulateTransitionSliders 
} from "./lib/api";


interface ChartDataItem {
  scope: string;
  value: number;
  fill: string;
}

export default function App() {
  const [showLanding, setShowLanding] = useState(true);
  const [loading, setLoading] = useState(false);
  const [emissions] = useState("No calculation yet");
  const [cbamCost] = useState("No calculation yet");
  const [criticStatus, setCriticStatus] = useState("Backend not checked");
  const [criticDetail, setCriticDetail] = useState("Refresh to verify the CarbonPilot backend");
  const [agentTrail] = useState<string[]>([]);
  const [chartData] = useState<ChartDataItem[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState("Upload a PDF, DOCX, or XLSX to extract candidate data.");
  const [candidateActivityData, setCandidateActivityData] = useState<Record<string, unknown> | null>(null);
  const [calculationResult, setCalculationResult] = useState<Record<string, unknown> | null>(null);
  const [calculationStatus, setCalculationStatus] = useState("Extract a document, then calculate its emissions.");
  const [baseline, setBaseline] = useState("0");
  const [solarPercent, setSolarPercent] = useState(0);
  const [simulationStatus, setSimulationStatus] = useState("Enter a real baseline to simulate a transition scenario.");

  // Carbon Risk Hotspots - Dynamic Warning Data
  const [hotspots] = useState<CarbonRiskHotspot[]>([
    {
      id: "hs-1",
      category: "Scope 1 - Direct Fuels",
      source: "Natural Gas Combustion (Furnace A)",
      riskLevel: "CRITICAL",
      sharePercentage: 54,
      recommendation: "Switch to electrification or green hydrogen mix to avoid CBAM tariff penalties."
    },
    {
      id: "hs-2",
      category: "Scope 2 - Purchased Electricity",
      source: "Grid Electricity (Baseline Factor)",
      riskLevel: "HIGH",
      sharePercentage: 28,
      recommendation: "Increase Solar PPA transition above 40% to offset high grid carbon intensity."
    },
    {
      id: "hs-3",
      category: "Scope 3 - Steel Inputs",
      source: "Upstream Steel Production & Logistics",
      riskLevel: "MEDIUM",
      sharePercentage: 18,
      recommendation: "Verify supplier CBAM embedded emissions certificates to lower default tax factor."
    }
  ]);

  const checkBackend = async () => {
    setLoading(true);
    try {
      const data = await getHealth();
      setCriticStatus(data.status === "ok" ? "Backend connected" : "Backend unavailable");
      setCriticDetail(data.service);
    } catch (error) {
      console.error("Error linking backend pipelines:", error);
      setCriticStatus("Backend unavailable");
      setCriticDetail("Start the FastAPI service and retry.");
    } finally {
      setLoading(false);
    }
  };

const uploadForExtraction = async () => {
    if (!selectedFile) return;
    setLoading(true);
    try {
      const result = await extractDocument(selectedFile);
      setCandidateActivityData(result.candidate_activity_data);
      setCalculationResult(null);
      setCalculationStatus("Candidate data ready. Click \"Calculate emissions\" to run the engine.");
      setUploadStatus(`Candidate data extracted from ${result.source_filename}. Review it before calculation.`);
    } catch (error) {
      setUploadStatus(error instanceof Error ? `Extraction failed: ${error.message}` : "Extraction failed.");
    } finally {
      setLoading(false);
    }
  };

  const calculateFromCandidate = async () => {
    if (!candidateActivityData) return;
    setLoading(true);
    try {
      const result = await calculateEmissions(candidateActivityData);
      setCalculationResult(result);
      setCalculationStatus(`Calculated ${String(result.total_tco2e)} tCO2e for ${String(result.facility_name)}.`);
    } catch (error) {
      setCalculationStatus(error instanceof Error ? `Calculation failed: ${error.message}` : "Calculation failed.");
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = async () => {
    if (!candidateActivityData) return;
    setLoading(true);
    try {
      const blob = await downloadPdfReport(candidateActivityData);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "carbonpilot-cbam-report.pdf";
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
      setCalculationStatus("PDF report downloaded.");
    } catch (error) {
      setCalculationStatus(error instanceof Error ? `Report download failed: ${error.message}` : "Report download failed.");
    } finally {
      setLoading(false);
    }
  };

  const runSliderSimulation = async () => {
    if (Number(baseline) <= 0) return;
    setLoading(true);
    const assumptions = {
      emission_reduction_factor: "0.20",
      transition_cost_eur_at_100_percent: "0",
      annual_operating_cost_eur_at_100_percent: "0",
      annual_operating_savings_eur_at_100_percent: "0",
      factor_source: "User-provided assumption",
      input_reference: "Dashboard input"
    };
    try {
      const result = await simulateTransitionSliders({
        baseline_tco2e: baseline,
        baseline_energy_tco2e: baseline,
        baseline_material_tco2e: "0",
        baseline_input_reference: "Dashboard baseline",
        energy_mix: { solar_percent: String(solarPercent), wind_percent: "0" },
        material_substitution: { recycled_percent: "0", low_carbon_percent: "0" },
        solar_assumptions: assumptions,
        wind_assumptions: assumptions,
        recycled_material_assumptions: assumptions,
        low_carbon_material_assumptions: assumptions,
        tax_schedule: [
          {
            year: 2026,
            carbon_price_eur_per_tco2e: "80",
            covered_emissions_rate: "1",
            free_allowance_tco2e: "0",
            tax_rate_source: "User-provided assumption",
            input_reference: "Dashboard input"
          }
        ]
      });
      setSimulationStatus(
        `Projected emissions: ${String(result.projected_emissions_tco2e)} tCO2e; reduction: ${String(result.emissions_reduction_tco2e)} tCO2e.`
      );
    } catch (error) {
      setSimulationStatus(error instanceof Error ? `Simulation failed: ${error.message}` : "Simulation failed.");
    } finally {
      setLoading(false);
    }
  };

  const getRiskBadgeColor = (level: string) => {
    switch (level) {
      case "CRITICAL":
        return "bg-rose-100 text-rose-800 border-rose-300";
      case "HIGH":
        return "bg-amber-100 text-amber-800 border-amber-300";
      default:
        return "bg-slate-100 text-slate-800 border-slate-300";
    }
  };
  
  if (showLanding) {
    return <LandingScreen onEnter={() => setShowLanding(false)} />;
  }

  return (
    <main className="min-h-screen bg-[#f2f6f3]">
      {/* Header section with responsive layout */}
      <header className="border-b border-carbon-line bg-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="grid h-10 w-10 shrink-0 place-items-center rounded-md bg-carbon-green text-white">
              <Factory size={22} aria-hidden="true" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-carbon-ink">CarbonPilot AI</h1>
              <p className="text-xs text-slate-500 sm:text-sm">CBAM-ready carbon intelligence</p>
            </div>
          </div>
          <button
            onClick={checkBackend}
            disabled={loading}
            className="inline-flex w-full items-center justify-center gap-2 rounded-md bg-carbon-ink px-4 py-2.5 text-sm font-medium text-white hover:bg-slate-800 sm:w-auto sm:py-2 disabled:opacity-50 transition-colors"
          >
            {loading ? <RefreshCw size={17} className="animate-spin" /> : <UploadCloud size={17} />}
            {loading ? "Checking backend..." : "Refresh backend status"}
          </button>
        </div>
      </header>

      {/* Main Container */}
      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-6 px-4 py-6 sm:px-6 lg:grid-cols-[1.25fr_0.75fr] lg:px-8">
        <section className="space-y-6">
          {/* Top Stat Cards */}
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <StatCard
              title="Total emissions"
              value={emissions}
              detail="Scope 1, 2 and CBAM-focused Scope 3"
              icon={<Activity size={20} aria-hidden="true" />}
            />
            <StatCard
              title="Estimated CBAM cost"
              value={cbamCost}
              detail="At EUR 80 per tonne"
              icon={<FileCheck2 size={20} aria-hidden="true" />}
            />
            <StatCard
              title="Critic status"
              value={criticStatus}
              detail={criticDetail}
              icon={<ShieldCheck size={20} aria-hidden="true" />}
            />
          </div>

          {/* Carbon Risk Hotspot Warning Cards Section (CP-49) */}
          <section className="rounded-lg border border-carbon-line bg-white p-4 shadow-sm sm:p-5">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2">
                <div className="rounded-md bg-amber-50 p-1.5 text-amber-600">
                  <AlertTriangle size={20} aria-hidden="true" />
                </div>
                <div>
                  <h2 className="text-base font-semibold text-carbon-ink">Carbon Risk Hotspots</h2>
                  <p className="text-xs text-slate-500 sm:text-sm">High-emission areas & CBAM tariff exposure</p>
                </div>
              </div>
              <span className="inline-flex items-center gap-1 rounded-full bg-rose-50 px-2.5 py-0.5 text-xs font-semibold text-rose-700">
                <TrendingUp size={12} /> High Exposure
              </span>
            </div>

            <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {hotspots.map((spot) => (
                <div
                  key={spot.id}
                  className="flex flex-col justify-between rounded-lg border border-slate-200 bg-slate-50/50 p-3.5 transition-all hover:border-slate-300 hover:bg-slate-50"
                >
                  <div>
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 truncate">
                        {spot.category}
                      </span>
                      <span
                        className={`inline-flex items-center shrink-0 rounded-md border px-1.5 py-0.5 text-[10px] font-bold ${getRiskBadgeColor(
                          spot.riskLevel
                        )}`}
                      >
                        {spot.riskLevel}
                      </span>
                    </div>

                    <h3 className="mt-2 flex items-center gap-1.5 text-sm font-semibold text-carbon-ink">
                      {spot.riskLevel === "CRITICAL" ? (
                        <Flame size={15} className="text-rose-500 shrink-0" />
                      ) : (
                        <Zap size={15} className="text-amber-500 shrink-0" />
                      )}
                      <span className="truncate">{spot.source}</span>
                    </h3>

                    <div className="mt-2.5">
                      <div className="flex justify-between text-xs text-slate-600">
                        <span>Emissions share</span>
                        <span className="font-semibold text-carbon-ink">{spot.sharePercentage}%</span>
                      </div>
                      <div className="mt-1 h-1.5 w-full rounded-full bg-slate-200">
                        <div
                          className={`h-1.5 rounded-full ${
                            spot.riskLevel === "CRITICAL" ? "bg-rose-500" : "bg-amber-500"
                          }`}
                          style={{ width: `${spot.sharePercentage}%` }}
                        />
                      </div>
                    </div>
                  </div>

                  <p className="mt-3 border-t border-slate-200/60 pt-2 text-xs text-slate-600 leading-relaxed">
                    <span className="font-semibold text-slate-700">Action: </span>
                    {spot.recommendation}
                  </p>
                </div>
              ))}
            </div>
          </section>

          {/* Optimization Sliders */}
          <section className="rounded-lg border border-carbon-line bg-white p-4 shadow-sm sm:p-5">
            <h2 className="text-base font-semibold text-carbon-ink">Optimization sliders</h2>
            <label className="mt-3 block text-sm text-slate-600">
              Baseline emissions (tCO2e)
              <input
                aria-label="Baseline emissions"
                className="mt-1 block w-full rounded border border-slate-300 p-2 text-sm focus:border-carbon-green focus:outline-none"
                type="number"
                min="0"
                value={baseline}
                onChange={(event) => setBaseline(event.target.value)}
              />
            </label>
            <label className="mt-3 block text-sm text-slate-600">
              Solar transition: {solarPercent}%
              <input
                aria-label="Solar transition"
                className="mt-1 block w-full cursor-pointer accent-carbon-green"
                type="range"
                min="0"
                max="100"
                value={solarPercent}
                onChange={(event) => setSolarPercent(Number(event.target.value))}
              />
            </label>
            <button
              type="button"
              disabled={loading || Number(baseline) <= 0}
              onClick={runSliderSimulation}
              className="mt-3 w-full rounded-md bg-carbon-green px-3 py-2 text-sm font-medium text-white sm:w-auto disabled:opacity-50 hover:bg-emerald-700 transition-colors"
            >
              Run real simulation
            </button>
            <p className="mt-3 text-xs sm:text-sm text-slate-600">{simulationStatus}</p>
          </section>

          {/* Document Extraction */}
          <section className="rounded-lg border border-carbon-line bg-white p-4 shadow-sm sm:p-5">
            <h2 className="text-base font-semibold text-carbon-ink">Document extraction</h2>
            <p className="mt-1 text-xs sm:text-sm text-slate-500">
              Files are sent directly to the strict Extractor Agent endpoint.
            </p>
            <input
              aria-label="Document to extract"
              className="mt-3 block w-full text-xs sm:text-sm text-slate-500 file:mr-4 file:rounded-md file:border-0 file:bg-slate-100 file:px-3 file:py-2 file:text-xs file:font-semibold file:text-slate-700 hover:file:bg-slate-200"
              type="file"
              accept=".pdf,.docx,.xlsx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
              onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
            />
            <button
              type="button"
              disabled={!selectedFile || loading}
              onClick={uploadForExtraction}
              className="mt-3 w-full rounded-md bg-carbon-green px-3 py-2 text-sm font-medium text-white sm:w-auto disabled:opacity-50 hover:bg-emerald-700 transition-colors"
            >
              Extract candidate data
            </button>
            <p className="mt-3 text-xs sm:text-sm text-slate-600">{uploadStatus}</p>
            <div className="mt-4 flex flex-col gap-2 border-t border-slate-100 pt-4 sm:flex-row">
              <button
                type="button"
                disabled={!candidateActivityData || loading}
                onClick={calculateFromCandidate}
                className="w-full rounded-md bg-carbon-ink px-3 py-2 text-sm font-medium text-white sm:w-auto disabled:opacity-50 hover:bg-slate-800 transition-colors"
              >
                Calculate emissions
              </button>
              <button
                type="button"
                disabled={!calculationResult || loading}
                onClick={downloadReport}
                className="w-full rounded-md border border-carbon-green px-3 py-2 text-sm font-medium text-carbon-green sm:w-auto disabled:opacity-50 hover:bg-emerald-50 transition-colors"
              >
                Download PDF report
              </button>
            </div>
            <p className="mt-3 text-xs sm:text-sm text-slate-600">{calculationStatus}</p>
          </section>

          {/* Emissions by scope chart */}
          <section className="rounded-lg border border-carbon-line bg-white p-4 shadow-sm sm:p-5">
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="text-base font-semibold text-carbon-ink">Emissions by scope</h2>
                <p className="text-xs sm:text-sm text-slate-500">Results appear after a real API run</p>
              </div>
              <span className="self-start rounded-md border border-carbon-line px-2.5 py-1 text-xs text-slate-600 sm:self-auto">
                Deterministic engine
              </span>
            </div>
            <div className="mt-5 h-64 sm:h-72 w-full overflow-hidden">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="scope" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </section>

          {/* Transformation scenario chart */}
          <section className="rounded-lg border border-carbon-line bg-white p-4 shadow-sm sm:p-5">
            <h2 className="text-base font-semibold text-carbon-ink">Transformation scenario</h2>
            <p className="text-xs sm:text-sm text-slate-500">Baseline vs optimized reduction path</p>
            <div className="mt-5 h-64 sm:h-72 w-full overflow-hidden">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={[]}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Area dataKey="baseline" stroke="#b7791f" fill="#f5dfbd" />
                  <Area dataKey="optimized" stroke="#1f8a5b" fill="#ccebdc" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </section>
        </section>

        {/* Sidebar */}
        <aside className="space-y-6">
          <section className="rounded-lg border border-carbon-line bg-white p-4 shadow-sm sm:p-5">
            <h2 className="text-base font-semibold text-carbon-ink">Agent audit trail</h2>
            <div className="mt-4 space-y-3">
              {agentTrail.length === 0 && <p className="text-sm text-slate-500">No agent run yet.</p>}
              {agentTrail.map((step, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between rounded-md border border-carbon-line px-3 py-2"
                >
                  <span className="text-sm font-medium text-carbon-ink">{step}</span>
                  <span className="rounded-md bg-green-50 px-2 py-1 text-xs font-medium text-carbon-green">
                    OK
                  </span>
                </div>
              ))}
            </div>
          </section>

          <section className="rounded-lg border border-carbon-line bg-white p-4 shadow-sm sm:p-5">
            <h2 className="text-base font-semibold text-carbon-ink">Evidence coverage</h2>
            <dl className="mt-4 space-y-4 text-sm">
              <div className="flex justify-between gap-4">
                <dt className="text-slate-500">Input references</dt>
                <dd className="font-semibold text-carbon-ink">-</dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt className="text-slate-500">Factor sources</dt>
                <dd className="font-semibold text-carbon-ink">-</dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt className="text-slate-500">Law references</dt>
                <dd className="font-semibold text-carbon-ink">-</dd>
              </div>
            </dl>
          </section>
        </aside>
      </div>
    </main>
  );
}