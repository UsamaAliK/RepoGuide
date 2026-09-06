const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

import { getToken, clearSession } from "@/lib/auth/token";

type ApiErrorBody = { detail?: string };

export class ApiError extends Error {
  constructor(message: string, public readonly status: number) {
    super(message);
    this.name = "ApiError";
  }
}

export async function apiRequest<T>(path: string, init: RequestInit): Promise<T> {
  let response: Response;
  const token = getToken();

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

  if (response.status === 401) {
    clearSession();
  }

  if (!response.ok) {
    const body = (await response.json().catch(() => ({}))) as ApiErrorBody;
    throw new ApiError(body.detail ?? `The API returned ${response.status}.`, response.status);
  }

  return response.json() as Promise<T>;
}
