"use client";

import { ChevronDown, FileCode2 } from "lucide-react";
import { useState } from "react";

import ReviewComment from "./ReviewComment";

interface Comment {
  line: number;
  severity: string;
  comment: string;
}

interface Review {
  summary: string;
  comments: Comment[];
}

interface Props {
  file: string;
  review: Review;
}

export default function FileReview({
  file,
  review,
}: Props) {

  const [open, setOpen] = useState(true);

  return (

    <div className="overflow-hidden rounded-2xl bg-white shadow-lg">

      <button
        onClick={() => setOpen(!open)}
        className="flex w-full items-center justify-between bg-slate-900 px-6 py-5 text-left text-white"
      >

        <div className="flex items-center gap-3">

          <FileCode2 />

          <span className="font-semibold">

            {file}

          </span>

        </div>

        <ChevronDown
          className={`transition ${
            open ? "rotate-180" : ""
          }`}
        />

      </button>

      {open && (

        <div className="space-y-6 p-6">

          <div>

            <h3 className="mb-2 font-semibold">

              AI Summary

            </h3>

            <p className="leading-7 text-gray-600">

              {review.summary}

            </p>

          </div>

          <div className="space-y-4">

            {review.comments.length === 0 ? (

              <div className="rounded-xl border border-green-300 bg-green-50 p-4 text-green-700">

                No issues detected.

              </div>

            ) : (

              review.comments.map((comment, index) => (

                <ReviewComment
                  key={index}
                  {...comment}
                />

              ))

            )}

          </div>

        </div>

      )}

    </div>

  );

}