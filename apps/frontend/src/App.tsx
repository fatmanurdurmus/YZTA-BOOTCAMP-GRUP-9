import { useState } from "react";
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle2,
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

interface ScenarioDataItem {
  month: string;
  baseline: number;
  optimized: number;
}

// Demo presentation baseline charts data
const INITIAL_SCOPE_DATA: ChartDataItem[] = [
  { scope: "Scope 1 (Direct)", value: 7500, fill: "#059669" },
  { scope: "Scope 2 (Energy)", value: 4200, fill: "#10b981" },
  { scope: "Scope 3 (Supply)", value: 2550, fill: "#34d399" },
];

const INITIAL_TRANSFORMATION_PATH: ScenarioDataItem[] = [
  { month: "Jan", baseline: 1200, optimized: 1200 },
  { month: "Feb", baseline: 1180, optimized: 1100 },
  { month: "Mar", baseline: 1210, optimized: 1050 },
  { month: "Apr", baseline: 1190, optimized: 980 },
  { month: "May", baseline: 1220, optimized: 920 },
  { month: "Jun", baseline: 1200, optimized: 850 },
  { month: "Jul", baseline: 1230, optimized: 810 },
  { month: "Aug", baseline: 1210, optimized: 780 },
  { month: "Sep", baseline: 1250, optimized: 740 },
  { month: "Oct", baseline: 1240, optimized: 710 },
  { month: "Nov", baseline: 1220, optimized: 680 },
  { month: "Dec", baseline: 1260, optimized: 650 },
];

export default function App() {
  const [loading, setLoading] = useState(false);
  const [emissions, setEmissions] = useState("14,250 tCO2e");
  const [cbamCost, setCbamCost] = useState("€1,140,000");
  const [criticStatus, setCriticStatus] = useState("Backend Connected");
  const [criticDetail, setCriticDetail] = useState("FastAPI & Agent pipeline ready");
  const [agentTrail, setAgentTrail] = useState<string[]>([
    "IngestionAgent: Document structure validated",
    "ExtractionAgent: Candidate activity data extracted",
    "CalculationEngine: Standardized factors applied"
  ]);
  const [chartData, setChartData] = useState<ChartDataItem[]>(INITIAL_SCOPE_DATA);
  const [scenarioData] = useState<ScenarioDataItem[]>(INITIAL_TRANSFORMATION_PATH);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState("Upload a PDF, DOCX, or XLSX to extract candidate data.");
  const [candidateActivityData, setCandidateActivityData] = useState<Record<string, unknown> | null>(null);
  const [calculationResult, setCalculationResult] = useState<Record<string, unknown> | null>(null);
  const [calculationStatus, setCalculationStatus] = useState("Extract a document, then calculate its emissions.");
  const [baseline, setBaseline] = useState("14250");
  const [solarPercent, setSolarPercent] = useState(35);
  const [simulationStatus, setSimulationStatus] = useState("Adjust transition slider to run transition scenario.");

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
      
      setAgentTrail((prev) => [
        `DocumentExtracted: ${result.source_filename}`,
        ...prev
      ]);
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
      
      const total = Number(result.total_tco2e) || 0;
      setEmissions(`${total.toLocaleString()} tCO2e`);
      setCbamCost(`€${(total * 80).toLocaleString()}`);
      
      setCalculationStatus(`Calculated ${total.toLocaleString()} tCO2e for ${String(result.facility_name || "Facility")}.`);
      
      // Update chart dynamically
      if (result.scope1_tco2e || result.scope2_tco2e || result.scope3_tco2e) {
        setChartData([
          { scope: "Scope 1 (Direct)", value: Number(result.scope1_tco2e) || 0, fill: "#059669" },
          { scope: "Scope 2 (Energy)", value: Number(result.scope2_tco2e) || 0, fill: "#10b981" },
          { scope: "Scope 3 (Supply)", value: Number(result.scope3_tco2e) || 0, fill: "#34d399" },
        ]);
      }
      
      setAgentTrail((prev) => [
        `CalculationEngine: Total ${total} tCO2e verified`,
        ...prev
      ]);
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

  return (
    <main className="min-h-screen bg-[#f8faf9] text-slate-900">
      {/* Header section with branding & navigation */}
      <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/95 backdrop-blur">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-3.5 sm:flex-row sm:items-center sm:justify-between sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <img 
  src="/logo.png" 
  alt="CarbonPilot AI Logo" 
  className="h-10 w-auto shrink-0 object-contain" 
/>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-bold tracking-tight text-slate-900">CarbonPilot AI</h1>
                <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-bold text-emerald-800">
                  CBAM Ready
                </span>
              </div>
              <p className="text-xs text-slate-500">Agentic Carbon Intelligence & Compliance Engine</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={checkBackend}
              disabled={loading}
              className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-slate-800 sm:w-auto disabled:opacity-50 transition-colors"
            >
              {loading ? <RefreshCw size={16} className="animate-spin" /> : <UploadCloud size={16} />}
              {loading ? "Connecting..." : "Sync Engine"}
            </button>
          </div>
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
              detail="Scope 1, 2 and CBAM Scope 3"
              trend="-14.2% YoY"
              icon={<Activity size={22} aria-hidden="true" />}
            />
            <StatCard
              title="Estimated CBAM cost"
              value={cbamCost}
              detail="At EUR 80 per tonne"
              trend="Tax Exposure"
              icon={<FileCheck2 size={22} aria-hidden="true" />}
            />
            <StatCard
              title="Critic status"
              value={criticStatus}
              detail={criticDetail}
              trend="Verified"
              icon={<ShieldCheck size={22} aria-hidden="true" />}
            />
          </div>

          {/* Carbon Risk Hotspot Warning Cards Section */}
          <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2.5">
                <div className="rounded-lg bg-amber-50 p-2 text-amber-600">
                  <AlertTriangle size={20} aria-hidden="true" />
                </div>
                <div>
                  <h2 className="text-base font-bold text-slate-900">Carbon Risk Hotspots</h2>
                  <p className="text-xs text-slate-500">High-emission areas & CBAM tariff exposure</p>
                </div>
              </div>
              <span className="inline-flex items-center gap-1.5 rounded-full bg-rose-50 px-3 py-1 text-xs font-semibold text-rose-700 border border-rose-200">
                <TrendingUp size={13} /> High Exposure
              </span>
            </div>

            <div className="mt-4 grid grid-cols-1 gap-3.5 sm:grid-cols-2 lg:grid-cols-3">
              {hotspots.map((spot) => (
                <div
                  key={spot.id}
                  className="flex flex-col justify-between rounded-xl border border-slate-200 bg-slate-50/50 p-4 transition-all hover:border-slate-300 hover:bg-slate-50 shadow-xs"
                >
                  <div>
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 truncate">
                        {spot.category}
                      </span>
                      <span
                        className={`inline-flex items-center shrink-0 rounded-md border px-2 py-0.5 text-[10px] font-bold ${getRiskBadgeColor(
                          spot.riskLevel
                        )}`}
                      >
                        {spot.riskLevel}
                      </span>
                    </div>

                    <h3 className="mt-2.5 flex items-center gap-1.5 text-sm font-bold text-slate-900">
                      {spot.riskLevel === "CRITICAL" ? (
                        <Flame size={16} className="text-rose-500 shrink-0" />
                      ) : (
                        <Zap size={16} className="text-amber-500 shrink-0" />
                      )}
                      <span className="truncate">{spot.source}</span>
                    </h3>

                    <div className="mt-3">
                      <div className="flex justify-between text-xs text-slate-600">
                        <span>Emissions share</span>
                        <span className="font-bold text-slate-900">{spot.sharePercentage}%</span>
                      </div>
                      <div className="mt-1.5 h-2 w-full rounded-full bg-slate-200">
                        <div
                          className={`h-2 rounded-full transition-all duration-500 ${
                            spot.riskLevel === "CRITICAL" ? "bg-rose-500" : "bg-amber-500"
                          }`}
                          style={{ width: `${spot.sharePercentage}%` }}
                        />
                      </div>
                    </div>
                  </div>

                  <p className="mt-3.5 border-t border-slate-200/80 pt-2.5 text-xs text-slate-600 leading-relaxed">
                    <span className="font-semibold text-slate-900">Action: </span>
                    {spot.recommendation}
                  </p>
                </div>
              ))}
            </div>
          </section>

          {/* Optimization Sliders */}
          <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="text-base font-bold text-slate-900">Optimization Sliders</h2>
            <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider">
                  Baseline emissions (tCO2e)
                </label>
                <input
                  aria-label="Baseline emissions"
                  className="mt-1.5 block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500"
                  type="number"
                  min="0"
                  value={baseline}
                  onChange={(event) => setBaseline(event.target.value)}
                />
              </div>
              <div>
                <div className="flex justify-between">
                  <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider">
                    Solar Transition Rate
                  </label>
                  <span className="text-xs font-bold text-emerald-600">{solarPercent}%</span>
                </div>
                <input
                  aria-label="Solar transition"
                  className="mt-3 block w-full cursor-pointer accent-emerald-600"
                  type="range"
                  min="0"
                  max="100"
                  value={solarPercent}
                  onChange={(event) => setSolarPercent(Number(event.target.value))}
                />
              </div>
            </div>
            <div className="mt-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <button
                type="button"
                disabled={loading || Number(baseline) <= 0}
                onClick={runSliderSimulation}
                className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white shadow-sm disabled:opacity-50 hover:bg-emerald-700 transition-colors"
              >
                Run Scenario Simulation
              </button>
              <p className="text-xs text-slate-600 italic">{simulationStatus}</p>
            </div>
          </section>

          {/* Document Extraction */}
          <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="text-base font-bold text-slate-900">Document Extraction Engine</h2>
            <p className="mt-1 text-xs text-slate-500">
              Files are processed securely by the Agentic Extractor pipeline (PDF, DOCX, XLSX).
            </p>
            <div className="mt-4 rounded-lg border-2 border-dashed border-slate-200 p-4 text-center hover:border-slate-300">
              <input
                aria-label="Document to extract"
                className="block w-full text-xs text-slate-500 file:mr-4 file:rounded-md file:border-0 file:bg-emerald-50 file:px-3 file:py-2 file:text-xs file:font-semibold file:text-emerald-700 hover:file:bg-emerald-100 cursor-pointer"
                type="file"
                accept=".pdf,.docx,.xlsx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
              />
            </div>
            <div className="mt-4 flex flex-col gap-2.5 sm:flex-row">
              <button
                type="button"
                disabled={!selectedFile || loading}
                onClick={uploadForExtraction}
                className="w-full rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white disabled:opacity-50 hover:bg-emerald-700 transition-colors"
              >
                Extract Candidate Data
              </button>
              <button
                type="button"
                disabled={!candidateActivityData || loading}
                onClick={calculateFromCandidate}
                className="w-full rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50 hover:bg-slate-800 transition-colors"
              >
                Calculate Emissions
              </button>
              <button
                type="button"
                disabled={!calculationResult || loading}
                onClick={downloadReport}
                className="w-full rounded-lg border border-emerald-600 px-4 py-2 text-sm font-medium text-emerald-700 disabled:opacity-50 hover:bg-emerald-50 transition-colors"
              >
                Download PDF Report
              </button>
            </div>
            <p className="mt-3 text-xs text-slate-600 font-medium">{uploadStatus}</p>
          </section>

          {/* Emissions by scope chart */}
          <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between border-b border-slate-100 pb-3">
              <div>
                <h2 className="text-base font-bold text-slate-900">Emissions Breakdown by Scope</h2>
                <p className="text-xs text-slate-500">Deterministic calculation results</p>
              </div>
              <span className="self-start rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600 sm:self-auto">
                Deterministic Engine
              </span>
            </div>
            <div className="mt-5 h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="scope" tick={{ fontSize: 12, fill: '#64748b' }} />
                  <YAxis tick={{ fontSize: 12, fill: '#64748b' }} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', borderRadius: '8px', color: '#fff', border: 'none' }}
                    itemStyle={{ color: '#10b981' }}
                  />
                  <Bar dataKey="value" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </section>

          {/* Transformation scenario chart */}
          <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="border-b border-slate-100 pb-3">
              <h2 className="text-base font-bold text-slate-900">Transformation Scenario Path</h2>
              <p className="text-xs text-slate-500">12-Month Baseline vs Optimized Decarbonization Trajectory</p>
            </div>
            <div className="mt-5 h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={scenarioData}>
                  <defs>
                    <linearGradient id="colorBaseline" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#f59e0b" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="colorOptimized" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.4}/>
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="month" tick={{ fontSize: 12, fill: '#64748b' }} />
                  <YAxis tick={{ fontSize: 12, fill: '#64748b' }} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', borderRadius: '8px', color: '#fff', border: 'none' }}
                  />
                  <Area type="monotone" dataKey="baseline" name="Baseline (tCO2e)" stroke="#f59e0b" fillOpacity={1} fill="url(#colorBaseline)" />
                  <Area type="monotone" dataKey="optimized" name="Optimized Path (tCO2e)" stroke="#10b981" fillOpacity={1} fill="url(#colorOptimized)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </section>
        </section>

        {/* Sidebar */}
        <aside className="space-y-6">
          <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex items-center gap-2 border-b border-slate-100 pb-3">
              <CheckCircle2 size={18} className="text-emerald-600" />
              <h2 className="text-base font-bold text-slate-900">Agent Audit Trail</h2>
            </div>
            <div className="mt-4 space-y-2.5">
              {agentTrail.map((step, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between rounded-lg border border-slate-100 bg-slate-50/50 px-3 py-2 text-xs"
                >
                  <span className="font-medium text-slate-700 truncate mr-2">{step}</span>
                  <span className="shrink-0 rounded-md bg-emerald-50 px-2 py-0.5 font-bold text-emerald-700 border border-emerald-200">
                    VERIFIED
                  </span>
                </div>
              ))}
            </div>
          </section>

          <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="text-base font-bold text-slate-900">Evidence & Regulatory Coverage</h2>
            <dl className="mt-4 space-y-3.5 text-xs">
              <div className="flex justify-between border-b border-slate-100 pb-2">
                <dt className="text-slate-500">Input References</dt>
                <dd className="font-bold text-slate-900">Structured Extractor</dd>
              </div>
              <div className="flex justify-between border-b border-slate-100 pb-2">
                <dt className="text-slate-500">Emission Factor Standard</dt>
                <dd className="font-bold text-slate-900">DEFRA / IPCC 2026</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-slate-500">Law References</dt>
                <dd className="font-bold text-emerald-700">EU CBAM Regulation</dd>
              </div>
            </dl>
          </section>
        </aside>
      </div>
    </main>
  );
}