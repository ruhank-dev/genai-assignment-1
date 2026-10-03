import { ReactNode, useEffect, useState } from "react";
import { api } from "../../services/api";
import type { HealthResponse } from "../../types";
import { BottomTabs, SideNav } from "./Navbar";

type Status = { kind: "loading" } | { kind: "down" } | { kind: "ok"; health: HealthResponse };

function HealthBadge() {
  const [s, setS] = useState<Status>({ kind: "loading" });
  useEffect(() => {
    api.health().then((health) => setS({ kind: "ok", health })).catch(() => setS({ kind: "down" }));
  }, []);
  if (s.kind === "loading") return <span className="glass-pill px-3 py-1.5 text-xs text-slate-500">checking backend…</span>;
  if (s.kind === "down") return <span className="glass-pill px-3 py-1.5 text-xs font-semibold text-rose-600">● backend offline</span>;
  const n = Object.values(s.health.models_loaded).filter(Boolean).length;
  const total = Object.keys(s.health.models_loaded).length;
  const ok = n === total;
  return (
    <span title={s.health.providers.join(", ")} className="glass-pill flex items-center gap-2 px-3 py-1.5 text-xs font-semibold">
      <span className={`h-2.5 w-2.5 rounded-full ${ok ? "bg-emerald-500" : "bg-amber-500"}`} />
      {ok ? "Models ready" : "Models missing"} {n}/{total}
    </span>
  );
}

export default function Shell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#ffd8be] via-[#fff4cc] to-[#cfd8ff] p-3 md:p-6">
      <div className="glass-frame mx-auto flex min-h-[calc(100vh-3rem)] max-w-[1500px] flex-col gap-4 p-4 md:p-6">
        <header className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-full bg-amber-700 font-display text-sm font-bold text-white">RK</div>
            <div>
              <div className="font-display text-lg font-bold leading-tight">GenAI Studio</div>
              <div className="text-xs text-slate-500">Muhammad Ruhan Kamran · AI-4009 Assignment 1</div>
            </div>
          </div>
          <HealthBadge />
        </header>
        <div className="flex flex-1 flex-col gap-4 md:flex-row">
          <div className="md:sticky md:top-6 md:self-start">
            <SideNav />
          </div>
          <main className="min-w-0 flex-1">{children}</main>
        </div>
        <footer className="flex justify-center md:justify-start">
          <BottomTabs />
        </footer>
      </div>
    </div>
  );
}
