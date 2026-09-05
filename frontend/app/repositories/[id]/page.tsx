import { RepositoryWorkspace } from "@/components/repository/RepositoryWorkspace";

type RepositoryPageProps = {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ url?: string; conversationId?: string }>;
};

export default async function RepositoryPage({ params, searchParams }: RepositoryPageProps) {
  const [{ id }, { url, conversationId }] = await Promise.all([params, searchParams]);
  const initialConversationId = conversationId ? Number(conversationId) : undefined;
  return <RepositoryWorkspace repositoryName={decodeURIComponent(id)} repositoryUrl={url ?? ""} initialConversationId={initialConversationId} />;
}