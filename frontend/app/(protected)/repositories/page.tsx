import { Suspense } from "react";
import Link from "next/link";

import RepositoriesContent from "./repositories-content";
import { ApiErrorCard } from "@/components/api-error-card";
import { RepositoriesLoading } from "@/components/repositories-loading";
import { Button } from "@/components/ui/button";
import { getRepositories } from "@/lib/api-server";

export const maxDuration = 60;

export default function RepositoriesPage() {
  return (
    <main className="w-full px-10 py-8 xl:px-12">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-4xl font-bold">Repositories</h1>
          <p className="mt-2 text-muted-foreground">Manage your connected GitHub repositories.</p>
        </div>
        <Button asChild><Link href="/repositories/connect">Connect Repository</Link></Button>
      </div>
      <Suspense fallback={<RepositoriesLoading />}>
        <RepositoriesData />
      </Suspense>
    </main>
  );
}

async function RepositoriesData() {
  let repositories: Awaited<ReturnType<typeof getRepositories>> | null = null;
  try {
    repositories = await getRepositories();
  } catch {
    repositories = null;
  }
  if (!repositories) return <ApiErrorCard title="Unable to load repositories" description="The backend may be starting up. Please try again." />;
  return <RepositoriesContent repositories={repositories} />;
}
