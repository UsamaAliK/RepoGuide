export function getRepositoryName(url: string): string | null {
  try {
    const parsed = new URL(url);
    if (parsed.hostname !== "github.com") return null;
    const [owner, repository] = parsed.pathname.split("/").filter(Boolean);
    if (!owner || !repository) return null;
    return `${owner}/${repository.replace(/\.git$/, "")}`;
  } catch {
    return null;
  }
}

export function sourceUrl(repositoryUrl: string, filePath: string, commitSha: string, startLine: number, endLine: number): string | null {
  const repository = getRepositoryName(repositoryUrl);
  return repository ? `https://github.com/${repository}/blob/${commitSha}/${filePath}#L${startLine}-L${endLine}` : null;
}
