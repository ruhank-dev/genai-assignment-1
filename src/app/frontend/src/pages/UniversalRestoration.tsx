import { useCallback, useEffect, useState } from "react";
import CorruptionCard, { describeApplied } from "../components/input/CorruptionCard";
import SampleCard from "../components/input/SampleCard";
import DiagnosticsBar from "../components/ui/DiagnosticsBar";
import ErrorHeatmapCard from "../components/ui/ErrorHeatmapCard";
import StatusCard from "../components/ui/StatusCard";
import SplitView from "../components/universal/SplitView";
import { useInference } from "../hooks/useInference";
import { useWorkspaceInput } from "../hooks/useWorkspaceInput";
import { api } from "../services/api";
import type { UniversalRestoreResponse } from "../types";

export default function UniversalRestoration() {
  const input = useWorkspaceInput();
  const call = useCallback((f: FormData) => api.restoreUniversal(f), []);
  const inf = useInference<UniversalRestoreResponse>(call);
  const [preview, setPreview] = useState<string | null>(null);

  useEffect(() => {
    if (!input.file) return setPreview(null);
    const url = URL.createObjectURL(input.file);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [input.file]);

  const submit = () => {
    if (!input.file) return;
    const form = new FormData();
    form.append("image", input.file);
    if (!input.asIs) input.corruptionFields(form);
    void inf.run(form);
  };

  const r = inf.data;
  const c = r?.corruption_applied;
  const label = c ? `Corrupted (${describeApplied(c)})` : r ? "Input (as uploaded)" : "Selected image";
  return (
    <div className="flex flex-col w-full gap-space-lg pb-4">
      {inf.error && (
        <div role="alert" className="rounded-full bg-error-container/70 backdrop-blur-xl text-on-error-container px-6 py-2 flex items-center justify-between shadow-sm">
          <span className="font-body-sm text-body-sm font-medium">{inf.error}</span>
          <button onClick={inf.dismissError} className="font-label-caption text-label-caption underline" type="button">Dismiss</button>
        </div>
      )}
      <div className="grid grid-cols-12 gap-gutter w-full">
        <StatusCard pipeline="Universal conv. autoencoder" inferenceMs={r?.inference_time_ms ?? null} />
        <SampleCard input={input} />
        <CorruptionCard input={input} action={{ label: "Restore Image", icon: "auto_awesome", busy: inf.loading, onClick: submit }} />
        <SplitView
          title="Restoration Verification"
          before={r?.corrupted_image ?? null}
          after={r?.restored_image ?? null}
          placeholder={preview}
          beforeLabel={label}
          afterLabel="Restored Output"
          beforeNote="Input to model"
          afterNote="Universal AE · 128×128"
        />
        <ErrorHeatmapCard
          className="col-span-12 lg:col-span-4"
          mode="error"
          map={r?.error_map ?? null}
          metrics={r?.metrics}
          inputMetrics={r?.input_metrics}
          reference={r ? (r.error_reference === "clean_upload" ? "Error measured against the clean image" : "Error measured against the uploaded input") : ""}
          exportData={r ? { metrics: r.metrics, input_metrics: r.input_metrics, reference: r.error_reference, corruption: r.corruption_applied } : undefined}
        />
        <DiagnosticsBar
          items={[
            { label: "Pipeline Latency", value: r ? `${r.inference_time_ms.toFixed(1)} ms` : "—" },
            { label: "Residual L1", value: r ? r.metrics.l1.toFixed(4) : "—" },
            { label: "Model I/O", value: "128×128 RGB" },
          ]}
        />
      </div>
    </div>
  );
}
