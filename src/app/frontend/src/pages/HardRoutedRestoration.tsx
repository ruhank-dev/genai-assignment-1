import { useCallback, useState } from "react";
import ClassifierCard from "../components/hard/ClassifierCard";
import EngineCard from "../components/hard/EngineCard";
import LoupeCard from "../components/hard/LoupeCard";
import ProfileCard from "../components/hard/ProfileCard";
import CorruptionCard from "../components/input/CorruptionCard";
import SampleCard from "../components/input/SampleCard";
import ErrorHeatmapCard from "../components/ui/ErrorHeatmapCard";
import RunBar from "../components/ui/RunBar";
import TopStatusBar from "../components/ui/TopStatusBar";
import { modelCount, useHealth } from "../hooks/useHealth";
import { useInference } from "../hooks/useInference";
import { useWorkspaceInput } from "../hooks/useWorkspaceInput";
import { api } from "../services/api";
import type { HardRoutedRestoreResponse } from "../types";

const NAMES: Record<string, string> = { clean: "Clean", salt_and_pepper: "Salt-and-Pepper", gaussian_blur: "Gaussian Blur", rectangular_occlusion: "Occlusion" };

export default function HardRoutedRestoration() {
  const input = useWorkspaceInput();
  const health = useHealth();
  const { n, total } = modelCount(health);
  const [bypass, setBypass] = useState(false);
  const call = useCallback(
    async (force: boolean) => {
      const p = await input.prepare();
      const form = new FormData();
      form.append("image", p.image);
      if (p.reference) form.append("reference", p.reference);
      form.append("force_bypass", String(force));
      return api.restoreHardRouted(form);
    },
    [input],
  );
  const inf = useInference<HardRoutedRestoreResponse, boolean>(call);
  const run = () => void inf.run(bypass);
  const r = inf.data;
  const specialist = r?.selected_expert ?? "Specialist";
  return (
    <div className="flex flex-col w-full gap-space-lg pb-6">
      <TopStatusBar
        health={health}
        ready={n === total}
        text={<>Specialist dispatch pool: <span className="text-tertiary font-bold">classifier + 3 specialists</span> • {n}/{total} ONNX models loaded • batch 1</>}
        badges={["Hard router", health.kind === "ok" ? health.health.providers[0].replace("ExecutionProvider", "") : "ONNX Runtime"]}
      />
      {inf.error && (
        <div role="alert" className="rounded-full bg-error-container/70 backdrop-blur-xl text-on-error-container px-6 py-2 flex items-center justify-between shadow-sm">
          <span className="font-body-sm text-body-sm font-medium">{inf.error}</span>
          <button onClick={inf.dismissError} className="font-label-caption text-label-caption underline" type="button">Dismiss</button>
        </div>
      )}
      <div className="grid grid-cols-12 gap-gutter items-stretch">
        <SampleCard input={input} className="col-span-12 lg:col-span-6" />
        <CorruptionCard input={input} className="col-span-12 lg:col-span-6" action={{ label: "Analyze & Restore", icon: "alt_route", busy: inf.loading, onClick: run }} />
        <ClassifierCard probs={r?.class_probabilities ?? null} predicted={r?.predicted_class ?? null} />
        <EngineCard r={r} bypass={bypass} onBypass={setBypass} />
        <LoupeCard
          input={r?.original_image ?? null}
          restored={r?.restored_image ?? null}
          heat={r?.error_map ?? null}
          inputLabel={r ? `Input (${NAMES[r.predicted_class]})` : "Input"}
          restoredLabel={r ? (r.selected_expert === "Identity Bypass" ? "Identity (unchanged)" : "Restored by specialist") : "Restored"}
          metrics={r?.metrics ?? null}
          vsClean={r?.error_reference === "clean_reference"}
          l1Input={r?.input_metrics ? r.input_metrics.l1 : null}
        />
        <ProfileCard
          rows={[
            { icon: "timelapse", label: "Routing Classifier", sub: "Stage 1", ms: r?.inference_time.classifier_ms ?? null, bg: "bg-primary-fixed", fg: "text-on-primary-fixed" },
            { icon: "memory", label: specialist === "Identity Bypass" ? "Identity Bypass" : "Specialist Network", sub: "Stage 2", ms: r?.inference_time.specialist_ms ?? null, bg: "bg-secondary-fixed", fg: "text-on-secondary-fixed-variant" },
            { icon: "speed", label: "Total Roundtrip", sub: "End-to-End", ms: r?.inference_time.total_ms ?? null, bg: "bg-tertiary-fixed", fg: "text-on-tertiary-fixed" },
          ]}
        />
        <ErrorHeatmapCard
          className="col-span-12"
          mode="error"
          map={r?.error_map ?? null}
          metrics={r?.metrics}
          inputMetrics={r?.input_metrics}
          reference={r ? (r.error_reference === "clean_reference" ? "Error measured against the clean reference image" : "Error measured against the uploaded input (no clean reference)") : ""}
          exportData={r ? { metrics: r.metrics, input_metrics: r.input_metrics, reference: r.error_reference } : undefined}
        />
      </div>
      <RunBar
        title="Run the routing pipeline"
        subtitle="Hard routing: one classifier decision (argmax) selects exactly one specialist or the identity branch"
        exportData={r ?? undefined}
        action={{ label: "Analyze & Restore", busy: inf.loading, disabled: !input.file, onClick: run }}
      />
    </div>
  );
}
