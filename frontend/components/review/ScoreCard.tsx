import { Card, CardContent } from "@/components/ui/card";

interface ScoreCardProps {
  title: string;
  score: number;
  color?: string;
}

import { Progress } from "@/components/ui/progress";

export default function ScoreCard({
  title,
  score,
  color = "text-primary",
}: ScoreCardProps) {
  return (
    <Card>
      <CardContent className="p-6">
        <p className="text-sm font-medium uppercase tracking-wide text-muted-foreground">
  {title}
</p>

        <h2 className={`mt-3 text-4xl font-bold ${color}`}>
          {score}
        </h2>

  <Progress
    value={score}
    className={`mt-4 ${
      score >= 90
        ? "[&>div]:bg-green-500"
        : score >= 75
        ? "[&>div]:bg-yellow-500"
        : "[&>div]:bg-red-500"
    }`}
/>

<div className="mt-2">

  <p className="text-xs text-muted-foreground">
    {score}/100
  </p>

  <p className="mt-1 text-sm font-medium">
  {score >= 90
    ? "✅ Excellent Code Quality"
    : score >= 75
    ? "🟡 Good With Minor Improvements"
    : score >= 60
    ? "🟠 Needs Improvement"
    : "🔴 Major Improvements Needed"}
</p>

</div>

      </CardContent>
    </Card>
  );
}