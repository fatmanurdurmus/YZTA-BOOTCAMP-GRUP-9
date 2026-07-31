import type { ReactNode } from "react";

type StatCardProps = {
  title: string;
  value: string;
  detail: string;
  icon: ReactNode;
  trend?: string;
};

export function StatCard({ title, value, detail, icon, trend }: StatCardProps) {
  return (
    <section className="group rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition-all hover:border-slate-300 hover:shadow-md">
      <div className="flex items-center justify-between gap-3">
        <div className="min-w-0 flex-1">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">{title}</p>
          <p className="mt-2 text-2xl font-bold tracking-tight text-carbon-ink truncate">
            {value}
          </p>
        </div>
        <div className="grid h-12 w-12 shrink-0 place-items-center rounded-lg bg-emerald-50 text-carbon-green transition-transform group-hover:scale-105">
          {icon}
        </div>
      </div>
      <div className="mt-3 flex items-center justify-between border-t border-slate-100 pt-3 text-xs">
        <span className="text-slate-500">{detail}</span>
        {trend && (
          <span className="inline-flex items-center rounded-md bg-emerald-50 px-2 py-0.5 text-[11px] font-semibold text-emerald-700">
            {trend}
          </span>
        )}
      </div>
    </section>
  );
}