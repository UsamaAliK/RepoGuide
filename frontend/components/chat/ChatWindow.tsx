import { SourcePanel } from "@/components/chat/SourcePanel";
import { MessageContent } from "@/components/chat/MessageContent";
import { Logo } from "@/components/layout/Logo";
import type { Source } from "@/types/api";

export type ChatMessage = { id: string; role: "user" | "assistant"; content: string; sources?: Source[] };
type ChatWindowProps = { messages: ChatMessage[]; isLoading: boolean; repositoryUrl: string };

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
            <div className="message-bubble"><MessageContent content={message.content} /></div>
          ) : (
            <div className="message-assistant">
              <span className="message-avatar" aria-hidden="true"><Logo size={20} /></span>
              <div className="message-assistant-body">
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