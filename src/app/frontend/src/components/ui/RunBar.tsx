import Icon, { PILL_BTN } from "./Icon";

interface Props {
  title: string;
  subtitle: string;
  icon?: string;
  exportData: unknown;
  action: { label: string; busy: boolean; disabled: boolean; onClick: () => void };
}

function download(data: unknown) {
  const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: "application/json" }));
  const a = document.createElement("a");
  a.href = url;
  a.download = "diagnostics.json";
  a.click();
  URL.revokeObjectURL(url);
}

/** Bottom control bar (Stitch "Specialist Override Threshold" row): description + Export Diagnostics JSON + primary run button. */
export default function RunBar({ title, subtitle, icon = "tune", exportData, action }: Props) {
  return (
    <div className="w-full rounded-lg bg-surface-container-lowest/40 backdrop-blur-2xl p-space-md shadow-sm flex flex-col md:flex-row items-center justify-between gap-space-md">
      <div className="flex items-center gap-space-sm w-full md:w-auto">
        <div className="w-10 h-10 rounded-full bg-primary-container/20 flex items-center justify-center text-primary shrink-0">
          <Icon name={icon} className="text-[22px]" />
        </div>
        <div className="flex flex-col min-w-0">
          <span className="font-title-card text-title-card text-on-surface">{title}</span>
          <span className="font-body-sm text-body-sm text-on-surface-variant truncate">{subtitle}</span>
        </div>
      </div>
      <div className="flex items-center gap-space-sm shrink-0 w-full md:w-auto justify-end">
        <button onClick={() => download(exportData)} disabled={exportData === undefined} className={PILL_BTN} type="button">
          Export Diagnostics JSON
        </button>
        <button
          onClick={action.onClick}
          disabled={action.disabled || action.busy}
          className="px-6 py-2.5 rounded-full bg-gradient-to-r from-primary-container to-inverse-primary text-on-primary-container font-label-prominent text-label-prominent font-bold shadow-md hover:scale-105 active:scale-95 transition-all flex items-center gap-2 disabled:opacity-40"
          type="button"
        >
          <Icon name="play_arrow" className="text-[18px]" />
          {action.busy ? "Running…" : action.label}
        </button>
      </div>
    </div>
  );
}
