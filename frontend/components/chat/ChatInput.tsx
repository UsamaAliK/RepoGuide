"use client";

import { FormEvent, KeyboardEvent, useEffect, useRef, useState } from "react";

type ChatInputProps = { disabled: boolean; onSubmit: (question: string) => Promise<void> };

export function ChatInput({ disabled, onSubmit }: ChatInputProps) {
  const [question, setQuestion] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const element = textareaRef.current;
    if (!element) return;
    element.style.height = "auto";
    element.style.height = `${Math.min(element.scrollHeight, 200)}px`;
  }, [question]);

  function send() {
    const trimmedQuestion = question.trim();
    if (!trimmedQuestion || disabled) return;
    setQuestion("");
    onSubmit(trimmedQuestion);
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    send();
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      send();
    }
  }

  return (
    <form className="chat-input" onSubmit={handleSubmit}>
      <label className="sr-only" htmlFor="question">Ask about this repository</label>
      <textarea
        id="question"
        ref={textareaRef}
        value={question}
        onChange={(event) => setQuestion(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask about this repository…"
        rows={1}
        disabled={disabled}
      />
      <button className="send-button" type="submit" disabled={disabled || !question.trim()} aria-label="Send question">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false">
          <path d="M12 19V5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
          <path d="M5 12l7-7 7 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>
    </form>
  );
}