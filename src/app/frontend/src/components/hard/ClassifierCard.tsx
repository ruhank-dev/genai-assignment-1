import Icon, { GLASS } from "../ui/Icon";

const ROWS: { key: string; label: string; dot: string; bar: string }[] = [
  { key: "clean", label: "Clean", dot: "bg-tertiary-fixed-dim", bar: "bg-tertiary" },
  { key: "salt_and_pepper", label: "Salt-and-Pepper", dot: "bg-primary-container", bar: "bg-primary-container" },
  { key: "gaussian_blur", label: "Gaussian Blur", dot: "bg-secondary", bar: "bg-secondary" },
  { key: "rectangular_occlusion", label: "Rectangular Occlusion", dot: "bg-error", bar: "bg-error" },
];

interface Props {
  probs: Record<string, number> | null;
  predicted: string | null;
}

const pct = (p: number) => `${(p * 100).toFixed(p > 0.9995 ? 1 : 2)}%`;

export default function ClassifierCard({ probs, predicted }: Props) {
  const top = predicted && probs ? probs[predicted] : 0;
  const vals = probs ? Object.values(probs) : [];
  const entropy = -vals.reduce((a, p) => a + (p > 0 ? p * Math.log(p) : 0), 0); // nats
  const kl = vals.length ? Math.log(vals.length) - entropy : 0; // KL(p || uniform)
  return (
    <div className={`col-span-12 lg:col-span-5 ${GLASS} shadow-sm flex flex-col justify-between relative overflow-hidden`}>
      <div className="absolute -right-16 -top-16 w-44 h-44 rounded-full bg-primary-container/10 blur-3xl pointer-events-none" />
      <div>
        <div className="flex items-start justify-between mb-space-sm">
          <div>
            <span className="font-label-caption text-label-caption uppercase tracking-wider text-on-surface-variant font-semibold">Inference Classifier</span>
            <h2 className="font-headline-sm text-headline-sm text-on-surface">Classifier Distribution</h2>
            <p className="font-body-sm text-body-sm text-on-surface-variant">Corruption classifier (CNN, 4 classes)</p>
          </div>
          <div className="px-3 py-1 rounded-full bg-tertiary-container/30 text-on-tertiary-container flex items-center gap-1 shadow-sm shrink-0">
            <Icon name="verified" className="text-[16px] text-tertiary" />
            <span className="font-label-prominent text-label-prominent font-bold">{probs ? `${(top * 100).toFixed(1)}% top-1` : "No result yet"}</span>
          </div>
        </div>
        <div className="space-y-4 my-space-md">
          {ROWS.map((r) => {
            const p = probs?.[r.key] ?? 0;
            const elected = predicted === r.key;
            return (
              <div key={r.key} className={elected ? "p-2.5 rounded bg-surface-container-lowest/70 shadow-sm relative" : ""}>
                <div className="flex justify-between items-center mb-1">
                  <span className={`font-title-card text-title-card flex items-center gap-1.5 ${elected ? "text-secondary font-bold" : "text-on-surface"}`}>
                    <span className={`w-2 h-2 rounded-full ${elected ? "bg-secondary animate-pulse" : r.dot}`} />
                    {r.label}
                    {elected && <span className="px-2 rounded-full bg-secondary-fixed text-on-secondary-fixed font-label-caption text-label-caption">Elected</span>}
                  </span>
                  <span className={elected ? "font-data-metric text-headline-sm text-secondary font-bold" : "font-data-tabular text-data-tabular text-on-surface-variant"}>{probs ? pct(p) : "—"}</span>
                </div>
                <div className={`w-full rounded-full bg-surface-container-highest/60 p-0.5 backdrop-blur-sm overflow-hidden ${elected ? "h-3.5" : "h-3"}`}>
                  <div className={`h-full rounded-full ${r.bar} transition-all duration-1000`} style={{ width: `${Math.max(p * 100, probs ? 0.6 : 0)}%` }} />
                </div>
              </div>
            );
          })}
        </div>
      </div>
      <div className="pt-space-sm flex items-center justify-between bg-surface-container-low/40 p-3 rounded mt-2">
        <span className="font-body-sm text-body-sm text-on-surface-variant">Entropy score: {probs ? `${entropy.toFixed(3)} nats` : "—"}</span>
        <span className="font-data-tabular text-data-tabular text-on-surface font-semibold">KL vs uniform: {probs ? kl.toFixed(3) : "—"}</span>
      </div>
    </div>
  );
}
