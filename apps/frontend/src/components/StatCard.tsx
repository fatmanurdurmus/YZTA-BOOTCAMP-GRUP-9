import type { ReactNode } from "react";

type StatCardProps = {
  title: string;
  value: string;
  detail: string;
  icon: ReactNode;
};

export function StatCard({ title, value, detail, icon }: StatCardProps) {
  return (
    <section className="rounded-lg border border-carbon-line bg-white p-4 shadow-sm transition-all hover:shadow-md">
      <div className="flex items-center justify-between gap-3">
        <div className="min-w-0 flex-1">
          <p className="text-xs sm:text-sm font-medium text-slate-600 truncate">{title}</p>
          <p className="mt-1.5 text-xl sm:text-2xl font-semibold tracking-tight text-carbon-ink truncate">
            {value}
          </p>
        </div>
        <div className="grid h-10 w-10 shrink-0 place-items-center rounded-md bg-carbon-panel text-carbon-green">
          {icon}
        </div>
      </div>
      <p className="mt-3 text-xs sm:text-sm text-slate-500 leading-snug">{detail}</p>
    </section>
  );
}