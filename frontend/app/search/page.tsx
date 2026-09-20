"use client";

import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { moviesApi } from "@/lib/api/movies";
import { ApiError } from "@/lib/api/client";
import { useDebouncedValue } from "@/lib/hooks";
import { MovieCard } from "@/components/MovieCard";
import { MovieCardSkeleton } from "@/components/Skeletons";
import { EmptyState, ErrorState } from "@/components/StateViews";
import type { Movie } from "@/lib/types";

const GENRES = ["Action", "Comedy", "Drama", "Horror", "Romance", "Sci-Fi", "Animation", "Thriller", "Adventure", "Crime"];

function SearchContent() {
  const searchParams = useSearchParams();
  const [query, setQuery] = useState(searchParams.get("q") ?? "");
  const [genre, setGenre] = useState<string | null>(null);
  const [results, setResults] = useState<Movie[] | null>(null);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const debouncedQuery = useDebouncedValue(query, 350);

  useEffect(() => {
    const trimmed = debouncedQuery.trim();
    if (!trimmed) {
      setResults(null);
      setError(null);
      return;
    }
    let cancelled = false;
    setLoading(true);
    setError(null);

    moviesApi
      .search(trimmed, genre ?? undefined, 1, 24)
      .then((res) => {
        if (cancelled) return;
        setResults(res.results);
        setTotal(res.total);
      })
      .catch((err) => {
        if (cancelled) return;
        setError(err instanceof ApiError ? err.message : "Search failed. Please try again.");
        setResults([]);
      })
      .finally(() => !cancelled && setLoading(false));

    return () => {
      cancelled = true;
    };
  }, [debouncedQuery, genre]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-ink">Search</h1>
        <p className="mt-1 text-sm text-ink-muted">Find movies by title, then narrow by genre.</p>
      </div>

      <div className="space-y-3">
        <div className="relative max-w-lg">
          <label htmlFor="search-input" className="sr-only">
            Search movies by title
          </label>
          <svg
            aria-hidden="true"
            viewBox="0 0 20 20"
            className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-faint"
            fill="none"
          >
            <circle cx="9" cy="9" r="6" stroke="currentColor" strokeWidth="1.5" />
            <path d="M14 14l4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
          <input
            id="search-input"
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search movies by title…"
            autoFocus
            className="w-full rounded-lg border border-base-border bg-base-surface py-2.5 pl-9 pr-3 text-sm text-ink placeholder:text-ink-faint focus:border-accent-soft focus:outline-none"
          />
        </div>

        <div className="flex flex-wrap gap-2" role="group" aria-label="Filter by genre">
          {GENRES.map((g) => (
            <button
              key={g}
              type="button"
              onClick={() => setGenre((current) => (current === g ? null : g))}
              aria-pressed={genre === g}
              className={`rounded-full border px-3 py-1 text-xs transition ${
                genre === g
                  ? "border-accent-soft bg-accent-soft/15 text-accent-soft"
                  : "border-base-border text-ink-muted hover:border-base-borderStrong hover:text-ink"
              }`}
            >
              {g}
            </button>
          ))}
        </div>
      </div>

      {error ? (
        <ErrorState message={error} />
      ) : query.trim() === "" ? (
        <EmptyState title="Search for a movie" description="Try a title, or pick a genre above to narrow things down." />
      ) : loading ? (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
          {Array.from({ length: 12 }).map((_, i) => (
            <MovieCardSkeleton key={i} />
          ))}
        </div>
      ) : (results ?? []).length === 0 ? (
        <EmptyState title="No movies found" description="Try a different title or clear the genre filter." />
      ) : (
        <>
          <p className="text-xs text-ink-faint">
            {total} result{total === 1 ? "" : "s"}
          </p>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
            {(results ?? []).map((m) => (
              <MovieCard key={m.movie_id} movieId={m.movie_id} title={m.title} genres={m.genres} />
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={null}>
      <SearchContent />
    </Suspense>
  );
}
