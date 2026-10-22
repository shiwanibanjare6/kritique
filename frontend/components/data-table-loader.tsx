"use client";

import dynamic from "next/dynamic";
import type { PullRequestListItem } from "@/types";
import { Skeleton } from "@/components/ui/skeleton";

const DataTable = dynamic(
  () => import("@/components/data-table").then((module) => module.DataTable),
  {
    ssr: false,
    loading: () => (
      <div className="space-y-4 px-4">
        <div className="flex justify-between gap-3">
          <Skeleton className="h-10 w-40" />
          <Skeleton className="h-10 w-72" />
        </div>
        <Skeleton className="h-[420px] w-full rounded-lg" />
      </div>
    ),
  },
);

export function DataTableLoader({ pullRequests }: { pullRequests: PullRequestListItem[] }) {
  return <DataTable pullRequests={pullRequests} />;
}
