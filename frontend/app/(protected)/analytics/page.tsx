"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { BarChart3, ChartLine, GitBranch, ListChecks, ShieldCheck, Star } from "lucide-react";

import api from "@/services/api";
import type { PullRequest } from "@/types";
import { SiteHeader } from "@/components/site-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/table";

const scoreClass = (score: number) => {
  if (score >= 90) return "bg-emerald-600 text-white";
  if (score >= 75) return "bg-amber-500 text-white";
  return "bg-red-600 text-white";
};

const formatScore = (value: number | null) =>
  value === null ? "—" : `${Math.round(value)}/100`;

export default function AnalyticsPage() {
  const [pullRequests, setPullRequests] = useState<PullRequest[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadAnalytics() {
      try {
        const response = await api.get<PullRequest[]>("/pull-requests");
        setPullRequests(response.data);
      } catch (error) {
        console.error("Failed to load analytics", error);
      } finally {
        setLoading(false);
      }
    }

    loadAnalytics();
  }, []);

  const reviewedPRs = useMemo(
    () => pullRequests.filter((pr) => pr.latest_review !== null),
    [pullRequests]
  );

  const totalRepositories = useMemo(
    () => new Set(pullRequests.map((pr) => pr.repository.id)).size,
    [pullRequests]
  );

  const averageScore = useMemo(() => {
    if (reviewedPRs.length === 0) return null;
    return (
      reviewedPRs.reduce(
        (sum, pr) => sum + pr.latest_review!.final_score,
        0
      ) / reviewedPRs.length
    );
  }, [reviewedPRs]);

  const averageSecurityScore = useMemo(() => {
    if (reviewedPRs.length === 0) return null;
    return (
      reviewedPRs.reduce(
        (sum, pr) => sum + pr.latest_review!.security_score,
        0
      ) / reviewedPRs.length
    );
  }, [reviewedPRs]);

  const averageStyleScore = useMemo(() => {
    if (reviewedPRs.length === 0) return null;
    return (
      reviewedPRs.reduce(
        (sum, pr) => sum + pr.latest_review!.style_score,
        0
      ) / reviewedPRs.length
    );
  }, [reviewedPRs]);

  const averageArchitectureScore = useMemo(() => {
    if (reviewedPRs.length === 0) return null;
    return (
      reviewedPRs.reduce(
        (sum, pr) => sum + pr.latest_review!.architecture_score,
        0
      ) / reviewedPRs.length
    );
  }, [reviewedPRs]);

  const repositoryPerformance = useMemo(() => {
    const map = new Map<
      number,
      {
        repository: PullRequest["repository"];
        reviewedCount: number;
        scoreSum: number;
      }
    >();

    pullRequests.forEach((pr) => {
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
      averageScore:
        entry.reviewedCount === 0
          ? null
          : entry.scoreSum / entry.reviewedCount,
    }));
  }, [pullRequests]);

  const recentReviews = useMemo(
    () =>
      reviewedPRs
        .slice()
        .sort(
          (a, b) =>
            new Date(b.latest_review!.created_at).getTime() -
            new Date(a.latest_review!.created_at).getTime()
        )
        .slice(0, 8),
    [reviewedPRs]
  );

  const hasData = !loading && pullRequests.length === 0;

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
                <h1 className="text-3xl font-bold tracking-tight">
                  Analytics
                </h1>
                <p className="mt-2 text-muted-foreground max-w-2xl">
                  Visualize repository scoring performance and review quality across all pull requests.
                </p>
              </div>
            </div>
          </div>
        </section>

        {hasData ? (
          <section className="px-4 lg:px-6">
            <Card className="mx-auto max-w-2xl">
              <CardContent className="p-10 text-center">
                <ChartLine className="mx-auto h-10 w-10 text-primary" />
                <h2 className="mt-6 text-xl font-semibold">
                  No analytics available yet
                </h2>
                <p className="mt-2 text-sm text-muted-foreground">
                  Connect a repository and review pull requests to populate analytics data.
                </p>
              </CardContent>
            </Card>
          </section>
        ) : (
          <>
            <section className="grid gap-4 px-4 lg:px-6 sm:grid-cols-2 xl:grid-cols-4">
              {[
                {
                  label: "Repositories",
                  value: totalRepositories,
                  icon: GitBranch,
                },
                {
                  label: "Pull Requests",
                  value: pullRequests.length,
                  icon: ListChecks,
                },
                {
                  label: "Reviewed PRs",
                  value: reviewedPRs.length,
                  icon: ShieldCheck,
                },
                {
                  label: "Average AI Score",
                  value:
                    averageScore === null
                      ? "—"
                      : `${Math.round(averageScore)}/100`,
                  icon: Star,
                },
              ].map((card) => {
                const Icon = card.icon;
                return (
                  <Card key={card.label}>
                    <CardContent className="space-y-4 p-6">
                      <div className="flex items-center justify-between gap-4">
                        <div>
                          <p className="text-sm font-medium text-muted-foreground">
                            {card.label}
                          </p>
                          <div className="mt-3">
  {loading ? (
    <Skeleton className="h-10 w-24" />
  ) : (
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

            <section className="grid gap-4 px-4 lg:px-6 xl:grid-cols-[1.1fr_0.9fr]">
              <Card>
                <CardHeader>
                  <CardTitle>Review Score Breakdown</CardTitle>
                  <CardDescription>
                    Average scores from reviewed pull requests.
                  </CardDescription>
                </CardHeader>
                <CardContent className="grid gap-4 sm:grid-cols-3">
                  <div className="rounded-xl border border-border p-4">
                    <p className="text-sm text-muted-foreground">Security</p>
                    <p className="mt-2 text-3xl font-semibold">
                      {formatScore(averageSecurityScore)}
                    </p>
                  </div>
                  <div className="rounded-xl border border-border p-4">
                    <p className="text-sm text-muted-foreground">Style</p>
                    <p className="mt-2 text-3xl font-semibold">
                      {formatScore(averageStyleScore)}
                    </p>
                  </div>
                  <div className="rounded-xl border border-border p-4">
                    <p className="text-sm text-muted-foreground">Architecture</p>
                    <p className="mt-2 text-3xl font-semibold">
                      {formatScore(averageArchitectureScore)}
                    </p>
                  </div>
                </CardContent>
              </Card>
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
                      {repositoryPerformance.map((row) => (
                        <TableRow key={row.repository.id}>
                          <TableCell>
                            <div className="flex flex-col gap-1">
                              <span className="font-medium">
                                {row.repository.full_name}
                              </span>
                            </div>
                          </TableCell>
                          <TableCell>{row.reviewedCount}</TableCell>
                          <TableCell>
                            <Badge
                              className={
                                row.averageScore === null
                                  ? "bg-muted text-foreground"
                                  : scoreClass(row.averageScore)
                              }
                            >
                              {formatScore(row.averageScore)}
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
                      {recentReviews.map((pr) => (
                        <TableRow key={pr.id}>
                          <TableCell>
                            <Link
                              href={`/pull-requests/${pr.id}`}
                              className="font-medium text-primary hover:underline"
                            >
                              #{pr.pr_number} {pr.title}
                            </Link>
                          </TableCell>
                          <TableCell>{pr.repository.full_name}</TableCell>
                          <TableCell>
                            <Badge className={scoreClass(pr.latest_review!.final_score)}>
                              {pr.latest_review!.final_score}/100
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
