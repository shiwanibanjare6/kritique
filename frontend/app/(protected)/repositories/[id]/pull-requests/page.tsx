import { Suspense } from "react";
import { notFound } from "next/navigation";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

import RepositoryDetailsContent from "./repository-pull-requests-content";
import { ApiErrorCard } from "@/components/api-error-card";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { ApiServerError, getRepositoryDetails } from "@/lib/api-server";

export default function RepositoryPullRequestsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  return (
    <main className="flex-1 w-full space-y-8 px-10 py-8">
      <div className="mb-8 flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-muted-foreground">Repository Details</p>
          <h1 className="text-4xl font-bold">Repository overview</h1>
          <p className="mt-2 text-muted-foreground">Review repository performance and view the latest pull requests.</p>
        </div>
        <Button variant="outline" asChild>
          <Link href="/repositories"><ArrowLeft className="mr-2 h-4 w-4" />Back to repositories</Link>
        </Button>
      </div>
      <Suspense fallback={<RepositoryDetailsSkeleton />}>
        <RepositoryData params={params} />
      </Suspense>
    </main>
  );
}

async function RepositoryData({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  let repository: Awaited<ReturnType<typeof getRepositoryDetails>> | null = null;
  let failure: unknown = null;
  try {
    repository = await getRepositoryDetails(id);
  } catch (error) {
    failure = error;
  }
  if (failure instanceof ApiServerError && failure.status === 404) notFound();
  if (failure || !repository) return <ApiErrorCard title="Unable to load repository" description="The backend may be starting up. Please try again." />;
  return <RepositoryDetailsContent repository={repository} />;
}

function RepositoryDetailsSkeleton() {
  return (
    <div className="space-y-6" aria-busy="true">
      <Skeleton className="h-80 rounded-3xl" />
      <div className="grid gap-6 md:grid-cols-3">
        <Skeleton className="h-36 rounded-3xl" />
        <Skeleton className="h-36 rounded-3xl" />
        <Skeleton className="h-36 rounded-3xl" />
      </div>
    </div>
  );
}
