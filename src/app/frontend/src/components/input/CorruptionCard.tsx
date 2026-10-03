import { ReactNode } from "react";
import { WorkspaceInput } from "../../hooks/useWorkspaceInput";
import type { AppliedCorruption, CorruptionKind } from "../../types";
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

const LABEL = Object.fromEntries(KINDS.map((k) => [k.id, k.label])) as Record<CorruptionKind, string>;

/** Human-readable description of what the backend applied (single corruption or a multi-step pipeline). */
export function describeApplied(a: AppliedCorruption, withType = false): string {
  if (a.type === "pipeline" && Array.isArray(a.steps))
    return a.steps.map((s) => `${LABEL[s.type as CorruptionKind]} (${SEVERITY_PARAMS[s.type as CorruptionKind][Number(s.severity) - 1]})`).join(" → ");
  const params = SEVERITY_PARAMS[a.type as CorruptionKind][Number(a.severity) - 1];
  return withType ? `${String(a.type).replace(/_/g, " ")} · ${params}` : params;
}

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
        <label className="mb-3 flex items-center gap-2 cursor-pointer select-none">
          <button
            role="switch"
            aria-checked={input.multi}
            aria-label="Use multiple corruptions"
            onClick={() => input.setMulti(!input.multi)}
            className={`w-9 h-5 rounded-full flex items-center px-0.5 transition-all ${input.multi ? "bg-primary-container justify-end" : "bg-surface-container-highest"}`}
            type="button"
          >
            <span className="w-4 h-4 rounded-full bg-surface-container-lowest shadow-sm" />
          </button>
          <span className="font-label-caption text-label-caption text-on-surface-variant">Use Multiple Corruptions (optional demo)</span>
        </label>
        {input.multi ? (
          <div className={`flex flex-col gap-2 ${input.asIs ? "opacity-40 pointer-events-none" : ""}`}>
            {input.steps.map((s, i) => (
              <div key={s.id} className="flex flex-col gap-1.5 p-2 rounded-[16px] bg-surface-container-lowest/40 shadow-inner" aria-label={`corruption step ${i + 1}`}>
                <div className="flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-primary-container text-on-primary-container flex items-center justify-center font-label-caption text-label-caption font-bold">{i + 1}</span>
                  <select
                    aria-label={`Corruption ${i + 1} type`}
                    value={s.kind}
                    onChange={(e) => input.updateStep(s.id, { kind: e.target.value as CorruptionKind })}
                    className="flex-1 rounded-full bg-surface-container-lowest/70 px-2 py-1 font-label-caption text-label-caption text-on-surface outline-none"
                  >
                    {KINDS.map((k) => (
                      <option key={k.id} value={k.id}>{k.label}</option>
                    ))}
                  </select>
                  <button
                    onClick={() => input.removeStep(s.id)}
                    disabled={input.steps.length <= 1}
                    aria-label={`Remove corruption ${i + 1}`}
                    className="px-2.5 py-1 rounded-full text-error font-label-caption text-label-caption hover:bg-error-container/50 disabled:opacity-30"
                    type="button"
                  >
                    Remove
                  </button>
                </div>
                <div className="flex items-center gap-1.5">
                  {["Low", "Medium", "High"].map((name, j) => (
                    <button
                      key={name}
                      onClick={() => input.updateStep(s.id, { severity: j + 1 })}
                      aria-label={`Corruption ${i + 1} severity ${name}`}
                      className={`flex-1 py-1 rounded-full font-label-caption text-label-caption transition-all ${
                        s.severity === j + 1 ? "bg-gradient-to-r from-[#f59e0b] to-[#facc15] text-[#121d26] font-bold shadow-sm" : "bg-surface-container-lowest/50 text-on-surface-variant hover:bg-surface-container-lowest/80"
                      }`}
                      type="button"
                    >
                      {name}
                    </button>
                  ))}
                </div>
              </div>
            ))}
            <button
              onClick={input.addStep}
              disabled={input.steps.length >= 6}
              className="py-1.5 rounded-full border border-dashed border-primary/60 text-primary font-label-prominent text-label-prominent hover:bg-primary-container/20 disabled:opacity-40"
              type="button"
            >
              + Add Corruption
            </button>
            <div aria-label="corruption pipeline" className="mt-1 flex flex-wrap items-center gap-1 font-label-caption text-label-caption text-on-surface-variant">
              <span className="uppercase tracking-wider">Pipeline</span>
              <span className="px-2 py-0.5 rounded-full bg-surface-container-lowest/60">Original</span>
              {input.steps.map((s) => (
                <span key={s.id} className="flex items-center gap-1">
                  <Icon name="arrow_forward" className="text-[14px]" />
                  <span className="px-2 py-0.5 rounded-full bg-primary-container/40 text-on-surface">{LABEL[s.kind]} · {SEVERITY_PARAMS[s.kind][s.severity - 1]}</span>
                </span>
              ))}
              <Icon name="arrow_forward" className="text-[14px]" />
              <span className="px-2 py-0.5 rounded-full bg-surface-container-lowest/60">Model</span>
            </div>
          </div>
        ) : (
          <>
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
          </>
        )}
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
