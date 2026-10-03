import { ReactNode } from "react";
import { NavLink } from "react-router-dom";

interface Item {
  to: string;
  label: string; // full workspace name (tooltip / aria label)
  short: string; // bottom tab text
  hint: string;
  icon: ReactNode;
}

const svg = (d: string) => (
  <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
    <path d={d} />
  </svg>
);

export const ITEMS: Item[] = [
  { to: "/universal", label: "Universal Restoration", short: "Universal Restoration", hint: "Task 1 · one autoencoder", icon: svg("M4 20 14 10M13 5l1-2 1 2 2 1-2 1-1 2-1-2-2-1zM18 12l.7-1.4L20 10l-1.3-.6L18 8l-.7 1.4L16 10l1.3.6z") },
  { to: "/hard-routed", label: "Hard-Routed Restoration", short: "Hard-Routed", hint: "Task 2 · classifier + specialists", icon: svg("M6 3v6a4 4 0 0 0 4 4h4a4 4 0 0 1 4 4v4M6 3 3 6M6 3l3 3M18 21l-3-3M18 21l3-3") },
  { to: "/soft-moe", label: "Soft Mixture-of-Experts Restoration", short: "Mixture of Experts", hint: "Task 3 · gated blend", icon: svg("m12 3 9 5-9 5-9-5 9-5zM3 13l9 5 9-5M3 17.5 12 22l9-4.5") },
  { to: "/face-to-sketch", label: "Face-to-Sketch Generator", short: "Face-to-Sketch", hint: "Task 4 · conditional GAN", icon: svg("M15 4l5 5L9 20H4v-5L15 4zM13 6l5 5") },
];

/** Floating vertical glass pill with one round icon per workspace (Stitch design). */
export function SideNav() {
  return (
    <nav aria-label="Workspaces" className="glass-pill flex flex-row justify-around gap-2 p-2 md:flex-col md:justify-start">
      {ITEMS.map((i) => (
        <NavLink
          key={i.to}
          to={i.to}
          title={`${i.label} — ${i.hint}`}
          aria-label={i.label}
          className={({ isActive }) =>
            `flex h-11 w-11 items-center justify-center rounded-full transition ${
              isActive ? "bg-white text-amber-600 shadow-md" : "text-slate-600 hover:bg-white/60"
            }`
          }
        >
          {i.icon}
        </NavLink>
      ))}
    </nav>
  );
}

/** Bottom pill tabs with the workspace names. */
export function BottomTabs() {
  return (
    <nav aria-label="Workspace tabs" className="glass-pill flex flex-wrap items-center gap-1 p-1.5">
      {ITEMS.map((i) => (
        <NavLink
          key={i.to}
          to={i.to}
          className={({ isActive }) =>
            `rounded-full px-4 py-2 text-sm transition ${isActive ? "bg-white font-display font-bold shadow-sm" : "text-slate-600 hover:bg-white/50"}`
          }
        >
          {i.short}
        </NavLink>
      ))}
    </nav>
  );
}

export default SideNav;
