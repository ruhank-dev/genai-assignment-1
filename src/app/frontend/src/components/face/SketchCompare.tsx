import { useState } from "react";
import type { SketchGenerateResponse } from "../../types";
import Icon, { GLASS, PILL_BTN } from "../ui/Icon";
import type { Adjust } from "./StyleCard";

const TINT: Record<Adjust["tone"], string> = { white: "#ffffff", warm: "#fff1d6", cool: "#e3efff" };

interface Props {
  r: SketchGenerateResponse | null;
  preview: string | null;
  size: string | null; // natural size of the uploaded photo
  adjust: Adjust;
  loading: boolean;
  canRun: boolean;
  onRun: () => void;
}

function save(url: string, name: string) {
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
}

/** "Synthesis Comparison View": original vs generated sketch, with Generate / Download / Copy actions. */
export default function SketchCompare({ r, preview, size, adjust, loading, canRun, onRun }: Props) {
  const [zoom, setZoom] = useState(false);
  const [copied, setCopied] = useState<string | null>(null);
  const style = { filter: `contrast(${adjust.weight}) brightness(${1 - (adjust.weight - 1) * 0.08})`, background: TINT[adjust.tone], mixBlendMode: "multiply" as const };
  const copy = async () => {
    if (!r) return;
    try {
      const blob = await (await fetch(r.sketch_image)).blob();
      await navigator.clipboard.write([new ClipboardItem({ "image/png": blob })]);
      setCopied("Copied to clipboard");
    } catch {
      setCopied("Clipboard not available in this browser");
    }
    setTimeout(() => setCopied(null), 2500);
  };
  return (
    <section className={`col-span-12 lg:col-span-9 ${GLASS} shadow-lg flex flex-col justify-between relative`}>
      <div className="flex items-center justify-between mb-space-md">
        <div className="flex items-center gap-2">
          <Icon name="compare" className="text-primary text-[22px]" />
          <h2 className="font-headline-sm text-headline-sm text-on-surface">Synthesis Comparison View</h2>
        </div>
        <div className="flex items-center gap-space-xs">
          <span className="px-2.5 py-1 rounded-full bg-surface-container-lowest/70 backdrop-blur-md text-on-surface-variant font-data-tabular text-data-tabular shadow-sm">Model I/O: 128×128</span>
          <span className="px-2.5 py-1 rounded-full bg-tertiary-container/20 text-tertiary font-label-caption text-label-caption font-semibold">Monochrome sketch</span>
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-space-md mb-space-md">
        <div className="rounded bg-surface-container-lowest/60 backdrop-blur-md p-space-sm flex flex-col shadow-sm">
          <div className="flex items-center justify-between pb-2">
            <span className="font-title-card text-title-card text-on-surface">Original Input</span>
            <span className="px-2 py-0.5 rounded-full bg-surface-container-highest text-on-surface-variant font-label-caption text-label-caption font-semibold">{size ?? "—"}</span>
          </div>
          <div className="relative w-full h-56 rounded overflow-hidden bg-surface-container-low shadow-inner flex items-center justify-center">
            {preview ? <img src={preview} alt="original face" className="w-full h-full object-cover" /> : <span className="text-body-sm text-on-surface-variant">Choose a photo</span>}
            {size && <div className="absolute bottom-2 left-2 px-2.5 py-0.5 rounded-full bg-inverse-surface/60 backdrop-blur-md text-surface font-label-caption text-label-caption">Source: {size.replace("x", " × ")}</div>}
          </div>
        </div>
        <div className="rounded bg-surface-container-lowest/60 backdrop-blur-md p-space-sm flex flex-col shadow-sm relative group">
          <div className="flex items-center justify-between pb-2">
            <div className="flex items-center gap-1.5">
              <span className="font-title-card text-title-card text-on-surface font-bold">Synthesized Sketch</span>
              <span className="w-2 h-2 rounded-full bg-primary-container" />
            </div>
            <span className="px-2 py-0.5 rounded-full bg-primary-fixed text-on-primary-fixed-variant font-label-caption text-label-caption font-bold shadow-sm">{r ? `Style ${r.selected_style}` : "No sketch yet"}</span>
          </div>
          <div className="relative w-full h-56 rounded overflow-hidden bg-surface-container-lowest shadow-inner flex items-center justify-center">
            {r ? <img src={r.sketch_image} alt="generated sketch" className="w-full h-full object-contain" style={style} /> : <span className="text-body-sm text-on-surface-variant px-4 text-center">{loading ? "Generating…" : "The generated sketch appears here"}</span>}
            {r && (
              <>
                <button onClick={() => setZoom(true)} className="absolute top-2 right-2 w-8 h-8 rounded-full bg-surface-container-lowest/80 backdrop-blur-md text-on-surface flex items-center justify-center hover:scale-110 transition-all shadow-sm" title="Zoom" aria-label="Zoom sketch" type="button">
                  <Icon name="zoom_in" className="text-[16px]" />
                </button>
                <div className="absolute bottom-2 left-2 px-2.5 py-0.5 rounded-full bg-inverse-surface/70 backdrop-blur-md text-surface font-label-caption text-label-caption">{r.style_description.replace("FS2K ", "")}</div>
              </>
            )}
          </div>
        </div>
      </div>
      <div className="flex flex-wrap items-center justify-between gap-space-md pt-space-xs">
        <div className="flex items-center gap-space-sm">
          <button onClick={onRun} disabled={!canRun || loading} className="px-6 py-3 rounded-full bg-gradient-to-r from-primary-container to-inverse-primary text-on-primary-container font-label-prominent text-label-prominent font-bold flex items-center gap-2 shadow-[0_6px_24px_rgba(245,158,11,0.35)] hover:shadow-[0_8px_32px_rgba(245,158,11,0.5)] transition-all disabled:opacity-40" type="button">
            <Icon name="draw" className="text-[20px]" />
            {loading ? "Generating…" : "Generate Sketch"}
          </button>
          <button onClick={() => r && save(r.sketch_image, `sketch_style_${r.selected_style}_${Date.now()}.png`)} disabled={!r} className={`${PILL_BTN} px-5 py-3`} type="button">
            <Icon name="download" className="text-[18px]" /> Download PNG
          </button>
        </div>
        <div className="flex items-center gap-space-xs">
          {copied && <span className="font-label-caption text-label-caption text-on-surface-variant">{copied}</span>}
          <button onClick={() => r && save(r.error_map, `stroke_heatmap_style_${r.selected_style}.png`)} disabled={!r} className="h-11 px-4 rounded-full bg-surface-container-lowest/60 backdrop-blur-md text-on-surface hover:bg-surface-container-lowest flex items-center gap-2 shadow-sm transition-all disabled:opacity-40" title="Download the stroke-intensity heat map" type="button">
            <Icon name="polyline" className="text-[18px] text-secondary" />
            <span className="font-label-prominent text-label-prominent">Download Heatmap</span>
          </button>
          <button onClick={() => void copy()} disabled={!r} className="w-11 h-11 rounded-full bg-surface-container-lowest/60 backdrop-blur-md text-on-surface hover:bg-surface-container-lowest flex items-center justify-center shadow-sm transition-all disabled:opacity-40" title="Copy to clipboard" aria-label="Copy to clipboard" type="button">
            <Icon name="content_copy" className="text-[18px]" />
          </button>
        </div>
      </div>
      {zoom && r && (
        <div className="fixed inset-0 z-50 flex cursor-zoom-out items-center justify-center bg-black/80 p-6" onClick={() => setZoom(false)}>
          <img src={r.sketch_image} alt="zoomed sketch" className="max-h-full max-w-full rounded-lg bg-white" style={{ width: 640, ...style }} />
        </div>
      )}
    </section>
  );
}
