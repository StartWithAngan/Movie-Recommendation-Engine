import { apiRequest } from "./client";
import type { TokenResponse, User } from "../types";

export const authApi = {
  register: (email: string, password: string, display_name: string) =>
    apiRequest<TokenResponse>("/api/auth/register", {
      method: "POST",
      body: { email, password, display_name },
      skipAuth: true,
    }),

  login: (email: string, password: string) =>
    apiRequest<TokenResponse>("/api/auth/login", {
      method: "POST",
      body: { email, password },
      skipAuth: true,
    }),

  me: () => apiRequest<User>("/api/auth/me"),
};
