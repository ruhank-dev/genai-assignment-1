import { useCallback, useState } from "react";
import CorruptionCard, { describeApplied } from "../components/input/CorruptionCard";
import SampleCard from "../components/input/SampleCard";
import BlendCard from "../components/moe/BlendCard";
import GatingCard from "../components/moe/GatingCard";
import IoPanels from "../components/moe/IoPanels";
import LatencyCard from "../components/moe/LatencyCard";
import ErrorHeatmapCard from "../components/ui/ErrorHeatmapCard";
import RunBar from "../components/ui/RunBar";
import TopStatusBar from "../components/ui/TopStatusBar";
import training from "../data/task3_training.json";
import { modelCount, useHealth } from "../hooks/useHealth";
import { useInference } from "../hooks/useInference";
import { useWorkspaceInput } from "../hooks/useWorkspaceInput";
import { api } from "../services/api";
import type { AppliedCorruption, SoftMoERestoreResponse } from "../types";

export default function SoftMoERestoration() {
  const input = useWorkspaceInput();
  const health = useHealth();
  const { n, total } = modelCount(health);
  const [applied, setApplied] = useState<AppliedCorruption | null>(null);
  const call = useCallback(
    async (_: void) => {
      const p = await input.prepare();
      setApplied(p.applied);
      const form = new FormData();
      form.append("image", p.image);
      if (p.reference) form.append("reference", p.reference);
      return api.restoreSoftMoE(form);
    },
    [input],
  );
  const inf = useInference<SoftMoERestoreResponse, void>(call);
  const run = () => void inf.run();
  const r = inf.data;
  const entropy = r ? -Object.values(r.routing_weights).reduce((a, p) => a + (p > 0 ? p * Math.log(p) : 0), 0) : null;
  const badge = applied ? describeApplied(applied, true) : r ? "uploaded as-is" : "no input yet";
  return (
    <div className="flex flex-col w-full gap-space-lg pb-6">
      <TopStatusBar
        health={health}
        ready={n === total}
        text={
          <>
            MoE runtime ready • Gating entropy: <span className="font-title-card">{entropy === null ? "—" : `${entropy.toFixed(2)} nats`}</span> • Dominant:{" "}
            <span className="text-tertiary font-title-card">{r ? r.dominant_expert.replace(/_/g, " ") : "—"}</span>
          </>
        }
        badges={["Continuous mix", health.kind === "ok" ? health.health.providers[0].replace("ExecutionProvider", "") : "ONNX Runtime"]}
      />
      {inf.error && (
        <div role="alert" className="rounded-full bg-error-container/70 backdrop-blur-xl text-on-error-container px-6 py-2 flex items-center justify-between shadow-sm">
          <span className="font-body-sm text-body-sm font-medium">{inf.error}</span>
          <button onClick={inf.dismissError} className="font-label-caption text-label-caption underline" type="button">Dismiss</button>
        </div>
      )}
      <div className="grid grid-cols-12 gap-gutter w-full">
        <SampleCard input={input} className="col-span-12 lg:col-span-6" />
        <CorruptionCard input={input} className="col-span-12 lg:col-span-6" action={{ label: "Run Soft MoE Restoration", icon: "layers", busy: inf.loading, onClick: run }} />
        <GatingCard weights={r?.routing_weights ?? null} dominant={r?.dominant_expert ?? null} tau={training.tau} />
        <BlendCard weights={r?.routing_weights ?? null} dominant={r?.dominant_expert ?? null} />
        <LatencyCard ms={r?.inference_time_ms ?? null} />
        <IoPanels input={r?.original_image ?? null} output={r?.restored_image ?? null} inputBadge={badge} metrics={r?.metrics ?? null} vsClean={r?.error_reference === "clean_reference"} />
        <ErrorHeatmapCard
          className="col-span-12"
          mode="error"
          map={r?.error_map ?? null}
          metrics={r?.metrics}
          inputMetrics={r?.input_metrics}
          reference={r ? (r.error_reference === "clean_reference" ? "Error measured against the clean reference image" : "Error measured against the uploaded input (no clean reference)") : ""}
          exportData={r ? { weights: r.routing_weights, metrics: r.metrics, input_metrics: r.input_metrics, reference: r.error_reference } : undefined}
        />
      </div>
      <RunBar
        title="Run the soft mixture"
        subtitle="All four branches execute; the gate's softmax weights decide how much each contributes to the output"
        icon="layers"
        exportData={r ?? undefined}
        action={{ label: "Run Soft MoE", busy: inf.loading, disabled: !input.file, onClick: run }}
      />
    </div>
  );
}
