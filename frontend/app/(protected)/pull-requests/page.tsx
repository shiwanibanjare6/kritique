import { SiteHeader } from "@/components/site-header";
import { DataTable } from "@/components/data-table";

export default function PullRequestsPage() {
  return (
    <>
      <SiteHeader />

      <main className="flex flex-1 flex-col">
        <div className="space-y-8 p-6">

          <div>
            <h1 className="text-3xl font-bold">
              Pull Requests
            </h1>

            <p className="text-muted-foreground mt-2">
              Browse all pull requests reviewed by Kritique.ai.
            </p>
          </div>

          <DataTable />

        </div>
      </main>
    </>
  );
}