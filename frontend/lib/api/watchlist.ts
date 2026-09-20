import { apiRequest } from "./client";
import type { WatchlistItem } from "../types";

export const watchlistApi = {
  add: (movieId: number) => apiRequest<{ status: string }>("/api/watchlist", { method: "POST", body: { movie_id: movieId } }),

  list: () => apiRequest<WatchlistItem[]>("/api/watchlist"),

  remove: (movieId: number) => apiRequest<void>(`/api/watchlist/${movieId}`, { method: "DELETE" }),
};
