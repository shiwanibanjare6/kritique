import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle2, AlertTriangle, XCircle } from "lucide-react";

interface Props {
  recommendation: string;
  risk: string;
  strengths: string[];
  weaknesses: string[];
}

export default function MergeRecommendation({
  recommendation,
  risk,
  strengths,
  weaknesses,
}: Props) {
  let Icon = CheckCircle2;
  let color = "text-green-500";

  if (recommendation.toLowerCase().includes("minor")) {
    Icon = AlertTriangle;
    color = "text-yellow-500";
  } else if (
    recommendation.toLowerCase().includes("required") ||
    recommendation.toLowerCase().includes("reject")
  ) {
    Icon = XCircle;
    color = "text-red-500";
  }

  return (
    <Card className="mb-8">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Icon className={`h-6 w-6 ${color}`} />
          AI Merge Recommendation
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-6">
        <div>
          <h2 className={`text-2xl font-bold ${color}`}>
            {recommendation}
          </h2>

          <p className="mt-2 text-muted-foreground">
            Risk Level:
            <span className="ml-2 font-semibold text-foreground">
              {risk}
            </span>
          </p>
        </div>

        <div>
          <h3 className="font-semibold">
            ✅ Strengths
          </h3>

          {strengths.length === 0 ? (
            <p className="mt-2 text-muted-foreground">
              No strengths provided.
            </p>
          ) : (
            <ul className="mt-2 list-disc space-y-1 pl-5 text-muted-foreground">
              {strengths.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          )}
        </div>

        <div>
          <h3 className="font-semibold">
            ⚠ Improvements
          </h3>

          {weaknesses.length === 0 ? (
            <p className="mt-2 text-muted-foreground">
              No improvements suggested.
            </p>
          ) : (
            <ul className="mt-2 list-disc space-y-1 pl-5 text-muted-foreground">
              {weaknesses.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          )}
        </div>
      </CardContent>
    </Card>
  );
}