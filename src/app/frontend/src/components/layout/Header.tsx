import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { HealthState, modelCount } from "../../hooks/useHealth";
import Icon from "../ui/Icon";
import { WORKSPACES } from "./workspaces";

function Search() {
  const nav = useNavigate();
  const [q, setQ] = useState("");
  const [open, setOpen] = useState(false);
  const input = useRef<HTMLInputElement>(null);
  const hits = useMemo(() => WORKSPACES.filter((w) => `${w.name} ${w.hint}`.toLowerCase().includes(q.toLowerCase())), [q]);

  useEffect(() => {
    const k = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        input.current?.focus();
      }
    };
    window.addEventListener("keydown", k);
    return () => window.removeEventListener("keydown", k);
  }, []);

  return (
    <div className="relative flex-1 max-w-md mx-6">
      <div className="relative flex items-center w-full h-11 px-4 rounded-full bg-surface-container-lowest/40 backdrop-blur-md border border-surface-container-lowest/70 shadow-[inset_0_1px_2px_rgba(255,255,255,0.8)]">
        <Icon name="search" className="text-on-surface-variant text-[20px] mr-2" />
        <input
          ref={input}
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onFocus={() => setOpen(true)}
          onBlur={() => setTimeout(() => setOpen(false), 150)}
          placeholder="Search images or models here"
          aria-label="Search workspaces"
          className="flex-1 bg-transparent outline-none font-body-sm text-body-sm text-on-surface placeholder:text-on-surface-variant"
        />
        <kbd className="px-2 py-0.5 rounded-full bg-surface-container-lowest/70 border border-surface-container-lowest text-on-surface-variant font-label-caption text-label-caption shadow-sm">⌘K</kbd>
      </div>
      {open && (
        <div className="absolute z-30 mt-2 w-full rounded-2xl bg-surface-container-lowest/95 backdrop-blur-xl shadow-lg p-2">
          {hits.length === 0 && <div className="px-3 py-2 text-body-sm text-on-surface-variant">No workspace matches “{q}”.</div>}
          {hits.map((w) => (
            <button key={w.to} onMouseDown={() => (nav(w.to), setQ(""))} className="w-full flex items-center gap-3 px-3 py-2 rounded-xl hover:bg-surface-container text-left">
              <Icon name={w.icon} className="text-primary-container text-[20px]" />
              <span className="flex flex-col">
                <span className="font-title-card text-title-card text-on-surface">{w.name}</span>
                <span className="font-label-caption text-label-caption text-on-surface-variant">{w.hint}</span>
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function Bell({ health }: { health: HealthState }) {
  const [open, setOpen] = useState(false);
  const { n, total } = modelCount(health);
  const problem = health.kind !== "ok" || n < total;
  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        aria-label="System status"
        className="relative w-10 h-10 rounded-full bg-surface-container-lowest/50 backdrop-blur-md border border-surface-container-lowest/80 flex items-center justify-center text-on-surface hover:bg-surface-container-lowest/80 transition-all"
        type="button"
      >
        <Icon name="notifications" className="text-[20px]" />
        {problem && <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-primary-container ring-2 ring-surface-container-lowest" />}
      </button>
      {open && (
        <div className="absolute right-0 z-30 mt-2 w-64 rounded-2xl bg-surface-container-lowest/95 backdrop-blur-xl shadow-lg p-4 text-body-sm">
          <div className="font-title-card text-title-card text-on-surface mb-2">System status</div>
          {health.kind === "down" && <div className="text-error">Backend offline — start the API (docker compose up).</div>}
          {health.kind === "ok" &&
            Object.entries(health.health.models_loaded).map(([k, v]) => (
              <div key={k} className="flex justify-between py-0.5">
                <span className="text-on-surface-variant">{k}</span>
                <span className={v ? "text-tertiary font-semibold" : "text-error font-semibold"}>{v ? "loaded" : "missing"}</span>
              </div>
            ))}
          {health.kind === "ok" && <div className="mt-2 text-on-surface-variant text-label-caption">Providers: {health.health.providers.join(", ")}</div>}
        </div>
      )}
    </div>
  );
}

interface Props {
  health: HealthState;
  dark: boolean;
  onTheme: (dark: boolean) => void;
}

export default function Header({ health, dark, onTheme }: Props) {
  return (
    <header className="w-full h-16 flex items-center justify-between shrink-0 mb-4 px-2">
      <div className="flex items-center gap-space-sm">
        <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center ring-2 ring-surface-container-lowest/80 shadow-sm">
          <Icon name="person" className="text-on-primary text-[20px]" />
        </div>
        <div className="flex flex-col">
          <span className="font-title-card text-title-card text-on-surface leading-none">Welcome, Ruhan!</span>
          <span className="font-label-caption text-label-caption text-on-surface-variant mt-0.5">GenAI Studio · AI-4009 Assignment 1</span>
        </div>
      </div>
      <Search />
      <div className="flex items-center gap-space-sm">
        <div className="flex items-center h-10 px-1.5 py-1 rounded-full bg-surface-container-lowest/50 backdrop-blur-md border border-surface-container-lowest/80 gap-1">
          {[false, true].map((d) => (
            <button
              key={String(d)}
              onClick={() => onTheme(d)}
              aria-label={d ? "Dark theme" : "Light theme"}
              className={`w-7 h-7 rounded-full flex items-center justify-center ${dark === d ? "bg-surface-container-lowest text-on-surface shadow-sm" : "text-on-surface-variant hover:text-on-surface"}`}
              type="button"
            >
              <Icon name={d ? "dark_mode" : "light_mode"} className="text-[16px]" />
            </button>
          ))}
        </div>
        <Bell health={health} />
      </div>
    </header>
  );
}
