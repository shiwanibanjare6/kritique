import { Skeleton } from "@/components/ui/skeleton";
import { SlowHint } from "@/components/slow-hint";

export function ProtectedPageLoading({ showHeading = true }: { showHeading?: boolean }) {
  return (
    <div className="flex flex-1 flex-col gap-8 p-6" aria-busy="true" aria-label="Loading page">
      {showHeading && <div className="space-y-3">
        <Skeleton className="h-9 w-56" />
        <Skeleton className="h-4 w-96 max-w-full" />
      </div>}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }, (_, index) => (
          <Skeleton key={index} className="h-32 rounded-xl" />
        ))}
      </div>
      <Skeleton className="h-72 rounded-xl" />
      <div className="min-h-5"><SlowHint /></div>
    </div>
  );
}
