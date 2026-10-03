import type { HardRoutedRestoreResponse } from "../../types";
import Icon, { GLASS } from "../ui/Icon";

const SHORT: Record<string, string> = { clean: "Clean", salt_and_pepper: "Noise", gaussian_blur: "Blur", rectangular_occlusion: "Occlusion" };
const WHY: Record<string, string> = {
  clean: "No corruption pattern was detected, so the identity branch returns the image unchanged (exact copy, no restoration cost).",
  salt_and_pepper: "Isolated black/white pixel spikes indicate impulsive noise. The classifier routed execution to the salt-and-pepper specialist autoencoder.",
  gaussian_blur: "Low high-frequency energy indicates a Gaussian low-pass degradation. The classifier routed execution to the blur specialist autoencoder.",
  rectangular_occlusion: "Large flat black regions indicate missing rectangular areas. The classifier routed execution to the occlusion specialist autoencoder.",
};

interface Props {
  r: HardRoutedRestoration | null;
  bypass: boolean;
  onBypass: (v: boolean) => void;
}
type HardRoutedRestoration = HardRoutedRestoreResponse;

export default function EngineCard({ r, bypass, onBypass }: Props) {
  const probs = r ? Object.entries(r.class_probabilities).sort((a, b) => b[1] - a[1]) : [];
  const top = probs[0]?.[1] ?? 0;
  const margin = probs.length > 1 ? top - probs[1][1] : 0;
  const ring = 251.2 * (1 - top);
  const steps = r
    ? [
        { icon: "photo_camera", t: "Raw Input", s: "128×128", cls: "bg-surface-container-highest text-on-surface" },
        { icon: "insights", t: "Classifier", s: `${r.inference_time.classifier_ms.toFixed(1)} ms`, cls: "bg-primary-container text-on-primary-container" },
        { icon: r.selected_expert === "Identity Bypass" ? "content_copy" : "auto_fix_high", t: r.selected_expert === "Identity Bypass" ? "Identity Bypass" : "Specialist", s: `${r.inference_time.specialist_ms.toFixed(1)} ms`, cls: "bg-secondary text-on-secondary" },
        { icon: "check_circle", t: "Final Merge", s: `${r.inference_time.total_ms.toFixed(1)} ms Total`, cls: "bg-tertiary text-on-tertiary" },
      ]
    : [];
  return (
    <div className={`col-span-12 lg:col-span-7 ${GLASS} shadow-sm flex flex-col justify-between relative overflow-hidden`}>
      <div className="absolute -left-12 bottom-0 w-48 h-48 rounded-full bg-secondary/10 blur-3xl pointer-events-none" />
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Icon name="alt_route" className="text-secondary" />
            <h2 className="font-headline-sm text-headline-sm text-on-surface">Hard Routing Engine</h2>
          </div>
          <div className="flex items-center gap-space-xs bg-surface-container-lowest/60 px-3 py-1.5 rounded-full shadow-sm">
            <span className="font-label-prominent text-label-prominent text-on-surface-variant">Force Identity Bypass</span>
            <button role="switch" aria-checked={bypass} aria-label="Force identity bypass" onClick={() => onBypass(!bypass)} className={`w-10 h-6 rounded-full p-0.5 flex items-center transition-all ${bypass ? "bg-primary-container justify-end" : "bg-surface-container-highest/80"}`} type="button">
              <div className="w-5 h-5 rounded-full bg-surface-container-lowest shadow-sm" />
            </button>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-12 gap-space-md items-center py-2">
          <div className="md:col-span-4 flex flex-col items-center justify-center p-3 rounded bg-surface-container-lowest/50 shadow-sm">
            <div className="relative w-32 h-32 flex items-center justify-center">
              <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                <circle className="text-surface-container-highest/60" cx="50" cy="50" fill="transparent" r="40" stroke="currentColor" strokeWidth="8" />
                <circle className="text-secondary transition-all duration-1000" cx="50" cy="50" fill="transparent" r="40" stroke="currentColor" strokeDasharray="251.2" strokeDashoffset={r ? ring : 251.2} strokeLinecap="round" strokeWidth="8" />
                <circle className="text-primary-container" cx="50" cy="50" fill="transparent" opacity="0.8" r="32" stroke="currentColor" strokeDasharray="201" strokeDashoffset={r ? 201 * (1 - top) : 201} strokeWidth="2" />
              </svg>
              <div className="absolute flex flex-col items-center">
                <span className="font-display-hero text-headline-lg font-bold text-on-surface leading-none">{r ? `${Math.round(top * 100)}%` : "—"}</span>
                <span className="font-label-caption text-label-caption text-on-surface-variant uppercase tracking-widest mt-0.5">{r ? SHORT[r.predicted_class] : "Idle"}</span>
              </div>
            </div>
            <span className="font-data-tabular text-data-tabular text-on-surface-variant mt-2">Margin vs 2nd: {r ? `+${margin.toFixed(2)}` : "—"}</span>
          </div>
          <div className="md:col-span-8 flex flex-col gap-3">
            <div className="p-3.5 rounded bg-secondary-container text-on-secondary-container shadow-sm flex items-center gap-3">
              <Icon name="verified_user" className="text-[24px]" />
              <div className="min-w-0">
                <div className="font-label-caption text-label-caption uppercase tracking-wider opacity-85">Execution Mandate{r?.forced_bypass ? " (forced)" : ""}</div>
                <div className="font-title-card text-title-card font-bold truncate">{r ? `Routed to: ${r.selected_expert}` : "Run the pipeline to see the routing decision"}</div>
              </div>
            </div>
            <p className="font-body-sm text-body-sm text-on-surface-variant">{r ? (r.forced_bypass ? "The identity bypass was forced by the switch above; the classifier probabilities are still reported." : WHY[r.predicted_class]) : "The classifier looks at the corrupted image, picks one corruption class (argmax) and dispatches to exactly one specialist, or to the identity branch for clean images."}</p>
          </div>
        </div>
        <div className="mt-4 p-3 rounded bg-surface-container-lowest/60 shadow-sm flex flex-col gap-2">
          <span className="font-label-caption text-label-caption uppercase tracking-wider text-on-surface-variant">Deterministic Execution Pipeline</span>
          <div className="flex items-center justify-between text-center overflow-x-auto py-1 gap-2 min-h-[64px]">
            {steps.length === 0 && <span className="text-body-sm text-on-surface-variant mx-auto">Input → Classifier → Specialist / Identity → Output</span>}
            {steps.map((s, i) => (
              <div key={s.t} className="flex items-center gap-2">
                {i > 0 && <Icon name="arrow_forward" className="text-outline-variant shrink-0" />}
                <div className="flex flex-col items-center min-w-[80px]">
                  <div className={`w-9 h-9 rounded-full flex items-center justify-center shadow-sm ${s.cls}`}>
                    <Icon name={s.icon} className="text-[18px]" />
                  </div>
                  <span className="font-label-caption text-label-caption text-on-surface mt-1 font-semibold">{s.t}</span>
                  <span className="font-data-tabular text-data-tabular text-on-surface-variant">{s.s}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
