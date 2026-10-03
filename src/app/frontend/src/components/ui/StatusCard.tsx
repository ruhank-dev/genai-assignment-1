import { useEffect, useState } from "react";
import { modelCount, useHealth } from "../../hooks/useHealth";
import Icon, { GLASS } from "./Icon";

function useClock(): string {
  const [t, setT] = useState(() => new Date());
  useEffect(() => {
    const i = setInterval(() => setT(new Date()), 1000);
    return () => clearInterval(i);
  }, []);
  return t.toLocaleTimeString("en-US");
}

interface Props {
  pipeline: string; // "Universal convolutional autoencoder"
  inferenceMs: number | null;
  className?: string;
}

/** Top-left telemetry card (Stitch): model readiness, live clock, active pipeline, latency and execution provider — all real. */
export default function StatusCard({ pipeline, inferenceMs, className = "col-span-12 lg:col-span-4" }: Props) {
  const health = useHealth();
  const { n, total } = modelCount(health);
  const clock = useClock();
  const provider = health.kind === "ok" ? health.health.providers[0].replace("ExecutionProvider", "") : "—";
  const ok = health.kind === "ok" && n === total;
  return (
    <div className={`${className} ${GLASS} flex flex-col justify-between relative overflow-hidden`}>
      <div className="absolute -top-12 -right-12 w-36 h-36 bg-tertiary-container/20 rounded-full blur-2xl pointer-events-none" />
      <div>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="relative flex h-2.5 w-2.5">
              {ok && <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-tertiary opacity-75" />}
              <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${ok ? "bg-tertiary" : "bg-error"}`} />
            </span>
            <span className="font-label-prominent text-label-prominent text-on-surface">
              {health.kind === "down" ? "Backend offline" : `Models ready ${n}/${total}`}
            </span>
          </div>
          <span className="font-data-tabular text-data-tabular px-2.5 py-1 rounded-full bg-surface-container-lowest/60 text-tertiary shadow-sm">ONNX Runtime</span>
        </div>
        <div className="mt-4 flex flex-col">
          <div className="font-display-hero text-display-hero text-on-surface tracking-tight leading-none">{clock}</div>
          <div className="flex items-center gap-1.5 mt-2">
            <Icon name="hub" className="text-[16px] text-primary-container" />
            <span className="font-label-prominent text-label-prominent text-on-surface-variant">
              Active Pipeline: <strong className="text-on-surface font-semibold">{pipeline}</strong>
            </span>
          </div>
        </div>
      </div>
      <div className="mt-6 pt-4 flex flex-wrap gap-2">
        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-secondary-container/15 text-secondary font-data-tabular text-data-tabular shadow-sm">
          <Icon name="bolt" className="text-[14px]" />
          <span>Inference {inferenceMs === null ? "—" : `${inferenceMs.toFixed(1)} ms`}</span>
        </div>
        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-surface-container-lowest/60 text-on-surface-variant font-data-tabular text-data-tabular shadow-sm">
          <Icon name="memory" className="text-[14px] text-tertiary" />
          <span>Provider: {provider}</span>
        </div>
      </div>
    </div>
  );
}
