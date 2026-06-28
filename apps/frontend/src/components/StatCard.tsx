import type { ReactNode } from "react";

type StatCardProps = {
  title: string;
  value: string;
  detail: string;
  icon: ReactNode;
};

export function StatCard({ title, value, detail, icon }: StatCardProps) {
  return (
    <section className="rounded-lg border border-carbon-line bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-slate-600">{title}</p>
          <p className="mt-2 text-2xl font-semibold tracking-normal text-carbon-ink">{value}</p>
        </div>
        <div className="grid h-10 w-10 place-items-center rounded-md bg-carbon-panel text-carbon-green">
          {icon}
        </div>
      </div>
      <p className="mt-3 text-sm text-slate-500">{detail}</p>
    </section>
  );
}
