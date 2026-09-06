import { LoginForm } from "@/components/auth/LoginForm";

export default function LoginPage() {
  return (
    <main className="auth-page">
      <section className="auth-panel">
        <p className="eyebrow">RepoGuide</p>
        <h1>Log in</h1>
        <LoginForm />
      </section>
    </main>
  );
}