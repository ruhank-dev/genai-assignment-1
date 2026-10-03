const STYLES = [
  { id: 1, title: "Style 1", desc: "Fine, light contours", weight: 1 },
  { id: 2, title: "Style 2", desc: "Heavy dark hatching", weight: 4 },
  { id: 3, title: "Style 3", desc: "Medium-weight contours", weight: 2.5 },
];

export default function StyleSelector({ value, onChange }: { value: number; onChange: (s: number) => void }) {
  return (
    <div role="radiogroup" aria-label="Sketch style" className="grid gap-3 sm:grid-cols-3">
      {STYLES.map((s) => (
        <button
          key={s.id}
          role="radio"
          aria-checked={value === s.id}
          onClick={() => onChange(s.id)}
          className={`rounded-xl p-4 text-left ring-1 transition ${value === s.id ? "bg-sky-500/15 shadow-glow ring-sky-400" : "bg-ink-900 ring-ink-700 hover:ring-slate-500"}`}
        >
          <svg viewBox="0 0 120 24" className="mb-3 h-6 w-full text-slate-200">
            <path d="M4 18 C 30 2, 50 22, 74 8 S 104 14, 116 6" fill="none" stroke="currentColor" strokeWidth={s.weight} strokeLinecap="round" />
          </svg>
          <div className="font-semibold">{s.title}</div>
          <div className="text-xs text-slate-400">{s.desc}</div>
        </button>
      ))}
    </div>
  );
}
