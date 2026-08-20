import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import {
  Sparkles,
  ShieldCheck,
  CircleCheckBig,
  TriangleAlert,
} from "lucide-react";

interface ReviewSummaryProps {
  summary: string;
  strengths?: string[];
  weaknesses?: string[];
  riskLevel?: string;
  mergeRecommendation?: string;
}

export default function ReviewSummary({
  summary,
  strengths = [],
  weaknesses = [],
  riskLevel = "Unknown",
  mergeRecommendation = "Not available",
}: ReviewSummaryProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-primary" />
          AI Review Summary
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-6">

        {/* Overall Summary */}
        <div className="rounded-xl border bg-muted/30 p-6">
          <p className="whitespace-pre-line leading-8 text-muted-foreground">
            {summary}
          </p>
        </div>

        {/* Strengths & Weaknesses */}
        <div className="grid gap-4 md:grid-cols-2">

          <div className="rounded-xl border p-5">
            <div className="mb-3 flex items-center gap-2">
              <CircleCheckBig className="h-5 w-5 text-green-500" />
              <h3 className="font-semibold">Strengths</h3>
            </div>

            {strengths.length > 0 ? (
              <ul className="space-y-2 text-sm text-muted-foreground">
                {strengths.map((item, index) => (
                  <li key={index}>• {item}</li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-muted-foreground">
                No strengths provided.
              </p>
            )}
          </div>

          <div className="rounded-xl border p-5">
            <div className="mb-3 flex items-center gap-2">
              <TriangleAlert className="h-5 w-5 text-yellow-500" />
              <h3 className="font-semibold">Weaknesses</h3>
            </div>

            {weaknesses.length > 0 ? (
              <ul className="space-y-2 text-sm text-muted-foreground">
                {weaknesses.map((item, index) => (
                  <li key={index}>• {item}</li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-muted-foreground">
                No weaknesses identified.
              </p>
            )}
          </div>

        </div>

        {/* Recommendation */}
        <div className="grid gap-4 md:grid-cols-2">

          <div className="rounded-xl border p-5">
            <div className="mb-2 flex items-center gap-2">
              <ShieldCheck className="h-5 w-5 text-blue-500" />
              <h3 className="font-semibold">Risk Level</h3>
            </div>

            <p className="text-sm text-muted-foreground">
              {riskLevel}
            </p>
          </div>

          <div className="rounded-xl border p-5">
            <div className="mb-2 flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              <h3 className="font-semibold">Recommendation</h3>
            </div>

            <p className="text-sm text-muted-foreground">
              {mergeRecommendation}
            </p>
          </div>

        </div>

      </CardContent>
    </Card>
  );
}