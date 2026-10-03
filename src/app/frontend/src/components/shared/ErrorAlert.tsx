interface Props {
  message: string;
  onDismiss: () => void;
  onRetry?: () => void;
}

export default function ErrorAlert({ message, onDismiss, onRetry }: Props) {
  return (
    <div role="alert" className="flex items-start justify-between gap-4 rounded-lg border border-rose-300 bg-rose-100/70 px-4 py-3 text-sm text-rose-700">
      <span>{message}</span>
      <span className="flex shrink-0 gap-3">
        {onRetry && (
          <button onClick={onRetry} className="font-semibold underline">
            Retry
          </button>
        )}
        <button onClick={onDismiss} aria-label="Dismiss error" className="font-semibold">
          ✕
        </button>
      </span>
    </div>
  );
}
