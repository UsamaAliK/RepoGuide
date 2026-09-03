import { DashboardLayout } from "@/components/layout/DashboardLayout";

export default function DashboardPage() {
  return (
    <DashboardLayout>
      <section className="dashboard-intro">
        <p className="eyebrow">Workspace</p>
        <h1>Your repositories</h1>
        <p>Connect a GitHub repository to begin asking source-grounded questions.</p>
      </section>
      <section className="empty-panel" aria-labelledby="repositories-heading">
        <h2 id="repositories-heading">No repositories yet</h2>
        <p>Repository indexing will be connected in the next increment.</p>
      </section>
    </DashboardLayout>
  );
}
