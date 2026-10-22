import { Suspense } from "react";
import Link from "next/link";
import { ArrowRight } from "lucide-react";

import { SiteHeader } from "@/components/site-header";
import { SectionCards } from "@/components/section-cards";
import { ChartAreaInteractive } from "@/components/chart-area-interactive";
import { ApiErrorCard } from "@/components/api-error-card";
import { SlowHint } from "@/components/slow-hint";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { getStatsSummary, getStatsTimeseries } from "@/lib/api-server";
import type { ReviewTimeseriesPoint } from "@/types";

export const maxDuration = 60;

export default function DashboardPage() {
  return (
    <>
      <SiteHeader />
      <main className="flex flex-1 flex-col">
        <div className="@container/main flex flex-1 flex-col gap-8 py-6">
          <section className="px-4 lg:px-6">
            <div className="flex flex-wrap gap-3">
              <Link href="/repositories"><Button>Repositories</Button></Link>
              <Link href="/analytics"><Button variant="secondary">Analytics</Button></Link>
            </div>
          </section>
          <section className="px-4 lg:px-6">
            <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
            <p className="mt-2 text-muted-foreground">
              Monitor your repositories, AI code reviews and pull request quality in one place.
            </p>
          </section>

          <Suspense fallback={<CardsSkeleton />}>
            <DashboardCards />
          </Suspense>

          <section className="space-y-4 px-4 lg:px-6">
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
              <div>
                <h2 className="text-2xl font-bold">AI Review Analytics</h2>
                <p className="text-muted-foreground">
                  Performance overview across all reviewed pull requests.
                </p>
              </div>
              <Link href="/analytics">
                <Button variant="outline">
                  View Analytics <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>
            <Suspense fallback={<ChartSkeleton />}>
              <DashboardChart />
            </Suspense>
          </section>
        </div>
      </main>
    </>
  );
}

async function DashboardCards() {
  let stats: { repositories: number; pullRequests: number; reviews: number; averageScore: number | null } | null = null;
  let failed = false;
  try {
    const summary = await getStatsSummary();
    stats = {
      repositories: summary.total_repositories,
      pullRequests: summary.total_pull_requests,
      reviews: summary.reviewed_pull_requests,
      averageScore: summary.average_final_score,
    };
  } catch {
    failed = true;
  }
  if (failed || !stats) return <section className="px-4 lg:px-6"><ApiErrorCard title="Unable to load dashboard statistics" /></section>;
  return <SectionCards stats={stats} />;
}

async function DashboardChart() {
  let points: ReviewTimeseriesPoint[] = [];
  let stats: { average: number | null; highest: number | null; lowest: number | null } | null = null;
  let failed = false;
  try {
    const [summary, timeseries] = await Promise.all([
      getStatsSummary(),
      getStatsTimeseries(30),
    ]);
    points = timeseries.items;
    stats = {
      average: summary.average_final_score,
      highest: summary.highest_final_score,
      lowest: summary.lowest_final_score,
    };
  } catch {
    failed = true;
  }
  if (failed || !stats) return <ApiErrorCard title="Unable to load review scores" />;
  return <ChartAreaInteractive points={points} stats={stats} mode="daily" />;
}

function CardsSkeleton() {
  return (
    <div className="grid gap-4 px-4 md:grid-cols-2 xl:grid-cols-4 lg:px-6" aria-busy="true">
      {Array.from({ length: 4 }, (_, index) => <Skeleton key={index} className="h-32 rounded-xl" />)}
      <div className="col-span-full min-h-5"><SlowHint /></div>
    </div>
  );
}

function ChartSkeleton() {
  return (
    <div className="space-y-4" aria-busy="true">
      <Skeleton className="h-[520px] rounded-xl" />
      <div className="min-h-5"><SlowHint /></div>
    </div>
  );
}
