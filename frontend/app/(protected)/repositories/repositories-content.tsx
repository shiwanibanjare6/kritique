"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { GitBranch, RefreshCw } from "lucide-react";

import type { Repository } from "@/types";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";

export default function RepositoriesContent({
  repositories,
  error = false,
}: {
  repositories: Repository[];
  error?: boolean;
}) {
  const router = useRouter();

  return (
    <>
      {error ? (
        <Card className="mx-auto max-w-2xl">
          <CardContent className="p-10 text-center">
            <CardTitle>Unable to load repositories</CardTitle>
            <CardDescription className="mt-2">
              Check that the API is available, then refresh this page.
            </CardDescription>
          </CardContent>
        </Card>
      ) : repositories.length === 0 ? (
        <Card className="mx-auto max-w-2xl">
          <CardContent className="p-10 text-center">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-primary/10 text-primary">
              <GitBranch className="h-6 w-6" />
            </div>
            <CardTitle className="mt-6 text-xl">No repositories connected</CardTitle>
            <CardDescription className="mt-2 text-sm text-muted-foreground">
              Connect a GitHub repository to start generating AI reviews and performance analytics.
            </CardDescription>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {repositories.map((repo) => (
            <Card
              key={repo.id}
              className="cursor-pointer transition-all hover:border-primary hover:shadow-lg"
              onClick={() => router.push(`/repositories/${repo.id}`)}
            >
              <CardContent className="space-y-4 p-6">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 text-primary">
                    <GitBranch className="h-5 w-5" />
                  </div>
                  <div>
                    <h2 className="font-semibold">{repo.name}</h2>
                    <p className="text-sm text-muted-foreground">{repo.owner}</p>
                  </div>
                </div>

                <div className="space-y-2 text-sm text-muted-foreground">
                  <p>Default Branch: {repo.default_branch}</p>
                  <p>Reviewed PRs: {repo.reviewed_pull_requests}</p>
                </div>

                <div className="flex flex-wrap gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                    }}
                  >
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Sync
                  </Button>
                  <Button size="sm" asChild onClick={(e) => e.stopPropagation()}>
                    <Link href={`/repositories/${repo.id}/pull-requests`}>
                      View PRs
                    </Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </>
  );
}
