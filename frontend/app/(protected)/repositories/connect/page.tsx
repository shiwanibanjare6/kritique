"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import api from "@/services/api";


interface GitHubRepository {
  github_id: number;
  owner: string;
  name: string;
  full_name: string;
  default_branch: string;
}

export default function ConnectRepositoryPage() {
  const { data: session } = useSession();
  const [repositories, setRepositories] = useState<GitHubRepository[]>([]);
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState<number | null>(null);

  useEffect(() => {
  if (!session?.accessToken) {
    return;
  }

  async function loadRepositories() {
    try {
      const res = await api.get("/github/github-repositories", {
        headers: {
          Authorization: `Bearer ${session.accessToken}`,
        },
      });

      setRepositories(res.data);
    } catch (error) {
      console.error("Failed to load GitHub repositories:", error);
    } finally {
      setLoading(false);
    }
  }

  loadRepositories();
}, [session]);

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

      alert(`${repo.full_name} connected successfully!`);
    } catch (error) {
      console.error(error);
      alert("Failed to connect repository.");
    } finally {
      setConnecting(null);
    }
  }

  return (
    <main className="w-full px-10 py-8">
      <h1 className="text-3xl font-bold">
        Connect Repository
      </h1>

      <p className="mt-2 text-muted-foreground">
        Select a GitHub repository to connect to Kritique.
      </p>

      {loading ? (
        <p className="mt-8">Loading repositories...</p>
      ) : repositories.length === 0 ? (
        <p className="mt-8">No repositories found.</p>
      ) : (
        <div className="mt-8 space-y-4">
          {repositories.map((repo) => (
            <div
              key={repo.github_id}
              className="flex items-center justify-between rounded-xl border p-5"
            >
              <div>
                <h2 className="font-semibold">
                  {repo.full_name}
                </h2>

                <p className="text-sm text-muted-foreground">
                  Default branch: {repo.default_branch}
                </p>
              </div>

              <button
                onClick={() => connectRepository(repo)}
                disabled={connecting === repo.github_id}
                className="rounded-lg bg-primary px-4 py-2 text-primary-foreground disabled:opacity-50"
              >
                {connecting === repo.github_id
                  ? "Connecting..."
                  : "Connect"}
              </button>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}