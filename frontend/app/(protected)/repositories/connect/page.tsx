import { Suspense } from "react";

import { ApiErrorCard } from "@/components/api-error-card";
import { ProtectedPageLoading } from "@/components/protected-page-loading";
import { getAvailableGitHubRepositories } from "@/lib/api-server";
import ConnectRepositoriesContent from "./connect-repositories-content";

export default function ConnectRepositoryPage() {
  return (
    <main className="w-full px-10 py-8">
      <h1 className="text-3xl font-bold">Connect Repository</h1>
      <p className="mt-2 text-muted-foreground">
        Select a GitHub repository to connect to Kritique.
      </p>
      <Suspense fallback={<ProtectedPageLoading showHeading={false} />}>
        <AvailableRepositories />
      </Suspense>
    </main>
  );
}

async function AvailableRepositories() {
  let repositories: Awaited<ReturnType<typeof getAvailableGitHubRepositories>> | null = null;
  try {
    repositories = await getAvailableGitHubRepositories();
  } catch {
    repositories = null;
  }
  if (!repositories) return <div className="mt-8"><ApiErrorCard title="Unable to load GitHub repositories" /></div>;
  return <ConnectRepositoriesContent repositories={repositories} />;
}
