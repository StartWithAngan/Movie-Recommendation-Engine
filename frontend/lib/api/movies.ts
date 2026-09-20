import { apiRequest, buildQuery } from "./client";
import type { Movie, MovieSearchResult } from "../types";

export const moviesApi = {
  list: (page = 1, pageSize = 20) =>
    apiRequest<MovieSearchResult>(`/api/movies${buildQuery({ page, page_size: pageSize })}`, { skipAuth: true }),

  search: (q: string, genre?: string, page = 1, pageSize = 20) =>
    apiRequest<MovieSearchResult>(
      `/api/movies/search${buildQuery({ q, genre, page, page_size: pageSize })}`,
      { skipAuth: true }
    ),

  get: (movieId: number) => apiRequest<Movie>(`/api/movies/${movieId}`, { skipAuth: true }),
};
