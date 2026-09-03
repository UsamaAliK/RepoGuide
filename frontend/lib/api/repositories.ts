import { apiRequest } from "@/lib/api/client";
import type { IndexRepositoryResponse } from "@/types/api";

export function indexRepository(url: string) {
  return apiRequest<IndexRepositoryResponse>("/index", {
    method: "POST",
    body: JSON.stringify({ url })
  });
}
