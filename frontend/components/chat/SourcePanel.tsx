"use client";

import { useState } from "react";
import { sourceUrl } from "@/lib/utils/repository";
import type { Source } from "@/types/api";

type SourcePanelProps = { sources: Source[]; repositoryUrl: string };

export function SourcePanel({ sources, repositoryUrl }: SourcePanelProps) {
  const [open, setOpen] = useState(false);
  if (sources.length === 0) return null;

  return (
    <section className="source-panel" aria-label="Retrieved sources">
      <button
        type="button"
        className="source-toggle"
        aria-expanded={open}
        onClick={() => setOpen((current) => !current)}
      >
        <svg className="source-caret" width="10" height="10" viewBox="0 0 16 16" aria-hidden="true">
          {open ? (
            <path d="M4.427 9.427l3.396 3.396a.25.25 0 00.354 0l3.396-3.396A.25.25 0 0011.793 9H4.207a.25.25 0 00-.78.427z" fill="currentColor" />
          ) : (
            <path d="M6.427 4.427l3.396 3.396a.25.25 0 010 .354L6.427 11.573A.25.25 0 016 11.293V4.707a.25.25 0 01.427-.28z" fill="currentColor" />
          )}
        </svg>
        {sources.length} {sources.length === 1 ? "source" : "sources"}
      </button>
      {open && (
        <ul>
          {sources.map((source) => {
            const href = sourceUrl(repositoryUrl, source.file_path, source.commit_sha, source.start_line, source.end_line);
            const label = <><span>{source.file_path}</span><small>Lines {source.start_line}–{source.end_line}</small></>;
            return <li key={`${source.file_path}-${source.start_line}-${source.end_line}`}>
              {href ? <a href={href} target="_blank" rel="noreferrer">{label}</a> : label}
            </li>;
          })}
        </ul>
      )}
    </section>
  );
}