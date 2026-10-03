import { useRef } from "react";
import { SAMPLES, WorkspaceInput } from "../../hooks/useWorkspaceInput";
import Icon, { GLASS } from "../ui/Icon";

/** "Choose a sample" card (Stitch): six clean pet photos + a custom upload tile. */
export default function SampleCard({ input, className = "col-span-12 lg:col-span-4" }: { input: WorkspaceInput; className?: string }) {
  const pick = useRef<HTMLInputElement>(null);
  return (
    <div className={`${className} ${GLASS} flex flex-col justify-between`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="font-title-card text-title-card text-on-surface">Choose a sample</span>
          <span className="font-data-tabular text-data-tabular px-2 py-0.5 rounded-full bg-surface-container-lowest/70 text-on-surface-variant">{SAMPLES.length} available</span>
        </div>
        <button onClick={input.shuffle} className="text-on-surface-variant hover:text-on-surface transition-colors" title="Pick a random sample" type="button">
          <Icon name="cached" className="text-[18px]" />
        </button>
      </div>
      <div className="grid grid-cols-4 gap-2.5">
        {SAMPLES.map((u) => {
          const active = input.sampleUrl === u;
          return (
            <button
              key={u}
              onClick={() => void input.pickSample(u)}
              aria-label="clean sample"
              className={`group relative aspect-square rounded-[18px] overflow-hidden shadow-sm transition-all ${active ? "ring-2 ring-primary-container scale-[1.02]" : "hover:scale-105"}`}
              type="button"
            >
              <img src={u} alt="clean sample" className="w-full h-full object-cover" />
              {active && <div className="absolute inset-0 bg-primary-container/15" />}
              {active && <span className="absolute bottom-1 right-1 w-2 h-2 rounded-full bg-primary-container shadow" />}
            </button>
          );
        })}
        <button
          onClick={() => pick.current?.click()}
          className="col-span-2 aspect-[2/0.95] rounded-[18px] bg-surface-container-lowest/30 hover:bg-surface-container-lowest/60 transition-all flex items-center justify-center gap-2 text-on-surface-variant hover:text-on-surface shadow-sm group"
          type="button"
        >
          <Icon name="cloud_upload" className="text-[20px] text-primary-container group-hover:scale-110 transition-transform" />
          <span className="font-label-caption text-label-caption font-semibold">{input.file && !input.sampleUrl ? input.file.name.slice(0, 16) : "Drop / Upload custom"}</span>
        </button>
        <input ref={pick} type="file" accept="image/jpeg,image/png" className="hidden" onChange={(e) => input.pickUpload(e.target.files?.[0])} />
      </div>
      {input.problem && <p className="mt-2 text-label-caption text-error">{input.problem}</p>}
    </div>
  );
}
