"use client";

import {
  AlertTriangle,
  Info,
} from "lucide-react";

interface Props {
  line: number;
  severity: string;
  comment: string;
}

export default function ReviewComment({
  line,
  severity,
  comment,
}: Props) {

  const Icon =
    severity === "error"
      ? AlertTriangle
      : severity === "warning"
      ? AlertTriangle
      : Info;

  const bg =
    severity === "error"
      ? "border-red-400 bg-red-50"
      : severity === "warning"
      ? "border-yellow-400 bg-yellow-50"
      : "border-blue-400 bg-blue-50";

  return (

    <div
      className={`rounded-xl border-l-4 p-5 ${bg}`}
    >

      <div className="mb-3 flex items-center gap-3">

        <Icon size={18} />

        <span className="font-semibold">

          Line {line}

        </span>

        <span className="rounded-full bg-white px-3 py-1 text-xs font-bold uppercase shadow">

          {severity}

        </span>

      </div>

      <p className="leading-7 text-gray-700">

        {comment}

      </p>

    </div>

  );

}