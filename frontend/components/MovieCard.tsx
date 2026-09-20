import Link from "next/link";
import { PosterArt } from "./PosterArt";
import { RecommendationReason } from "./RecommendationReason";
import { StarRating } from "./StarRating";
import { formatGenres, formatScore, parseMovieTitle } from "@/lib/utils";

export function MovieCard({
  movieId,
  title,
  genres,
  reason,
  score,
  userRating,
  className,
}: {
  movieId: number;
  title: string;
  genres?: string[];
  reason?: string;
  score?: number;
  userRating?: number;
  className?: string;
}) {
  const { name, year } = parseMovieTitle(title);

  return (
    <Link
      href={`/movies/${movieId}`}
      className={`group block rounded-xl transition focus-visible:ring-2 focus-visible:ring-accent-soft ${className ?? ""}`}
    >
      <PosterArt title={title} className="aspect-[2/3] w-full transition group-hover:scale-[1.02] group-hover:shadow-glow" />
      <div className="mt-2.5 space-y-0.5">
        <h3 className="line-clamp-2 text-sm font-medium text-ink" title={title}>
          {name}
        </h3>
        <div className="flex items-center gap-2 text-xs text-ink-faint">
          {year && <span>{year}</span>}
          {genres && genres.length > 0 && <span className="truncate">{formatGenres(genres, 2)}</span>}
        </div>
        {typeof userRating === "number" && (
          <div className="pt-0.5">
            <StarRating value={userRating} readOnly size="sm" />
          </div>
        )}
        {reason && <RecommendationReason reason={reason} />}
        {typeof score === "number" && !reason && <p className="text-xs text-ink-faint">{formatScore(score)}</p>}
      </div>
    </Link>
  );
}
