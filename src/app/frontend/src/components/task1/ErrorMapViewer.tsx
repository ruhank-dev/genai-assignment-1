interface Props {
  src: string;
  reference: "clean_upload" | "input";
}

export default function ErrorMapViewer({ src, reference }: Props) {
  return (
    <figure className="glass p-3">
      <figcaption className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">Absolute error map</figcaption>
      <img src={src} alt="absolute error map" className="mx-auto aspect-square w-full max-w-sm rounded-lg object-contain" />
      <div className="mx-auto mt-3 max-w-sm">
        <div className="h-2 rounded-full" style={{ background: "linear-gradient(90deg,#000004,#570f6e,#bc3754,#f98e09,#fcffa4)" }} />
        <div className="mt-1 flex justify-between text-[10px] text-slate-500">
          <span>0</span>
          <span>|restored − {reference === "clean_upload" ? "clean image" : "input"}| (scale 0 – 0.5)</span>
          <span>≥ 0.5</span>
        </div>
      </div>
    </figure>
  );
}
