import { useCallback, useEffect, useState } from "react";
import FaceInput from "../components/face/FaceInput";
import QueueCard from "../components/face/QueueCard";
import SketchCompare from "../components/face/SketchCompare";
import StyleCard, { Adjust } from "../components/face/StyleCard";
import ErrorHeatmapCard from "../components/ui/ErrorHeatmapCard";
import Icon from "../components/ui/Icon";
import { useInference } from "../hooks/useInference";
import { api } from "../services/api";
import type { SketchGenerateResponse } from "../types";

export default function FaceToSketch() {
  const [file, setFile] = useState<File | null>(null);
  const [style, setStyle] = useState(2);
  const [adjust, setAdjust] = useState<Adjust>({ weight: 1, tone: "white" });
  const [problem, setProblem] = useState<string | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [size, setSize] = useState<string | null>(null);
  const call = useCallback((a: { file: File; style: number }) => {
    const form = new FormData();
    form.append("image", a.file);
    form.append("style", String(a.style));
    return api.generateSketch(form);
  }, []);
  const inf = useInference<SketchGenerateResponse, { file: File; style: number }>(call);

  useEffect(() => {
    if (!file) {
      setPreview(null);
      return setSize(null);
    }
    const url = URL.createObjectURL(file);
    setPreview(url);
    const img = new Image();
    img.onload = () => setSize(`${img.naturalWidth}x${img.naturalHeight}`);
    img.src = url;
    return () => URL.revokeObjectURL(url);
  }, [file]);

  const run = (s = style) => file && void inf.run({ file, style: s });
  const pickStyle = (s: number) => {
    setStyle(s);
    if (inf.data && file) run(s); // switching style after a result regenerates immediately
  };
  const err = inf.error ?? problem;
  const r = inf.data;
  return (
    <div className="flex flex-col w-full gap-space-lg pb-6">
      <div className="w-full flex flex-col md:flex-row items-center justify-between gap-space-md">
        <div className="flex items-center gap-space-sm">
          <span className="w-2.5 h-2.5 rounded-full bg-tertiary-container animate-pulse shadow-sm" />
          <span className="font-headline-sm text-headline-sm text-on-surface">Face-to-Sketch Studio</span>
          <span className="px-2.5 py-0.5 rounded-full bg-surface-container-highest/60 font-label-caption text-label-caption text-on-surface-variant backdrop-blur-md">Conditional GAN · FiLM style embedding</span>
        </div>
        {err && (
          <div role="alert" className="flex items-center gap-space-sm px-4 py-2 rounded-full bg-error-container/70 backdrop-blur-xl text-on-error-container shadow-sm">
            <Icon name="warning" className="text-[18px] text-error" />
            <span className="font-body-sm text-body-sm font-medium">{err}</span>
            {inf.error && file && (
              <button onClick={() => run()} className="ml-1 px-2.5 py-0.5 rounded-full bg-surface-container-lowest/80 text-error font-label-caption text-label-caption hover:bg-surface-container-lowest shadow-sm" type="button">Retry</button>
            )}
            <button onClick={() => (inf.dismissError(), setProblem(null))} aria-label="Dismiss error" className="font-label-caption text-label-caption" type="button">✕</button>
          </div>
        )}
      </div>
      <div className="grid grid-cols-12 gap-gutter w-full">
        <FaceInput file={file} onFile={setFile} onProblem={setProblem} />
        <StyleCard style={style} onStyle={pickStyle} adjust={adjust} onAdjust={setAdjust} />
        <SketchCompare r={r} preview={preview} size={size} adjust={adjust} loading={inf.loading} canRun={!!file} onRun={() => run()} />
        <QueueCard loading={inf.loading} r={r} style={style} />
        <ErrorHeatmapCard
          className="col-span-12"
          title="Stroke Intensity Heatmap"
          mode="stroke"
          map={r?.error_map ?? null}
          stats={r?.stats}
          reference="Heat map of the generated sketch's stroke density (1 − luminance); there is no ground-truth sketch for a new photo"
          exportData={r ? { style: r.selected_style, stats: r.stats, inference_time_ms: r.inference_time_ms } : undefined}
        />
      </div>
    </div>
  );
}
