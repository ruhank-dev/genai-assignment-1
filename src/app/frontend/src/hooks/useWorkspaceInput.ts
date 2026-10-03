import { useCallback, useState } from "react";
import { api, dataUrlToFile } from "../services/api";
import type { AppliedCorruption, CorruptionKind, PipelineStep } from "../types";

export const SAMPLES = [1, 2, 3, 4, 5, 6].map((n) => `/samples/pet_${n}.jpg`);
const MAX_MB = 10;

export interface Prepared {
  image: File; // what the model receives
  reference: File | null; // the clean image it was made from (enables true error maps / metrics)
  applied: AppliedCorruption | null;
}

/** Shared input state of the three restoration workspaces: chosen image (bundled sample or upload),
 *  corruption kind/severity, and the "already corrupted" switch. */
export function useWorkspaceInput() {
  const [file, setFile] = useState<File | null>(null);
  const [sampleUrl, setSampleUrl] = useState<string | null>(null);
  const [kind, setKind] = useState<CorruptionKind>("gaussian_blur");
  const [severity, setSeverity] = useState(2);
  const [asIs, setAsIs] = useState(false);
  const [multi, setMulti] = useState(false); // optional demo mode: several corruptions in sequence
  const [steps, setSteps] = useState<PipelineStep[]>([{ id: 1, kind: "gaussian_blur", severity: 2 }]);
  const [problem, setProblem] = useState<string | null>(null);

  const pickSample = useCallback(async (url: string) => {
    try {
      const blob = await (await fetch(url)).blob();
      setFile(new File([blob], url.split("/").pop() ?? "sample.jpg", { type: blob.type || "image/jpeg" }));
      setSampleUrl(url);
      setProblem(null);
    } catch {
      setProblem("Could not load the sample image.");
    }
  }, []);

  const pickUpload = useCallback((f: File | undefined) => {
    if (!f) return;
    if (!["image/jpeg", "image/png"].includes(f.type)) return setProblem("Only JPEG and PNG images are supported.");
    if (f.size > MAX_MB * 1024 * 1024) return setProblem(`File is larger than ${MAX_MB} MB.`);
    setProblem(null);
    setFile(f);
    setSampleUrl(null);
  }, []);

  const shuffle = useCallback(() => void pickSample(SAMPLES[Math.floor(Math.random() * SAMPLES.length)]), [pickSample]);

  const addStep = useCallback(() => setSteps((s) => (s.length >= 6 ? s : [...s, { id: Math.max(0, ...s.map((x) => x.id)) + 1, kind: "salt_and_pepper", severity: 2 }])), []);
  const removeStep = useCallback((id: number) => setSteps((s) => (s.length <= 1 ? s : s.filter((x) => x.id !== id))), []);
  const updateStep = useCallback((id: number, patch: Partial<PipelineStep>) => setSteps((s) => s.map((x) => (x.id === id ? { ...x, ...patch } : x))), []);

  /** Form fields that describe the corruption to apply (single, or the multi-step pipeline). */
  const corruptionFields = useCallback((form: FormData) => {
    form.append("apply_corruption", "true");
    if (multi) form.append("pipeline", JSON.stringify(steps.map((s) => ({ type: s.kind, severity: s.severity }))));
    else {
      form.append("corruption_type", kind);
      form.append("severity", String(severity));
    }
  }, [multi, steps, kind, severity]);

  /** Apply the chosen corruption server-side (unless the image is already corrupted) and return model input + reference. */
  const prepare = useCallback(async (): Promise<Prepared> => {
    if (!file) throw new Error("Choose a sample or upload an image first.");
    if (asIs) return { image: file, reference: null, applied: null };
    const form = new FormData();
    form.append("image", file);
    corruptionFields(form);
    const r = await api.restoreUniversal(form);
    return { image: dataUrlToFile(r.corrupted_image, multi ? "corrupted_pipeline.png" : `corrupted_${kind}_${severity}.png`), reference: file, applied: r.corruption_applied };
  }, [file, asIs, multi, kind, severity, corruptionFields]);

  return { file, sampleUrl, kind, severity, asIs, multi, steps, setMulti, addStep, removeStep, updateStep, corruptionFields, problem, setKind, setSeverity, setAsIs, pickSample, pickUpload, shuffle, prepare };
}

export type WorkspaceInput = ReturnType<typeof useWorkspaceInput>;
