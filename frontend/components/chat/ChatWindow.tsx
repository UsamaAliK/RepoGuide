"use client";

import { useState } from "react";
import { SourcePanel } from "@/components/chat/SourcePanel";
import { MessageContent } from "@/components/chat/MessageContent";
import { Logo } from "@/components/layout/Logo";
import type { Source } from "@/types/api";

export type ChatMessage = { id: string; role: "user" | "assistant"; content: string; sources?: Source[] };
type ChatWindowProps = { messages: ChatMessage[]; isLoading: boolean; repositoryUrl: string };

function CopyMessageButton({ content }: { content: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback
    }
  };

  return (
    <button
      type="button"
      className="message-copy-button"
      onClick={handleCopy}
      aria-label={copied ? "Message copied to clipboard" : "Copy message text"}
      title="Copy message"
    >
      <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true" focusable="false">
        {copied ? (
          <path d="M13.78 4.22a.75.75 0 010 1.06l-7.25 7.25a.75.75 0 01-1.06 0L2.22 9.28a.75.75 0 011.06-1.06L6 10.94l6.72-6.72a.75.75 0 011.06 0z" />
        ) : (
          <>
            <path d="M0 6.75C0 5.784.784 5 1.75 5h1.5a.75.75 0 010 1.5h-1.5a.25.25 0 00-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 00.25-.25v-1.5a.75.75 0 011.5 0v1.5A1.75 1.75 0 019.25 16h-7.5A1.75 1.75 0 010 14.25v-7.5z" />
            <path d="M5 1.75C5 .784 5.784 0 6.75 0h7.5C15.216 0 16 .784 16 1.75v7.5A1.75 1.75 0 0114.25 11h-7.5A1.75 1.75 0 015 9.25v-7.5zm1.75-.25a.25.25 0 00-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 00.25-.25v-7.5a.25.25 0 00-.25-.25h-7.5z" />
          </>
        )}
      </svg>
    </button>
  );
}

export function ChatWindow({ messages, isLoading, repositoryUrl }: ChatWindowProps) {
  if (messages.length === 0) {
    return (
      <div className="chat-empty">
        <div className="chat-empty-logo"><Logo size={28} /></div>
        <h1>Ask a question</h1>
        <p>Answers are generated from the indexed repository and include the retrieved source ranges.</p>
      </div>
    );
  }

  return (
    <div className="chat-messages" aria-live="polite">
      {messages.map((message) => (
        <article className={`message message-${message.role}`} key={message.id}>
          {message.role === "user" ? (
            <div className="message-bubble-wrapper">
              <div className="message-bubble"><MessageContent content={message.content} /></div>
              <CopyMessageButton content={message.content} />
            </div>
          ) : (
            <div className="message-assistant">
              <span className="message-avatar" aria-hidden="true"><Logo size={20} /></span>
              <div className="message-assistant-body">
                <div className="message-header">
                  <CopyMessageButton content={message.content} />
                </div>
                <MessageContent content={message.content} />
                {message.sources && <SourcePanel repositoryUrl={repositoryUrl} sources={message.sources} />}
              </div>
            </div>
          )}
        </article>
      ))}
      {isLoading && (
        <article className="message message-assistant">
          <div className="message-assistant">
            <span className="message-avatar" aria-hidden="true"><Logo size={20} /></span>
            <div className="message-assistant-body">
              <span className="loading-dots" aria-label="Preparing answer"><span /><span /><span /></span>
            </div>
          </div>
        </article>
      )}
    </div>
  );
}