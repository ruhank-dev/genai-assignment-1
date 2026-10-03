import type { Metrics } from "../../types";
import Icon from "../ui/Icon";

const PANEL = "col-span-6 rounded-[28px] bg-gradient-to-b from-surface-container-lowest/70 to-surface-container-lowest/30 backdrop-blur-2xl p-space-md shadow-sm flex flex-col gap-space-sm";

interface Props {
  input: string | null;
  output: string | null;
  inputBadge: string;
  metrics: Metrics | null;
  vsClean: boolean;
}

function save(url: string) {
  const a = document.createElement("a");
  a.href = url;
  a.download = `restored_soft_moe_${Date.now()}.png`;
  a.click();
}

export default function IoPanels({ input, output, inputBadge, metrics, vsClean }: Props) {
  return (
    <div className="col-span-12 grid grid-cols-12 gap-gutter">
      <div className={PANEL}>
        <div className="flex items-center justify-between px-2">
          <div className="flex items-center gap-2">
            <Icon name="broken_image" className="text-outline text-[20px]" />
            <span className="font-title-card text-title-card text-on-surface">Input Image (model input)</span>
          </div>
          <span className="px-2.5 py-0.5 rounded-full bg-error-container text-on-error-container font-label-caption text-label-caption">{inputBadge}</span>
        </div>
        <div className="relative w-full h-64 rounded-2xl overflow-hidden shadow-inner bg-surface-container-lowest/40 flex items-center justify-center">
          {input ? <img src={input} alt="input image" className="w-full h-full object-contain" /> : <span className="text-body-sm text-on-surface-variant">Input appears here</span>}
          <div className="absolute top-3 right-3 px-2.5 py-1 rounded-full bg-surface-container-lowest/90 backdrop-blur-md text-on-surface font-label-caption text-label-caption shadow-sm">Input (x)</div>
        </div>
      </div>
      <div className={PANEL}>
        <div className="flex items-center justify-between px-2">
          <div className="flex items-center gap-2">
            <Icon name="auto_awesome" className="text-primary-container text-[20px]" />
            <span className="font-title-card text-title-card text-on-surface font-semibold">Blended Output (soft MoE)</span>
          </div>
          <span className="px-2.5 py-0.5 rounded-full bg-tertiary-fixed text-on-tertiary-fixed font-data-tabular text-data-tabular">
            {metrics ? `PSNR ${metrics.psnr.toFixed(1)} dB • SSIM ${metrics.ssim.toFixed(3)} ${vsClean ? "(vs clean)" : "(vs input)"}` : "PSNR — • SSIM —"}
          </span>
        </div>
        <div className="relative w-full h-64 rounded-2xl overflow-hidden shadow-inner bg-surface-container-lowest/40 flex items-center justify-center">
          {output ? <img src={output} alt="blended output" className="w-full h-full object-contain" /> : <span className="text-body-sm text-on-surface-variant">Restored output appears here</span>}
          <div className="absolute top-3 right-3 px-2.5 py-1 rounded-full bg-primary-container text-on-primary font-label-caption text-label-caption shadow-sm">Blend (x̂)</div>
          {output && (
            <button onClick={() => save(output)} className="absolute bottom-3 right-3 px-4 py-1.5 rounded-full bg-gradient-to-r from-primary-container to-inverse-primary text-on-primary font-label-prominent text-label-prominent shadow-md hover:scale-105 transition-all" type="button">
              Download PNG
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
