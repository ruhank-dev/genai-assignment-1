import { GLASS_TALL } from "../ui/Icon";
import Icon from "../ui/Icon";

export const EXPERTS = [
  { key: "identity_clean", tag: "E₁", name: "Identity branch", sub: "x (no restoration)", dot: "bg-secondary", bar: "bg-secondary", stroke: "text-secondary" },
  { key: "expert_salt", tag: "E₂", name: "Salt expert", sub: "Task 2 specialist", dot: "bg-primary-container", bar: "bg-primary-container", stroke: "text-primary-container" },
  { key: "expert_blur", tag: "E₃", name: "Blur expert", sub: "Task 2 specialist", dot: "bg-tertiary", bar: "bg-tertiary", stroke: "text-tertiary" },
  { key: "expert_occlusion", tag: "E₄", name: "Occlusion expert", sub: "Task 2 specialist", dot: "bg-outline", bar: "bg-outline", stroke: "text-outline" },
];

export const pct = (w: number) => `${(w * 100).toFixed(w > 0.9995 ? 1 : w < 0.0005 ? 2 : 1)}%`;

export default function GatingCard({ weights, dominant, tau }: { weights: Record<string, number> | null; dominant: string | null; tau: number }) {
  return (
    <div className={`col-span-12 lg:col-span-5 ${GLASS_TALL} flex flex-col justify-between`}>
      <div className="flex flex-col gap-1">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Icon name="tune" className="text-secondary text-[22px]" />
            <h2 className="font-headline-sm text-headline-sm text-on-surface">Soft Gating Distribution</h2>
          </div>
          <span className="px-2.5 py-1 rounded-full bg-surface-container-high/70 text-on-surface-variant font-data-tabular text-data-tabular">w ∈ Δ³</span>
        </div>
        <p className="font-body-sm text-body-sm text-on-surface-variant">w = softmax( G(x) / τ ),  Σ wᵢ = 1</p>
      </div>
      <div className="flex flex-col gap-3.5 my-space-md">
        {EXPERTS.map((e) => {
          const w = weights?.[e.key] ?? 0;
          const top = dominant === e.key;
          return top ? (
            <div key={e.key} className="p-3.5 rounded-2xl bg-gradient-to-r from-primary-container/20 via-surface-container-lowest/90 to-primary-container/10 shadow-md relative overflow-hidden">
              <div className="absolute -right-6 -bottom-6 w-24 h-24 bg-primary-container/20 rounded-full blur-2xl pointer-events-none" />
              <div className="flex items-center justify-between relative z-10">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-primary-container animate-pulse" />
                  <span className="font-title-card text-title-card text-on-surface font-bold">{e.tag}: {e.name}</span>
                  <span className="px-2 py-0.5 rounded-full bg-primary-container text-on-primary font-label-caption text-label-caption font-bold tracking-wide">DOMINANT EXPERT</span>
                </div>
                <span className="font-data-metric text-data-metric text-on-surface font-bold">{pct(w)}</span>
              </div>
              <div className="w-full h-2.5 rounded-full bg-surface-container-highest overflow-hidden mt-2 relative z-10">
                <div className="h-full rounded-full bg-gradient-to-r from-primary-container to-inverse-primary shadow-sm transition-all duration-1000" style={{ width: `${w * 100}%` }} />
              </div>
            </div>
          ) : (
            <div key={e.key} className="p-3 rounded-2xl bg-surface-container-lowest/60 shadow-sm flex flex-col gap-1.5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${e.dot}`} />
                  <span className="font-title-card text-title-card text-on-surface">{e.tag}: {e.name}</span>
                  <span className="font-label-caption text-label-caption text-on-surface-variant">{e.sub}</span>
                </div>
                <span className="font-data-metric text-headline-sm text-on-surface">{weights ? pct(w) : "—"}</span>
              </div>
              <div className="w-full h-2 rounded-full bg-surface-container overflow-hidden p-0.5">
                <div className={`h-full rounded-full ${e.bar} transition-all duration-1000`} style={{ width: `${w * 100}%` }} />
              </div>
            </div>
          );
        })}
      </div>
      <div className="pt-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="font-label-caption text-label-caption text-on-surface-variant">Temperature τ</span>
          <span className="px-2.5 py-1 rounded-full bg-surface-container-lowest/80 font-data-tabular text-data-tabular text-on-surface shadow-sm">{tau.toFixed(2)} (baked into the ONNX graph)</span>
        </div>
      </div>
    </div>
  );
}
