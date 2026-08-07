"use client";

import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  Tooltip,
  CartesianGrid,
  YAxis,
} from "recharts";

import { PullRequest } from "@/types/pullRequest";

interface Props {
  prs: PullRequest[];
}

export default function ScoreChart({
  prs,
}: Props) {

  const data = prs
    .filter((p) => p.latest_review)
    .map((p) => ({
      name: `PR ${p.pr_number}`,
      score: p.latest_review!.final_score,
    }));

  return (

    <div className="rounded-2xl bg-white p-6 shadow-lg">

      <h2 className="mb-6 text-2xl font-bold">

        AI Review Scores

      </h2>

      <div style={{ width: "100%", height: 350 }}>

        <ResponsiveContainer>

          <BarChart data={data}>

            <CartesianGrid strokeDasharray="4 4" />

            <XAxis dataKey="name" />

            <YAxis domain={[0, 100]} />

            <Tooltip />

            <Bar
              dataKey="score"
              radius={[8, 8, 0, 0]}
            />

          </BarChart>

        </ResponsiveContainer>

      </div>

    </div>

  );

}