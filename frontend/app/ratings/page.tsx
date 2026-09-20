"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AuthGuard } from "@/components/AuthGuard";
import { PosterArt } from "@/components/PosterArt";
import { StarRating } from "@/components/StarRating";
import { EmptyState, ErrorState } from "@/components/StateViews";
import { ratingsApi } from "@/lib/api/ratings";
import { ApiError } from "@/lib/api/client";
import { parseMovieTitle } from "@/lib/utils";
import type { Rating } from "@/lib/types";

function RatingsContent() {
  const [ratings, setRatings] = useState<Rating[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [savingId, setSavingId] = useState<number | null>(null);

  function load() {
    setError(null);
    ratingsApi
      .list()
      .then(setRatings)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Couldn't load your ratings."));
  }

  useEffect(load, []);

  async function handleChangeRating(movieId: number, newRating: number) {
    setSavingId(movieId);
    try {
      await ratingsApi.rate(movieId, newRating);
      setRatings((current) => current?.map((r) => (r.movie_id === movieId ? { ...r, rating: newRating } : r)) ?? null);
    } catch {
      // Leave the displayed rating as-is; a fuller implementation would surface a toast here.
    } finally {
      setSavingId(null);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-ink">My ratings</h1>
        <p className="mt-1 text-sm text-ink-muted">Change a rating any time — recommendations update automatically.</p>
      </div>

      {error ? (
        <ErrorState message={error} onRetry={load} />
      ) : ratings === null ? (
        <div className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="skeleton h-20 w-full rounded-xl" />
          ))}
        </div>
      ) : ratings.length === 0 ? (
        <EmptyState
          title="You haven't rated any movies yet"
          description="Rate a few movies to unlock personalized recommendations."
          action={
            <Link href="/search" className="accent-gradient-bg rounded-lg px-4 py-2 text-sm font-medium text-white">
              Find something to rate
            </Link>
          }
        />
      ) : (
        <ul className="space-y-3">
          {ratings.map((r) => {
            const { name, year } = parseMovieTitle(r.title ?? `Movie #${r.movie_id}`);
            return (
              <li key={r.movie_id} className="glass flex items-center gap-4 rounded-xl p-3">
                <Link href={`/movies/${r.movie_id}`} className="shrink-0">
                  <PosterArt title={r.title ?? name} className="h-20 w-14" />
                </Link>
                <div className="min-w-0 flex-1">
                  <Link href={`/movies/${r.movie_id}`} className="truncate text-sm font-medium text-ink hover:underline">
                    {name} {year && <span className="text-ink-faint">({year})</span>}
                  </Link>
                  <div className="mt-1.5">
                    <StarRating
                      value={r.rating}
                      onChange={savingId === r.movie_id ? undefined : (v) => handleChangeRating(r.movie_id, v)}
                      size="sm"
                    />
                  </div>
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

export default function RatingsPage() {
  return (
    <AuthGuard>
      <RatingsContent />
    </AuthGuard>
  );
}
