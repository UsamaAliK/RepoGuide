import { apiRequest } from "@/lib/api/client";
import type { AskResponse } from "@/types/api";

export function askRepository(url: string, question: string) {
  return apiRequest<AskResponse>("/ask", {
    method: "POST",
    body: JSON.stringify({ url, question })
  });
}
