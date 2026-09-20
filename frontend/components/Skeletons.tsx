import { cn } from "@/lib/utils";

export function MovieCardSkeleton({ className }: { className?: string }) {
  return (
    <div className={cn("w-full", className)}>
      <div className="skeleton aspect-[2/3] w-full rounded-xl" />
      <div className="skeleton mt-3 h-4 w-3/4 rounded" />
      <div className="skeleton mt-2 h-3 w-1/2 rounded" />
    </div>
  );
}

export function MovieRowSkeleton({ count = 6 }: { count?: number }) {
  return (
    <div className="row-scroll">
      {Array.from({ length: count }).map((_, i) => (
        <MovieCardSkeleton key={i} className="w-36 sm:w-44" />
      ))}
    </div>
  );
}

export function StatCardSkeleton() {
  return (
    <div className="glass rounded-2xl p-5">
      <div className="skeleton h-3 w-20 rounded" />
      <div className="skeleton mt-3 h-7 w-16 rounded" />
    </div>
  );
}
