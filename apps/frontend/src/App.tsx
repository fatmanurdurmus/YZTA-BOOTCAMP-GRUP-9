import { Activity, Factory, FileCheck2, ShieldCheck, UploadCloud } from "lucide-react";
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
import { agentSteps, emissionsTrend, scopeData } from "./lib/sampleData";

export default function App() {
  return (
    <main className="min-h-screen bg-[#f2f6f3]">
      <header className="border-b border-carbon-line bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="grid h-10 w-10 place-items-center rounded-md bg-carbon-green text-white">
              <Factory size={22} aria-hidden="true" />
            </div>
            <div>
              <h1 className="text-lg font-semibold text-carbon-ink">CarbonPilot AI</h1>
              <p className="text-sm text-slate-500">CBAM-ready carbon intelligence</p>
            </div>
          </div>
          <button className="inline-flex items-center gap-2 rounded-md bg-carbon-ink px-4 py-2 text-sm font-medium text-white hover:bg-slate-800">
            <UploadCloud size={17} aria-hidden="true" />
            Upload data
          </button>
        </div>
      </header>

      <div className="mx-auto grid max-w-7xl gap-6 px-4 py-6 sm:px-6 lg:grid-cols-[1.25fr_0.75fr] lg:px-8">
        <section className="space-y-6">
          <div className="grid gap-4 sm:grid-cols-3">
            <StatCard
              title="Total emissions"
              value="45.25 tCO2e"
              detail="Scope 1, 2 and CBAM-focused Scope 3"
              icon={<Activity size={20} aria-hidden="true" />}
            />
            <StatCard
              title="Estimated CBAM cost"
              value="EUR 3,620"
              detail="At EUR 80 per tonne"
              icon={<FileCheck2 size={20} aria-hidden="true" />}
            />
            <StatCard
              title="Critic status"
              value="Passed"
              detail="All lines include source evidence"
              icon={<ShieldCheck size={20} aria-hidden="true" />}
            />
          </div>

          <section className="rounded-lg border border-carbon-line bg-white p-5 shadow-sm">
            <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h2 className="text-base font-semibold text-carbon-ink">Emissions by scope</h2>
                <p className="text-sm text-slate-500">Demo steel facility, 2026-Q1</p>
              </div>
              <span className="rounded-md border border-carbon-line px-3 py-1 text-sm text-slate-600">
                Deterministic engine
              </span>
            </div>
            <div className="mt-5 h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={scopeData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="scope" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </section>

          <section className="rounded-lg border border-carbon-line bg-white p-5 shadow-sm">
            <h2 className="text-base font-semibold text-carbon-ink">Transformation scenario</h2>
            <p className="text-sm text-slate-500">Baseline vs optimized reduction path</p>
            <div className="mt-5 h-72">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={emissionsTrend}>
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

        <aside className="space-y-6">
          <section className="rounded-lg border border-carbon-line bg-white p-5 shadow-sm">
            <h2 className="text-base font-semibold text-carbon-ink">Agent audit trail</h2>
            <div className="mt-4 space-y-3">
              {agentSteps.map((step) => (
                <div
                  key={step}
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

          <section className="rounded-lg border border-carbon-line bg-white p-5 shadow-sm">
            <h2 className="text-base font-semibold text-carbon-ink">Evidence coverage</h2>
            <dl className="mt-4 space-y-4 text-sm">
              <div className="flex justify-between gap-4">
                <dt className="text-slate-500">Input references</dt>
                <dd className="font-semibold text-carbon-ink">5 / 5</dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt className="text-slate-500">Factor sources</dt>
                <dd className="font-semibold text-carbon-ink">5 / 5</dd>
              </div>
              <div className="flex justify-between gap-4">
                <dt className="text-slate-500">Law references</dt>
                <dd className="font-semibold text-carbon-ink">2</dd>
              </div>
            </dl>
          </section>
        </aside>
      </div>
    </main>
  );
}
