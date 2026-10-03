import ImagePanel from "../shared/ImagePanel";
import MetricBadge from "../shared/MetricBadge";
import type { SketchGenerateResponse } from "../../types";

export default function SketchViewer({ result }: { result: SketchGenerateResponse }) {
  const name = `sketch_style_${result.selected_style}_${Date.now()}.png`;
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        <MetricBadge label="Style" tone="amber" value={result.style_description} />
        <MetricBadge label="Inference" value={`${result.inference_time_ms.toFixed(1)} ms`} />
        <a href={result.sketch_image} download={name} className="rounded-lg bg-emerald-500 px-4 py-1.5 text-sm font-semibold text-ink-950">
          Download PNG
        </a>
      </div>
      <ImagePanel items={[{ label: "Original face", src: result.original_image }, { label: "Generated sketch", src: result.sketch_image }]} />
    </div>
  );
}
