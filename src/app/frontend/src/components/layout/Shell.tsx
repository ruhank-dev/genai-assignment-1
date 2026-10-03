import { ReactNode, useEffect, useState } from "react";
import { NavLink, useLocation } from "react-router-dom";
import { useHealth } from "../../hooks/useHealth";
import Icon from "../ui/Icon";
import Header from "./Header";
import { WORKSPACES } from "./workspaces";

function themeStored(): boolean {
  try {
    return localStorage.getItem("genai-theme") === "dark";
  } catch {
    return false;
  }
}

/** Fixed glass frame exactly as in the Stitch design: header, floating icon rail, scrolling main area, footer tabs. */
export default function Shell({ children }: { children: (resetKey: number) => ReactNode }) {
  const health = useHealth();
  const [dark, setDark] = useState(themeStored);
  const [resetKey, setResetKey] = useState(0);
  const loc = useLocation();

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    try {
      localStorage.setItem("genai-theme", dark ? "dark" : "light");
    } catch {
      /* storage unavailable */
    }
  }, [dark]);

  return (
    <div id="app-root" className="min-h-screen w-full bg-gradient-to-br from-[#ffd8be] via-[#fff4cc] to-[#cfd8ff] relative overflow-x-hidden font-body-md text-on-surface antialiased">
      <div className="fixed inset-0 pointer-events-none z-0">
        <div className="absolute -top-32 -left-32 w-96 h-96 bg-[#ffd1b3] rounded-full blur-[100px] opacity-70" />
        <div className="absolute top-1/4 right-0 w-[500px] h-[500px] bg-[#c3ceff] rounded-full blur-[120px] opacity-60" />
        <div className="absolute -bottom-32 left-1/3 w-[600px] h-[400px] bg-[#d5f0e3] rounded-full blur-[110px] opacity-60" />
      </div>
      <div className="relative z-10 max-w-[1400px] h-[min(960px,calc(100vh-3rem))] min-h-[640px] mx-auto my-6 rounded-[40px] bg-surface-container-lowest/25 backdrop-blur-2xl border border-surface-container-lowest/60 shadow-[0_20px_60px_-15px_rgba(31,38,135,0.08),inset_0_1px_2px_rgba(255,255,255,0.9)] p-6 flex flex-col justify-between overflow-hidden">
        <Header health={health} dark={dark} onTheme={setDark} />
        <div className="flex-1 flex gap-space-lg overflow-hidden min-h-0 relative">
          <aside className="w-16 shrink-0 flex flex-col items-center justify-center">
            <nav aria-label="Workspaces" className="rounded-full bg-surface-container-lowest/40 backdrop-blur-xl border border-surface-container-lowest/70 p-2 flex flex-col items-center gap-3 shadow-sm">
              {WORKSPACES.map((w) => (
                <NavLink
                  key={w.to}
                  to={w.to}
                  title={w.name}
                  aria-label={w.name}
                  className={({ isActive }) =>
                    `w-10 h-10 rounded-full flex items-center justify-center transition-all ${
                      isActive ? "bg-surface-container-lowest text-primary-container shadow-md scale-105" : "text-on-surface-variant hover:bg-surface-container-lowest/60 hover:text-on-surface"
                    }`
                  }
                >
                  <Icon name={w.icon} className="text-[20px]" />
                </NavLink>
              ))}
            </nav>
          </aside>
          <main key={loc.pathname + resetKey} className="flex-1 overflow-y-auto pr-1 h-full min-h-0">
            {children(resetKey)}
          </main>
        </div>
        <footer className="w-full h-14 shrink-0 flex items-center justify-between px-2 pt-2">
          <nav aria-label="Workspace tabs" className="flex items-center gap-1.5 p-1 rounded-full bg-surface-container-lowest/45 backdrop-blur-xl border border-surface-container-lowest/70 shadow-sm">
            {WORKSPACES.map((w) => (
              <NavLink
                key={w.to}
                to={w.to}
                className={({ isActive }) =>
                  `px-4 py-2 rounded-full transition-all ${
                    isActive ? "bg-surface-container-lowest text-on-surface font-title-card text-title-card shadow-sm" : "font-label-prominent text-label-prominent text-on-surface-variant hover:text-on-surface"
                  }`
                }
              >
                {w.tab}
              </NavLink>
            ))}
          </nav>
          <button
            onClick={() => setResetKey((k) => k + 1)}
            title="New session — clear this workspace"
            aria-label="New session"
            className="w-11 h-11 rounded-full bg-surface-container-lowest/60 backdrop-blur-xl border border-surface-container-lowest/80 flex items-center justify-center text-on-surface hover:bg-surface-container-lowest hover:scale-105 transition-all shadow-sm"
            type="button"
          >
            <Icon name="add" className="text-[22px]" />
          </button>
        </footer>
      </div>
    </div>
  );
}
