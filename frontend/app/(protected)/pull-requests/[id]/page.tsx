import { Suspense } from "react";
import { notFound } from "next/navigation";

import PullRequestDetailsContent from "./pull-request-details-content";
import { ApiErrorCard } from "@/components/api-error-card";
import { ProtectedPageLoading } from "@/components/protected-page-loading";
import { ApiServerError, getPullRequest } from "@/lib/api-server";

export default function PullRequestDetailsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  return (
    <Suspense fallback={<ProtectedPageLoading />}>
      <PullRequestData params={params} />
    </Suspense>
  );
}

async function PullRequestData({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  let pullRequest: Awaited<ReturnType<typeof getPullRequest>> | null = null;
  let failure: unknown = null;
  try {
    pullRequest = await getPullRequest(id);
  } catch (error) {
    failure = error;
  }
  if (failure instanceof ApiServerError && failure.status === 404) notFound();
  if (failure || !pullRequest) return <div className="px-8 py-8"><ApiErrorCard title="Unable to load pull request" /></div>;
  return <PullRequestDetailsContent pr={pullRequest} />;
}
