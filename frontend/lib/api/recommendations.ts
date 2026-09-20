import { apiRequest, buildQuery } from "./client";
import type { Recommendation, RecommendationResponse } from "../types";

export const recommendationsApi = {
  get: (topK = 12) => apiRequest<RecommendationResponse>(`/api/recommendations${buildQuery({ top_k: topK })}`),

  similar: (movieId: number, topK = 12) =>
    apiRequest<Recommendation[]>(`/api/recommendations/similar/${movieId}${buildQuery({ top_k: topK })}`, {
      skipAuth: true,
    }),
};
