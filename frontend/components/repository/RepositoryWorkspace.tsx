"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ChatWindow, type ChatMessage } from "@/components/chat/ChatWindow";
import { ChatInput } from "@/components/chat/ChatInput";
import { ApiError } from "@/lib/api/client";
import { askRepository } from "@/lib/api/chat";
import { getMessages } from "@/lib/api/conversations";

type RepositoryWorkspaceProps = { repositoryName: string; repositoryUrl: string; initialConversationId?: number };

export function RepositoryWorkspace({ repositoryName, repositoryUrl, initialConversationId }: RepositoryWorkspaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(repositoryUrl ? null : "This workspace is missing a repository URL. Return to the dashboard and index the repository again.");
  const [isAsking, setIsAsking] = useState(false);

  useEffect(() => {
    if (!initialConversationId || initialConversationId === conversationId) return;
    let cancelled = false;
    (async () => {
      setError(null);
      try {
        const history = await getMessages(initialConversationId);
        if (!cancelled) {
          setMessages(history.map((m) => ({ id: String(m.id), role: m.role as ChatMessage["role"], content: m.content, sources: m.sources })));
          setConversationId(initialConversationId);
        }
      } catch (caughtError) {
        if (!cancelled) setError(caughtError instanceof ApiError ? caughtError.message : "Conversation could not be loaded.");
      }
    })();
    return () => { cancelled = true; };
  }, [initialConversationId, conversationId]);

  async function handleQuestion(question: string) {
    if (!repositoryUrl) return;
    const questionMessage: ChatMessage = { id: crypto.randomUUID(), role: "user", content: question };
    setMessages((current) => [...current, questionMessage]);
    setError(null);
    setIsAsking(true);

    try {
      const response = await askRepository(repositoryUrl, question, conversationId ?? 0);
      setMessages((current) => [...current, { id: crypto.randomUUID(), role: "assistant", content: response.answer, sources: response.sources }]);
      setConversationId(response.conversation_id);
      window.dispatchEvent(new CustomEvent("repochat:conversation", { detail: { id: response.conversation_id } }));
    } catch (caughtError) {
      setError(caughtError instanceof ApiError ? caughtError.message : "The question could not be answered. Please try again.");
    } finally {
      setIsAsking(false);
    }
  }

  return (
    <div className="workspace-shell">
      <header className="workspace-header">
        <Link className="brand" href="/dashboard">RepoGuide</Link>
        <span className="repository-name">{repositoryName}</span>
        <Link className="text-link" href="/dashboard">Change repository</Link>
      </header>
      <main className="workspace-main">
        <section className="chat-panel" aria-label={`Chat about ${repositoryName}`}>
          <ChatWindow messages={messages} isLoading={isAsking} repositoryUrl={repositoryUrl} />
          {error && <p className="form-error chat-error" role="alert">{error}</p>}
          <ChatInput disabled={isAsking || !repositoryUrl} onSubmit={handleQuestion} />
        </section>
      </main>
    </div>
  );
}