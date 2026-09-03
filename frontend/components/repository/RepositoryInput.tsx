"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { ApiError } from "@/lib/api/client";
import { indexRepository } from "@/lib/api/repositories";
import { getRepositoryName } from "@/lib/utils/repository";

export function RepositoryInput() {
  const router = useRouter();
  const [url, setUrl] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isIndexing, setIsIndexing] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const repositoryName = getRepositoryName(url.trim());

    if (!repositoryName) {
      setError("Enter a GitHub repository URL, for example https://github.com/owner/repository.");
      return;
    }

    setError(null);
    setIsIndexing(true);

    try {
      await indexRepository(url.trim());
      router.push(`/repositories/${encodeURIComponent(repositoryName)}?url=${encodeURIComponent(url.trim())}`);
    } catch (caughtError) {
      setError(caughtError instanceof ApiError ? caughtError.message : "Repository indexing failed. Please try again.");
    } finally {
      setIsIndexing(false);
    }
  }

  return (
    <form className="repository-form" onSubmit={handleSubmit} noValidate>
      <label htmlFor="repository-url">GitHub repository URL</label>
      <div className="form-row">
        <input id="repository-url" name="url" type="url" placeholder="https://github.com/owner/repository" value={url} onChange={(event) => setUrl(event.target.value)} disabled={isIndexing} required />
        <button className="button" type="submit" disabled={isIndexing}>{isIndexing ? "Indexing…" : "Index repository"}</button>
      </div>
      {error && <p className="form-error" role="alert">{error}</p>}
    </form>
  );
}
