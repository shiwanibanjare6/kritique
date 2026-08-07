import Link from "next/link";

import { ArrowRight } from "lucide-react";

import { SiteHeader } from "@/components/site-header";
import { SectionCards } from "@/components/section-cards";
import { ChartAreaInteractive } from "@/components/chart-area-interactive";

import { Button } from "@/components/ui/button";

export default function DashboardPage() {
  return (
    <>
      <SiteHeader />

      <main className="flex flex-1 flex-col">
        <div className="@container/main flex flex-1 flex-col gap-8 py-6">
          <section className="px-4 lg:px-6">
            <div className="flex flex-wrap gap-3">
              <Link href="/repositories">
                <Button>Repositories</Button>
              </Link>

              <Link href="/analytics">
                <Button variant="secondary">Analytics</Button>
              </Link>
            </div>
          </section>

          <section className="px-4 lg:px-6">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>

              <p className="mt-2 text-muted-foreground">
                Monitor your repositories, AI code reviews and pull request quality in one place.
              </p>
            </div>
          </section>

          <SectionCards />

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
                  View Analytics
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>

            <ChartAreaInteractive />
          </section>
        </div>
      </main>
    </>
  );
}