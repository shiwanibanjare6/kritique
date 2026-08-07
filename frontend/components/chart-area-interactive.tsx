"use client";

import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  XAxis,
  YAxis,
} from "recharts";



import api from "@/services/api";
import type { PullRequest } from "@/types";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart";

interface ChartData {
  pr: string;
  score: number;
}

const chartConfig = {
  score: {
    label: "AI Score",
    color: "var(--primary)",
  },
} satisfies ChartConfig;



export function ChartAreaInteractive() {
  const [chartData, setChartData] = useState<ChartData[]>([]);
  const [loading, setLoading] = useState(true);

  const averageScore =
  chartData.length > 0
    ? Math.round(
        chartData.reduce((sum, item) => sum + item.score, 0) /
          chartData.length
      )
    : 0;

const highestScore =
  chartData.length > 0
    ? Math.max(...chartData.map((item) => item.score))
    : 0;

const lowestScore =
  chartData.length > 0
    ? Math.min(...chartData.map((item) => item.score))
    : 0;

  useEffect(() => {
    async function loadChart() {
      try {
        const response = await api.get<PullRequest[]>("/pull-requests");

        const data = response.data
          .filter((pr) => pr.latest_review)
          .map((pr) => ({
            pr: `PR #${pr.pr_number}`,
            score: pr.latest_review!.final_score,
          }));

        setChartData(data);
      } catch (error) {
        console.error("Failed to load chart:", error);
      } finally {
        setLoading(false);
      }
    }

    loadChart();
  }, []);

  return (
    <Card>
      <CardHeader>
        <CardTitle>AI Review Scores</CardTitle>

        <CardDescription>
          Review score for each analyzed pull request
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-6">
  {loading ? (
    <div className="flex h-[300px] items-center justify-center text-muted-foreground">
      Loading chart...
    </div>
  ) : chartData.length === 0 ? (
    <div className="flex h-[300px] items-center justify-center text-muted-foreground">
      No reviewed pull requests found.
    </div>
  ) : (
    <>
      {/* Statistics */}
      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-lg border p-4">
          <p className="text-sm text-muted-foreground">
            Average Score
          </p>

          <h2 className="mt-2 text-3xl font-bold">
            {averageScore}
          </h2>
        </div>

        <div className="rounded-lg border p-4">
          <p className="text-sm text-muted-foreground">
            Highest Score
          </p>

          <h2 className="mt-2 text-3xl font-bold text-green-600">
            {highestScore}
          </h2>
        </div>

        <div className="rounded-lg border p-4">
          <p className="text-sm text-muted-foreground">
            Lowest Score
          </p>

          <h2 className="mt-2 text-3xl font-bold text-red-600">
            {lowestScore}
          </h2>
        </div>
      </div>

      {/* Chart */}
      {/* Chart */}
      <ChartContainer
        config={chartConfig}
        className="h-[420px] w-full"
      >
        <BarChart
          data={chartData}
          margin={{
            top: 20,
            right: 20,
            left: 10,
            bottom: 20,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" />

          <XAxis
            dataKey="pr"
            tickLine={false}
            axisLine={false}
          />

          <YAxis
            domain={[0, 100]}
            padding={{top: 20}}
            tickLine={false}
            axisLine={false}
          />

          <ChartTooltip
            cursor={false}
            content={<ChartTooltipContent />}
          />

          <Bar
  dataKey="score"
  radius={[10, 10, 0, 0]}
  fill="var(--primary)"
  label={{
    position: "top",
    fill: "currentColor",
    fontSize: 12,
  }}
/>
        </BarChart>
      </ChartContainer>
    </>
  )}
</CardContent>
    </Card>
  );
}