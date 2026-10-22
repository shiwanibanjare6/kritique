"use client";

import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  XAxis,
  YAxis,
} from "recharts";

import type { PullRequestScorePoint, ReviewTimeseriesPoint } from "@/types";
import { formatScore } from "@/lib/format-score";
import {
  ChartContainer,
  ChartTooltip,
  type ChartConfig,
} from "@/components/ui/chart";

const dailyChartConfig = {
  average_score: {
    label: "Average AI Score",
    color: "var(--primary)",
  },
} satisfies ChartConfig;

const pullRequestChartConfig = {
  score: { label: "AI Score", color: "var(--primary)" },
} satisfies ChartConfig;

export default function ScoreChart({
  points,
  mode = "pull-request",
}: {
  points: PullRequestScorePoint[] | ReviewTimeseriesPoint[];
  mode?: "pull-request" | "daily";
}) {
  const isDaily = mode === "daily";
  const dailyData = (points as ReviewTimeseriesPoint[]).map((point) => ({
    date: point.date,
    average_score: point.average_score,
    review_count: point.review_count,
  }));
  const pullRequestData = (points as PullRequestScorePoint[]).map((point) => ({
    pr: `PR #${point.prNumber}`,
    score: point.score,
  }));
  const chartWidth = isDaily
    ? Math.max(640, Math.min(1440, points.length * 28))
    : Math.max(640, points.length * 64);

  return (
    <div className="w-full overflow-x-auto">
      <div style={{ width: chartWidth, height: 420 }}>
        <ChartContainer
          config={isDaily ? dailyChartConfig : pullRequestChartConfig}
          className="h-full w-full"
        >
          {isDaily ? (
            <AreaChart data={dailyData} margin={{ top: 24, right: 20, left: 10, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                interval="preserveStartEnd"
                minTickGap={20}
                tickLine={false}
                axisLine={false}
                tickFormatter={(value: string) =>
                  new Date(`${value}T00:00:00`).toLocaleDateString("en", {
                    month: "short",
                    day: "numeric",
                  })
                }
              />
              <YAxis
                domain={[0, 100]}
                tickFormatter={(value: number) => formatScore(value)}
                tickLine={false}
                axisLine={false}
              />
              <ChartTooltip
                cursor={false}
                content={({ active, payload, label }) => active && payload?.length ? (
                  <div className="rounded-lg border bg-background p-3 text-sm shadow-xl">
                    <p className="font-medium">
                      {new Date(`${String(label)}T00:00:00`).toLocaleDateString("en", {
                        month: "short",
                        day: "numeric",
                        year: "numeric",
                      })}
                    </p>
                    <p className="text-muted-foreground">
                      Average score: {formatScore(Number(payload[0].value))}
                    </p>
                    <p className="text-muted-foreground">
                      Reviews: {Number(payload[0].payload.review_count)}
                    </p>
                  </div>
                ) : null}
              />
              <Area
                dataKey="average_score"
                type="monotone"
                stroke="var(--primary)"
                strokeWidth={2}
                fill="var(--primary)"
                fillOpacity={0.18}
                connectNulls={false}
                dot={false}
              />
            </AreaChart>
          ) : (
            <BarChart data={pullRequestData} margin={{ top: 24, right: 20, left: 10, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="pr" interval={0} tickLine={false} axisLine={false} />
              <YAxis
                domain={[0, 100]}
                tickFormatter={(value: number) => formatScore(value)}
                tickLine={false}
                axisLine={false}
              />
              <ChartTooltip
                cursor={false}
                content={({ active, payload, label }) => active && payload?.length ? (
                  <div className="rounded-lg border bg-background p-3 text-sm shadow-xl">
                    <p className="font-medium">{String(label)}</p>
                    <p className="text-muted-foreground">
                      Score: {formatScore(Number(payload[0].value))}
                    </p>
                  </div>
                ) : null}
              />
              <Bar
                dataKey="score"
                barSize={44}
                radius={[10, 10, 0, 0]}
                fill="var(--primary)"
                label={{
                  position: "top",
                  fill: "currentColor",
                  fontSize: 12,
                  formatter: (value) => formatScore(Number(value)),
                }}
              />
            </BarChart>
          )}
        </ChartContainer>
      </div>
    </div>
  );
}
