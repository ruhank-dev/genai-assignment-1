import { useState } from "react";

export interface PanelItem {
  label: string;
  src: string;
  caption?: string;
}

/** Side-by-side comparison; click an image to zoom; 128x128 results are scaled smoothly. */
export default function ImagePanel({ items }: { items: PanelItem[] }) {
  const [zoom, setZoom] = useState<string | null>(null);
  return (
    <>
      <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${items.length}, minmax(0, 1fr))` }}>
        {items.map((i) => (
          <figure key={i.label} className="glass p-3">
            <figcaption className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">{i.label}</figcaption>
            <img
              src={i.src}
              alt={i.label}
              onClick={() => setZoom(i.src)}
              className="aspect-square w-full cursor-zoom-in rounded-lg object-contain"
            />
            {i.caption && <p className="mt-2 text-xs text-slate-500">{i.caption}</p>}
          </figure>
        ))}
      </div>
      <p className="text-center text-xs text-slate-500">Models work on 128×128 images; results are scaled up smoothly for display (click an image to zoom).</p>
      {zoom && (
        <div className="fixed inset-0 z-50 flex cursor-zoom-out items-center justify-center bg-black/80 p-6" onClick={() => setZoom(null)}>
          <img src={zoom} alt="zoomed result" className="max-h-full max-w-full rounded-lg" style={{ width: 512 }} />
        </div>
      )}
    </>
  );
}
