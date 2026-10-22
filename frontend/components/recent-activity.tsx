import Link from "next/link";
import {
  CheckCircle2,
  Clock3,
  ArrowRight,
} from "lucide-react";

import type { PullRequest } from "@/types";
import { formatScore } from "@/lib/format-score";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import { Button } from "@/components/ui/button";

export function RecentActivity({ pullRequests }: { pullRequests: PullRequest[] }) {

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>
          Recent Activity
        </CardTitle>

        <Button
          variant="ghost"
          asChild
        >
          <Link href="/pull-requests">
            View All

            <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
        </Button>
      </CardHeader>

      <CardContent>

        {pullRequests.length === 0 && (
          <p className="text-muted-foreground">
            No pull requests found.
          </p>
        )}

        <div className="space-y-4">

          {pullRequests.map((pr) => (

            <Link
              key={pr.id}
              href={`/pull-requests/${pr.id}`}
            >
              <div className="flex items-center justify-between rounded-lg border p-4 transition hover:bg-muted">

                <div>

                  <h3 className="font-medium">
                    PR #{pr.pr_number} · {pr.title}
                  </h3>

                  <p className="text-sm text-muted-foreground">
                    {pr.repository.name}
                  </p>

                </div>

                {pr.latest_review ? (

                  <div className="flex items-center gap-2 text-green-600">

                    <CheckCircle2 className="h-5 w-5" />

                    <span className="font-semibold">
                      {formatScore(pr.latest_review.final_score)}/100
                    </span>

                  </div>

                ) : (

                  <div className="flex items-center gap-2 text-yellow-500">

                    <Clock3 className="h-5 w-5" />

                    <span>
                      Waiting
                    </span>

                  </div>

                )}

              </div>
            </Link>

          ))}

        </div>

      </CardContent>
    </Card>
  );
}
