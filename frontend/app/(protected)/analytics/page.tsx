"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { BarChart3, ChartLine, GitBranch, ListChecks, ShieldCheck, Star } from "lucide-react";

import api from "@/services/api";
import type { PullRequest, Repository } from "@/types";
import { formatScore } from "@/lib/format-score";
import { ChartAreaInteractive } from "@/components/chart-area-interactive";
import { SiteHeader } from "@/components/site-header";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/table";

const ALL_REPOSITORIES = "all";
const ALL_PULL_REQUESTS = "all";

const scoreClass = (score: number) => {
  if (score >= 90) return "bg-emerald-600 text-white";
  if (score >= 75) return "bg-amber-500 text-white";
  return "bg-red-600 text-white";
};

const formatScoreWithScale = (value: number | null) =>
  value === null ? "—" : `${formatScore(value)}/100`;

function averageScore(
  pullRequests: PullRequest[],
  getScore: (pullRequest: PullRequest) => number,
) {
  if (pullRequests.length === 0) return null;
  return pullRequests.reduce((sum, pullRequest) => sum + getScore(pullRequest), 0) / pullRequests.length;
}

export default function AnalyticsPage() {
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [pullRequests, setPullRequests] = useState<PullRequest[]>([]);
  const [selectedRepositoryId, setSelectedRepositoryId] = useState(ALL_REPOSITORIES);
  const [selectedPullRequestId, setSelectedPullRequestId] = useState(ALL_PULL_REQUESTS);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(false);

  useEffect(() => {
    let active = true;

    async function loadAnalyticsData() {
      try {
        const [repositoryResponse, pullRequestResponse] = await Promise.all([
          api.get<Repository[]>("/github/repositories"),
          api.get<PullRequest[]>("/pull-requests/"),
        ]);

        if (!active) return;
        setRepositories(repositoryResponse.data);
        setPullRequests(pullRequestResponse.data);
      } catch (error) {
        console.error("Failed to load analytics", error);
        if (active) setLoadError(true);
      } finally {
        if (active) setLoading(false);
      }
    }

    loadAnalyticsData();
    return () => {
      active = false;
    };
  }, []);

  const availablePullRequests = useMemo(
    () => selectedRepositoryId === ALL_REPOSITORIES
      ? pullRequests
      : pullRequests.filter((pr) => pr.repository.id === Number(selectedRepositoryId)),
    [pullRequests, selectedRepositoryId],
  );

  const scopedPullRequests = useMemo(
    () => selectedPullRequestId === ALL_PULL_REQUESTS
      ? availablePullRequests
      : availablePullRequests.filter((pr) => pr.id === Number(selectedPullRequestId)),
    [availablePullRequests, selectedPullRequestId],
  );

  const reviewedPRs = useMemo(
    () => scopedPullRequests.filter((pr) => pr.latest_review !== null),
    [scopedPullRequests],
  );

  const totalRepositories = selectedPullRequestId !== ALL_PULL_REQUESTS
    ? (scopedPullRequests.length > 0 ? 1 : 0)
    : selectedRepositoryId !== ALL_REPOSITORIES
      ? (repositories.some((repo) => String(repo.id) === selectedRepositoryId) ? 1 : 0)
      : repositories.length;

  const averageFinalScore = useMemo(
    () => averageScore(reviewedPRs, (pr) => pr.latest_review!.final_score),
    [reviewedPRs],
  );
  const averageSecurityScore = useMemo(
    () => averageScore(reviewedPRs, (pr) => pr.latest_review!.security_score),
    [reviewedPRs],
  );
  const averageStyleScore = useMemo(
    () => averageScore(reviewedPRs, (pr) => pr.latest_review!.style_score),
    [reviewedPRs],
  );
  const averageArchitectureScore = useMemo(
    () => averageScore(reviewedPRs, (pr) => pr.latest_review!.architecture_score),
    [reviewedPRs],
  );

  const repositoryPerformance = useMemo(() => {
    const map = new Map<number, {
      repository: PullRequest["repository"];
      reviewedCount: number;
      scoreSum: number;
    }>();

    scopedPullRequests.forEach((pr) => {
      const entry = map.get(pr.repository.id) ?? {
        repository: pr.repository,
        reviewedCount: 0,
        scoreSum: 0,
      };

      if (pr.latest_review) {
        entry.reviewedCount += 1;
        entry.scoreSum += pr.latest_review.final_score;
      }
      map.set(pr.repository.id, entry);
    });

    return Array.from(map.values()).map((entry) => ({
      ...entry,
      averageScore: entry.reviewedCount === 0 ? null : entry.scoreSum / entry.reviewedCount,
    }));
  }, [scopedPullRequests]);

  const recentReviews = useMemo(
    () => reviewedPRs
      .slice()
      .sort((a, b) =>
        new Date(b.latest_review!.created_at).getTime() -
        new Date(a.latest_review!.created_at).getTime(),
      )
      .slice(0, 8),
    [reviewedPRs],
  );

  function handleRepositoryChange(repositoryId: string) {
    setSelectedRepositoryId(repositoryId);
    if (selectedPullRequestId === ALL_PULL_REQUESTS) return;

    const currentPullRequest = pullRequests.find(
      (pr) => String(pr.id) === selectedPullRequestId,
    );
    const stillBelongsToRepository = currentPullRequest && (
      repositoryId === ALL_REPOSITORIES ||
      String(currentPullRequest.repository.id) === repositoryId
    );
    if (!stillBelongsToRepository) setSelectedPullRequestId(ALL_PULL_REQUESTS);
  }

  const noScopePullRequests = !loading && !loadError && scopedPullRequests.length === 0;
  const noReviewedPullRequests = !loading && !loadError && reviewedPRs.length === 0;

  return (
    <main className="flex flex-1 flex-col">
      <SiteHeader />
      <div className="@container/main flex flex-1 flex-col gap-8 py-6">
        <section className="px-4 lg:px-6">
          <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div className="space-y-3">
              <div className="inline-flex items-center gap-2 rounded-full bg-primary/10 px-3 py-1 text-sm text-primary">
                <BarChart3 className="h-4 w-4" />
                Analytics Overview
              </div>
              <div>
                <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
                <p className="mt-2 max-w-2xl text-muted-foreground">
                  Visualize repository scoring performance and review quality across your pull requests.
                </p>
              </div>
            </div>
          </div>
        </section>

        <section className="px-4 lg:px-6">
          <Card>
            <CardContent className="grid gap-4 p-5 md:grid-cols-2">
              <div className="grid gap-2">
                <label className="text-sm font-medium" htmlFor="analytics-repository">
                  Repository
                </label>
                <Select
                  value={selectedRepositoryId}
                  onValueChange={handleRepositoryChange}
                  disabled={loading || loadError || repositories.length === 0}
                >
                  <SelectTrigger id="analytics-repository" className="w-full" aria-label="Repository">
                    <SelectValue placeholder={loading ? "Loading repositories..." : "All Repositories"} />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value={ALL_REPOSITORIES}>All Repositories</SelectItem>
                    {repositories.map((repository) => (
                      <SelectItem key={repository.id} value={String(repository.id)}>
                        {repository.full_name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {loading && <Skeleton className="h-3 w-36" />}
                {!loading && !loadError && repositories.length === 0 && (
                  <p className="text-xs text-muted-foreground">No connected repositories found.</p>
                )}
              </div>

              <div className="grid gap-2">
                <label className="text-sm font-medium" htmlFor="analytics-pull-request">
                  Pull Request
                </label>
                <Select
                  value={selectedPullRequestId}
                  onValueChange={setSelectedPullRequestId}
                  disabled={loading || loadError || availablePullRequests.length === 0}
                >
                  <SelectTrigger id="analytics-pull-request" className="w-full" aria-label="Pull Request">
                    <SelectValue placeholder={loading ? "Loading pull requests..." : "All Pull Requests"} />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value={ALL_PULL_REQUESTS}>All Pull Requests</SelectItem>
                    {availablePullRequests.map((pr) => (
                      <SelectItem key={pr.id} value={String(pr.id)}>
                        #{pr.pr_number} {pr.title}
                        {selectedRepositoryId === ALL_REPOSITORIES
                          ? ` (${pr.repository.full_name})`
                          : ""}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {loading && <Skeleton className="h-3 w-36" />}
                {!loading && !loadError && availablePullRequests.length === 0 && (
                  <p className="text-xs text-muted-foreground">No pull requests in this scope.</p>
                )}
              </div>
            </CardContent>
          </Card>
        </section>

        {loadError && (
          <section className="px-4 lg:px-6" role="alert">
            <Card className="border-destructive/50">
              <CardContent className="p-6">
                <CardTitle>Unable to load analytics</CardTitle>
                <CardDescription className="mt-2">
                  The analytics data could not be loaded. Please try again later.
                </CardDescription>
              </CardContent>
            </Card>
          </section>
        )}

        {!loadError && (
          <>
            <section className="grid gap-4 px-4 sm:grid-cols-2 lg:px-6 xl:grid-cols-4">
              {[
                { label: "Repositories", value: totalRepositories, icon: GitBranch },
                { label: "Pull Requests", value: scopedPullRequests.length, icon: ListChecks },
                { label: "Reviewed PRs", value: reviewedPRs.length, icon: ShieldCheck },
                {
                  label: "Average AI Score",
                  value: formatScoreWithScale(averageFinalScore),
                  icon: Star,
                },
              ].map((card) => {
                const Icon = card.icon;
                return (
                  <Card key={card.label}>
                    <CardContent className="space-y-4 p-6">
                      <div className="flex items-center justify-between gap-4">
                        <div>
                          <p className="text-sm font-medium text-muted-foreground">{card.label}</p>
                          <div className="mt-3">
                            {loading ? <Skeleton className="h-10 w-24" /> : (
                              <p className="text-3xl font-semibold">{card.value}</p>
                            )}
                          </div>
                        </div>
                        <div className="rounded-2xl bg-primary/10 p-3 text-primary">
                          <Icon className="h-6 w-6" />
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </section>

            {noScopePullRequests && (
              <section className="px-4 lg:px-6">
                <Card>
                  <CardContent className="p-6 text-sm text-muted-foreground">
                    No pull requests are available in the selected scope.
                  </CardContent>
                </Card>
              </section>
            )}

            {noReviewedPullRequests && !noScopePullRequests && (
              <section className="px-4 lg:px-6">
                <Card>
                  <CardContent className="flex items-start gap-3 p-6">
                    <ChartLine className="mt-0.5 h-5 w-5 text-primary" />
                    <div>
                      <p className="font-medium">
                        {selectedPullRequestId !== ALL_PULL_REQUESTS
                          ? "No review data for this pull request"
                          : "No reviewed pull requests in this scope"}
                      </p>
                      <p className="mt-1 text-sm text-muted-foreground">
                        Score analytics will appear after a pull request has been reviewed.
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </section>
            )}

            <section className="grid gap-4 px-4 lg:px-6 xl:grid-cols-[1.1fr_0.9fr]">
              <Card>
                <CardHeader>
                  <CardTitle>Review Score Breakdown</CardTitle>
                  <CardDescription>Average scores from reviewed pull requests in this scope.</CardDescription>
                </CardHeader>
                <CardContent className="grid gap-4 sm:grid-cols-3">
                  {[
                    ["Security", averageSecurityScore],
                    ["Style", averageStyleScore],
                    ["Architecture", averageArchitectureScore],
                  ].map(([label, score]) => (
                    <div key={String(label)} className="rounded-xl border border-border p-4">
                      <p className="text-sm text-muted-foreground">{label}</p>
                      <div className="mt-2 text-3xl font-semibold">
                        {loading ? <Skeleton className="h-9 w-24" /> : formatScoreWithScale(score as number | null)}
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </section>

            <section className="space-y-4 px-4 lg:px-6">
              <ChartAreaInteractive pullRequests={scopedPullRequests} loading={loading} />
            </section>

            <section className="grid gap-4 px-4 lg:px-6 xl:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Repository Performance</CardTitle>
                </CardHeader>
                <CardContent className="overflow-x-auto p-0">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Repository</TableHead>
                        <TableHead>Reviewed PRs</TableHead>
                        <TableHead>Average Score</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {repositoryPerformance.length === 0 ? (
                        <TableRow><TableCell colSpan={3} className="py-8 text-center text-muted-foreground">No repository data in this scope.</TableCell></TableRow>
                      ) : repositoryPerformance.map((row) => (
                        <TableRow key={row.repository.id}>
                          <TableCell className="font-medium">{row.repository.full_name}</TableCell>
                          <TableCell>{row.reviewedCount}</TableCell>
                          <TableCell>
                            <Badge className={row.averageScore === null ? "bg-muted text-foreground" : scoreClass(row.averageScore)}>
                              {formatScoreWithScale(row.averageScore)}
                            </Badge>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Recent Reviews</CardTitle>
                </CardHeader>
                <CardContent className="overflow-x-auto p-0">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>PR</TableHead>
                        <TableHead>Repository</TableHead>
                        <TableHead>Final Score</TableHead>
                        <TableHead>Author</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {recentReviews.length === 0 ? (
                        <TableRow><TableCell colSpan={4} className="py-8 text-center text-muted-foreground">No recent reviews in this scope.</TableCell></TableRow>
                      ) : recentReviews.map((pr) => (
                        <TableRow key={pr.id}>
                          <TableCell>
                            <Link href={`/pull-requests/${pr.id}`} className="font-medium text-primary hover:underline">
                              #{pr.pr_number} {pr.title}
                            </Link>
                          </TableCell>
                          <TableCell>{pr.repository.full_name}</TableCell>
                          <TableCell>
                            <Badge className={scoreClass(pr.latest_review!.final_score)}>
                              {formatScore(pr.latest_review!.final_score)}/100
                            </Badge>
                          </TableCell>
                          <TableCell>{pr.author}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            </section>
          </>
        )}
      </div>
    </main>
  );
}
