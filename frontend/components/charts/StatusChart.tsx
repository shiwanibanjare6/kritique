"use client";

import {
  PieChart,
  Pie,
  ResponsiveContainer,
  Tooltip,
  Cell,
} from "recharts";

import { PullRequest } from "@/types/pullRequest";

interface Props {
  prs: PullRequest[];
}

export default function StatusChart({
  prs,
}: Props) {

  const open = prs.filter(
    (p) => p.state === "open"
  ).length;

  const closed = prs.filter(
    (p) => p.state === "closed"
  ).length;

  const data = [
    {
      name: "Open",
      value: open,
    },
    {
      name: "Closed",
      value: closed,
    },
  ];

  return (

    <div className="rounded-2xl bg-white p-6 shadow-lg">

      <h2 className="mb-6 text-2xl font-bold">

        Pull Request Status

      </h2>

      <div style={{ width: "100%", height: 350 }}>

        <ResponsiveContainer>

          <PieChart>

            <Pie
              data={data}
              dataKey="value"
              label
              outerRadius={110}
            >

              <Cell fill="#22c55e" />

              <Cell fill="#ef4444" />

            </Pie>

            <Tooltip />

          </PieChart>

        </ResponsiveContainer>

      </div>

    </div>

  );

}