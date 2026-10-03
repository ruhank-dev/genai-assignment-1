const ROWS: { key: string; label: string; bar: string }[] = [
  { key: "clean", label: "Clean", bar: "bg-emerald-400" },
  { key: "salt_and_pepper", label: "Salt-and-Pepper", bar: "bg-amber-400" },
  { key: "gaussian_blur", label: "Gaussian Blur", bar: "bg-sky-400" },
  { key: "rectangular_occlusion", label: "Rectangular Occlusion", bar: "bg-rose-400" },
];

export default function ClassifierProbabilities({ probs, predicted }: { probs: Record<string, number>; predicted: string }) {
  return (
    <div className="space-y-3 rounded-xl bg-ink-900 p-4 ring-1 ring-ink-700">
      <div className="text-sm font-semibold">Classifier probabilities</div>
      {ROWS.map((r) => {
        const p = probs[r.key] ?? 0;
        return (
          <div key={r.key} className={r.key === predicted ? "" : "opacity-70"}>
            <div className="mb-1 flex justify-between text-xs">
              <span className={r.key === predicted ? "font-semibold" : ""}>{r.label}</span>
              <span className="tabular-nums">{(p * 100).toFixed(2)}%</span>
            </div>
            <div className="h-2.5 overflow-hidden rounded-full bg-ink-800">
              <div className={`h-full ${r.bar}`} style={{ width: `${Math.max(p * 100, 0.5)}%` }} />
            </div>
          </div>
        );
      })}
    </div>
  );
}
