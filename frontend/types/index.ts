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
}