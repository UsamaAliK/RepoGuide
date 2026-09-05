import { apiRequest } from "@/lib/api/client";
import type { IndexRepositoryResponse, RepositoryInfo } from "@/types/api";

export function indexRepository(url: string) {
  return apiRequest<IndexRepositoryResponse>("/index", {
    method: "POST",
    body: JSON.stringify({ url })
  });
}

export function getRepositories() {
  return apiRequest<RepositoryInfo[]>("/api/repositories", { method: "GET" });
}

export function getRepositoryById(id: number) {
  return apiRequest<RepositoryInfo>(`/api/repositories/${id}`, { method: "GET" });
}
