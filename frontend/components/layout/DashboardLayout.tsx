import Link from "next/link";
import type { ReactNode } from "react";

type DashboardLayoutProps = { children: ReactNode };

export function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <Link className="brand" href="/">RepoGuide</Link>
        <nav aria-label="Primary navigation">
          <Link className="nav-link nav-link-active" href="/dashboard">Repositories</Link>
        </nav>
        <p className="sidebar-note">Grounded answers for the code you ship.</p>
      </aside>
      <main className="app-main">{children}</main>
    </div>
  );
}
