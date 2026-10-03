import type {
  HardRoutedRestoreResponse,
  HealthResponse,
  SketchGenerateResponse,
  SoftMoERestoreResponse,
  UniversalRestoreResponse,
} from "../types";

const BASE: string = import.meta.env.VITE_API_BASE ?? "";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function parseError(res: Response): Promise<string> {
  try {
    const body: { detail?: unknown } = await res.json();
    if (typeof body.detail === "string") return body.detail;
    if (Array.isArray(body.detail)) return body.detail.map((d: { msg?: string }) => d.msg ?? "invalid input").join("; ");
  } catch {
    /* fall through */
  }
  return `Request failed (HTTP ${res.status})`;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(BASE + path, init);
  } catch {
    throw new ApiError("Cannot reach the backend. Is it running?", 0);
  }
  if (!res.ok) throw new ApiError(await parseError(res), res.status);
  return (await res.json()) as T;
}

const post = <T>(path: string, form: FormData) => request<T>(path, { method: "POST", body: form });

export const api = {
  health: () => request<HealthResponse>("/health"),
  restoreUniversal: (f: FormData) => post<UniversalRestoreResponse>("/api/v1/restore/universal", f),
  restoreHardRouted: (f: FormData) => post<HardRoutedRestoreResponse>("/api/v1/restore/hard-routed", f),
  restoreSoftMoE: (f: FormData) => post<SoftMoERestoreResponse>("/api/v1/restore/soft-moe", f),
  generateSketch: (f: FormData) => post<SketchGenerateResponse>("/api/v1/sketch/generate", f),
};

export function dataUrlToFile(dataUrl: string, name: string): File {
  const [head, b64] = dataUrl.split(",");
  const mime = /data:(.*?);/.exec(head)?.[1] ?? "image/png";
  const bin = atob(b64);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return new File([bytes], name, { type: mime });
}
