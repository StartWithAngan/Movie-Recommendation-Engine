"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AuthGuard } from "@/components/AuthGuard";
import { StarRating } from "@/components/StarRating";
import { StatCardSkeleton } from "@/components/Skeletons";
import { ErrorState } from "@/components/StateViews";
import { useAuth } from "@/lib/auth-context";
import { profileApi } from "@/lib/api/profile";
import { ApiError } from "@/lib/api/client";
import { parseMovieTitle } from "@/lib/utils";
import type { Analytics, ProfileStats } from "@/lib/types";

function StatCard({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="glass rounded-2xl p-5">
      <p className="text-xs uppercase tracking-wide text-ink-faint">{label}</p>
      <p className="mt-1.5 text-2xl font-bold text-ink">{value}</p>
    </div>
  );
}

/** favorite_genres is `[]` when empty, `{genre: count}` otherwise — see lib/types.ts. */
function genreEntries(favoriteGenres: Analytics["favorite_genres"]): [string, number][] {
  return Array.isArray(favoriteGenres) ? [] : Object.entries(favoriteGenres);
}

function RatingDistributionBars({ distribution }: { distribution: Record<string, number> }) {
  const entries = Object.entries(distribution)
    .map(([rating, count]) => [Number(rating), count] as [number, number])
    .sort((a, b) => a[0] - b[0]);
  const max = Math.max(1, ...entries.map(([, count]) => count));

  if (entries.length === 0) return null;

  return (
    <div className="flex items-end gap-2" role="img" aria-label="Rating distribution">
      {entries.map(([rating, count]) => (
        <div key={rating} className="flex flex-1 flex-col items-center gap-1.5">
          <div className="flex h-24 w-full items-end">
            <div
              className="accent-gradient-bg w-full rounded-t-md"
              style={{ height: `${Math.max(4, (count / max) * 100)}%` }}
              title={`${count} rating${count === 1 ? "" : "s"} at ${rating}`}
            />
          </div>
          <span className="text-xs text-ink-faint">{rating}</span>
        </div>
      ))}
    </div>
  );
}

function ProfileContent() {
  const { user } = useAuth();
  const [stats, setStats] = useState<ProfileStats | null>(null);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [error, setError] = useState<string | null>(null);

  function load() {
    setError(null);
    Promise.all([profileApi.getStats(), profileApi.getAnalytics()])
      .then(([s, a]) => {
        setStats(s);
        setAnalytics(a);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "Couldn't load your profile."));
  }

  useEffect(load, []);

  if (error) return <ErrorState message={error} onRetry={load} />;

  return (
    <div className="space-y-10">
      <section>
        <h1 className="text-2xl font-bold text-ink">Profile</h1>
        {user && (
          <p className="mt-1 text-sm text-ink-muted">
            {user.display_name} · {user.email}
          </p>
        )}
      </section>

      <section className="grid grid-cols-2 gap-4 sm:grid-cols-3">
        {stats === null ? (
          <>
            <StatCardSkeleton />
            <StatCardSkeleton />
            <StatCardSkeleton />
          </>
        ) : (
          <>
            <StatCard label="Ratings" value={stats.ratings_count} />
            <StatCard label="Average rating" value={stats.avg_rating_given.toFixed(2)} />
            <StatCard
              label="Favorite genres"
              value={
                stats.favorite_genres.length > 0 ? (
                  <span className="text-base font-semibold">{stats.favorite_genres.slice(0, 3).join(" · ")}</span>
                ) : (
                  <span className="text-base font-normal text-ink-faint">Rate a few movies</span>
                )
              }
            />
          </>
        )}
      </section>

      <section>
        <h2 className="mb-4 text-lg font-semibold text-ink">Top-rated movies</h2>
        {stats === null ? (
          <div className="skeleton h-40 w-full rounded-xl" />
        ) : stats.top_rated_movies.length === 0 ? (
          <p className="text-sm text-ink-muted">No ratings yet.</p>
        ) : (
          <ul className="divide-y divide-base-border overflow-hidden rounded-xl border border-base-border">
            {stats.top_rated_movies.map((m) => {
              const { name, year } = parseMovieTitle(m.title ?? `Movie #${m.movie_id}`);
              return (
                <li key={m.movie_id} className="flex items-center justify-between gap-4 bg-base-surface px-4 py-3">
                  <Link href={`/movies/${m.movie_id}`} className="truncate text-sm text-ink hover:underline">
                    {name} {year && <span className="text-ink-faint">({year})</span>}
                  </Link>
                  <StarRating value={m.rating} readOnly size="sm" />
                </li>
              );
            })}
          </ul>
        )}
      </section>

      <section>
        <h2 className="mb-4 text-lg font-semibold text-ink">Analytics</h2>
        {analytics === null ? (
          <div className="skeleton h-40 w-full rounded-xl" />
        ) : analytics.ratings_count === 0 ? (
          <p className="text-sm text-ink-muted">Rate a few movies to see your analytics here.</p>
        ) : (
          <div className="glass grid grid-cols-1 gap-6 rounded-2xl p-5 sm:grid-cols-2">
            <div>
              <p className="mb-3 text-sm font-medium text-ink">Rating distribution</p>
              <RatingDistributionBars distribution={analytics.rating_distribution} />
            </div>
            <div>
              <p className="mb-3 text-sm font-medium text-ink">Favorite genres</p>
              <div className="flex flex-wrap gap-2">
                {genreEntries(analytics.favorite_genres).map(([genre, count]) => (
                  <span
                    key={genre}
                    className="rounded-full border border-base-border px-3 py-1 text-xs text-ink-muted"
                  >
                    {genre} · {count}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}

export default function ProfilePage() {
  return (
    <AuthGuard>
      <ProfileContent />
    </AuthGuard>
  );
}
