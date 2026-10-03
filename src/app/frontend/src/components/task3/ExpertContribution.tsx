const PARTS: { key: string; sym: string; color: string }[] = [
  { key: "identity_clean", sym: "x", color: "bg-emerald-400" },
  { key: "expert_salt", sym: "A_salt(x)", color: "bg-amber-400" },
  { key: "expert_blur", sym: "A_blur(x)", color: "bg-sky-400" },
  { key: "expert_occlusion", sym: "A_occ(x)", color: "bg-rose-400" },
];

/** Shows x̂ = Σ w_k · branch_k as a stacked contribution strip. */
export default function ExpertContribution({ weights }: { weights: Record<string, number> }) {
  return (
    <div className="rounded-xl bg-ink-900 p-4 ring-1 ring-ink-700">
      <div className="mb-2 text-sm font-semibold">Expert contribution to the output</div>
      <div className="flex h-8 overflow-hidden rounded-lg">
        {PARTS.map((p) => (
          <div key={p.key} className={`${p.color} flex items-center justify-center text-[10px] font-semibold text-ink-950`} style={{ width: `${(weights[p.key] ?? 0) * 100}%` }}>
            {(weights[p.key] ?? 0) > 0.08 ? `${((weights[p.key] ?? 0) * 100).toFixed(0)}%` : ""}
          </div>
        ))}
      </div>
      <p className="mt-3 font-mono text-xs text-slate-300">
        x̂ = {PARTS.map((p) => `${(weights[p.key] ?? 0).toFixed(2)}·${p.sym}`).join(" + ")}
      </p>
      <p className="mt-1 text-xs text-slate-400">The output is a convex combination: all four branches run and the gate decides how much each contributes.</p>
    </div>
  );
}
