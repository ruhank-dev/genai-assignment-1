import { ReactNode, useEffect, useState } from "react";
import { api } from "../../services/api";
import type { HealthResponse } from "../../types";
import Navbar from "./Navbar";

type Status = { kind: "loading" } | { kind: "down" } | { kind: "ok"; health: HealthResponse };

function HealthBadge() {
  const [s, setS] = useState<Status>({ kind: "loading" });
  useEffect(() => {
    api.health().then((health) => setS({ kind: "ok", health })).catch(() => setS({ kind: "down" }));
  }, []);
  if (s.kind === "loading") return <span className="text-xs text-slate-400">checking backend…</span>;
  if (s.kind === "down") return <span className="rounded bg-rose-500/20 px-2 py-1 text-xs text-rose-300">backend offline</span>;
  const n = Object.values(s.health.models_loaded).filter(Boolean).length;
  const total = Object.keys(s.health.models_loaded).length;
  const ok = n === total;
  return (
    <span
      title={s.health.providers.join(", ")}
      className={`rounded px-2 py-1 text-xs ${ok ? "bg-emerald-500/20 text-emerald-300" : "bg-amber-500/20 text-amber-300"}`}
    >
      {ok ? "models ready" : "models missing"} · {n}/{total}
    </span>
  );
}

export default function Shell({ children }: { children: ReactNode }) {
  return (
    <div className="flex h-full flex-col md:flex-row">
      <aside className="shrink-0 border-b border-ink-700 bg-ink-900 md:w-72 md:border-b-0 md:border-r">
        <div className="flex items-center justify-between px-5 pt-5">
          <div>
            <div className="text-lg font-bold tracking-tight">GenAI Studio</div>
            <div className="text-xs text-slate-400">AI-4009 · Assignment 1</div>
          </div>
          <HealthBadge />
        </div>
        <Navbar />
      </aside>
      <main className="min-w-0 flex-1 overflow-y-auto p-5 md:p-8">{children}</main>
    </div>
  );
}
