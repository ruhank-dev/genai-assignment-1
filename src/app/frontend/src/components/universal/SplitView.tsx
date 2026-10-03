import { useRef, useState } from "react";
import Icon, { GLASS } from "../ui/Icon";

interface Props {
  title: string;
  before: string | null; // image shown on the left (model input)
  after: string | null; // image shown on the right (restored output)
  beforeLabel: string;
  afterLabel: string;
  beforeNote: string;
  afterNote: string;
  placeholder: string | null; // preview shown before the first run
  className?: string;
}

/** Split view of input vs. output with zoom, fullscreen and a before/after slider (Stitch "Multi-Pass Synthesis" card). */
export default function SplitView({ title, before, after, beforeLabel, afterLabel, beforeNote, afterNote, placeholder, className = "col-span-12 lg:col-span-8" }: Props) {
  const box = useRef<HTMLDivElement>(null);
  const [compare, setCompare] = useState(false);
  const [pos, setPos] = useState(50);
  const [zoom, setZoom] = useState(false);
  const left = before ?? placeholder;
  return (
    <div className={`${className} ${GLASS} flex flex-col shadow-md relative`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="font-title-card text-title-card text-on-surface">{title}</span>
          <span className="font-data-tabular text-data-tabular px-2.5 py-0.5 rounded-full bg-surface-container-lowest/60 text-secondary">{compare ? "Slider View" : "Split View Active"}</span>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={() => setZoom(true)} disabled={!after} className="w-8 h-8 rounded-full bg-surface-container-lowest/60 hover:bg-surface-container-lowest flex items-center justify-center text-on-surface transition-all shadow-sm disabled:opacity-40" title="Zoom in" type="button">
            <Icon name="zoom_in" className="text-[18px]" />
          </button>
          <button onClick={() => void box.current?.requestFullscreen?.()} className="w-8 h-8 rounded-full bg-surface-container-lowest/60 hover:bg-surface-container-lowest flex items-center justify-center text-on-surface transition-all shadow-sm" title="Fullscreen" type="button">
            <Icon name="fullscreen" className="text-[18px]" />
          </button>
        </div>
      </div>
      <div ref={box} className="relative w-full aspect-[16/9] min-h-[300px] rounded-lg overflow-hidden grid grid-cols-2 gap-3 p-1.5 bg-surface-container-lowest/30 shadow-inner">
        {compare && before && after ? (
          <div className="col-span-2 relative rounded-[20px] overflow-hidden shadow-sm">
            <img src={before} alt="before" className="absolute inset-0 w-full h-full object-contain bg-surface-container-lowest/40" />
            <img src={after} alt="after" className="absolute inset-0 w-full h-full object-contain bg-surface-container-lowest/40" style={{ clipPath: `inset(0 0 0 ${pos}%)` }} />
            <input type="range" min={0} max={100} value={pos} onChange={(e) => setPos(Number(e.target.value))} aria-label="before / after position" className="absolute bottom-3 left-1/2 -translate-x-1/2 w-2/3" />
          </div>
        ) : (
          <>
            <Panel src={left} dot="bg-error" label={beforeLabel} note={beforeNote} side="left" />
            <Panel src={after} dot="bg-tertiary" label={afterLabel} note={afterNote} side="right" empty="Restored output appears here" />
          </>
        )}
        <button
          onClick={() => setCompare(!compare)}
          disabled={!before || !after}
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-10 px-3.5 py-1.5 rounded-full bg-surface-container-lowest/90 backdrop-blur-xl shadow-lg flex items-center gap-2 hover:scale-105 transition-all select-none disabled:opacity-60"
          type="button"
        >
          <Icon name="chevron_left" className="text-[16px] text-on-surface-variant" />
          <span className="font-label-prominent text-label-prominent text-on-surface whitespace-nowrap">Compare before / after</span>
          <Icon name="chevron_right" className="text-[16px] text-on-surface-variant" />
        </button>
      </div>
      {zoom && after && (
        <div className="fixed inset-0 z-50 flex cursor-zoom-out items-center justify-center bg-black/80 p-6" onClick={() => setZoom(false)}>
          <img src={after} alt="zoomed result" className="max-h-full max-w-full rounded-lg" style={{ width: 640 }} />
        </div>
      )}
    </div>
  );
}

function Panel({ src, dot, label, note, side, empty }: { src: string | null; dot: string; label: string; note: string; side: "left" | "right"; empty?: string }) {
  const pos = side === "left" ? "left-3" : "right-3";
  return (
    <div className="relative w-full h-full rounded-[20px] overflow-hidden shadow-sm bg-surface-container-lowest/40 flex items-center justify-center">
      {src ? <img src={src} alt={label} className="w-full h-full object-contain" /> : <span className="px-4 text-center font-label-caption text-label-caption text-on-surface-variant">{empty ?? "Choose an image"}</span>}
      <div className={`absolute top-3 ${pos} px-3 py-1 rounded-full bg-surface-container-lowest/75 backdrop-blur-md shadow-sm flex items-center gap-1.5`}>
        <span className={`w-2 h-2 rounded-full ${dot}`} />
        <span className="font-label-caption text-label-caption text-on-surface font-semibold">{label}</span>
      </div>
      <div className={`absolute bottom-3 ${pos} px-2.5 py-0.5 rounded-full bg-surface-container-lowest/60 backdrop-blur-sm text-on-surface-variant font-data-tabular text-data-tabular`}>{note}</div>
    </div>
  );
}
