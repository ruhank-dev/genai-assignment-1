/** Material Symbols icon (same icon font as the Stitch design). */
export default function Icon({ name, className = "", fill = false }: { name: string; className?: string; fill?: boolean }) {
  return (
    <span className={`material-symbols-outlined ${className}`} style={fill ? { fontVariationSettings: "'FILL' 1" } : undefined}>
      {name}
    </span>
  );
}

/** Class strings shared by the glass cards (taken from the Stitch markup). */
export const GLASS = "rounded-lg bg-surface-container-lowest/40 backdrop-blur-2xl p-space-lg shadow-md";
export const GLASS_TALL = "rounded-[28px] bg-gradient-to-b from-surface-container-lowest/70 to-surface-container-lowest/30 backdrop-blur-2xl p-space-lg shadow-sm";
export const PRIMARY_BTN =
  "w-full py-3 px-6 rounded-full bg-gradient-to-r from-primary-container to-[#facc15] hover:brightness-105 active:scale-[0.99] text-on-primary-fixed font-headline-sm text-headline-sm font-bold shadow-[0_8px_24px_-4px_rgba(245,158,11,0.45)] transition-all flex items-center justify-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed";
export const PILL_BTN = "px-5 py-2.5 rounded-full bg-surface-container-lowest/70 backdrop-blur-md text-on-surface hover:bg-surface-container-lowest font-label-prominent text-label-prominent shadow-sm transition-all flex items-center gap-2 disabled:opacity-40";
