"use client";

import { useEffect, useState } from "react";
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

import api from "@/services/api";
import type { PullRequest } from "@/types";

export function SectionCards() {
  const [pullRequests, setPullRequests] = useState<PullRequest[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const response = await api.get<PullRequest[]>("/pull-requests");
        setPullRequests(response.data);
      } catch (error) {
        console.error("Failed to load dashboard:", error);
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);

  const totalRepositories = new Set(
    pullRequests.map((pr) => pr.repository.id)
  ).size;

  const totalPullRequests = pullRequests.length;

  const totalReviews = pullRequests.filter(
    (pr) => pr.latest_review !== null
  ).length;

  const averageScore =
    totalReviews === 0
      ? 0
      : Math.round(
          pullRequests
            .filter((pr) => pr.latest_review)
            .reduce(
              (sum, pr) => sum + pr.latest_review!.final_score,
              0
            ) / totalReviews
        );

  const cards = [
    {
      title: "Repositories",
      value: totalRepositories,
      description: "Connected GitHub repositories",
      icon: GitBranch,
    },
    {
      title: "Pull Requests",
      value: totalPullRequests,
      description: "Tracked pull requests",
      icon: GitPullRequest,
    },
    {
      title: "AI Reviews",
      value: totalReviews,
      description: "Completed AI code reviews",
      icon: Bot,
    },
    {
      title: "Average Score",
      value: `${averageScore}/100`,
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
                  {loading ? "--" : card.value}
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