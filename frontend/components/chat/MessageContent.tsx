"use client";

import { useState, type ReactNode } from "react";

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback
    }
  };

  return (
    <button
      type="button"
      className="code-copy-button"
      onClick={handleCopy}
      aria-label={copied ? "Copied to clipboard" : "Copy code"}
    >
      <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true" focusable="false">
        {copied ? (
          <path d="M13.78 4.22a.75.75 0 010 1.06l-7.25 7.25a.75.75 0 01-1.06 0L2.22 9.28a.75.75 0 011.06-1.06L6 10.94l6.72-6.72a.75.75 0 011.06 0z" />
        ) : (
          <>
            <path d="M0 6.75C0 5.784.784 5 1.75 5h1.5a.75.75 0 010 1.5h-1.5a.25.25 0 00-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 00.25-.25v-1.5a.75.75 0 011.5 0v1.5A1.75 1.75 0 019.25 16h-7.5A1.75 1.75 0 010 14.25v-7.5z" />
            <path d="M5 1.75C5 .784 5.784 0 6.75 0h7.5C15.216 0 16 .784 16 1.75v7.5A1.75 1.75 0 0114.25 11h-7.5A1.75 1.75 0 015 9.25v-7.5zm1.75-.25a.25.25 0 00-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 00.25-.25v-7.5a.25.25 0 00-.25-.25h-7.5z" />
          </>
        )}
      </svg>
      <span>{copied ? "Copied" : "Copy"}</span>
    </button>
  );
}

function renderInline(text: string): ReactNode[] {
  return text.split(/(`[^`]+`|\*\*[^*]+\*\*)/g).map((part, index) => {
    if (part.startsWith("`") && part.endsWith("`")) {
      return <code key={index}>{part.slice(1, -1)}</code>;
    }
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={index}>{part.slice(2, -2)}</strong>;
    }
    return part;
  });
}

type ListNode = { level: number; ordered: boolean; content: string; children: ListNode[] };

const LIST_LINE = /^(\s*)([*+-]|\d+\.)\s+(.*)$/;

function isListBlock(lines: string[]): boolean {
  return lines.some((line) => line.trim()) && lines.filter((line) => line.trim()).every((line) => LIST_LINE.test(line));
}

function buildListTree(lines: string[]): ListNode[] {
  const root: ListNode = { level: -1, ordered: false, content: "", children: [] };
  const stack = [root];
  for (const raw of lines) {
    if (raw.trim() === "") continue;
    const match = raw.match(LIST_LINE);
    if (!match) continue;
    const level = match[1].replace(/^\t/, "  ").length;
    const node: ListNode = { level, ordered: /^\d+\./.test(match[2]), content: match[3], children: [] };
    while (stack.length > 1 && stack[stack.length - 1].level >= level) stack.pop();
    stack[stack.length - 1].children.push(node);
    stack.push(node);
  }
  return root.children;
}

function renderList(nodes: ListNode[]): ReactNode {
  const ordered = nodes.some((node) => node.ordered);
  const ListTag = ordered ? "ol" : "ul";
  return (
    <ListTag>
      {nodes.map((node, index) => (
        <li key={index}>
          <span>{renderInline(node.content)}</span>
          {node.children.length > 0 && renderList(node.children)}
        </li>
      ))}
    </ListTag>
  );
}

const HEADING_LINE = /^(#{1,6})\s+(.*)$/;

function renderBlock(block: string, index: number): ReactNode {
  const lines = block.split("\n");
  if (isListBlock(lines)) {
    return <div key={index}>{renderList(buildListTree(lines))}</div>;
  }
  const heading = block.match(HEADING_LINE);
  if (heading) {
    const Tag = `h${heading[1].length}` as "h1" | "h2" | "h3" | "h4" | "h5" | "h6";
    return <Tag key={index}>{renderInline(heading[2])}</Tag>;
  }
  return <p key={index}>{renderInline(block)}</p>;
}

function renderParagraphs(text: string) {
  return text.split(/\n{2,}/).map((block, index) => renderBlock(block, index));
}

export function MessageContent({ content }: { content: string }) {
  const blocks = content.split(/```/);
  return (
    <div className="message-content">
      {blocks.map((block, index) => {
        if (index % 2 === 1) {
          const firstNewline = block.indexOf("\n");
          const lang = firstNewline === -1 ? "" : block.slice(0, firstNewline).trim();
          const code = firstNewline === -1 ? block : block.slice(firstNewline + 1);
          return (
            <div key={index} className="code-block-wrapper">
              <div className="code-block-header">
                {lang && <span className="code-block-lang">{lang}</span>}
                <CopyButton text={code} />
              </div>
              <pre><code>{code}</code></pre>
            </div>
          );
        }
        if (block.trim()) {
          return <div key={index}>{renderParagraphs(block)}</div>;
        }
        return null;
      })}
    </div>
  );
}