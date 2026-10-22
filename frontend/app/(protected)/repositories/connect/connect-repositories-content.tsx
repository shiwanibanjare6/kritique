"use client";

import { useState } from "react";
import { toast } from "sonner";

import type { GitHubRepository } from "@/lib/api-server";
import api from "@/services/api";

export default function ConnectRepositoriesContent({
  repositories,
}: {
  repositories: GitHubRepository[];
}) {
  const [connecting, setConnecting] = useState<number | null>(null);

  async function connectRepository(repo: GitHubRepository) {
    try {
      setConnecting(repo.github_id);
      await api.post("/github/repositories/connect", null, {
        params: {
          github_id: repo.github_id,
          owner: repo.owner,
          name: repo.name,
          full_name: repo.full_name,
          default_branch: repo.default_branch,
        },
      });
      toast.success("Repository connected successfully");
    } catch (error) {
      console.error(error);
      toast.error("Failed to connect repository. Please try again.");
    } finally {
      setConnecting(null);
    }
  }

  if (repositories.length === 0) {
    return <p className="mt-8">No repositories found.</p>;
  }

  return (
    <div className="mt-8 space-y-4">
      {repositories.map((repo) => (
        <div key={repo.github_id} className="flex items-center justify-between rounded-xl border p-5">
          <div>
            <h2 className="font-semibold">{repo.full_name}</h2>
            <p className="text-sm text-muted-foreground">Default branch: {repo.default_branch}</p>
          </div>
          <button
            onClick={() => connectRepository(repo)}
            disabled={connecting === repo.github_id}
            className="rounded-lg bg-primary px-4 py-2 text-primary-foreground disabled:opacity-50"
          >
            {connecting === repo.github_id ? "Connecting..." : "Connect"}
          </button>
        </div>
      ))}
    </div>
  );
}
