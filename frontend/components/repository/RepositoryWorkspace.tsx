"use client";

import Link from "next/link";
import { useState } from "react";
import { ChatWindow, type ChatMessage } from "@/components/chat/ChatWindow";
import { ChatInput } from "@/components/chat/ChatInput";
import { ApiError } from "@/lib/api/client";
import { askRepository } from "@/lib/api/chat";

type RepositoryWorkspaceProps = { repositoryName: string; repositoryUrl: string };

export function RepositoryWorkspace({ repositoryName, repositoryUrl }: RepositoryWorkspaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [error, setError] = useState<string | null>(repositoryUrl ? null : "This workspace is missing a repository URL. Return to the dashboard and index the repository again.");
  const [isAsking, setIsAsking] = useState(false);

  async function handleQuestion(question: string) {
    if (!repositoryUrl) return;
    const questionMessage: ChatMessage = { id: crypto.randomUUID(), role: "user", content: question };
    setMessages((current) => [...current, questionMessage]);
    setError(null);
    setIsAsking(true);

    try {
      const response = await askRepository(repositoryUrl, question);
      setMessages((current) => [...current, { id: crypto.randomUUID(), role: "assistant", content: response.answer, sources: response.sources }]);
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
        <aside className="file-panel" aria-label="Repository files">
          <p className="panel-heading">Files</p>
          <p className="panel-message">File browsing requires a backend file-content endpoint.</p>
        </aside>
        <section className="chat-panel" aria-label={`Chat about ${repositoryName}`}>
          <ChatWindow messages={messages} isLoading={isAsking} repositoryUrl={repositoryUrl} />
          {error && <p className="form-error chat-error" role="alert">{error}</p>}
          <ChatInput disabled={isAsking || !repositoryUrl} onSubmit={handleQuestion} />
        </section>
      </main>
    </div>
  );
}
