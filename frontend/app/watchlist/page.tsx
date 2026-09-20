"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AuthGuard } from "@/components/AuthGuard";
import { PosterArt } from "@/components/PosterArt";
import { EmptyState, ErrorState } from "@/components/StateViews";
import { watchlistApi } from "@/lib/api/watchlist";
import { ApiError } from "@/lib/api/client";
import { parseMovieTitle } from "@/lib/utils";
import type { WatchlistItem } from "@/lib/types";

function WatchlistContent() {
  const [items, setItems] = useState<WatchlistItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [removingId, setRemovingId] = useState<number | null>(null);

  function load() {
    setError(null);
    watchlistApi
      .list()
      .then(setItems)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Couldn't load your watchlist."));
  }

  useEffect(load, []);

  async function handleRemove(movieId: number) {
    const previous = items;
    setRemovingId(movieId);
    setItems((current) => current?.filter((i) => i.movie_id !== movieId) ?? null); // optimistic
    try {
      await watchlistApi.remove(movieId);
    } catch (err) {
      setItems(previous ?? null); // revert
      setError(err instanceof ApiError ? err.message : "Couldn't remove that movie.");
    } finally {
      setRemovingId(null);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-baseline justify-between">
        <div>
          <h1 className="text-2xl font-bold text-ink">Your watchlist</h1>
          <p className="mt-1 text-sm text-ink-muted">Movies you've saved to watch later.</p>
        </div>
        {items && items.length > 0 && <span className="text-sm text-ink-faint">{items.length} saved</span>}
      </div>

      {error ? (
        <ErrorState message={error} onRetry={load} />
      ) : items === null ? (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4 lg:grid-cols-6">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="skeleton aspect-[2/3] rounded-xl" />
          ))}
        </div>
      ) : items.length === 0 ? (
        <EmptyState
          title="Your watchlist is empty"
          description="Add movies from their detail page to save them here."
          action={
            <Link href="/search" className="accent-gradient-bg rounded-lg px-4 py-2 text-sm font-medium text-white">
              Browse movies
            </Link>
          }
        />
      ) : (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4 lg:grid-cols-6">
          {items.map((item) => {
            const { name, year } = parseMovieTitle(item.title);
            return (
              <div key={item.movie_id} className="group relative">
                <Link href={`/movies/${item.movie_id}`}>
                  <PosterArt title={item.title} className="aspect-[2/3] w-full transition group-hover:scale-[1.02]" />
                  <p className="mt-2 line-clamp-2 text-sm font-medium text-ink">{name}</p>
                  {year && <p className="text-xs text-ink-faint">{year}</p>}
                </Link>
                <button
                  onClick={() => handleRemove(item.movie_id)}
                  disabled={removingId === item.movie_id}
                  aria-label={`Remove ${name} from watchlist`}
                  className="absolute right-2 top-2 rounded-full bg-black/60 p-1.5 text-white/80 opacity-0 backdrop-blur transition hover:text-white group-hover:opacity-100 focus-visible:opacity-100 disabled:opacity-60"
                >
                  <svg viewBox="0 0 20 20" className="h-3.5 w-3.5" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
                    <path d="M5 5l10 10M15 5L5 15" strokeLinecap="round" />
                  </svg>
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default function WatchlistPage() {
  return (
    <AuthGuard>
      <WatchlistContent />
    </AuthGuard>
  );
}
