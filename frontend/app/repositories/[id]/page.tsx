import { RepositoryWorkspace } from "@/components/repository/RepositoryWorkspace";

type RepositoryPageProps = {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ url?: string }>;
};

export default async function RepositoryPage({ params, searchParams }: RepositoryPageProps) {
  const [{ id }, { url }] = await Promise.all([params, searchParams]);
  return <RepositoryWorkspace repositoryName={decodeURIComponent(id)} repositoryUrl={url ?? ""} />;
}
