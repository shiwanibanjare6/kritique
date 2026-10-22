import { Suspense } from "react";

import AnalyticsContent from "./analytics-content";
import { SiteHeader } from "@/components/site-header";
import { ProtectedPageLoading } from "@/components/protected-page-loading";
import { ApiErrorCard } from "@/components/api-error-card";
import { getPullRequests, getRepositories } from "@/lib/api-server";
import type { AnalyticsPullRequest } from "@/types";

export default function AnalyticsPage() {
  return (
    <>
      <SiteHeader />
      <section className="px-4 py-6 lg:px-6">
        <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
        <p className="mt-2 max-w-2xl text-muted-foreground">
          Visualize repository scoring performance and review quality across your pull requests.
        </p>
      </section>
      <Suspense fallback={<ProtectedPageLoading showHeading={false} />}>
        <AnalyticsData />
      </Suspense>
    </>
  );
}

async function AnalyticsData() {
  let data: { repositories: Awaited<ReturnType<typeof getRepositories>>; pullRequests: AnalyticsPullRequest[] } | null = null;
  try {
    const [repositories, pullRequests] = await Promise.all([
      getRepositories(),
      getPullRequests(),
    ]);
    const analyticsPullRequests: AnalyticsPullRequest[] = pullRequests.map((pr) => ({
      id: pr.id,
      pr_number: pr.pr_number,
      title: pr.title,
      author: pr.author,
      repository: {
        id: pr.repository.id,
        name: pr.repository.name,
        full_name: pr.repository.full_name,
        owner: pr.repository.owner,
      },
      latest_review: pr.latest_review
        ? {
            final_score: pr.latest_review.final_score,
            security_score: pr.latest_review.security_score,
            style_score: pr.latest_review.style_score,
            architecture_score: pr.latest_review.architecture_score,
            created_at: pr.latest_review.created_at,
          }
        : null,
    }));
    data = { repositories, pullRequests: analyticsPullRequests };
  } catch {}
  if (!data) return <section className="px-4 pb-6 lg:px-6"><ApiErrorCard title="Unable to load analytics" /></section>;
  return <AnalyticsContent repositories={data.repositories} pullRequests={data.pullRequests} />;
}
