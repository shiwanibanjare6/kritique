import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import { Sparkles } from "lucide-react";

interface ReviewSummaryProps {
  summary: string;
}

export default function ReviewSummary({
  summary,
}: ReviewSummaryProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-primary" />
          AI Review Summary
        </CardTitle>
      </CardHeader>

      <CardContent>

        <div className="rounded-xl border bg-muted/30 p-6">

          <p className="whitespace-pre-line leading-8 text-muted-foreground">
            {summary}
          </p>

        </div>

      </CardContent>
    </Card>
  );
}