type Tone = "sky" | "emerald" | "amber" | "slate";

const TONES: Record<Tone, string> = {
  sky: "bg-sky-500/15 text-sky-200 ring-sky-500/40",
  emerald: "bg-emerald-500/15 text-emerald-200 ring-emerald-500/40",
  amber: "bg-amber-500/15 text-amber-200 ring-amber-500/40",
  slate: "bg-ink-800 text-slate-200 ring-ink-700",
};

export default function MetricBadge({ label, value, tone = "sky" }: { label: string; value: string; tone?: Tone }) {
  return (
    <span className={`inline-flex items-baseline gap-2 rounded-full px-3 py-1 text-xs ring-1 ${TONES[tone]}`}>
      <span className="opacity-70">{label}</span>
      <span className="font-semibold tabular-nums">{value}</span>
    </span>
  );
}
