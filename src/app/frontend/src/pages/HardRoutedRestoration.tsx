import { useState } from "react";
import ErrorAlert from "../components/shared/ErrorAlert";
import ImagePanel from "../components/shared/ImagePanel";
import ImageUploader from "../components/shared/ImageUploader";
import LoadingSpinner from "../components/shared/LoadingSpinner";
import SampleCorruptor from "../components/shared/SampleCorruptor";
import ClassifierProbabilities from "../components/task2/ClassifierProbabilities";
import LatencyBreakdown from "../components/task2/LatencyBreakdown";
import RoutingCard from "../components/task2/RoutingCard";
import { useInference } from "../hooks/useInference";
import { api } from "../services/api";
import type { HardRoutedRestoreResponse } from "../types";

export default function HardRoutedRestoration() {
  const [file, setFile] = useState<File | null>(null);
  const inf = useInference<HardRoutedRestoreResponse>(api.restoreHardRouted);

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
        <h1 className="text-2xl font-bold">Hard-Routed Restoration</h1>
        <p className="text-sm text-slate-500">A classifier names the corruption, then exactly one specialist (or the identity bypass) restores the image.</p>
      </header>

      <section className="grid gap-5 lg:grid-cols-2">
        <ImageUploader file={file} onFile={setFile} label="Upload an image (clean or corrupted)" />
        <SampleCorruptor onFile={setFile} />
      </section>

      <button disabled={!file || inf.loading} onClick={submit} className="btn-primary">
        Analyze &amp; Restore
      </button>

      {inf.loading && <LoadingSpinner />}
      {inf.error && <ErrorAlert message={inf.error} onDismiss={inf.dismissError} onRetry={submit} />}

      {r && (
        <section className="space-y-4">
          <LatencyBreakdown t={r.inference_time} />
          <div className="grid gap-4 lg:grid-cols-2">
            <ClassifierProbabilities probs={r.class_probabilities} predicted={r.predicted_class} />
            <RoutingCard predicted={r.predicted_class} probability={r.class_probabilities[r.predicted_class] ?? 0} expert={r.selected_expert} />
          </div>
          <ImagePanel items={[{ label: "Input", src: r.original_image }, { label: "Restored", src: r.restored_image }]} />
        </section>
      )}
    </div>
  );
}
