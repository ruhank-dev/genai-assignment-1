import { modelCount, useHealth } from "../../hooks/useHealth";
import Icon, { GLASS } from "../ui/Icon";

interface Row {
  icon: string;
  label: string;
  sub: string;
  ms: number | null;
  bg: string;
  fg: string;
}

export default function ProfileCard({ rows, className = "col-span-12 lg:col-span-4", title = "Execution Profile" }: { rows: Row[]; className?: string; title?: string }) {
  const health = useHealth();
  const { n, total } = modelCount(health);
  const provider = health.kind === "ok" ? health.health.providers.join(" → ") : "—";
  return (
    <div className={`${className} ${GLASS} shadow-sm flex flex-col justify-between`}>
      <div>
        <div className="flex items-center justify-between mb-space-sm">
          <div>
            <span className="font-label-caption text-label-caption uppercase tracking-wider text-on-surface-variant font-semibold">Latency Metrics</span>
            <h2 className="font-headline-sm text-headline-sm text-on-surface">{title}</h2>
          </div>
          <span className="px-2.5 py-0.5 rounded-full bg-tertiary-container/30 text-on-tertiary-container font-data-tabular text-data-tabular font-bold flex items-center gap-1 shadow-sm">⚡ Measured</span>
        </div>
        <div className="space-y-3 my-2">
          {rows.map((r) => (
            <div key={r.label} className="p-3.5 rounded bg-surface-container-lowest/70 backdrop-blur-md shadow-sm flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${r.bg} ${r.fg}`}>
                  <Icon name={r.icon} className="text-[18px]" />
                </div>
                <div className="flex flex-col">
                  <span className="font-label-caption text-label-caption text-on-surface-variant">{r.label}</span>
                  <span className="font-title-card text-title-card text-on-surface">{r.sub}</span>
                </div>
              </div>
              <div className="font-data-metric text-data-metric font-bold text-on-surface">
                {r.ms === null ? "—" : r.ms.toFixed(1)} <span className="text-body-sm font-normal text-on-surface-variant">ms</span>
              </div>
            </div>
          ))}
        </div>
      </div>
      <div className="pt-space-sm mt-space-sm bg-surface-container-low/40 p-3.5 rounded">
        <div className="flex justify-between items-center mb-1.5">
          <span className="font-label-prominent text-label-prominent text-on-surface">Runtime</span>
          <span className="font-data-tabular text-data-tabular text-on-surface font-semibold">{n}/{total} ONNX models loaded</span>
        </div>
        <div className="w-full h-2 rounded-full bg-surface-container-highest/60 overflow-hidden p-0.5">
          <div className="h-full rounded-full bg-secondary-container" style={{ width: `${(n / total) * 100}%` }} />
        </div>
        <div className="flex justify-between items-center mt-2 font-label-caption text-label-caption text-on-surface-variant">
          <span>Provider: {provider}</span>
          <span className="text-tertiary font-semibold">Batch 1 · 128×128</span>
        </div>
      </div>
    </div>
  );
}
