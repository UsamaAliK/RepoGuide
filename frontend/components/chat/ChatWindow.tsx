import { SourcePanel } from "@/components/chat/SourcePanel";
import type { Source } from "@/types/api";

export type ChatMessage = { id: string; role: "user" | "assistant"; content: string; sources?: Source[] };
type ChatWindowProps = { messages: ChatMessage[]; isLoading: boolean; repositoryUrl: string };

export function ChatWindow({ messages, isLoading, repositoryUrl }: ChatWindowProps) {
  if (messages.length === 0) {
    return <div className="chat-empty"><h1>Ask a question</h1><p>Answers are generated from the indexed repository and include the retrieved source ranges.</p></div>;
  }

  return (
    <div className="chat-messages" aria-live="polite">
      {messages.map((message) => (
        <article className={`message message-${message.role}`} key={message.id}>
          <p className="message-role">{message.role === "user" ? "You" : "RepoGuide"}</p>
          <div className="message-content">{message.content.split("\n").map((line, index) => <p key={index}>{line || "\u00a0"}</p>)}</div>
          {message.sources && <SourcePanel repositoryUrl={repositoryUrl} sources={message.sources} />}
        </article>
      ))}
      {isLoading && <p className="loading-message">Searching the repository and preparing an answer…</p>}
    </div>
  );
}
