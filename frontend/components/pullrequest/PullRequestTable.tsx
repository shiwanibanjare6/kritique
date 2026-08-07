"use client";

import { PullRequest } from "@/types/pullRequest";
import PullRequestRow from "./PullRequestRow";

interface Props {
  prs: PullRequest[];
}

export default function PullRequestTable({ prs }: Props) {
  if (prs.length === 0) {
    return (
      <div className="rounded-2xl bg-white p-16 text-center shadow">
        <h2 className="text-3xl font-bold">
          No Pull Requests Found
        </h2>

        <p className="mt-4 text-gray-500">
          Try changing the search or filters.
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-2xl bg-white shadow-lg">

      <table className="w-full">

        <thead className="border-b bg-slate-100">

          <tr>

            <th className="px-6 py-5 text-left">PR</th>

            <th className="px-6 py-5 text-left">Title</th>

            <th className="px-6 py-5 text-left">Repository</th>

            <th className="px-6 py-5 text-left">Author</th>

            <th className="px-6 py-5 text-left">Status</th>

            <th className="px-6 py-5 text-left">Score</th>

            <th className="px-6 py-5 text-center">
              Action
            </th>

          </tr>

        </thead>

        <tbody>

          {prs.map((pr) => (
            <PullRequestRow
              key={pr.id}
              pr={pr}
            />
          ))}

        </tbody>

      </table>

    </div>
  );
}