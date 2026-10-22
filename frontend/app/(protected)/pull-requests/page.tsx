import { Suspense } from "react";

import { SiteHeader } from "@/components/site-header";
import { DataTableLoader } from "@/components/data-table-loader";
import { ApiErrorCard } from "@/components/api-error-card";
import { ProtectedPageLoading } from "@/components/protected-page-loading";
import { getPullRequestSummary } from "@/lib/api-server";
import type { PullRequestListItem } from "@/types";

export const maxDuration = 60;

export default function PullRequestsPage() {
  return (
    <>
      <SiteHeader />

      <main className="flex flex-1 flex-col">
        <div className="space-y-8 p-6">

          <div>
            <h1 className="text-3xl font-bold">
              Pull Requests
            </h1>

            <p className="text-muted-foreground mt-2">
              Browse all pull requests reviewed by Kritique.ai.
            </p>
          </div>

          <Suspense fallback={<ProtectedPageLoading showHeading={false} />}>
            <PullRequestsData />
          </Suspense>

        </div>
      </main>
    </>
  );
}

async function PullRequestsData() {
  let listItems: PullRequestListItem[] | null = null;
  try {
    const result = await getPullRequestSummary(500);
    listItems = result.items;
  } catch {
    listItems = null;
  }
  if (!listItems) return <ApiErrorCard title="Unable to load pull requests" description="Please try again." />;
  return <DataTableLoader pullRequests={listItems} />;
}
