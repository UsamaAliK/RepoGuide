import Link from "next/link";

export default function HomePage() {
  return (
    <main className="landing-shell">
      <header className="landing-header">
        <Link className="brand" href="/">RepoGuide</Link>
        <Link className="text-link" href="/dashboard">Open workspace</Link>
      </header>
      <section className="landing-content">
        <p className="eyebrow">Repository-aware coding tutor</p>
        <h1>Understand a codebase from the code itself.</h1>
        <p className="landing-copy">Ask focused questions about a GitHub repository and follow the answer back to the exact source files and lines.</p>
        <Link className="button" href="/dashboard">Open dashboard</Link>
      </section>
    </main>
  );
}
