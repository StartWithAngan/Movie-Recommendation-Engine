import type { Movie, Recommendation, Rating, WatchlistItem } from "@/lib/types";
import { MovieCard } from "./MovieCard";

type RowItem = Movie | Recommendation | Rating | WatchlistItem;

function isRecommendation(item: RowItem): item is Recommendation {
  return "reason" in item && "score" in item;
}
function isRating(item: RowItem): item is Rating {
  return "rating" in item;
}
function isMovie(item: RowItem): item is Movie {
  return "genres" in item;
}

export function MovieRow({ items, cardWidthClassName = "w-36 sm:w-44" }: { items: RowItem[]; cardWidthClassName?: string }) {
  return (
    <div className="row-scroll scrollbar-thin" role="list">
      {items.map((item) => (
        <div role="listitem" key={item.movie_id} className={cardWidthClassName}>
          <MovieCard
            movieId={item.movie_id}
            title={item.title || `Movie #${item.movie_id}`}
            genres={isMovie(item) ? item.genres : undefined}
            reason={isRecommendation(item) ? item.reason : undefined}
            score={isRecommendation(item) ? item.score : undefined}
            userRating={isRating(item) ? item.rating : undefined}
          />
        </div>
      ))}
    </div>
  );
}
