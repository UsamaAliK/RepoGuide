import { apiRequest } from "@/lib/api/client";
import type { ChatResponse } from "@/types/api";

export function askRepository(url: string, question: string, conversationId: number) {
  return apiRequest<ChatResponse>("/api/chat", {
    method: "POST",
    body: JSON.stringify({ url, question, conversation_id: conversationId })
  });
}