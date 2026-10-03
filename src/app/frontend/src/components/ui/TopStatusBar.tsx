import { ReactNode } from "react";
import { HealthState } from "../../hooks/useHealth";

/** Rounded status strip at the top of the Hard-Routed / Soft-MoE pages (Stitch): live readiness + two badges. */
export default function TopStatusBar({ health, ready, text, badges }: { health: HealthState; ready: boolean; text: ReactNode; badges: string[] }) {
  const ok = health.kind === "ok" && ready;
  return (
    <div className="w-full flex items-center justify-between px-space-lg py-space-sm rounded-full bg-surface-container-lowest/60 backdrop-blur-xl shadow-sm gap-3">
      <div className="flex items-center gap-space-sm min-w-0">
        <span className="relative flex h-2.5 w-2.5 shrink-0">
          {ok && <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-tertiary opacity-75" />}
          <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${ok ? "bg-tertiary" : "bg-error"}`} />
        </span>
        <span className="font-data-tabular text-data-tabular text-on-surface truncate">{health.kind === "down" ? "Backend offline" : text}</span>
      </div>
      <div className="flex items-center gap-space-xs shrink-0">
        {badges.map((b, i) => (
          <span key={b} className={`px-2.5 py-0.5 rounded-full font-label-caption text-label-caption uppercase tracking-wider ${i === 0 ? "bg-secondary-fixed text-on-secondary-fixed-variant" : "bg-primary-fixed text-on-primary-fixed"}`}>
            {b}
          </span>
        ))}
      </div>
    </div>
  );
}
