"use client";

import Link from "next/link";

import {
  ArrowRight,
  CheckCircle2,
  Clock3,
} from "lucide-react";

import { PullRequest } from "@/types/pullRequest";

interface Props {
  pr: PullRequest;
}

export default function PullRequestRow({
  pr,
}: Props) {

  const score = pr.latest_review?.final_score ?? 0;

  const scoreClass =
    score >= 90
      ? "bg-green-100 text-green-700"
      : score >= 70
      ? "bg-yellow-100 text-yellow-700"
      : "bg-red-100 text-red-700";

  return (

    <tr className="border-b transition hover:bg-slate-50">

      <td className="px-6 py-6 font-bold">

        #{pr.pr_number}

      </td>

      <td className="px-6 py-6">

        <div className="font-semibold">

          {pr.title}

        </div>

        <div className="mt-1 text-sm text-gray-500">

          {pr.base_branch}

          {" ← "}

          {pr.head_branch}

        </div>

      </td>

      <td className="px-6 py-6">

        {pr.repository.full_name}

      </td>

      <td className="px-6 py-6">

        {pr.author}

      </td>

      <td className="px-6 py-6">

        {pr.state === "open" ? (

          <span className="flex items-center gap-2 text-green-600">

            <Clock3 size={18} />

            OPEN

          </span>

        ) : (

          <span className="flex items-center gap-2 text-red-600">

            <CheckCircle2 size={18} />

            CLOSED

          </span>

        )}

      </td>

      <td className="px-6 py-6">

        {pr.latest_review ? (

          <span
            className={`rounded-full px-3 py-2 text-sm font-bold ${scoreClass}`}
          >

            {score}

          </span>

        ) : (

          <span className="text-gray-400">

            --

          </span>

        )}

      </td>

      <td className="px-6 py-6 text-center">

        <Link
          href={`/pull-requests/${pr.id}`}
          className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-white transition hover:bg-blue-700"
        >

          Review

          <ArrowRight size={18} />

        </Link>

      </td>

    </tr>

  );

}