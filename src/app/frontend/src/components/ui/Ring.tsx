/** Circular gauge (Stitch "ring"): value 0..1, big text + caption in the middle. */
export default function Ring({ value, main, caption, size = "w-28 h-28", stroke = "url(#ringGradient)" }: { value: number; main: string; caption: string; size?: string; stroke?: string }) {
  const v = Math.min(1, Math.max(0, value));
  return (
    <div className={`relative ${size} flex items-center justify-center shrink-0`}>
      <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
        <defs>
          <linearGradient id="ringGradient" x1="0%" x2="100%" y1="0%" y2="100%">
            <stop offset="0%" stopColor="#f59e0b" />
            <stop offset="100%" stopColor="#facc15" />
          </linearGradient>
        </defs>
        <circle className="stroke-surface-container-highest/60" cx="50" cy="50" fill="none" r="40" strokeWidth="8" />
        <circle className="transition-all duration-1000 ease-out" cx="50" cy="50" fill="none" r="40" stroke={stroke} strokeDasharray="251.2" strokeDashoffset={251.2 * (1 - v)} strokeLinecap="round" strokeWidth="8" />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
        <span className="font-data-metric text-data-metric text-on-surface font-bold leading-none">{main}</span>
        <span className="font-label-caption text-label-caption text-on-surface-variant mt-0.5">{caption}</span>
      </div>
    </div>
  );
}
