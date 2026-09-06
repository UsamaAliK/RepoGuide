import { RegisterForm } from "@/components/auth/RegisterForm";

export default function RegisterPage() {
  return (
    <main className="auth-page">
      <section className="auth-panel">
        <p className="eyebrow">RepoGuide</p>
        <h1>Create account</h1>
        <RegisterForm />
      </section>
    </main>
  );
}