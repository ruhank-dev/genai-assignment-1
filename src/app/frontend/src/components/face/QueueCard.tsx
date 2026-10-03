import type { SketchGenerateResponse } from "../../types";
import Icon, { GLASS } from "../ui/Icon";

/** "Synthesis Queue": live status of the single request (idle / running / done) and its real latency. */
export default function QueueCard({ loading, r, style }: { loading: boolean; r: SketchGenerateResponse | null; style: number }) {
  const state = loading ? "Generating sketch…" : r ? "Sketch ready" : "Idle — waiting for a photo";
  return (
    <section className={`col-span-12 lg:col-span-3 ${GLASS} shadow-lg flex flex-col justify-between relative overflow-hidden`}>
      <div className="absolute -bottom-16 -left-16 w-40 h-40 bg-secondary-fixed/40 rounded-full blur-2xl pointer-events-none" />
      <div>
        <div className="flex items-center justify-between mb-space-md">
          <span className="font-title-card text-title-card text-on-surface">Synthesis Queue</span>
          <Icon name="hourglass_top" className="text-secondary text-[20px]" />
        </div>
        <div className="p-space-md rounded bg-surface-container-lowest/70 backdrop-blur-xl shadow-md mb-space-md flex flex-col gap-space-sm">
          <div className="flex items-center justify-between">
            <span className="font-label-prominent text-label-prominent text-on-surface">Active Task</span>
            <span className="font-data-tabular text-data-tabular text-secondary font-bold">{loading ? "running" : r ? "done" : "idle"}</span>
          </div>
          <div className="flex items-center gap-space-sm">
            <div className={`w-8 h-8 shrink-0 rounded-full border-4 ${loading ? "border-secondary border-t-transparent animate-spin" : r ? "border-tertiary" : "border-surface-container-highest"}`} />
            <div className="flex-1 flex flex-col min-w-0">
              <span className="font-body-sm text-body-sm text-on-surface truncate">{state}</span>
              <span className="font-label-caption text-label-caption text-on-surface-variant">Style {style} · conditional GAN</span>
            </div>
          </div>
          <div className="w-full h-1.5 rounded-full bg-surface-container-highest overflow-hidden">
            <div className={`h-full rounded-full bg-gradient-to-r from-secondary-container to-secondary ${loading ? "w-2/3 animate-pulse" : r ? "w-full" : "w-0"}`} />
          </div>
        </div>
        <div className="flex flex-col gap-2">
          {[
            ["Inference Latency", r ? `${r.inference_time_ms.toFixed(1)} ms` : "—"],
            ["Output Size", "128 × 128 RGB"],
            ["Model", "U-Net + FiLM, PatchGAN"],
          ].map(([k, v]) => (
            <div key={k} className="flex items-center justify-between px-3 py-2 rounded-full bg-surface-container-lowest/50 text-body-sm">
              <span className="font-label-caption text-label-caption text-on-surface-variant">{k}</span>
              <span className="font-data-tabular text-data-tabular text-on-surface font-semibold">{v}</span>
            </div>
          ))}
        </div>
      </div>
      <div className="mt-space-md p-space-sm rounded bg-surface-container/60 backdrop-blur-md flex items-center gap-space-sm">
        <Icon name="image_search" className="text-secondary text-[24px] shrink-0" />
        <p className="font-body-sm text-xs text-on-surface-variant leading-relaxed">Or drag any JPG/PNG portrait onto the input card to convert it with the selected style.</p>
      </div>
    </section>
  );
}
