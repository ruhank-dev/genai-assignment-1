import { useCallback, useEffect, useRef, useState } from "react";

/** Live webcam preview with snapshot / retake / accept controls. Calls onCapture(File) when the user accepts. */
export default function WebcamCapture({ onCapture }: { onCapture: (f: File) => void }) {
  const video = useRef<HTMLVideoElement>(null);
  const stream = useRef<MediaStream | null>(null);
  const [shot, setShot] = useState<{ url: string; blob: Blob } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const stop = useCallback(() => {
    stream.current?.getTracks().forEach((t) => t.stop());
    stream.current = null;
  }, []);

  const start = useCallback(async () => {
    setError(null);
    try {
      stream.current = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } });
      if (video.current) video.current.srcObject = stream.current;
    } catch {
      setError("Camera unavailable. Allow camera access in the browser (needs https or localhost) or use file upload.");
    }
  }, []);

  useEffect(() => {
    void start();
    return stop;
  }, [start, stop]);

  const snap = () => {
    const v = video.current;
    if (!v || !v.videoWidth) return;
    const c = document.createElement("canvas");
    c.width = v.videoWidth;
    c.height = v.videoHeight;
    c.getContext("2d")?.drawImage(v, 0, 0);
    c.toBlob((b) => b && setShot({ url: URL.createObjectURL(b), blob: b }), "image/png");
  };

  const retake = () => {
    if (shot) URL.revokeObjectURL(shot.url);
    setShot(null);
  };

  if (error) return <p className="rounded-lg bg-rose-500/10 p-4 text-sm text-rose-200">{error}</p>;
  return (
    <div className="space-y-3">
      <div className="relative overflow-hidden rounded-xl bg-black">
        <video ref={video} autoPlay playsInline muted className={`w-full ${shot ? "hidden" : ""}`} />
        {shot && <img src={shot.url} alt="captured snapshot" className="w-full" />}
      </div>
      <div className="flex gap-2">
        {!shot ? (
          <button onClick={snap} className="rounded-lg bg-sky-500 px-4 py-2 text-sm font-semibold text-ink-950">
            Take snapshot
          </button>
        ) : (
          <>
            <button onClick={() => onCapture(new File([shot.blob], "webcam.png", { type: "image/png" }))} className="rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-ink-950">
              Use this photo
            </button>
            <button onClick={retake} className="rounded-lg px-4 py-2 text-sm ring-1 ring-ink-700">
              Retake
            </button>
          </>
        )}
      </div>
    </div>
  );
}
