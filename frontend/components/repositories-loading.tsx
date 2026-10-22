import { Skeleton } from "@/components/ui/skeleton";
import { SlowHint } from "@/components/slow-hint";

export function RepositoriesLoading({ includeHeader = false }: { includeHeader?: boolean }) {
  return (
    <div className="space-y-6" aria-busy="true" aria-label="Loading repositories">
      {includeHeader && (
        <div className="flex items-center justify-between gap-4">
          <div className="space-y-2">
            <Skeleton className="h-10 w-64" />
            <Skeleton className="h-4 w-72 max-w-full" />
          </div>
          <Skeleton className="h-10 w-44" />
        </div>
      )}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 3 }, (_, index) => (
          <div key={index} className="space-y-4 rounded-xl border p-6">
            <div className="flex h-10 items-center gap-3">
              <Skeleton className="h-10 w-10 shrink-0 rounded-xl" />
              <div className="space-y-2">
                <Skeleton className="h-4 w-32" />
                <Skeleton className="h-3 w-24" />
              </div>
            </div>
            <div className="space-y-2 py-1">
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-4 w-2/3" />
            </div>
            <div className="flex h-9 gap-2">
              <Skeleton className="h-9 w-20" />
              <Skeleton className="h-9 w-24" />
            </div>
          </div>
        ))}
      </div>
      <div className="min-h-5"><SlowHint /></div>
    </div>
  );
}
