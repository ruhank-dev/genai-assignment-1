import { NavLink } from "react-router-dom";

const ITEMS = [
  { to: "/universal", label: "Universal Restoration", hint: "Task 1 · one autoencoder" },
  { to: "/hard-routed", label: "Hard-Routed Restoration", hint: "Task 2 · classifier + specialists" },
  { to: "/soft-moe", label: "Soft Mixture-of-Experts", hint: "Task 3 · gated blend" },
  { to: "/face-to-sketch", label: "Face-to-Sketch Generator", hint: "Task 4 · conditional GAN" },
];

export default function Navbar() {
  return (
    <nav className="flex flex-col gap-1 p-3">
      {ITEMS.map((i) => (
        <NavLink
          key={i.to}
          to={i.to}
          className={({ isActive }) =>
            `rounded-lg px-3 py-2.5 transition ${isActive ? "bg-sky-500/15 ring-1 ring-sky-400/60" : "hover:bg-ink-800"}`
          }
        >
          <div className="text-sm font-semibold">{i.label}</div>
          <div className="text-xs text-slate-400">{i.hint}</div>
        </NavLink>
      ))}
    </nav>
  );
}
