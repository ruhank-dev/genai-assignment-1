import { useCallback, useEffect, useRef, useState } from "react";
import Icon, { GLASS } from "../ui/Icon";

interface Props {
  file: File | null;
  onFile: (f: File | null) => void;
  onProblem: (msg: string | null) => void;
}

const OK = ["image/jpeg", "image/png"];

/** Upload / webcam input card (Stitch "Upload photo | Use webcam"): live preview, face guide overlay, shutter, drop zone. */
export default function FaceInput({ file, onFile, onProblem }: Props) {
  const [tab, setTab] = useState<"upload" | "webcam">("upload");
  const [facing, setFacing] = useState<"user" | "environment">("user");
  const [live, setLive] = useState(false);
  const [shot, setShot] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);
  const video = useRef<HTMLVideoElement>(null);
  const stream = useRef<MediaStream | null>(null);
  const picker = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!file) return setPreview(null);
    const url = URL.createObjectURL(file);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  const stop = useCallback(() => {
    stream.current?.getTracks().forEach((t) => t.stop());
    stream.current = null;
    setLive(false);
  }, []);

  useEffect(() => {
    if (tab !== "webcam" || shot) return stop();
    let cancelled = false;
    navigator.mediaDevices
      .getUserMedia({ video: { facingMode: facing } })
      .then((s) => {
        if (cancelled) return s.getTracks().forEach((t) => t.stop());
        stream.current = s;
        if (video.current) video.current.srcObject = s;
        setLive(true);
        onProblem(null);
      })
      .catch(() => onProblem("Camera unavailable — allow camera access (needs https or localhost) or use Upload photo."));
    return () => {
      cancelled = true;
      stop();
    };
  }, [tab, facing, shot, stop, onProblem]);

  const accept = (f: File | undefined) => {
    if (!f) return;
    if (!OK.includes(f.type)) return onProblem("Only JPEG and PNG images are supported.");
    if (f.size > 10 * 1024 * 1024) return onProblem("File is larger than 10 MB.");
    onProblem(null);
    onFile(f);
  };

  const snap = () => {
    const v = video.current;
    if (!v || !v.videoWidth) return;
    const c = document.createElement("canvas");
    c.width = v.videoWidth;
    c.height = v.videoHeight;
    c.getContext("2d")?.drawImage(v, 0, 0);
    c.toBlob((b) => {
      if (!b) return;
      onFile(new File([b], "webcam.png", { type: "image/png" }));
      setShot(true);
    }, "image/png");
  };

  const switchTab = (t: "upload" | "webcam") => {
    setTab(t);
    setShot(false);
    onFile(null);
  };

  return (
    <section
      className={`col-span-12 lg:col-span-5 ${GLASS} flex flex-col justify-between shadow-lg relative overflow-hidden`}
      onDragOver={(e) => e.preventDefault()}
      onDrop={(e) => {
        e.preventDefault();
        accept(e.dataTransfer.files[0]);
      }}
    >
      <div className="absolute -top-20 -right-20 w-52 h-52 bg-secondary-fixed/50 rounded-full blur-3xl pointer-events-none" />
      <div className="flex items-center justify-between gap-space-sm relative z-10 mb-space-md">
        <div className="p-1 rounded-full bg-surface-container-lowest/70 backdrop-blur-md flex items-center shadow-sm">
          {(["upload", "webcam"] as const).map((t) => (
            <button key={t} onClick={() => switchTab(t)} className={`px-3.5 py-1.5 rounded-full font-label-prominent text-label-prominent transition-all ${tab === t ? "bg-surface-container-lowest text-on-surface shadow-sm" : "text-on-surface-variant hover:text-on-surface"}`} type="button">
              {t === "upload" ? "Upload photo" : "Use webcam"}
            </button>
          ))}
        </div>
        <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full font-data-tabular text-data-tabular ${live ? "bg-tertiary-container/20 text-tertiary" : "bg-surface-container-highest/60 text-on-surface-variant"}`}>
          <span className={`w-1.5 h-1.5 rounded-full ${live ? "bg-tertiary animate-ping" : "bg-outline"}`} />
          {live ? "LIVE" : tab === "webcam" ? (shot ? "SNAPSHOT" : "CAMERA OFF") : "UPLOAD"}
        </div>
      </div>
      <div className="relative w-full h-[320px] rounded bg-inverse-surface/90 shadow-inner flex items-center justify-center overflow-hidden">
        {tab === "webcam" && !shot && <video ref={video} autoPlay playsInline muted className="w-full h-full object-cover opacity-90" />}
        {(tab === "upload" || shot) && preview && <img src={preview} alt="selected face" className="w-full h-full object-cover" />}
        {tab === "upload" && !preview && <span className="text-inverse-on-surface/70 font-body-sm text-body-sm px-6 text-center">Drop a front-facing face photo here or press Browse</span>}
        <svg className="absolute inset-0 w-full h-full pointer-events-none" fill="none" viewBox="0 0 400 320" preserveAspectRatio="none">
          <rect className="text-primary-container" height="210" opacity="0.85" rx="20" stroke="currentColor" strokeDasharray="4 3" strokeWidth="1.5" width="180" x="110" y="55" />
          <path className="text-primary-container" d="M100 75 V60 H120 M280 60 H300 V75 M100 245 V260 H120 M280 260 H300 V245" stroke="currentColor" strokeLinecap="round" strokeWidth="3" />
        </svg>
        <div className="absolute top-3 left-3 px-3 py-1 rounded-full bg-inverse-surface/60 backdrop-blur-md text-surface flex items-center gap-1.5 shadow-sm">
          <Icon name="face" className="text-[14px] text-tertiary-fixed-dim" />
          <span className="font-data-tabular text-data-tabular tracking-wide">ALIGN FACE IN THE FRAME</span>
        </div>
        {tab === "webcam" && (
          <div className="absolute bottom-4 inset-x-0 flex items-center justify-center gap-space-md z-20">
            <button onClick={() => (shot ? (setShot(false), onFile(null)) : setFacing(facing === "user" ? "environment" : "user"))} className="w-9 h-9 rounded-full bg-surface-container-lowest/50 backdrop-blur-md text-on-surface flex items-center justify-center hover:bg-surface-container-lowest transition-all shadow-sm" title={shot ? "Retake" : "Flip camera"} aria-label={shot ? "Retake" : "Flip camera"} type="button">
              <Icon name={shot ? "replay" : "flip_camera_ios"} className="text-[18px]" />
            </button>
            <button onClick={snap} disabled={!live} aria-label="Take snapshot" className="w-14 h-14 rounded-full bg-surface-container-lowest/80 backdrop-blur-xl flex items-center justify-center text-on-surface hover:scale-105 active:scale-95 transition-all shadow-xl disabled:opacity-50" type="button">
              <div className="w-11 h-11 rounded-full bg-gradient-to-br from-primary-container to-inverse-primary flex items-center justify-center shadow-md">
                <Icon name="photo_camera" className="text-on-primary-container text-[22px]" />
              </div>
            </button>
            <div className="w-9 h-9" />
          </div>
        )}
      </div>
      <div onClick={() => picker.current?.click()} className="mt-space-md w-full p-2.5 rounded-full bg-surface-container-lowest/60 backdrop-blur-md flex items-center justify-between shadow-sm cursor-pointer hover:bg-surface-container-lowest transition-all">
        <div className="flex items-center gap-2 pl-2">
          <Icon name="cloud_upload" className="text-on-surface-variant text-[18px]" />
          <span className="font-body-sm text-body-sm text-on-surface-variant truncate">{file ? file.name : "Drop portrait image (JPG, PNG) or tap to browse"}</span>
        </div>
        <span className="px-3 py-1 rounded-full bg-surface-container font-label-caption text-label-caption text-on-surface font-semibold shadow-sm">Browse</span>
        <input ref={picker} type="file" accept="image/jpeg,image/png" className="hidden" onChange={(e) => (switchToUpload(e.target.files?.[0]), (e.target.value = ""))} />
      </div>
    </section>
  );

  function switchToUpload(f: File | undefined) {
    if (!f) return;
    setTab("upload");
    setShot(false);
    accept(f);
  }
}
