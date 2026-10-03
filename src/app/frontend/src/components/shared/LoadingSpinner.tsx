export default function LoadingSpinner({ label = "Running model…" }: { label?: string }) {
  return (
    <div role="status" className="flex items-center gap-3 rounded-lg bg-ink-800 px-4 py-3 text-sm text-slate-600">
      <span className="h-4 w-4 animate-spin rounded-full border-2 border-sky-400 border-t-transparent" />
      {label}
    </div>
  );
}
