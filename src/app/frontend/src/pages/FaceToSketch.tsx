import { useState } from "react";
import ErrorAlert from "../components/shared/ErrorAlert";
import ImageUploader from "../components/shared/ImageUploader";
import LoadingSpinner from "../components/shared/LoadingSpinner";
import SketchViewer from "../components/task4/SketchViewer";
import StyleSelector from "../components/task4/StyleSelector";
import WebcamCapture from "../components/task4/WebcamCapture";
import { useInference } from "../hooks/useInference";
import { api } from "../services/api";
import type { SketchGenerateResponse } from "../types";

type Source = "upload" | "webcam";

export default function FaceToSketch() {
  const [source, setSource] = useState<Source>("upload");
  const [file, setFile] = useState<File | null>(null);
  const [style, setStyle] = useState(1);
  const inf = useInference<SketchGenerateResponse>(api.generateSketch);

  const submit = (s = style) => {
    if (!file) return;
    const form = new FormData();
    form.append("image", file);
    form.append("style", String(s));
    void inf.run(form);
  };

  const pickStyle = (s: number) => {
    setStyle(s);
    if (inf.data) submit(s); // switching style after a result regenerates immediately
  };

  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <header>
        <h1 className="text-2xl font-bold">Face-to-Sketch Generator</h1>
        <p className="text-sm text-slate-500">A style-conditioned GAN turns a face photo into a sketch in one of three FS2K styles.</p>
      </header>

      <div className="flex gap-2">
        {(["upload", "webcam"] as Source[]).map((m) => (
          <button key={m} onClick={() => (setSource(m), setFile(null))} className={`rounded-lg px-4 py-2 text-sm ring-1 ${source === m ? "bg-amber-300/60 ring-amber-400" : "ring-ink-700"}`}>
            {m === "upload" ? "Upload a photo" : "Use webcam"}
          </button>
        ))}
      </div>

      {source === "upload" ? <ImageUploader file={file} onFile={setFile} label="Drop a face photo here or click to browse" /> : <WebcamCapture onCapture={setFile} />}
      {source === "webcam" && file && <p className="text-xs text-emerald-700">Webcam photo ready.</p>}

      <StyleSelector value={style} onChange={pickStyle} />

      <button disabled={!file || inf.loading} onClick={() => submit()} className="btn-primary">
        Generate Sketch
      </button>

      {inf.loading && <LoadingSpinner label="Generating sketch…" />}
      {inf.error && <ErrorAlert message={inf.error} onDismiss={inf.dismissError} onRetry={() => submit()} />}
      {inf.data && <SketchViewer result={inf.data} />}
    </div>
  );
}
