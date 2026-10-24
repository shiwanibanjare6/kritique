export interface ReviewComment {
  line: number | null;
  severity: string;
  comment: string;
}

export interface FileReview {
  file: string;
  review: {
    summary: string;
    status?: "reviewed" | "skipped" | "failed";
    reason?: string;
    truncated?: boolean;
    security_score?: number;
    style_score?: number;
    architecture_score?: number;
    final_score?: number;
    merge_recommendation?: string;
    risk_level?: string;
    strengths?: string[];
    weaknesses?: string[];
    comments: ReviewComment[];
    agent_results?: Array<Record<string, unknown>>;
  };
}

export interface LatestReview {
  id: number;
  summary: string;
  security_score: number;
  style_score: number;
  architecture_score: number;
  final_score: number;
  created_at: string;
  agent_output: FileReview[];
  pipeline_metrics?: Array<Record<string, unknown>> | null;
  duration_ms?: number | null;
  files_reviewed?: number | null;
  files_skipped?: number | null;
  files_failed?: number | null;
  summary_source?: string | null;
}

export interface Repository {
  id: number;
  name: string;
  full_name: string;
  owner: string;
}

export interface PullRequest {
  id: number;
  pr_number: number;
  title: string;
  author: string;
  state: string;
  base_branch: string;
  head_branch: string;
  repository: Repository;
  latest_review: LatestReview | null;
}
