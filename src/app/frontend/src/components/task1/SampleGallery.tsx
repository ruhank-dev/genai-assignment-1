import { useState } from "react";

const SAMPLES = [1, 2, 3, 4, 5, 6].map((n) => `/samples/pet_${n}.jpg`);

/** Bundled clean pet photos; clicking one loads it as a File for the pipeline. */
export default function SampleGallery({ onPick }: { onPick: (f: File, url: string) => void }) {
  const [active, setActive] = useState<string | null>(null);
  const [problem, setProblem] = useState<string | null>(null);

  const pick = async (url: string) => {
    try {
      const blob = await (await fetch(url)).blob();
      setActive(url);
      setProblem(null);
      onPick(new File([blob], url.split("/").pop() ?? "sample.jpg", { type: blob.type || "image/jpeg" }), url);
    } catch {
      setProblem("Could not load the sample image.");
    }
  };

  return (
    <div>
      <div className="grid grid-cols-3 gap-2 sm:grid-cols-6">
        {SAMPLES.map((u) => (
          <button
            key={u}
            onClick={() => pick(u)}
            className={`overflow-hidden rounded-lg ring-1 transition ${active === u ? "shadow-glow ring-amber-400" : "ring-white/70 bg-white/50 hover:bg-white/80"}`}
          >
            <img src={u} alt="clean sample" className="aspect-square w-full object-cover" />
          </button>
        ))}
      </div>
      {problem && <p className="mt-2 text-xs text-rose-600">{problem}</p>}
    </div>
  );
}
