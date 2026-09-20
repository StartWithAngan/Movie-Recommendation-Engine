import type { ReactNode } from "react";
import { MovieRowSkeleton } from "./Skeletons";
import { EmptyState } from "./StateViews";

export function RecommendationSection({
  title,
  subtitle,
  isLoading,
  isEmpty,
  emptyMessage,
  children,
  action,
}: {
  title: string;
  subtitle?: string;
  isLoading: boolean;
  isEmpty: boolean;
  emptyMessage?: string;
  children: ReactNode;
  action?: ReactNode;
}) {
  return (
    <section className="animate-fade-in">
      <div className="mb-4 flex items-end justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-ink sm:text-xl">{title}</h2>
          {subtitle && <p className="mt-0.5 text-sm text-ink-muted">{subtitle}</p>}
        </div>
        {action}
      </div>
      {isLoading ? (
        <MovieRowSkeleton />
      ) : isEmpty ? (
        <EmptyState title={emptyMessage ?? "Nothing to show here yet."} />
      ) : (
        children
      )}
    </section>
  );
}
