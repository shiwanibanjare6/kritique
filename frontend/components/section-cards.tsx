import {
  Bot,
  GitBranch,
  GitPullRequest,
  Star,
} from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import { formatScore } from "@/lib/format-score";

export function SectionCards({ stats }: { stats: {
  repositories: number;
  pullRequests: number;
  reviews: number;
  averageScore: number | null;
} }) {

  const cards = [
    {
      title: "Repositories",
      value: stats.repositories,
      description: "Connected GitHub repositories",
      icon: GitBranch,
    },
    {
      title: "Pull Requests",
      value: stats.pullRequests,
      description: "Tracked pull requests",
      icon: GitPullRequest,
    },
    {
      title: "AI Reviews",
      value: stats.reviews,
      description: "Completed AI code reviews",
      icon: Bot,
    },
    {
      title: "Average Score",
      value: stats.averageScore === null ? "—" : `${formatScore(stats.averageScore)}/100`,
      description: "Overall AI review score",
      icon: Star,
    },
  ];

  return (
    <div className="grid gap-4 px-4 md:grid-cols-2 xl:grid-cols-4 lg:px-6">
      {cards.map((card) => {
        const Icon = card.icon;

        return (
          <Card
            key={card.title}
            className="bg-gradient-to-t from-primary/5 to-card shadow-xs"
          >
            <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-2">
              <div>
                <CardDescription>{card.title}</CardDescription>

                <CardTitle className="mt-2 text-3xl font-bold">
                  {card.value}
                </CardTitle>
              </div>

              <div className="rounded-lg bg-primary/10 p-3">
                <Icon className="h-6 w-6 text-primary" />
              </div>
            </CardHeader>

            <CardContent>
              <p className="text-sm text-muted-foreground">
                {card.description}
              </p>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
