import { useState } from "react";
import type { Metrics } from "../../types";
import Icon, { GLASS } from "../ui/Icon";

interface Props {
  input: string | null;
  restored: string | null;
  heat: string | null;
  inputLabel: string;
  restoredLabel: string;
  metrics: Metrics | null;
  vsClean: boolean; // metrics measured against the clean reference (true) or against the input (false)
  l1Input: number | null;
  className?: string;
  title?: string;
}

/** "Visual Restoration & Loupe Inspection" (Stitch): input vs restored, 3x loupe on the restored centre, A/B diff overlay. */
export default function LoupeCard({ input, restored, heat, inputLabel, restoredLabel, metrics, vsClean, l1Input, className = "col-span-12 lg:col-span-8", title = "Visual Restoration & Loupe Inspection" }: Props) {
  const [diff, setDiff] = useState(false);
  return (
    <div className={`${className} ${GLASS} shadow-sm flex flex-col justify-between`}>
      <div className="flex items-center justify-between mb-space-sm">
        <div>
          <span className="font-label-caption text-label-caption uppercase tracking-wider text-on-surface-variant font-semibold">High-Fidelity Inspection</span>
          <h2 className="font-headline-sm text-headline-sm text-on-surface">{title}</h2>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-2.5 py-1 rounded-full bg-surface-container-lowest/70 text-on-surface font-data-tabular text-data-tabular shadow-sm">PSNR: {metrics ? `${metrics.psnr.toFixed(1)} dB` : "—"}</span>
          <span className="px-2.5 py-1 rounded-full bg-surface-container-lowest/70 text-on-surface font-data-tabular text-data-tabular shadow-sm">SSIM: {metrics ? metrics.ssim.toFixed(3) : "—"}</span>
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-space-md relative">
        <Pane src={input} empty="Input appears here" tag={inputLabel} tagClass="bg-surface-container-lowest/80 text-on-surface" foot={l1Input === null ? "Input to the model" : `Input L1 error: ${l1Input.toFixed(4)}`} footTag="Input" footClass="text-error" />
        <Pane src={restored} overlay={diff ? heat : null} empty="Restored output appears here" tag={restoredLabel} tagClass="bg-secondary text-on-secondary" icon="auto_fix_high" loupe={restored} foot={metrics ? `Output L1 error: ${metrics.l1.toFixed(4)}` : "Output of the model"} footTag="Restored" footClass="text-tertiary" />
      </div>
      <div className="mt-3 flex items-center justify-between pt-2">
        <div className="flex items-center gap-space-xs">
          <Icon name="verified" className="text-primary-container text-[18px]" />
          <span className="font-body-sm text-body-sm text-on-surface-variant">{metrics ? `Metrics measured against the ${vsClean ? "clean reference image" : "uploaded input (no clean reference available)"}.` : "Results appear after you run the pipeline."}</span>
        </div>
        <button onClick={() => setDiff(!diff)} disabled={!heat} className={`px-3.5 py-1.5 rounded-full text-on-surface hover:bg-surface-container-lowest text-label-prominent font-label-prominent shadow-sm flex items-center gap-1.5 transition-all disabled:opacity-40 ${diff ? "bg-primary-container/60" : "bg-surface-container-lowest/80"}`} type="button">
          <Icon name="compare" className="text-[16px]" /> A/B Diff Overlay
        </button>
      </div>
    </div>
  );
}

interface PaneProps {
  src: string | null;
  empty: string;
  tag: string;
  tagClass: string;
  icon?: string;
  overlay?: string | null;
  loupe?: string | null;
  foot: string;
  footTag: string;
  footClass: string;
}

function Pane({ src, empty, tag, tagClass, icon, overlay, loupe, foot, footTag, footClass }: PaneProps) {
  return (
    <div className="relative group rounded overflow-hidden shadow-sm bg-surface-container-high/40 flex flex-col">
      <div className="relative h-64 w-full overflow-hidden flex items-center justify-center">
        {src ? <img src={src} alt={tag} className="w-full h-full object-contain" /> : <span className="px-4 text-center text-body-sm text-on-surface-variant">{empty}</span>}
        {overlay && <img src={overlay} alt="difference overlay" className="absolute inset-0 w-full h-full object-contain opacity-60 mix-blend-multiply" />}
        <div className={`absolute top-3 left-3 px-2.5 py-1 rounded-full backdrop-blur-md font-label-caption text-label-caption shadow-sm flex items-center gap-1 ${tagClass}`}>
          {icon && <Icon name={icon} className="text-[14px]" />}
          {tag}
        </div>
        {loupe && (
          <div className="absolute bottom-4 right-4 w-28 h-28 rounded-full shadow-xl bg-surface-container-lowest/90 overflow-hidden" title="3x loupe on the image centre">
            <div className="w-full h-full" style={{ backgroundImage: `url(${loupe})`, backgroundSize: "300%", backgroundPosition: "50% 50%", imageRendering: "auto" }} />
            <div className="absolute bottom-1 inset-x-0 text-center font-label-caption text-[9px] font-bold text-on-surface">3× Loupe</div>
          </div>
        )}
      </div>
      <div className="p-3 bg-surface-container-lowest/60 flex items-center justify-between">
        <span className="font-body-sm text-body-sm text-on-surface-variant">{foot}</span>
        <span className={`font-data-tabular text-data-tabular font-medium ${footClass}`}>{src ? footTag : ""}</span>
      </div>
    </div>
  );
}
