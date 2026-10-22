"use client";

import dynamic from "next/dynamic";
import type { PullRequestScorePoint, ReviewTimeseriesPoint } from "@/types";
import { formatScore } from "@/lib/format-score";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

const ScoreChart = dynamic(() => import("@/components/score-chart"), {
  ssr: false,
  loading: () => (
    <div className="w-full overflow-x-auto">
      <Skeleton className="h-[420px] min-w-[640px] w-full" />
    </div>
  ),
});

export function ChartAreaInteractive({
  points,
  stats,
  mode = "pull-request",
}: {
  points: PullRequestScorePoint[] | ReviewTimeseriesPoint[];
  stats?: { average: number | null; highest: number | null; lowest: number | null };
  mode?: "pull-request" | "daily";
}) {
  const scores = points.map((point) => mode === "daily"
    ? (point as ReviewTimeseriesPoint).average_score
    : (point as PullRequestScorePoint).score);
  const averageScore = stats ? stats.average : (scores.length
    ? scores.reduce((sum, score) => sum + score, 0) / scores.length
    : null);
  const highestScore = stats ? stats.highest : (scores.length ? Math.max(...scores) : null);
  const lowestScore = stats ? stats.lowest : (scores.length ? Math.min(...scores) : null);

  return (
    <Card>
      <CardHeader>
        <CardTitle>{mode === "daily" ? "Daily AI Review Score" : "Pull Request Review Scores"}</CardTitle>
        <CardDescription>
          {mode === "daily"
            ? "Average final score for reviews created each day"
            : "Final AI review score for each analyzed pull request"}
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-6">
        {points.length > 0 ? (
          <>
            <div className="grid gap-4 md:grid-cols-3">
              <div className="rounded-lg border p-4">
                <p className="text-sm text-muted-foreground">Average Score</p>
                <h2 className="mt-2 text-3xl font-bold">{averageScore === null ? "—" : formatScore(averageScore)}</h2>
              </div>
              <div className="rounded-lg border p-4">
                <p className="text-sm text-muted-foreground">Highest Score</p>
                <h2 className="mt-2 text-3xl font-bold text-green-600">{highestScore === null ? "—" : formatScore(highestScore)}</h2>
              </div>
              <div className="rounded-lg border p-4">
                <p className="text-sm text-muted-foreground">Lowest Score</p>
                <h2 className="mt-2 text-3xl font-bold text-red-600">{lowestScore === null ? "—" : formatScore(lowestScore)}</h2>
              </div>
            </div>
            <ScoreChart points={points} mode={mode} />
          </>
        ) : <div className="flex h-[300px] items-center justify-center text-muted-foreground">No review history found.</div>}
      </CardContent>
    </Card>
  );
}
