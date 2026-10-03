import { useCallback, useState } from "react";

export interface InferenceState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  run: (form: FormData) => Promise<void>;
  reset: () => void;
  dismissError: () => void;
}

/** Wraps one API call with loading / error / result state (every async operation has all three). */
export function useInference<T>(call: (form: FormData) => Promise<T>): InferenceState<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = useCallback(
    async (form: FormData) => {
      setLoading(true);
      setError(null);
      try {
        setData(await call(form));
      } catch (e) {
        setData(null);
        setError(e instanceof Error ? e.message : "Unexpected error");
      } finally {
        setLoading(false);
      }
    },
    [call],
  );

  return { data, loading, error, run, reset: () => setData(null), dismissError: () => setError(null) };
}
