const NAMES: Record<string, string> = {
  clean: "Clean",
  salt_and_pepper: "Salt-and-Pepper",
  gaussian_blur: "Gaussian Blur",
  rectangular_occlusion: "Rectangular Occlusion",
};

interface Props {
  predicted: string;
  probability: number;
  expert: string;
}

export default function RoutingCard({ predicted, probability, expert }: Props) {
  const bypass = expert === "Identity Bypass";
  return (
    <div className="glass p-4 ring-2 ring-amber-400/70">
      <div className="text-xs uppercase tracking-wide text-slate-500">Routing decision (argmax)</div>
      <div className="mt-1 text-lg font-bold">
        {NAMES[predicted] ?? predicted} <span className="text-indigo-600">({(probability * 100).toFixed(1)}%)</span>
      </div>
      <div className="mt-2 text-sm">
        Routed to: <span className={`rounded px-2 py-0.5 font-mono text-xs ${bypass ? "bg-emerald-100 text-emerald-700" : "bg-indigo-100 text-indigo-700"}`}>{expert}</span>
      </div>
      {bypass && <p className="mt-2 text-xs text-slate-500">The image looks clean, so no restoration expert is run (exact copy).</p>}
    </div>
  );
}
