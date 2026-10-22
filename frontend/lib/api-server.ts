import "server-only";

import { cache } from "react";
import { auth } from "@/auth";
import type { PullRequest, PullRequestListItem, Repository, ReviewTimeseriesPoint, StatsSummary } from "@/types";

const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_URL ||
  (process.env.NODE_ENV === "production"
    ? "https://kritique-6zrw.onrender.com"
    : "http://127.0.0.1:8000")
).replace(/\/$/, "");

const configuredTimeout = Number(process.env.API_TIMEOUT_MS);
export const API_TIMEOUT_MS = Number.isFinite(configuredTimeout) && configuredTimeout > 0
  ? configuredTimeout
  : 45_000;

export class ApiServerError extends Error {
  constructor(
    message: string,
    public readonly status: number | null = null,
  ) {
    super(message);
    this.name = "ApiServerError";
  }
}

async function getServerAccessToken(): Promise<string> {
  const session = await auth();
  if (!session?.accessToken) {
    throw new ApiServerError("Your GitHub session is missing an access token.", 401);
  }
  return session.accessToken;
}

async function fetchApi<T>(path: string): Promise<T> {
  const accessToken = await getServerAccessToken();
  const url = `${API_BASE_URL}/api/v1${path}`;
  const startedAt = performance.now();
  let response: Response;
  const logTiming = () => {
    if (process.env.DEBUG_API_TIMING === "true") {
      console.info(
        `[api-server] backend fetch ${path}: ${Math.round(performance.now() - startedAt)}ms`,
      );
    }
  };

  try {
    response = await fetch(url, {
      cache: "no-store",
      headers: {
        Accept: "application/json",
        Authorization: `Bearer ${accessToken}`,
      },
      signal: AbortSignal.timeout(API_TIMEOUT_MS),
    });
  } catch (error) {
    logTiming();
    if (error instanceof Error && error.name === "TimeoutError") {
      throw new ApiServerError(`Backend request timed out after ${API_TIMEOUT_MS}ms.`, 504);
    }
    throw new ApiServerError("The backend could not be reached.");
  }

  if (!response.ok) {
    logTiming();
    throw new ApiServerError(
      `Backend request failed with HTTP ${response.status}.`,
      response.status,
    );
  }

  try {
    const data = (await response.json()) as T;
    logTiming();
    return data;
  } catch {
    logTiming();
    throw new ApiServerError("Backend returned invalid JSON.", response.status);
  }
}

// React cache memoizes within one server render. These user-scoped responses
// are never written to Next.js's persistent/shared Data Cache.
export const getPullRequests = cache(() => fetchApi<PullRequest[]>("/pull-requests/"));

export const getPullRequestSummary = cache((
  limit = 500,
  offset = 0,
  state = "",
  q = "",
) => {
  const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  if (state) params.set("state", state);
  if (q) params.set("q", q);
  return fetchApi<{ items: PullRequestListItem[]; total: number }>(`/pull-requests/summary?${params}`);
});

export const getStatsSummary = cache(() => fetchApi<StatsSummary>("/stats/summary"));

export const getStatsTimeseries = cache((days = 30) =>
  fetchApi<{ items: ReviewTimeseriesPoint[] }>(`/stats/timeseries?days=${days}`),
);

export const getRepositories = cache(() => fetchApi<Repository[]>("/github/repositories"));

export const getPullRequest = cache((id: string) =>
  fetchApi<PullRequest>(`/pull-requests/${encodeURIComponent(id)}`),
);

export interface GitHubRepository {
  github_id: number;
  owner: string;
  name: string;
  full_name: string;
  default_branch: string;
}

export const getAvailableGitHubRepositories = cache(() =>
  fetchApi<GitHubRepository[]>("/github/github-repositories"),
);

export interface RepositoryDetails extends Repository {
  total_pull_requests: number;
  reviewed_pull_requests: number;
  average_score: number;
  latest_pull_requests: Array<{
    id: number;
    pr_number: number;
    title: string;
    author: string;
    state: string;
  }>;
}

export const getRepositoryDetails = cache((id: string) =>
  fetchApi<RepositoryDetails>(`/github/repositories/${encodeURIComponent(id)}`),
);
