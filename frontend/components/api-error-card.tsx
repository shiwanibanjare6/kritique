"use client";

import { useRouter } from "next/navigation";
import { RefreshCw } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardTitle } from "@/components/ui/card";

export function ApiErrorCard({
  title = "Unable to load this data",
  description = "The backend may be starting up. Please try again.",
}: {
  title?: string;
  description?: string;
}) {
  const router = useRouter();

  return (
    <Card className="border-destructive/50" role="alert">
      <CardContent className="flex flex-wrap items-center justify-between gap-4 p-6">
        <div>
          <CardTitle>{title}</CardTitle>
          <CardDescription className="mt-2">{description}</CardDescription>
        </div>
        <Button variant="outline" onClick={() => router.refresh()}>
          <RefreshCw className="mr-2 h-4 w-4" />
          Retry
        </Button>
      </CardContent>
    </Card>
  );
}
