type Tone = "sky" | "emerald" | "amber" | "slate";

// "sky" keeps its prop name for existing callers; it now renders the indigo secondary colour of the glass design.
const TONES: Record<Tone, string> = {
  sky: "bg-indigo-100/80 text-indigo-700",
  emerald: "bg-emerald-100/80 text-emerald-700",
  amber: "bg-amber-100/90 text-amber-800",
  slate: "bg-white/70 text-slate-600",
};

export default function MetricBadge({ label, value, tone = "sky" }: { label: string; value: string; tone?: Tone }) {
  return (
    <span className={`inline-flex items-baseline gap-2 rounded-full px-3 py-1.5 text-xs shadow-sm ${TONES[tone]}`}>
      <span className="opacity-70">{label}</span>
      <span className="font-bold tabular-nums">{value}</span>
    </span>
  );
}
