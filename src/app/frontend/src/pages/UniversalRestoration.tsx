import { useState } from "react";
import CorruptionControls, { SEVERITIES } from "../components/task1/CorruptionControls";
import ErrorMapViewer from "../components/task1/ErrorMapViewer";
import SampleGallery from "../components/task1/SampleGallery";
import ErrorAlert from "../components/shared/ErrorAlert";
import ImagePanel from "../components/shared/ImagePanel";
import ImageUploader from "../components/shared/ImageUploader";
import LoadingSpinner from "../components/shared/LoadingSpinner";
import MetricBadge from "../components/shared/MetricBadge";
import { useInference } from "../hooks/useInference";
import { api } from "../services/api";
import type { CorruptionKind, UniversalRestoreResponse } from "../types";

type Mode = "upload" | "studio";

export default function UniversalRestoration() {
  const [mode, setMode] = useState<Mode>("studio");
  const [file, setFile] = useState<File | null>(null);
  const [kind, setKind] = useState<CorruptionKind>("salt_and_pepper");
  const [severity, setSeverity] = useState(2);
  const inf = useInference<UniversalRestoreResponse>(api.restoreUniversal);

  const submit = () => {
    if (!file) return;
    const form = new FormData();
    form.append("image", file);
    if (mode === "studio") {
      form.append("apply_corruption", "true");
      form.append("corruption_type", kind);
      form.append("severity", String(severity));
    }
    void inf.run(form);
  };

  const r = inf.data;
  const c = r?.corruption_applied;
  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <header>
        <h1 className="text-2xl font-bold">Universal Restoration</h1>
        <p className="text-sm text-slate-500">One autoencoder restores clean, noisy, blurred and occluded images without being told which.</p>
      </header>

      <div className="flex gap-2">
        {(["studio", "upload"] as Mode[]).map((m) => (
          <button
            key={m}
            onClick={() => (setMode(m), setFile(null))}
            className={`rounded-lg px-4 py-2 text-sm ring-1 ${mode === m ? "bg-amber-300/60 ring-amber-400" : "ring-ink-700"}`}
          >
            {m === "studio" ? "Corruption studio (clean sample)" : "Upload a corrupted image"}
          </button>
        ))}
      </div>

      <section className="grid gap-5 lg:grid-cols-2">
        <div className="space-y-3">
          {mode === "studio" && <SampleGallery onPick={(f) => setFile(f)} />}
          <ImageUploader file={file} onFile={setFile} label={mode === "studio" ? "…or upload your own clean image" : "Upload an already corrupted image"} />
        </div>
        {mode === "studio" && (
          <div className="glass p-4">
            <div className="mb-3 text-sm font-semibold">Runtime corruption</div>
            <CorruptionControls kind={kind} severity={severity} onChange={(k, s) => (setKind(k), setSeverity(s))} />
          </div>
        )}
      </section>

      <button disabled={!file || inf.loading} onClick={submit} className="btn-primary">
        Restore Image
      </button>

      {inf.loading && <LoadingSpinner />}
      {inf.error && <ErrorAlert message={inf.error} onDismiss={inf.dismissError} onRetry={submit} />}

      {r && (
        <section className="space-y-4">
          <div className="flex flex-wrap gap-2">
            <MetricBadge label="Inference" value={`${r.inference_time_ms.toFixed(1)} ms`} />
            <MetricBadge
              label="Corruption"
              tone="amber"
              value={c ? `${String(c.type).replace(/_/g, " ")} · ${SEVERITIES[c.type as CorruptionKind][Number(c.severity) - 1]}` : "none applied (uploaded as-is)"}
            />
          </div>
          <ImagePanel items={[{ label: "Input to model", src: r.corrupted_image }, { label: "Restored", src: r.restored_image }]} />
          <ErrorMapViewer src={r.error_map} reference={r.error_reference} />
        </section>
      )}
    </div>
  );
}
