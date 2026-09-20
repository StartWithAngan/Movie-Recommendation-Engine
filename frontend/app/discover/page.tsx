"use client";

import { useEffect, useMemo, useState } from "react";
import { AuthGuard } from "@/components/AuthGuard";
import { MovieRow } from "@/components/MovieRow";
import { RecommendationSection } from "@/components/RecommendationSection";
import { ErrorState } from "@/components/StateViews";
import { useAuth } from "@/lib/auth-context";
import { moviesApi } from "@/lib/api/movies";
import { ratingsApi } from "@/lib/api/ratings";
import { recommendationsApi } from "@/lib/api/recommendations";
import { ApiError } from "@/lib/api/client";
import type { Movie, Rating, Recommendation } from "@/lib/types";

function topRatedAnchors(ratings: Rating[], count: number): Rating[] {
  return [...ratings].sort((a, b) => b.rating - a.rating).slice(0, count);
}

function DiscoverContent() {
  const { user } = useAuth();

  const [recommendations, setRecommendations] = useState<Recommendation[] | null>(null);
  const [isColdStart, setIsColdStart] = useState(false);
  const [ratings, setRatings] = useState<Rating[] | null>(null);
  const [similarToTop, setSimilarToTop] = useState<Recommendation[] | null>(null);
  const [similarToSecond, setSimilarToSecond] = useState<Recommendation[] | null>(null);
  const [browseMovies, setBrowseMovies] = useState<Movie[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function loadAll() {
    setError(null);
    try {
      const [recRes, myRatings] = await Promise.all([recommendationsApi.get(12), ratingsApi.list()]);
      setRecommendations(recRes.recommendations);
      setIsColdStart(recRes.is_cold_start);
      setRatings(myRatings);

      if (!recRes.is_cold_start && myRatings.length > 0) {
        const anchors = topRatedAnchors(myRatings, 2);
        recommendationsApi
          .similar(anchors[0].movie_id, 12)
          .then(setSimilarToTop)
          .catch(() => setSimilarToTop([]));

        if (anchors[1]) {
          recommendationsApi
            .similar(anchors[1].movie_id, 12)
            .then(setSimilarToSecond)
            .catch(() => setSimilarToSecond([]));
        } else {
          setSimilarToSecond([]);
        }
      } else {
        setSimilarToTop([]);
        setSimilarToSecond([]);
      }

      const ratedIds = new Set(myRatings.map((r) => r.movie_id));
      const catalog = await moviesApi.list(1, 24);
      setBrowseMovies(catalog.results.filter((m) => !ratedIds.has(m.movie_id)).slice(0, 12));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unable to load your recommendations.");
    }
  }

  useEffect(() => {
    loadAll();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const anchors = useMemo(() => (ratings ? topRatedAnchors(ratings, 2) : []), [ratings]);
  const highlyRated = useMemo(
    () => (recommendations ?? []).filter((r) => r.reason === "Similar to movies you rated highly"),
    [recommendations]
  );

  if (error) {
    return <ErrorState message={error} onRetry={loadAll} />;
  }

  return (
    <div className="space-y-12">
      <section>
        <h1 className="text-2xl font-bold text-ink sm:text-3xl">
          {user ? `Welcome back, ${user.display_name}` : "Welcome back"}
        </h1>
        <p className="mt-1 text-sm text-ink-muted">
          {recommendations === null
            ? "Loading your recommendations…"
            : isColdStart
            ? "Start rating movies to unlock personalized recommendations."
            : "Here's what we think you'll enjoy next."}
        </p>
      </section>

      <RecommendationSection
        title={isColdStart ? "Popular right now" : "Recommended for you"}
        subtitle={isColdStart ? "Popular picks to get you started." : "A hybrid ranking based on your rating history."}
        isLoading={recommendations === null}
        isEmpty={(recommendations ?? []).length === 0}
        emptyMessage="Rate a few movies to unlock recommendations."
      >
        <MovieRow items={recommendations ?? []} />
      </RecommendationSection>

      {!isColdStart && (
        <RecommendationSection
          title="Because you rated highly"
          subtitle="Picks that echo the movies you loved most."
          isLoading={recommendations === null}
          isEmpty={highlyRated.length === 0}
          emptyMessage="Rate a few more movies you loved to see this section fill in."
        >
          <MovieRow items={highlyRated} />
        </RecommendationSection>
      )}

      {!isColdStart && anchors[0] && (
        <RecommendationSection
          title={`More like ${anchors[0].title ?? "a movie you rated"}`}
          subtitle="Similar movies, based on genre and content."
          isLoading={similarToTop === null}
          isEmpty={(similarToTop ?? []).length === 0}
          emptyMessage="No close matches found for this one yet."
        >
          <MovieRow items={similarToTop ?? []} />
        </RecommendationSection>
      )}

      {!isColdStart && anchors[1] && (
        <RecommendationSection
          title={`More like ${anchors[1].title ?? "a movie you rated"}`}
          subtitle="Similar movies, based on genre and content."
          isLoading={similarToSecond === null}
          isEmpty={(similarToSecond ?? []).length === 0}
        >
          <MovieRow items={similarToSecond ?? []} />
        </RecommendationSection>
      )}

      <RecommendationSection
        title="Continue exploring"
        subtitle="More titles from the catalog you haven't rated yet."
        isLoading={browseMovies === null}
        isEmpty={(browseMovies ?? []).length === 0}
        emptyMessage="You've rated everything we have on this page — try searching for something specific."
      >
        <MovieRow items={browseMovies ?? []} />
      </RecommendationSection>
    </div>
  );
}

export default function DiscoverPage() {
  return (
    <AuthGuard>
      <DiscoverContent />
    </AuthGuard>
  );
}
