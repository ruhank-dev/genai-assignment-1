import { ReactNode } from "react";
import { WorkspaceInput } from "../../hooks/useWorkspaceInput";
import type { CorruptionKind } from "../../types";
import Icon, { GLASS, PRIMARY_BTN } from "../ui/Icon";

export const KINDS: { id: CorruptionKind; label: string }[] = [
  { id: "salt_and_pepper", label: "Salt & Pepper" },
  { id: "gaussian_blur", label: "Gaussian blur" },
  { id: "rectangular_occlusion", label: "Occlusion" },
];

export const SEVERITY_PARAMS: Record<CorruptionKind, string[]> = {
  salt_and_pepper: ["p = 0.03", "p = 0.08", "p = 0.15"],
  gaussian_blur: ["k=3, σ=0.7", "k=5, σ=1.5", "k=7, σ=2.5"],
  rectangular_occlusion: ["1 box · ~10%", "2 boxes · ~20%", "3 boxes · ~35%"],
};

interface Props {
  input: WorkspaceInput;
  action: { label: string; icon: string; busy: boolean; onClick: () => void };
  className?: string;
  children?: ReactNode; // extra controls rendered above the action button
}

/** "Runtime Corruption" card (Stitch) with the primary action button. */
export default function CorruptionCard({ input, action, className = "col-span-12 lg:col-span-4", children }: Props) {
  return (
    <div className={`${className} ${GLASS} flex flex-col justify-between`}>
      <div>
        <div className="flex items-center justify-between mb-3">
          <span className="font-title-card text-title-card text-on-surface">Runtime Corruption</span>
          <Icon name="tune" className="text-[18px] text-on-surface-variant" />
        </div>
        <div className={`flex items-center gap-1.5 p-1 rounded-full bg-surface-container-lowest/50 shadow-inner ${input.asIs ? "opacity-40 pointer-events-none" : ""}`}>
          {KINDS.map((k) => (
            <button
              key={k.id}
              onClick={() => input.setKind(k.id)}
              className={`flex-1 py-1.5 px-2 rounded-full font-label-caption text-label-caption text-center transition-all ${
                input.kind === k.id ? "bg-surface-container-lowest text-on-surface shadow-sm font-semibold" : "text-on-surface-variant hover:text-on-surface"
              }`}
              type="button"
            >
              {k.label}
            </button>
          ))}
        </div>
        <div className={`mt-4 ${input.asIs ? "opacity-40 pointer-events-none" : ""}`}>
          <div className="flex items-center justify-between text-on-surface-variant mb-2">
            <span className="font-label-caption text-label-caption uppercase tracking-wider">Severity</span>
            <span className="font-data-tabular text-data-tabular text-primary font-semibold">{SEVERITY_PARAMS[input.kind][input.severity - 1]}</span>
          </div>
          <div className="flex items-center gap-2">
            {["Low", "Medium", "High"].map((s, i) => (
              <button
                key={s}
                onClick={() => input.setSeverity(i + 1)}
                className={`flex-1 py-1.5 rounded-full font-label-prominent text-label-prominent text-center transition-all ${
                  input.severity === i + 1 ? "bg-gradient-to-r from-[#f59e0b] to-[#facc15] text-[#121d26] shadow-sm font-bold" : "bg-surface-container-lowest/50 text-on-surface-variant hover:bg-surface-container-lowest/80"
                }`}
                type="button"
              >
                {s}
              </button>
            ))}
          </div>
        </div>
        <label className="mt-3 flex items-center gap-2 cursor-pointer select-none">
          <button
            role="switch"
            aria-checked={input.asIs}
            aria-label="Image is already corrupted"
            onClick={() => input.setAsIs(!input.asIs)}
            className={`w-9 h-5 rounded-full flex items-center px-0.5 transition-all ${input.asIs ? "bg-primary-container justify-end" : "bg-surface-container-highest"}`}
            type="button"
          >
            <span className="w-4 h-4 rounded-full bg-surface-container-lowest shadow-sm" />
          </button>
          <span className="font-label-caption text-label-caption text-on-surface-variant">Image is already corrupted (skip corruption)</span>
        </label>
        {children}
      </div>
      <div className="mt-5">
        <button className={PRIMARY_BTN} disabled={!input.file || action.busy} onClick={action.onClick} type="button">
          <Icon name={action.icon} className="text-[20px]" />
          <span>{action.busy ? "Running…" : action.label}</span>
        </button>
      </div>
    </div>
  );
}
