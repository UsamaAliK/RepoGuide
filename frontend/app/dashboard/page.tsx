import { AuthGuard } from "@/components/auth/AuthGuard";
import { RepositoryInput } from "@/components/repository/RepositoryInput";

export default function DashboardPage() {
  return (
    <AuthGuard>
      <main className="app-main">
        <section className="dashboard-intro">
          <p className="eyebrow">Workspace</p>
          <h1>Your repositories</h1>
          <p>Connect a GitHub repository to begin asking source-grounded questions.</p>
        </section>
        <section className="empty-panel" aria-labelledby="repositories-heading">
          <h2 id="repositories-heading">Connect a repository</h2>
          <p>RepoGuide indexes the default branch and answers only from retrieved repository context.</p>
          <RepositoryInput />
        </section>
      </main>
    </AuthGuard>
  );
}
