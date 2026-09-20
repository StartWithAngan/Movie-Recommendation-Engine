import { apiRequest } from "./client";
import type { Rating } from "../types";

export const ratingsApi = {
  /**
   * POST /api/ratings upserts — calling it again for the same movie changes
   * the existing rating. There is no DELETE /api/ratings/{id} on the
   * backend, so removing a rating isn't offered in the UI (see
   * docs/frontend_notes — we adapt to the API rather than inventing one).
   */
  rate: (movieId: number, rating: number) =>
    apiRequest<{ status: string }>("/api/ratings", { method: "POST", body: { movie_id: movieId, rating } }),

  list: () => apiRequest<Rating[]>("/api/ratings"),
};
