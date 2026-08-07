"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { GitBranch, Plus, RefreshCw } from "lucide-react";

import api from "@/services/api";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
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

export default function RepositoriesPage() {
  const [repositories, setRepositories] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(true);

  const router = useRouter();

  useEffect(() => {
    async function loadRepositories() {
      try {
        const res = await api.get("/github/repositories");
        setRepositories(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    loadRepositories();
  }, []);

  return (
    <main className="w-full px-10 py-8 xl:px-12">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-4xl font-bold">Repositories</h1>
          <p className="mt-2 text-muted-foreground">
            Manage your connected GitHub repositories.
          </p>
        </div>

        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Connect Repository
        </Button>
      </div>

      {loading ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, index) => (
            <Card key={index} className="p-6">
              <CardContent className="space-y-4">
                <Skeleton className="h-6 w-40" />
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-4 w-full" />
                <div className="flex gap-2">
                  <Skeleton className="h-9 w-24 rounded-lg" />
                  <Skeleton className="h-9 w-24 rounded-lg" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
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
    </main>
  );
}