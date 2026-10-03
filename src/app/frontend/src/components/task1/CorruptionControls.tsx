import type { CorruptionKind } from "../../types";

export const KINDS: { id: CorruptionKind; label: string }[] = [
  { id: "salt_and_pepper", label: "Salt-and-pepper" },
  { id: "gaussian_blur", label: "Gaussian blur" },
  { id: "rectangular_occlusion", label: "Rectangular occlusion" },
];

export const SEVERITIES: Record<CorruptionKind, string[]> = {
  salt_and_pepper: ["p = 0.03", "p = 0.08", "p = 0.15"],
  gaussian_blur: ["k=3, σ=0.7", "k=5, σ=1.5", "k=7, σ=2.5"],
  rectangular_occlusion: ["1 box · ~10%", "2 boxes · ~20%", "3 boxes · ~35%"],
};

interface Props {
  kind: CorruptionKind;
  severity: number;
  onChange: (kind: CorruptionKind, severity: number) => void;
}

export default function CorruptionControls({ kind, severity, onChange }: Props) {
  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-2">
        {KINDS.map((k) => (
          <button
            key={k.id}
            onClick={() => onChange(k.id, severity)}
            className={`rounded-full px-3 py-1.5 text-sm ring-1 ${kind === k.id ? "bg-amber-300/60 ring-amber-400" : "ring-white/70 bg-white/50 hover:bg-white/80"}`}
          >
            {k.label}
          </button>
        ))}
      </div>
      <div className="flex flex-wrap gap-2">
        {SEVERITIES[kind].map((s, i) => (
          <button
            key={s}
            onClick={() => onChange(kind, i + 1)}
            className={`rounded-lg px-3 py-1.5 text-xs ring-1 ${severity === i + 1 ? "bg-amber-300/60 ring-amber-400" : "ring-white/70 bg-white/50 hover:bg-white/80"}`}
          >
            {["Low", "Medium", "High"][i]} · {s}
          </button>
        ))}
      </div>
    </div>
  );
}
