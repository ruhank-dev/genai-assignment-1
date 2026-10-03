import { useState } from "react";
import ErrorAlert from "../components/shared/ErrorAlert";
import ImagePanel from "../components/shared/ImagePanel";
import ImageUploader from "../components/shared/ImageUploader";
import LoadingSpinner from "../components/shared/LoadingSpinner";
import MetricBadge from "../components/shared/MetricBadge";
import SampleCorruptor from "../components/shared/SampleCorruptor";
import ExpertContribution from "../components/task3/ExpertContribution";
import GatingWeights from "../components/task3/GatingWeights";
import { useInference } from "../hooks/useInference";
import { api } from "../services/api";
import type { SoftMoERestoreResponse } from "../types";

export default function SoftMoERestoration() {
  const [file, setFile] = useState<File | null>(null);
  const inf = useInference<SoftMoERestoreResponse>(api.restoreSoftMoE);

  const submit = () => {
    if (!file) return;
    const form = new FormData();
    form.append("image", file);
    void inf.run(form);
  };

  const r = inf.data;
  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <header>
        <h1 className="text-2xl font-bold">Soft Mixture-of-Experts Restoration</h1>
        <p className="text-sm text-slate-400">A gate assigns a continuous weight to the identity branch and the three experts; the output is their weighted sum.</p>
      </header>

      <section className="grid gap-5 lg:grid-cols-2">
        <ImageUploader file={file} onFile={setFile} label="Upload an image (clean, corrupted or mixed)" />
        <SampleCorruptor onFile={setFile} />
      </section>

      <button disabled={!file || inf.loading} onClick={submit} className="rounded-lg bg-sky-500 px-5 py-2.5 font-semibold text-ink-950 disabled:opacity-40">
        Run Soft MoE Restoration
      </button>

      {inf.loading && <LoadingSpinner />}
      {inf.error && <ErrorAlert message={inf.error} onDismiss={inf.dismissError} onRetry={submit} />}

      {r && (
        <section className="space-y-4">
          <MetricBadge label="Inference" value={`${r.inference_time_ms.toFixed(1)} ms`} />
          <div className="grid gap-4 lg:grid-cols-2">
            <GatingWeights weights={r.routing_weights} dominant={r.dominant_expert} />
            <ExpertContribution weights={r.routing_weights} />
          </div>
          <ImagePanel items={[{ label: "Input", src: r.original_image }, { label: "Restored (soft blend)", src: r.restored_image }]} />
        </section>
      )}
    </div>
  );
}
