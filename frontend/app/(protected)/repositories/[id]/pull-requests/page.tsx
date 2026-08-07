"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { ArrowLeft, GitBranch, User, CheckCircle2 } from "lucide-react";

import api from "@/services/api";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

interface Repository {
  id: number;
  github_id: number;
  owner: string;
  name: string;
  full_name: string;
  default_branch: string;
  total_pull_requests: number;
  reviewed_pull_requests: number;
  average_score: number;
  latest_pull_requests: {
    id: number;
    pr_number: number;
    title: string;
    author: string;
    state: string;
  }[];
}

export default function RepositoryDetailsPage() {
  const params = useParams();
  const id = params.id as string;
  const [repository, setRepository] = useState<Repository | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    async function loadRepository() {
      try {
        const response = await api.get<Repository>(`/github/repositories/${id}`);
        setRepository(response.data);
      } catch (err) {
        console.error(err);
        setError(true);
      } finally {
        setLoading(false);
      }
    }

    loadRepository();
  }, [id]);

  return (
    <main className="flex-1 w-full space-y-8 px-10 py-8">
      <div className="mb-8 flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-muted-foreground">
            Repository Details
          </p>
          <h1 className="text-4xl font-bold">Repository overview</h1>
          <p className="mt-2 text-muted-foreground">
            Review repository performance and view the latest pull requests.
          </p>
        </div>

        <Button variant="outline" asChild>
          <Link href="/repositories">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to repositories
          </Link>
        </Button>
      </div>

      {loading ? (
        <div className="space-y-6">
          <Skeleton className="h-80 rounded-3xl" />
          <div className="grid gap-6 md:grid-cols-3">
            <Skeleton className="h-36 rounded-3xl" />
            <Skeleton className="h-36 rounded-3xl" />
            <Skeleton className="h-36 rounded-3xl" />
          </div>
        </div>
      ) : error || !repository ? (
        <Card className="mx-auto max-w-2xl">
          <CardContent className="p-10 text-center">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-red-500/10 text-red-600">
              <CheckCircle2 className="h-6 w-6" />
            </div>
            <CardTitle className="mt-6">Unable to load repository</CardTitle>
            <CardDescription className="mt-2 text-sm text-muted-foreground">
              Try again later or return to the repositories list.
            </CardDescription>
          </CardContent>
        </Card>
      ) : (
        <>
          <Card className="rounded-3xl border-border shadow-sm">
            <CardContent className="space-y-8 p-8">
              <div className="flex flex-col gap-8 xl:flex-row xl:items-start xl:justify-between">
                <div>
                  <h2 className="text-3xl font-bold">{repository.name}</h2>
                  <p className="mt-2 text-muted-foreground">{repository.full_name}</p>
                </div>
                <div className="rounded-2xl border border-border bg-muted px-4 py-3 text-sm">
                  <p className="text-muted-foreground">Default branch</p>
                  <p className="font-semibold">{repository.default_branch}</p>
                </div>
              </div>

              <div className="grid gap-6 lg:grid-cols-3">
                <div className="rounded-2xl border border-border bg-muted/20 p-6">
                  <p className="mt-1 text-sm text-muted-foreground">Owner</p>
                  <p className="mt-2 text-lg font-semibold">{repository.owner}</p>
                </div>
                <div className="rounded-2xl border border-border bg-muted/20 p-6">
                  <p className="mt-1 text-sm text-muted-foreground">Repository ID</p>
                  <p className="mt-2 text-lg font-semibold">{repository.id}</p>
                </div>
                <div className="rounded-2xl border border-border bg-muted/20 p-6">
                  <p className="mt-1 text-sm text-muted-foreground">Total pull requests</p>
                  <p className="mt-2 text-lg font-semibold">{repository.total_pull_requests}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="grid gap-8 lg:grid-cols-3">
            <Card className="rounded-3xl">
              <CardContent className="space-y-3 p-8">
                <p className="text-sm text-muted-foreground">Total Pull Requests</p>
                <h2 className="text-5xl font-bold tracking-tight">{repository.total_pull_requests}</h2>
              </CardContent>
            </Card>
            <Card className="rounded-3xl">
              <CardContent className="space-y-3 p-8">
                <p className="text-sm text-muted-foreground">Reviewed Pull Requests</p>
                <h2 className="text-5xl font-bold tracking-tight">{repository.reviewed_pull_requests}</h2>
              </CardContent>
            </Card>
            <Card className="rounded-3xl">
              <CardContent className="space-y-3 p-8">
                <p className="text-sm text-muted-foreground">Average AI Score</p>
                <h2 className="text-5xl font-bold tracking-tight">{repository.average_score}/100</h2>
              </CardContent>
            </Card>
          </div>

          <Card className="rounded-3xl">
            <CardHeader className="border-b pb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <CardTitle>Latest Pull Requests</CardTitle>
              <Button size="sm" asChild>
                <Link href="/pull-requests">
                  View all pull requests
                </Link>
              </Button>
            </CardHeader>
            <CardContent className="space-y-3">
              {repository.latest_pull_requests.length === 0 ? (
                <div className="rounded-2xl border border-dashed border-border p-8 text-center">
                  <p className="text-sm text-muted-foreground">No pull requests have been synced for this repository yet.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {repository.latest_pull_requests.map((pr) => (
                    <Link
                      key={pr.id}
                      href={`/pull-requests/${pr.id}`}
                      className="flex items-center justify-between rounded-2xl border border-border bg-card p-6 transition-all hover:border-primary hover:bg-muted/40"
                    >
                      <div>
                        <p className="text-lg font-semibold">#{pr.pr_number} {pr.title}</p>
                        <p className="text-sm text-muted-foreground">{pr.author}</p>
                      </div>
                      <Badge
    className={
        pr.state === "open"
            ? "bg-green-600 text-white"
            : "bg-gray-500 text-white"
    }
>
                        {pr.state}
                      </Badge>
                    </Link>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </main>
  );
}
