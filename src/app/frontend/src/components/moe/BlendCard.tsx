import { GLASS_TALL } from "../ui/Icon";
import { EXPERTS, pct } from "./GatingCard";

const R = 48;
const CIRC = 2 * Math.PI * R;

/** "Synthesis Blend": x̂ = Σ wᵢ·Eᵢ(x) as a multi-segment donut and stacked bar of the real gate weights. */
export default function BlendCard({ weights, dominant }: { weights: Record<string, number> | null; dominant: string | null }) {
  let offset = 0;
  const top = EXPERTS.find((e) => e.key === dominant);
  return (
    <div className={`col-span-12 lg:col-span-3 ${GLASS_TALL} flex flex-col justify-between`}>
      <div className="flex flex-col gap-1">
        <div className="flex items-center justify-between">
          <h3 className="font-title-card text-title-card text-on-surface">Synthesis Blend</h3>
          <span className="px-2 py-0.5 rounded-full bg-tertiary-container/30 text-on-tertiary-container font-label-caption text-label-caption">Linear Comb.</span>
        </div>
        <div className="mt-2 px-3 py-1.5 rounded-xl bg-surface-container-lowest/80 shadow-sm flex items-center justify-center">
          <span className="font-title-card text-body-md text-primary tracking-wide">x̂ = Σ wᵢ · Eᵢ(x)</span>
        </div>
      </div>
      <div className="relative w-44 h-44 mx-auto my-3 flex items-center justify-center">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
          <circle className="text-surface-container" cx="60" cy="60" fill="none" r={R} stroke="currentColor" strokeWidth="12" />
          {weights &&
            EXPERTS.map((e) => {
              const len = (weights[e.key] ?? 0) * CIRC;
              const el = <circle key={e.key} className={e.stroke} cx="60" cy="60" fill="none" r={R} stroke="currentColor" strokeWidth="12" strokeDasharray={`${len} ${CIRC - len}`} strokeDashoffset={-offset} />;
              offset += len;
              return el;
            })}
        </svg>
        <div className="absolute flex flex-col items-center justify-center text-center">
          <span className="font-data-metric text-data-metric text-on-surface leading-tight">{weights && dominant ? pct(weights[dominant]) : "—"}</span>
          <span className="font-label-caption text-label-caption text-on-surface-variant font-semibold">{top ? top.name : "No result"}</span>
        </div>
      </div>
      <div className="flex flex-col gap-2">
        <span className="font-label-caption text-label-caption text-on-surface-variant">Weight allotment</span>
        <div className="w-full h-3 rounded-full bg-surface-container flex overflow-hidden p-0.5 gap-0.5">
          {EXPERTS.map((e) => (
            <div key={e.key} className={`h-full ${e.bar}`} style={{ width: `${(weights?.[e.key] ?? 0) * 100}%` }} title={`${e.tag}: ${weights ? pct(weights[e.key]) : "—"}`} />
          ))}
        </div>
        <div className="flex items-center justify-between text-on-surface-variant font-data-tabular text-data-tabular pt-1">
          {EXPERTS.map((e) => (
            <span key={e.key} className={`flex items-center gap-1 ${dominant === e.key ? "font-bold text-on-surface" : ""}`}>
              <span className={`w-1.5 h-1.5 rounded-full ${e.dot}`} />
              {weights ? pct(weights[e.key]) : "—"}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
