import training from "../../data/task3_training.json";
import { GLASS_TALL } from "../ui/Icon";

const W = 200;
const H = 48;

/** SVG polyline of the real Task 3 validation-SSIM curve (results/task3/final_history.json). */
function curve(): { line: string; area: string } {
  const v = training.val_ssim;
  const lo = Math.min(...v);
  const hi = Math.max(...v);
  const pts = v.map((y, i) => `${((i / (v.length - 1)) * W).toFixed(1)},${(H - 4 - ((y - lo) / (hi - lo)) * (H - 10)).toFixed(1)}`);
  return { line: `M ${pts.join(" L ")}`, area: `M ${pts.join(" L ")} L ${W},${H} L 0,${H} Z` };
}

export default function LatencyCard({ ms }: { ms: number | null }) {
  const c = curve();
  return (
    <div className={`col-span-12 lg:col-span-4 ${GLASS_TALL} flex flex-col justify-between`}>
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <span className="font-label-caption text-label-caption uppercase tracking-wider text-on-surface-variant">Latency &amp; Dispatch</span>
          <span className="px-2.5 py-0.5 rounded-full bg-secondary-fixed text-on-secondary-fixed font-data-tabular text-data-tabular">All 4 branches run</span>
        </div>
        <div className="flex items-baseline gap-2 mt-1">
          <span className="font-display-hero text-display-hero text-on-surface">{ms === null ? "—" : ms.toFixed(1)}</span>
          <span className="font-title-card text-headline-sm text-on-surface-variant">ms</span>
        </div>
        <p className="font-body-sm text-body-sm text-on-surface-variant">Single ONNX graph: gate + identity + 3 expert autoencoders + weighted sum, batch 1, 128×128.</p>
      </div>
      <div className="my-space-sm p-space-sm rounded-2xl bg-surface-container-lowest/60 shadow-sm flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <span className="font-label-prominent text-label-prominent text-on-surface">Training Curve (validation SSIM)</span>
          <span className="font-data-tabular text-data-tabular text-tertiary">best {training.best_val_ssim.toFixed(4)}</span>
        </div>
        <svg className="w-full h-12 text-secondary" fill="none" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none">
          <path d={c.line} fill="none" stroke="currentColor" strokeLinecap="round" strokeWidth="2.5" vectorEffect="non-scaling-stroke" />
          <path d={c.area} fill="currentColor" fillOpacity="0.1" />
        </svg>
        <span className="font-label-caption text-label-caption text-on-surface-variant">{training.val_ssim.length} epochs: {training.warmup_epochs} gate warm-up + {training.val_ssim.length - training.warmup_epochs} joint fine-tuning</span>
      </div>
      <div className="grid grid-cols-2 gap-2 pt-1">
        <div className="p-2.5 rounded-xl bg-surface-container-lowest/50 shadow-sm flex flex-col">
          <span className="font-label-caption text-label-caption text-on-surface-variant">Temperature (τ)</span>
          <span className="font-title-card text-title-card text-on-surface mt-0.5">τ = {training.tau.toFixed(2)}</span>
        </div>
        <div className="p-2.5 rounded-xl bg-surface-container-lowest/50 shadow-sm flex flex-col">
          <span className="font-label-caption text-label-caption text-on-surface-variant">Loss weights</span>
          <span className="font-title-card text-tertiary mt-0.5 text-body-sm">λce {training.lambda_ce} · λbal {training.lambda_balance}</span>
        </div>
      </div>
    </div>
  );
}
