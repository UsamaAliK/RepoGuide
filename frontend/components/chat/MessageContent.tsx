import type { ReactNode } from "react";

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

function renderParagraphs(text: string) {
  return text.split(/\n{2,}/).map((block, index) => {
    const lines = block.split("\n");
    if (isListBlock(lines)) {
      return <div key={index}>{renderList(buildListTree(lines))}</div>;
    }
    return <p key={index}>{renderInline(block)}</p>;
  });
}

export function MessageContent({ content }: { content: string }) {
  const blocks = content.split(/```/);
  return (
    <div className="message-content">
      {blocks.map((block, index) => {
        if (index % 2 === 1) {
          const firstNewline = block.indexOf("\n");
          const code = firstNewline === -1 ? block : block.slice(firstNewline + 1);
          return <pre key={index}><code>{code}</code></pre>;
        }
        if (block.trim()) {
          return <div key={index}>{renderParagraphs(block)}</div>;
        }
        return null;
      })}
    </div>
  );
}