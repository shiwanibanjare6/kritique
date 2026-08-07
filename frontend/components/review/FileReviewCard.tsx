import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import { Badge } from "@/components/ui/badge";

import {
  FileCode2,
  AlertTriangle,
  AlertCircle,
  CheckCircle2,
} from "lucide-react";

import type { FileReview } from "@/types";

interface Props {
  review: FileReview;
}

function getSeverityIcon(severity: string) {
  switch (severity.toLowerCase()) {
    case "high":
      return <AlertCircle className="h-4 w-4 text-red-500" />;

    case "medium":
      return <AlertTriangle className="h-4 w-4 text-yellow-500" />;

    default:
      return <CheckCircle2 className="h-4 w-4 text-green-500" />;
  }
}

export default function FileReviewCard({
  review,
}: Props) {
  return (
    <Card>

      <CardHeader>

        <CardTitle className="flex items-center gap-2">

          <FileCode2 className="h-5 w-5" />

          {review.file}

        </CardTitle>

      </CardHeader>

      <CardContent className="space-y-6">

        <div>

   <h3 className="flex items-center gap-2 text-lg font-semibold">
  📋 Summary
</h3>

          <div className="rounded-lg border bg-muted/30 p-4">
  <p className="whitespace-pre-line leading-7 text-muted-foreground">
    {review.review.summary}
  </p>
</div>

        </div>

        <div className="space-y-4">

          <h3 className="flex items-center gap-2 text-lg font-semibold">
  💡 AI Suggestions
</h3>

          {review.review.comments.length === 0 ? (
            <p className="text-muted-foreground">
              No issues detected. The AI did not find any improvements for this file.
            </p>
          ) : (
            review.review.comments.map((comment, index) => (
              <div
                key={index}
                className={`rounded-lg border p-4 ${
  comment.severity === "high"
    ? "border-red-500/30"
    : comment.severity === "medium"
    ? "border-yellow-500/30"
    : "border-green-500/30"
}`}
              >
                <div className="flex items-center justify-between">

                  <div className="flex items-center gap-2">

                    {getSeverityIcon(comment.severity)}

                    <span className="font-medium">
                      Line {comment.line}
                    </span>

                  </div>

                  <Badge
  variant="outline"
  className="capitalize"
>
                    {comment.severity}
                  </Badge>

                </div>

                <p className="mt-3 leading-7 text-muted-foreground">
  {comment.comment}
</p>

              </div>
            ))
          )}

        </div>

      </CardContent>

    </Card>
  );
}