import { useState } from "react";
import { api, dataUrlToFile } from "../../services/api";
import type { CorruptionKind } from "../../types";
import CorruptionControls from "../task1/CorruptionControls";
import SampleGallery from "../task1/SampleGallery";
import ErrorAlert from "./ErrorAlert";

/** Pick a clean sample, choose a corruption + severity, and get a corrupted File back (created server-side
 *  through the universal endpoint). Lets the hard-routed / soft-MoE pages be demonstrated without external images. */
export default function SampleCorruptor({ onFile }: { onFile: (f: File) => void }) {
  const [clean, setClean] = useState<File | null>(null);
  const [kind, setKind] = useState<CorruptionKind>("gaussian_blur");
  const [severity, setSeverity] = useState(2);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const make = async () => {
    if (!clean) return;
    setBusy(true);
    setError(null);
    const form = new FormData();
    form.append("image", clean);
    form.append("apply_corruption", "true");
    form.append("corruption_type", kind);
    form.append("severity", String(severity));
    try {
      const r = await api.restoreUniversal(form);
      onFile(dataUrlToFile(r.corrupted_image, `corrupted_${kind}_${severity}.png`));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create the corrupted sample");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-3 rounded-xl bg-ink-900 p-4 ring-1 ring-ink-700">
      <div className="text-sm font-semibold">Corruption studio — make a test input</div>
      <SampleGallery onPick={(f) => setClean(f)} />
      <CorruptionControls kind={kind} severity={severity} onChange={(k, s) => (setKind(k), setSeverity(s))} />
      <button
        disabled={!clean || busy}
        onClick={make}
        className="rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-ink-950 disabled:opacity-40"
      >
        {busy ? "Creating…" : "Apply corruption → use as input"}
      </button>
      {error && <ErrorAlert message={error} onDismiss={() => setError(null)} />}
    </div>
  );
}
