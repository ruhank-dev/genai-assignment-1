const EXPERTS: { key: string; label: string; bar: string }[] = [
  { key: "identity_clean", label: "Identity (clean)", bar: "bg-emerald-400" },
  { key: "expert_salt", label: "Salt expert", bar: "bg-amber-400" },
  { key: "expert_blur", label: "Blur expert", bar: "bg-sky-400" },
  { key: "expert_occlusion", label: "Occlusion expert", bar: "bg-rose-400" },
];

export default function GatingWeights({ weights, dominant }: { weights: Record<string, number>; dominant: string }) {
  const sum = Object.values(weights).reduce((a, b) => a + b, 0);
  return (
    <div className="space-y-3 rounded-xl bg-ink-900 p-4 ring-1 ring-ink-700">
      <div className="flex items-center justify-between text-sm font-semibold">
        <span>Gating weights</span>
        <span className="text-xs font-normal text-slate-400">Σ = {(sum * 100).toFixed(2)}%</span>
      </div>
      {EXPERTS.map((e) => {
        const w = weights[e.key] ?? 0;
        const top = e.key === dominant;
        return (
          <div key={e.key} className={`rounded-lg p-2 ${top ? "shadow-glow" : ""}`}>
            <div className="mb-1 flex justify-between text-xs">
              <span className="flex items-center gap-2">
                {e.label}
                {top && <span className="rounded bg-sky-500/30 px-1.5 py-0.5 text-[10px] font-semibold text-sky-100">DOMINANT</span>}
              </span>
              <span className="tabular-nums">{(w * 100).toFixed(2)}%</span>
            </div>
            <div className="h-3 overflow-hidden rounded-full bg-ink-800">
              <div className={`h-full ${e.bar}`} style={{ width: `${w * 100}%` }} />
            </div>
          </div>
        );
      })}
    </div>
  );
}
