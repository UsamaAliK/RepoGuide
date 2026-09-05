import { apiRequest } from "@/lib/api/client";
import type { Conversation, Message } from "@/types/api";

export function getAllConversations() {
  return apiRequest<Conversation[]>("/api/conversations", { method: "GET" });
}

export function getConversations(repositoryId: number) {
  return apiRequest<Conversation[]>("/api/conversations/" + repositoryId, { method: "GET" });
}

export function getMessages(conversationId: number) {
  return apiRequest<Message[]>("/api/messages/" + conversationId, { method: "GET" });
}