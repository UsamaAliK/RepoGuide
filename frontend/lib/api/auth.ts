import { apiRequest } from "@/lib/api/client";
import type { TokenResponse } from "@/types/api";

export function login(username: string, password: string) {
  return apiRequest<TokenResponse>("/api/login", {
    method: "POST",
    body: JSON.stringify({ username, password })
  });
}

export function register(username: string, password: string) {
  return apiRequest<TokenResponse>("/api/register", {
    method: "POST",
    body: JSON.stringify({ username, password })
  });
}