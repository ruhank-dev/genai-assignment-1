import { useCallback, useState } from "react";

export interface InferenceState<T, A> {
  data: T | null;
  loading: boolean;
  error: string | null;
  run: (arg: A) => Promise<void>;
  reset: () => void;
  dismissError: () => void;
}

/** Wraps one async operation with loading / error / result state (every async operation has all three). */
export function useInference<T, A = FormData>(call: (arg: A) => Promise<T>): InferenceState<T, A> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = useCallback(
    async (arg: A) => {
      setLoading(true);
      setError(null);
      try {
        setData(await call(arg));
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
