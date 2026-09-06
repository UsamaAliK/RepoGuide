"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { ApiError } from "@/lib/api/client";
import { getAllConversations } from "@/lib/api/conversations";
import { getRepositories } from "@/lib/api/repositories";
import { useAuth } from "@/lib/auth/AuthContext";
import type { Conversation, RepositoryInfo } from "@/types/api";

export function ConversationSidebar() {
  const { isAuthenticated, username, logout } = useAuth();
  const pathname = usePathname();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [repositories, setRepositories] = useState<RepositoryInfo[]>([]);
  const [activeId, setActiveId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (pathname === "/") return;

    let cancelled = false;
    async function refresh() {
      try {
        const [history, repos] = await Promise.all([getAllConversations(), getRepositories()]);
        if (!cancelled) {
          setConversations(history);
          setRepositories(repos);
          setError(null);
        }
      } catch (caughtError) {
        if (!cancelled) setError(caughtError instanceof ApiError ? caughtError.message : "Conversations could not be loaded.");
      }
    }

    refresh();
    const syncActive = () => {
      const id = new URLSearchParams(window.location.search).get("conversationId");
      setActiveId(id ? Number(id) : null);
    };
    const onConversationUpdated = (event: Event) => {
      const id = (event as CustomEvent<{ id: number }>).detail.id;
      setActiveId(id);
      refresh();
    };

    syncActive();
    window.addEventListener("popstate", syncActive);
    window.addEventListener("repochat:conversation", onConversationUpdated);
    return () => {
      cancelled = true;
      window.removeEventListener("popstate", syncActive);
      window.removeEventListener("repochat:conversation", onConversationUpdated);
    };
  }, [pathname]);

  if (pathname === "/") return null;

  return (
    <aside className="sidebar" aria-label="Conversations">
      <Link className="brand" href="/dashboard">RepoGuide</Link>
      <nav aria-label="Primary navigation">
        <Link className="nav-link nav-link-active" href="/dashboard">Repositories</Link>
      </nav>
      <div className="conversation-section">
        <p className="panel-heading">Chats</p>
        {error ? (
          <p className="panel-message">{error}</p>
        ) : conversations.length === 0 ? (
          <p className="panel-message">No conversations yet.</p>
        ) : (
          <ul className="conversation-list">
            {conversations.map((conversation) => {
              const repository = repositories.find((r) => r.id === conversation.repository_id);
              const repoName = repository ? `${repository.owner}/${repository.repo_name}` : "repository";
              const path = repository
                ? `/repositories/${encodeURIComponent(repoName)}?url=${encodeURIComponent(repository.github_url)}&conversationId=${conversation.id}`
                : "/dashboard";
              return (
                <li key={conversation.id}>
                  <Link
                    className={`conversation-item${conversation.id === activeId ? " conversation-item-active" : ""}`}
                    href={path}
                    onClick={() => setActiveId(conversation.id)}
                  >
                    <span className="conversation-title">{conversation.title}</span>
                    <small className="conversation-repo">{repoName}</small>
                  </Link>
                </li>
              );
            })}
          </ul>
        )}
      </div>
      {isAuthenticated && (
        <div className="sidebar-user">
          <span>{username}</span>
          <button className="button-as-link" type="button" onClick={logout}>Log out</button>
        </div>
      )}
    </aside>
  );
}