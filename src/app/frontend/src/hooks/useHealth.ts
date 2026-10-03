import { useEffect, useState } from "react";
import { api } from "../services/api";
import type { HealthResponse } from "../types";

export type HealthState = { kind: "loading" } | { kind: "down" } | { kind: "ok"; health: HealthResponse };

/** Polls /health once on mount and every 15 s (backend / model readiness for the header, bell and status cards). */
export function useHealth(): HealthState {
  const [s, setS] = useState<HealthState>({ kind: "loading" });
  useEffect(() => {
    let alive = true;
    const poll = () =>
      api
        .health()
        .then((health) => alive && setS({ kind: "ok", health }))
        .catch(() => alive && setS({ kind: "down" }));
    void poll();
    const t = setInterval(poll, 15000);
    return () => {
      alive = false;
      clearInterval(t);
    };
  }, []);
  return s;
}

export function modelCount(s: HealthState): { n: number; total: number } {
  if (s.kind !== "ok") return { n: 0, total: 7 };
  const v = Object.values(s.health.models_loaded);
  return { n: v.filter(Boolean).length, total: v.length };
}
