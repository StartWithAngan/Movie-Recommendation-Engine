/**
 * These types mirror backend/app/schemas/schemas.py exactly. If the backend
 * schema changes, update here — never add fields the API doesn't return.
 */

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: string;
  email: string;
  display_name: string;
}

export interface Movie {
  movie_id: number;
  title: string;
  genres: string[];
}

export interface MovieSearchResult {
  results: Movie[];
  total: number;
}

export interface Rating {
  movie_id: number;
  rating: number;
  title?: string | null;
}

export interface Recommendation {
  movie_id: number;
  title: string;
  score: number;
  reason: string;
}

export interface RecommendationResponse {
  recommendations: Recommendation[];
  is_cold_start: boolean;
}

export interface WatchlistItem {
  movie_id: number;
  title: string;
}

export interface ProfileStats {
  ratings_count: number;
  avg_rating_given: number;
  favorite_genres: string[];
  top_rated_movies: Rating[];
}

/**
 * The backend's /api/analytics has no Pydantic response_model (see
 * backend/app/api/profile.py), so its shape is looser than the rest of the
 * API. One real quirk to work around on the frontend rather than in the
 * backend: favorite_genres is a bare `[]` when the user has no ratings yet,
 * but a `{genre: count}` object once they do. Treat it as possibly either.
 */
export interface Analytics {
  ratings_count: number;
  rating_distribution: Record<string, number>;
  favorite_genres: Record<string, number> | [];
  avg_rating_given?: number;
}

export interface HealthStatus {
  status: string;
  environment: string;
  database: string;
  ml_artifacts_loaded: boolean;
}
