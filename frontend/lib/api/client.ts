const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

import { getToken, getRefreshToken, storeSession, clearSession, getUsername } from "@/lib/auth/token";

type ApiErrorBody = { detail?: string };
type RefreshResponse = { access_token: string; refresh_token: string };

export class ApiError extends Error {
  constructor(message: string, public readonly status: number) {
    super(message);
    this.name = "ApiError";
  }
}

let refreshPromise: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return null;

  try {
    const response = await fetch(`${apiBaseUrl}/api/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken })
    });
    if (!response.ok) return null;
    const data = (await response.json()) as RefreshResponse;
    storeSession(data.access_token, data.refresh_token, getUsername() ?? "");
    return data.access_token;
  } catch {
    return null;
  }
}

function refreshOnce(): Promise<string | null> {
  if (!refreshPromise) {
    refreshPromise = refreshAccessToken().finally(() => {
      refreshPromise = null;
    });
  }
  return refreshPromise;
}

export async function apiRequest<T>(path: string, init: RequestInit): Promise<T> {
  const token = getToken();

  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...init.headers
      }
    });
  } catch {
    throw new ApiError("Could not reach the RepoGuide API. Confirm the FastAPI server is running.", 0);
  }

  let attempt = 0;
  while (response.status === 401 && token && attempt < 1) {
    const newToken = await refreshOnce();
    if (!newToken) {
      clearSession();
      break;
    }
    try {
      response = await fetch(`${apiBaseUrl}${path}`, {
        ...init,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${newToken}`,
          ...init.headers
        }
      });
    } catch {
      throw new ApiError("Could not reach the RepoGuide API. Confirm the FastAPI server is running.", 0);
    }
    attempt += 1;
  }

  if (!response.ok) {
    const body = (await response.json().catch(() => ({}))) as ApiErrorBody;
    throw new ApiError(body.detail ?? `The API returned ${response.status}.`, response.status);
  }

  return response.json() as Promise<T>;
}