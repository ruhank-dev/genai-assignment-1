import { useEffect, useRef, useState } from "react";

const MAX_MB = 10;
const OK_TYPES = ["image/jpeg", "image/png"];

interface Props {
  file: File | null;
  onFile: (f: File | null) => void;
  label?: string;
}

export default function ImageUploader({ file, onFile, label = "Drop an image here or click to browse" }: Props) {
  const input = useRef<HTMLInputElement>(null);
  const [drag, setDrag] = useState(false);
  const [problem, setProblem] = useState<string | null>(null);
  const [preview, setPreview] = useState<string | null>(null);

  useEffect(() => {
    if (!file) return setPreview(null);
    const url = URL.createObjectURL(file);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  const accept = (f: File | undefined) => {
    if (!f) return;
    if (!OK_TYPES.includes(f.type)) return setProblem("Only JPEG and PNG images are supported.");
    if (f.size > MAX_MB * 1024 * 1024) return setProblem(`File is larger than ${MAX_MB} MB.`);
    setProblem(null);
    onFile(f);
  };

  return (
    <div>
      <div
        role="button"
        tabIndex={0}
        onClick={() => input.current?.click()}
        onKeyDown={(e) => e.key === "Enter" && input.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setDrag(true);
        }}
        onDragLeave={() => setDrag(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDrag(false);
          accept(e.dataTransfer.files[0]);
        }}
        className={`flex min-h-40 cursor-pointer items-center justify-center rounded-xl border-2 border-dashed p-4 text-center text-sm transition ${
          drag ? "border-sky-400 bg-sky-500/10" : "border-ink-700 hover:border-slate-500"
        }`}
      >
        {preview ? (
          <img src={preview} alt="selected upload" className="max-h-52 rounded-lg" />
        ) : (
          <span className="text-slate-400">{label}</span>
        )}
        <input ref={input} type="file" accept="image/jpeg,image/png" className="hidden" onChange={(e) => accept(e.target.files?.[0])} />
      </div>
      {problem && <p className="mt-2 text-xs text-rose-300">{problem}</p>}
      {file && (
        <button className="mt-2 text-xs text-slate-400 underline" onClick={() => onFile(null)}>
          clear selection
        </button>
      )}
    </div>
  );
}
