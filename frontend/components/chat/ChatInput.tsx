"use client";

import { FormEvent, useState } from "react";

type ChatInputProps = { disabled: boolean; onSubmit: (question: string) => Promise<void> };

export function ChatInput({ disabled, onSubmit }: ChatInputProps) {
  const [question, setQuestion] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmedQuestion = question.trim();
    if (!trimmedQuestion || disabled) return;
    setQuestion("");
    await onSubmit(trimmedQuestion);
  }

  return (
    <form className="chat-input" onSubmit={handleSubmit}>
      <label className="sr-only" htmlFor="question">Ask about this repository</label>
      <textarea id="question" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Ask about this repository…" rows={3} disabled={disabled} />
      <button className="button" type="submit" disabled={disabled || !question.trim()}>Ask</button>
    </form>
  );
}
