"use client";

import { usePathname } from "next/navigation";

import { Separator } from "@/components/ui/separator";
import { SidebarTrigger } from "@/components/ui/sidebar";

const pageTitles: Record<string, { title: string; subtitle: string }> = {
  "/": {
    title: "Dashboard",
    subtitle: "Overview of your AI code reviews",
  },
  "/repositories": {
    title: "Repositories",
    subtitle: "Manage connected GitHub repositories",
  },
  "/pull-requests": {
    title: "Pull Requests",
    subtitle: "Browse and review pull requests",
  },
  "/analytics": {
    title: "Analytics",
    subtitle: "Insights into AI review performance",
  },
  "/settings": {
    title: "Settings",
    subtitle: "Manage your Kritique.ai preferences",
  },
  "/help": {
    title: "Help",
    subtitle: "Documentation and support",
  },
};

export function SiteHeader() {
  const pathname = usePathname();

  const page =
    pageTitles[pathname] ?? {
      title: "Kritique.ai",
      subtitle: "AI Code Review Platform",
    };

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center border-b bg-background/95 backdrop-blur">
      <div className="flex w-full items-center justify-between px-6">
        <div className="flex items-center gap-4">
          <SidebarTrigger />

          <Separator
            orientation="vertical"
            className="h-6"
          />

          <div>
            <h1 className="text-xl font-bold tracking-tight">
              {page.title}
            </h1>

            <p className="text-sm text-muted-foreground">
              {page.subtitle}
            </p>
          </div>
        </div>
      </div>
    </header>
  );
}