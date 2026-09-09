const TOKEN_KEY = "repoguide_token";
const REFRESH_TOKEN_KEY = "repoguide_refresh_token";
const USERNAME_KEY = "repoguide_username";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function getUsername(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(USERNAME_KEY);
}

export function storeSession(token: string, refreshToken: string, username: string) {
  window.localStorage.setItem(TOKEN_KEY, token);
  window.localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  window.localStorage.setItem(USERNAME_KEY, username);
}

export function clearSession() {
  window.localStorage.removeItem(TOKEN_KEY);
  window.localStorage.removeItem(REFRESH_TOKEN_KEY);
  window.localStorage.removeItem(USERNAME_KEY);
}