import { notFound } from "next/navigation"
import {
  GitBranch,
  User,
  FolderGit2,
  CircleCheckBig,
} from "lucide-react"

import FileReviewCard from "@/components/review/FileReviewCard";

import ReviewSummary from "@/components/review/ReviewSummary";

import ScoreCard from "@/components/review/ScoreCard";

import type { PullRequest } from "@/types"

import { Badge } from "@/components/ui/badge";

import Link from "next/link";

import MergeRecommendation from "@/components/review/MergeRecommendation";

import {
  ArrowLeft,
  ExternalLink,
} from "lucide-react";

import { Button } from "@/components/ui/button";

interface Props {
  params: Promise<{
    id: string
  }>
}

async function getPullRequest(id: string): Promise<PullRequest> {
  const res = await fetch(
    const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const res = await fetch(
  `${API_URL}/api/v1/pull-requests/${id}`,
  {
    cache: "no-store",
  }
)
    {
      cache: "no-store",
    }
  )

  if (!res.ok) {
    notFound()
  }

  return res.json()
}

export default async function PullRequestDetailsPage({
  params,
}: Props) {
  const { id } = await params

  const pr = await getPullRequest(id)

  const review = pr.latest_review

  return (
    <main className="flex-1 w-full px-8 py-8 space-y-8">

      {/* Header */}

      <div className="mb-8 flex items-center justify-between">

  <Button
    asChild
    variant="outline"
  >
    <Link href="/">
      <ArrowLeft className="mr-2 h-4 w-4" />
      Dashboard
    </Link>
  </Button>

  <Button
    asChild
  >
    <a
      href={pr.url}
      target="_blank"
      rel="noopener noreferrer"
    >
      <ExternalLink className="mr-2 h-4 w-4" />

      Open on GitHub
    </a>
  </Button>

</div>

      <div className="mb-8 space-y-3">

        <div className="flex items-center gap-3">

  <h1 className="text-4xl font-bold">
    #{pr.pr_number}
  </h1>

  <h2 className="text-3xl font-semibold">
    {pr.title}
  </h2>

</div>

<p className="text-muted-foreground">

  Repository:

  <span className="ml-2 font-medium text-foreground">
    {pr.repository.name}
  </span>

</p>

      </div>

      {/* Information */}

      <div className="mb-8 grid gap-8 md:grid-cols-2 xl:grid-cols-4">

        <div className="rounded-xl border p-6">

          <FolderGit2 className="mb-4 h-6 w-6 text-primary" />

          <p className="text-sm text-muted-foreground">
            Repository
          </p>

          <h3 className="mt-2 font-semibold">
            {pr.repository.name}
          </h3>

        </div>

        <div className="rounded-xl border p-6">

          <User className="mb-4 h-6 w-6 text-primary" />

          <p className="text-sm text-muted-foreground">
            Author
          </p>

          <h3 className="mt-2 font-semibold">
            {pr.author}
          </h3>

        </div>

        <div className="rounded-xl border p-6">

          <GitBranch className="mb-4 h-6 w-6 text-primary" />

          <p className="text-sm text-muted-foreground">
            Branches
          </p>

          <h3 className="mt-2 font-semibold">
            {pr.head_branch}
          </h3>

          <p className="text-xs text-muted-foreground">
            →
          </p>

          <h3 className="font-semibold">
            {pr.base_branch}
          </h3>

        </div>

        <div className="rounded-xl border p-6">

          <CircleCheckBig className="mb-4 h-6 w-6 text-green-500" />

          <p className="text-sm text-muted-foreground">
            Status
          </p>

          <Badge
  className={
    pr.state === "open"
      ? "bg-green-500"
      : "bg-gray-500"
  }
>
  {pr.state}
</Badge>

        </div>

      </div>

      {!review && (
        <div className="rounded-xl border p-6">
          No AI review available.
        </div>
      )}

      {review && (
        
  <>
<MergeRecommendation
  recommendation={review.merge_recommendation}
  risk={review.risk_level}
  strengths={review.strengths}
  weaknesses={review.weaknesses}
/>
    <section className="mb-8 grid gap-8 md:grid-cols-2 xl:grid-cols-4">
      <ScoreCard
        title="Overall Score"
        score={review.final_score}
      />

      <ScoreCard
        title="Security"
        score={review.security_score}
        color="text-green-500"
      />

      <ScoreCard
        title="Style"
        score={review.style_score}
        color="text-blue-500"
      />

      <ScoreCard
        title="Architecture"
        score={review.architecture_score}
        color="text-orange-500"
      />
    </section>
    <section className="mb-8">
  <ReviewSummary
  summary={review.summary}
  strengths={review.strengths}
  weaknesses={review.weaknesses}
  riskLevel={review.risk_level}
  mergeRecommendation={review.merge_recommendation}
/>
</section>

<section className="space-y-8">

  <div className="flex items-center justify-between">

<h2 className="text-2xl font-bold">

Files Reviewed

</h2>

<Badge variant="secondary">

{review.agent_output.length} Files

</Badge>

</div>

<div className="space-y-6">
  {review.agent_output.map((fileReview, index) => (
    <FileReviewCard
      key={index}
      review={fileReview}
    />
  ))}
</div>

</section>
  </>
)}

    </main>
  )
}