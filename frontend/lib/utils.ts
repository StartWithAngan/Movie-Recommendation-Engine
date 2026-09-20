/** MovieLens titles are formatted "Name (YYYY)" — parse without a backend field for it. */
export function parseMovieTitle(rawTitle: string): { name: string; year: string | null } {
  const match = rawTitle.match(/^(.*)\s\((\d{4})\)\s*$/);
  if (match) return { name: match[1], year: match[2] };
  return { name: rawTitle, year: null };
}

const NO_GENRES_SENTINEL = "(no genres listed)";

export function formatGenres(genres: string[], max = 3): string {
  const clean = genres.filter((g) => g !== NO_GENRES_SENTINEL);
  if (clean.length === 0) return "Genres unavailable";
  return clean.slice(0, max).join(" · ");
}

export function cn(...classes: Array<string | false | null | undefined>): string {
  return classes.filter(Boolean).join(" ");
}

export function formatScore(score: number): string {
  // Content-based scores are cosine similarity in [0,1]; hybrid/collaborative
  // scores can be normalized [0,1] or a 1-5 rating scale depending on path.
  // Treat anything <= 1 as a percentage match; otherwise show as a rating.
  if (score <= 1) return `${Math.round(score * 100)}% match`;
  return `${score.toFixed(1)} / 5 predicted`;
}
