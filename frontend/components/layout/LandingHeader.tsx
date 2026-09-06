"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth/AuthContext";

export function LandingHeader() {
  const { isAuthenticated, isLoading, username, logout } = useAuth();

  return (
    <header className="landing-header">
      <Link className="brand" href="/">RepoGuide</Link>
      {isLoading ? null : isAuthenticated ? (
        <div className="landing-header-actions">
          <Link className="text-link" href="/dashboard">Open workspace</Link>
          <span className="auth-username">{username}</span>
          <button className="button-as-link" type="button" onClick={logout}>Log out</button>
        </div>
      ) : (
        <div className="landing-header-actions">
          <Link className="text-link" href="/login">Log in</Link>
          <Link className="button" href="/register">Sign up</Link>
        </div>
      )}
    </header>
  );
}