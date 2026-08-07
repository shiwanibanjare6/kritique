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
  created_at: string;
  agent_output: FileReview[];
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