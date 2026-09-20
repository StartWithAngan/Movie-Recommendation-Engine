/**
 * The backend already returns plain-English reasons (see
 * ml/models/hybrid.py's _explain / recommend_for_app_user — e.g. "Similar
 * to movies you rated highly", "Based on your rating patterns", "Popular
 * movies recommended for new users"). This component just renders that
 * string with a small icon; it does not reinterpret or invent wording.
 */
export function RecommendationReason({ reason }: { reason: string }) {
  return (
    <p className="mt-1 flex items-center gap-1.5 text-xs text-accent-soft">
      <svg viewBox="0 0 16 16" className="h-3 w-3 shrink-0" fill="currentColor" aria-hidden="true">
        <path d="M8 1.2l1.6 3.9 4.2.4-3.2 2.8.9 4.1L8 10.3l-3.5 2.1.9-4.1-3.2-2.8 4.2-.4L8 1.2z" />
      </svg>
      <span className="truncate">{reason}</span>
    </p>
  );
}
