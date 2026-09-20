"use client";

import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { PosterArt } from "@/components/PosterArt";
import { StarRating } from "@/components/StarRating";
import { MovieRow } from "@/components/MovieRow";
import { MovieRowSkeleton } from "@/components/Skeletons";
import { ErrorState, EmptyState } from "@/components/StateViews";
import { useAuth } from "@/lib/auth-context";
import { moviesApi } from "@/lib/api/movies";
import { ratingsApi } from "@/lib/api/ratings";
import { recommendationsApi } from "@/lib/api/recommendations";
import { watchlistApi } from "@/lib/api/watchlist";
import { ApiError } from "@/lib/api/client";
import { formatGenres, parseMovieTitle } from "@/lib/utils";
import type { Movie, Recommendation } from "@/lib/types";

export default function MovieDetailPage() {
  const params = useParams<{ id: string }>();
  const movieId = Number(params.id);
  const router = useRouter();
  const { isAuthenticated } = useAuth();

  const [movie, setMovie] = useState<Movie | null>(null);
  const [notFound, setNotFound] = useState(false);
  const [similar, setSimilar] = useState<Recommendation[] | null>(null);
  const [myRating, setMyRating] = useState<number>(0);
  const [inWatchlist, setInWatchlist] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [statusIsError, setStatusIsError] = useState(false);
  const [ratingBusy, setRatingBusy] = useState(false);
  const [watchlistBusy, setWatchlistBusy] = useState(false);

  useEffect(() => {
    if (!Number.isFinite(movieId)) return;

    moviesApi
      .get(movieId)
      .then(setMovie)
      .catch((err) => {
        if (err instanceof ApiError && err.status === 404) setNotFound(true);
      });

    recommendationsApi
      .similar(movieId, 12)
      .then(setSimilar)
      .catch(() => setSimilar([]));

    if (isAuthenticated) {
      ratingsApi
        .list()
        .then((ratings) => {
          const existing = ratings.find((r) => r.movie_id === movieId);
          if (existing) setMyRating(existing.rating);
        })
        .catch(() => {});

      watchlistApi
        .list()
        .then((items) => setInWatchlist(items.some((i) => i.movie_id === movieId)))
        .catch(() => {});
    }
  }, [movieId, isAuthenticated]);

  async function handleRate(rating: number) {
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }
    setRatingBusy(true);
    setStatusMessage(null);
    try {
      await ratingsApi.rate(movieId, rating);
      setMyRating(rating);
      setStatusIsError(false);
      setStatusMessage("Rating saved — your recommendations will update.");
    } catch (err) {
      setStatusIsError(true);
      setStatusMessage(err instanceof ApiError ? err.message : "Couldn't save your rating.");
    } finally {
      setRatingBusy(false);
    }
  }

  async function toggleWatchlist() {
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }
    setWatchlistBusy(true);
    setStatusMessage(null);
    const nextState = !inWatchlist;
    setInWatchlist(nextState); // optimistic — safe because both add/remove are idempotent on the backend
    try {
      if (nextState) {
        await watchlistApi.add(movieId);
        setStatusMessage("Added to your watchlist.");
      } else {
        await watchlistApi.remove(movieId);
        setStatusMessage("Removed from your watchlist.");
      }
      setStatusIsError(false);
    } catch (err) {
      setInWatchlist(!nextState); // revert
      setStatusIsError(true);
      setStatusMessage(err instanceof ApiError ? err.message : "Couldn't update your watchlist.");
    } finally {
      setWatchlistBusy(false);
    }
  }

  if (notFound) {
    return <EmptyState title="Movie not found" description="This title doesn't exist in our catalog." />;
  }

  if (!movie) {
    return (
      <div className="animate-pulse">
        <div className="flex flex-col gap-8 sm:flex-row">
          <div className="skeleton aspect-[2/3] w-full rounded-xl sm:w-64" />
          <div className="flex-1 space-y-3">
            <div className="skeleton h-8 w-2/3 rounded" />
            <div className="skeleton h-4 w-1/3 rounded" />
          </div>
        </div>
      </div>
    );
  }

  const { name, year } = parseMovieTitle(movie.title);

  return (
    <div className="space-y-12">
      <section className="flex flex-col gap-8 sm:flex-row">
        <PosterArt title={movie.title} className="aspect-[2/3] w-full shrink-0 sm:w-64" />

        <div className="flex-1">
          <h1 className="text-3xl font-bold text-ink">{name}</h1>
          <p className="mt-1 text-ink-muted">
            {year && <span>{year}</span>}
            {year && movie.genres.length > 0 && <span> · </span>}
            <span>{formatGenres(movie.genres, 6)}</span>
          </p>

          <div className="mt-6 space-y-4">
            <div>
              <p className="mb-1.5 text-sm font-medium text-ink">Your rating</p>
              <StarRating value={myRating} onChange={ratingBusy ? undefined : handleRate} size="lg" label="Rate this movie" />
            </div>

            <button
              onClick={toggleWatchlist}
              disabled={watchlistBusy}
              className={`inline-flex items-center gap-2 rounded-lg border px-4 py-2 text-sm font-medium transition disabled:opacity-60 ${
                inWatchlist
                  ? "border-accent-soft bg-accent-soft/15 text-accent-soft"
                  : "border-base-border text-ink hover:border-base-borderStrong"
              }`}
              aria-pressed={inWatchlist}
            >
              <svg viewBox="0 0 20 20" className="h-4 w-4" fill={inWatchlist ? "currentColor" : "none"} stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
                <path d="M5 3.5A1.5 1.5 0 016.5 2h7A1.5 1.5 0 0115 3.5v14l-5-3-5 3v-14z" strokeLinejoin="round" />
              </svg>
              {inWatchlist ? "In your watchlist" : "Add to watchlist"}
            </button>

            {statusMessage && (
              <p role="status" className={`text-sm ${statusIsError ? "text-red-300" : "text-ink-muted"}`}>
                {statusMessage}
              </p>
            )}

            {!isAuthenticated && <p className="text-sm text-ink-faint">Sign in to rate movies and build your watchlist.</p>}
          </div>
        </div>
      </section>

      <section>
        <h2 className="mb-4 text-lg font-semibold text-ink">Similar movies</h2>
        {similar === null ? (
          <MovieRowSkeleton />
        ) : similar.length === 0 ? (
          <EmptyState title="No similar movies found" />
        ) : (
          <MovieRow items={similar} />
        )}
      </section>
    </div>
  );
}
