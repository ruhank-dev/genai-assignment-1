import type { Metrics } from "../../types";
import Icon, { GLASS } from "./Icon";
import Ring from "./Ring";

const INFERNO = "linear-gradient(90deg,#000004,#570f6e,#bc3754,#f98e09,#fcffa4)";

interface Props {
  title?: string;
  map: string | null; // data URL of the heat map (null before the first run)
  mode: "error" | "stroke";
  reference?: string; // human description of what the error is measured against
  metrics?: Metrics | null;
  inputMetrics?: Metrics | null;
  stats?: { mean_ink: number; dark_fraction: number } | null;
  exportData?: unknown;
  className?: string;
}

function download(name: string, data: unknown) {
  const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: "application/json" }));
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  URL.revokeObjectURL(url);
}

const f = (v: number | undefined, d = 3) => (v === undefined || !Number.isFinite(v) ? "—" : v.toFixed(d));

/** Shared "Error Map & Metrics" card shown at the bottom of every workspace (Stitch design + real heat map). */
export default function ErrorHeatmapCard({ title = "Error Map & Metrics", map, mode, reference, metrics, inputMetrics, stats, exportData, className = "" }: Props) {
  const wide = !className.includes("lg:col-span"); // full-width cards lay the heat map out beside the gauge
  const gain = metrics && inputMetrics ? metrics.psnr - inputMetrics.psnr : null;
  const ringValue = mode === "error" ? (metrics ? metrics.psnr / 40 : 0) : stats ? Math.min(1, stats.mean_ink / 0.3) : 0;
  return (
    <div className={`${className} ${GLASS} flex flex-col justify-between`}>
      <div>
        <div className="flex items-center justify-between mb-3">
          <span className="font-title-card text-title-card text-on-surface">{title}</span>
          <Icon name="analytics" className="text-[18px] text-on-surface-variant" />
        </div>
        <div className={`flex flex-col ${wide ? "md:flex-row" : ""} gap-4 items-center bg-surface-container-lowest/30 rounded-[20px] shadow-inner p-3 mb-4`}>
          <div className={`w-full ${wide ? "md:w-56" : "max-w-[190px]"} shrink-0 aspect-square rounded-[16px] overflow-hidden bg-surface-container-lowest/50 flex items-center justify-center`}>
            {map ? (
              <img src={map} alt={mode === "error" ? "absolute error heat map" : "stroke intensity heat map"} className="w-full h-full object-contain" />
            ) : (
              <span className="px-4 text-center font-label-caption text-label-caption text-on-surface-variant">Run the model to see the {mode === "error" ? "error heat map" : "stroke-intensity heat map"}</span>
            )}
          </div>
          <div className={`flex-1 flex flex-wrap items-center ${wide ? "justify-center gap-16" : "justify-around gap-3"} w-full`}>
            <Ring value={ringValue} main={mode === "error" ? f(metrics?.psnr, 1) : stats ? `${(stats.mean_ink * 100).toFixed(1)}%` : "—"} caption={mode === "error" ? "dB PSNR" : "mean ink"} />
            <div className="flex flex-col gap-2">
              {mode === "error" ? (
                <>
                  <Chip label="PSNR gain" value={gain === null ? "n/a" : `${gain >= 0 ? "+" : ""}${gain.toFixed(1)} dB`} tone="text-tertiary" />
                  <Chip label="SSIM score" value={f(metrics?.ssim)} tone="text-secondary" />
                </>
              ) : (
                <>
                  <Chip label="Dark pixels" value={stats ? `${(stats.dark_fraction * 100).toFixed(1)}%` : "—"} tone="text-tertiary" />
                  <Chip label="Mean ink" value={stats ? f(stats.mean_ink) : "—"} tone="text-secondary" />
                </>
              )}
            </div>
          </div>
        </div>
        <div className="flex flex-col gap-1.5 mt-2">
          <div className="flex items-center justify-between text-on-surface-variant">
            <span className="font-label-caption text-label-caption">{mode === "error" ? "Residual MSE" : "Stroke intensity (1 − luminance)"}</span>
            <span className="font-data-tabular text-data-tabular">{mode === "error" ? `${f(metrics?.mse, 4)} avg` : "scale 0 – 0.6"}</span>
          </div>
          <div className="h-3 w-full rounded-full shadow-inner" style={{ background: INFERNO }} />
          <div className="flex items-center justify-between font-label-caption text-label-caption text-on-surface-variant px-0.5">
            {mode === "error" ? (
              <>
                <span>0 (identical)</span>
                <span>|restored − reference|, scale 0 – 0.5</span>
                <span>≥ 0.5</span>
              </>
            ) : (
              <>
                <span>0 (paper)</span>
                <span>generated stroke density</span>
                <span>≥ 0.6 (ink)</span>
              </>
            )}
          </div>
        </div>
      </div>
      <div className="mt-4 pt-3 flex items-center justify-between text-on-surface-variant">
        <span className="font-label-caption text-label-caption flex items-center gap-1">
          <Icon name={map ? "check_circle" : "hourglass_empty"} className="text-[15px] text-tertiary" />
          {map ? reference : "Waiting for a result"}
        </span>
        <button onClick={() => exportData !== undefined && download("heatmap_metrics.json", exportData)} disabled={!map} className="font-data-tabular text-data-tabular text-secondary hover:underline disabled:opacity-40" type="button">
          Export Log
        </button>
      </div>
    </div>
  );
}

function Chip({ label, value, tone }: { label: string; value: string; tone: string }) {
  return (
    <div className="px-3 py-1.5 rounded-full bg-surface-container-lowest/60 shadow-sm">
      <span className="font-label-caption text-label-caption text-on-surface-variant block">{label}</span>
      <span className={`font-data-tabular text-data-tabular font-bold ${tone}`}>{value}</span>
    </div>
  );
}
