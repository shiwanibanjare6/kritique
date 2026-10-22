"use client";

import Link from "next/link";

import type { RepositoryDetails } from "@/lib/api-server";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatScore } from "@/lib/format-score";

export default function RepositoryDetailsContent({ repository }: { repository: RepositoryDetails }) {

  return (
    <section className="space-y-8">
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
                <h2 className="text-5xl font-bold tracking-tight">{formatScore(repository.average_score)}/100</h2>
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
    </section>
  );
}
