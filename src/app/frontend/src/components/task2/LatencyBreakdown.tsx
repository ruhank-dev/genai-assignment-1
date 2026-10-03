import MetricBadge from "../shared/MetricBadge";

export default function LatencyBreakdown({ t }: { t: { classifier_ms: number; specialist_ms: number; total_ms: number } }) {
  return (
    <div className="flex flex-wrap gap-2">
      <MetricBadge label="Classifier" value={`${t.classifier_ms.toFixed(1)} ms`} />
      <MetricBadge label="Specialist" tone={t.specialist_ms === 0 ? "slate" : "amber"} value={`${t.specialist_ms.toFixed(1)} ms`} />
      <MetricBadge label="Total" tone="emerald" value={`${t.total_ms.toFixed(1)} ms`} />
    </div>
  );
}
