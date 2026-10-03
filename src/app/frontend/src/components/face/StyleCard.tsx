import Icon, { GLASS } from "../ui/Icon";

export const STYLES = [
  { id: 1, title: "Fine Light Contours", desc: "Thin, light graphite-like outlines with lots of white paper.", tag: "Linework" },
  { id: 2, title: "Heavy Hatching", desc: "Dense dark strokes and cross-hatching with strong tonal contrast.", tag: "Tonal Depth" },
  { id: 3, title: "Medium Dynamic", desc: "Medium-weight contour strokes between the two other styles.", tag: "Expressive" },
];

export interface Adjust {
  weight: number; // display contrast multiplier
  tone: "white" | "warm" | "cool";
}

interface Props {
  style: number;
  onStyle: (s: number) => void;
  adjust: Adjust;
  onAdjust: (a: Adjust) => void;
}

const TONES: { id: Adjust["tone"]; label: string }[] = [
  { id: "white", label: "Paper white" },
  { id: "warm", label: "Warm" },
  { id: "cool", label: "Cool" },
];

/** "Artistic Sketch Styles" card: three FS2K style cards (thumbnails are real generator outputs) + display adjustments. */
export default function StyleCard({ style, onStyle, adjust, onAdjust }: Props) {
  return (
    <section className={`col-span-12 lg:col-span-7 ${GLASS} flex flex-col justify-between shadow-lg relative`}>
      <div className="flex items-center justify-between mb-space-md">
        <div>
          <h2 className="font-headline-sm text-headline-sm text-on-surface">Artistic Sketch Styles</h2>
          <p className="font-body-sm text-body-sm text-on-surface-variant">Learned style embedding conditions the generator and the discriminator</p>
        </div>
        <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-secondary-fixed/50 text-secondary font-label-caption text-label-caption shadow-sm">
          <Icon name="brush" className="text-[16px]" />
          FS2K · 3 styles
        </div>
      </div>
      <div role="radiogroup" aria-label="Sketch style" className="grid grid-cols-1 md:grid-cols-3 gap-space-sm mb-space-md">
        {STYLES.map((s) => {
          const on = style === s.id;
          return (
            <div
              key={s.id}
              role="radio"
              aria-checked={on}
              aria-label={`Style ${s.id} ${s.title}`}
              tabIndex={0}
              onClick={() => onStyle(s.id)}
              onKeyDown={(e) => e.key === "Enter" && onStyle(s.id)}
              className={`cursor-pointer rounded p-3 transition-all flex flex-col justify-between group relative ${on ? "bg-surface-container-lowest/90 shadow-xl scale-[1.02] ring-2 ring-primary-container" : "bg-surface-container-lowest/50 hover:bg-surface-container-lowest/80 shadow-sm"}`}
            >
              <div className="relative w-full h-24 rounded overflow-hidden mb-2.5 bg-surface-container-low">
                <img src={`/samples/style_${s.id}.jpg`} alt={`Style ${s.id} example`} className="w-full h-full object-cover group-hover:scale-105 transition-all duration-300" />
                <span className={`absolute top-1.5 right-1.5 px-2 py-0.5 rounded-full font-label-caption text-label-caption ${on ? "bg-primary-container text-on-primary-container font-bold shadow-sm" : "bg-surface-container-lowest/80 text-on-surface-variant"}`}>{on ? "ACTIVE" : `Style ${s.id}`}</span>
              </div>
              <div>
                <div className="flex items-center gap-1">
                  <span className={`font-title-card text-title-card text-on-surface ${on ? "font-bold" : ""}`}>{s.title}</span>
                  {on && <Icon name="verified" className="text-[16px] text-primary-container" fill />}
                </div>
                <span className="font-body-sm text-xs text-on-surface-variant block mt-0.5">{s.desc}</span>
              </div>
              <div className="mt-3 flex items-center justify-between">
                <span className={`font-label-caption text-label-caption ${on ? "text-primary font-semibold" : "text-on-surface-variant"}`}>{s.tag}</span>
                <div className={`w-8 h-4 rounded-full flex items-center p-0.5 ${on ? "bg-primary-container justify-end" : "bg-surface-container-highest"}`}>
                  <div className="w-3 h-3 rounded-full bg-surface-container-lowest shadow-sm" />
                </div>
              </div>
            </div>
          );
        })}
      </div>
      <div className="p-space-sm rounded bg-surface-container-lowest/55 backdrop-blur-md flex flex-col gap-space-sm shadow-sm">
        <div className="flex items-center justify-between text-body-sm">
          <span className="font-label-prominent text-label-prominent text-on-surface flex items-center gap-1.5">
            <Icon name="line_weight" className="text-[18px] text-primary" />
            Stroke Weight (display adjustment)
          </span>
          <span className="font-data-tabular text-data-tabular text-primary font-bold">×{adjust.weight.toFixed(2)}</span>
        </div>
        <input type="range" min={0.6} max={1.8} step={0.05} value={adjust.weight} onChange={(e) => onAdjust({ ...adjust, weight: Number(e.target.value) })} aria-label="Stroke weight" className="w-full h-2 bg-surface-container-highest rounded-full appearance-none cursor-pointer accent-primary-container" />
        <div className="flex items-center justify-between pt-1">
          <span className="font-body-sm text-body-sm text-on-surface-variant">Paper tone <span className="text-label-caption">(does not change the model output)</span></span>
          <div className="flex items-center p-1 rounded-full bg-surface-container-highest/60 backdrop-blur-md gap-1">
            {TONES.map((t) => (
              <button key={t.id} onClick={() => onAdjust({ ...adjust, tone: t.id })} className={`px-2.5 py-1 rounded-full font-label-caption text-label-caption ${adjust.tone === t.id ? "bg-surface-container-lowest text-on-surface font-semibold shadow-sm" : "text-on-surface-variant hover:text-on-surface"}`} type="button">
                {t.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
