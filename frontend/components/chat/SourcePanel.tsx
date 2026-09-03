import { sourceUrl } from "@/lib/utils/repository";
import type { Source } from "@/types/api";

type SourcePanelProps = { sources: Source[]; repositoryUrl: string };

export function SourcePanel({ sources, repositoryUrl }: SourcePanelProps) {
  if (sources.length === 0) return null;

  return (
    <section className="source-panel" aria-label="Retrieved sources">
      <h2>Sources</h2>
      <ul>
        {sources.map((source) => {
          const href = sourceUrl(repositoryUrl, source.file_path, source.commit_sha, source.start_line, source.end_line);
          const label = <><span>{source.file_path}</span><small>Lines {source.start_line}–{source.end_line}</small></>;
          return <li key={`${source.file_path}-${source.start_line}-${source.end_line}`}>
            {href ? <a href={href} target="_blank" rel="noreferrer">{label}</a> : label}
          </li>;
        })}
      </ul>
    </section>
  );
}
