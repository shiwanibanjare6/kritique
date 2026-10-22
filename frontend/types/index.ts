export interface ReviewComment {
  line: number;
  severity: string;
  comment: string;
}

export interface FileReview {
  file: string;
  review: {
    summary: string;

    security_score: number;
    style_score: number;
    architecture_score: number;
    final_score: number;

    // NEW
    merge_recommendation: string;
    risk_level: string;
    strengths: string[];
    weaknesses: string[];

    comments: ReviewComment[];
  };
}

export interface LatestReview {
  id: number;

  summary: string;

  security_score: number;
  style_score: number;
  architecture_score: number;
  final_score: number;

  merge_recommendation: string;
  risk_level: string;
  strengths: string[];
  weaknesses: string[];

  created_at: string;

  agent_output: FileReview[];
}

export interface Repository {
  id: number;
  github_id: number;
  owner: string;
  name: string;
  full_name: string;
  default_branch: string;

  total_pull_requests?: number;
  reviewed_pull_requests?: number;
  average_score?: number;
}

export interface PullRequest {
  id: number;
  pr_number: number;
  title: string;
  author: string;
  state: string;

  base_branch: string;
  head_branch: string;

  url: string; // <-- add this

  repository: Repository;
  latest_review: LatestReview | null;
  review_status?: "pending" | "queued" | "processing" | "completed" | "failed";
}

export interface PullRequestScorePoint {
  id: number;
  prNumber: number;
  score: number;
}

export type PullRequestListItem = Pick<
  PullRequest,
  "id" | "pr_number" | "title" | "author" | "state" | "base_branch" | "head_branch" | "review_status"
> & {
  repository: Pick<Repository, "id" | "name" | "full_name" | "owner">;
  latest_review: Pick<LatestReview, "final_score" | "security_score" | "style_score" | "architecture_score" | "created_at"> | null;
};

export interface StatsSummary {
  total_repositories: number;
  total_pull_requests: number;
  reviewed_pull_requests: number;
  average_final_score: number | null;
  average_security_score: number | null;
  average_style_score: number | null;
  average_architecture_score: number | null;
  highest_final_score: number | null;
  lowest_final_score: number | null;
}

export interface ReviewTimeseriesPoint {
  date: string;
  review_count: number;
  average_score: number;
}

export type AnalyticsPullRequest = Pick<
  PullRequest,
  "id" | "pr_number" | "title" | "author"
> & {
  repository: Pick<Repository, "id" | "name" | "full_name" | "owner">;
  latest_review: Pick<LatestReview, "final_score" | "security_score" | "style_score" | "architecture_score" | "created_at"> | null;
};
