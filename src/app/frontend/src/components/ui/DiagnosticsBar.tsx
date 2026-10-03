import { modelCount, useHealth } from "../../hooks/useHealth";
import Icon from "./Icon";

/** Bottom pill "Realtime Diagnostics" (Stitch): items are supplied by each page; the right side shows backend health. */
export default function DiagnosticsBar({ items }: { items: { label: string; value: string }[] }) {
  const health = useHealth();
  const { n, total } = modelCount(health);
  return (
    <div className="col-span-12 rounded-full bg-surface-container-lowest/40 backdrop-blur-2xl px-space-lg py-2.5 flex flex-wrap items-center justify-between shadow-sm gap-2">
      <div className="flex flex-wrap items-center gap-3">
        <Icon name="speed" className="text-[18px] text-primary-container" />
        <span className="font-label-prominent text-label-prominent text-on-surface">Realtime Diagnostics:</span>
        {items.map((it, i) => (
          <span key={it.label} className="flex items-center gap-3">
            {i > 0 && <span className="text-outline-variant">•</span>}
            <span className="font-data-tabular text-data-tabular text-on-surface-variant">
              {it.label}: <strong className="text-on-surface">{it.value}</strong>
            </span>
          </span>
        ))}
      </div>
      <div className="flex items-center gap-2">
        <span className={`w-2 h-2 rounded-full ${health.kind === "ok" && n === total ? "bg-tertiary" : "bg-error"}`} />
        <span className="font-label-caption text-label-caption text-on-surface-variant font-medium">
          {health.kind === "down" ? "Backend offline" : `Backend healthy • ${n}/${total} models loaded`}
        </span>
      </div>
    </div>
  );
}
