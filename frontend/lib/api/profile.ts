import { apiRequest } from "./client";
import type { Analytics, ProfileStats } from "../types";

export const profileApi = {
  getStats: () => apiRequest<ProfileStats>("/api/profile"),
  getAnalytics: () => apiRequest<Analytics>("/api/analytics"),
};
