"use client";

import * as React from "react";
import Link from "next/link";

import { NavMain } from "@/components/nav-main";
import { NavSecondary } from "@/components/nav-secondary";
import { NavUser } from "@/components/nav-user";

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";

import {
  LayoutDashboardIcon,
  DatabaseIcon,
  ListTreeIcon,
  ChartColumnIncreasingIcon,
  Settings2Icon,
  CircleHelpIcon,
  ShieldCheckIcon,
} from "lucide-react";

const data = {
  navMain: [
    {
      title: "Dashboard",
      url: "/dashboard",
      icon: <LayoutDashboardIcon />,
    },
    {
      title: "Repositories",
      url: "/repositories",
      icon: <DatabaseIcon />,
    },
    {
      title: "Pull Requests",
      url: "/pull-requests",
      icon: <ListTreeIcon />,
    },
    {
      title: "Analytics",
      url: "/analytics",
      icon: <ChartColumnIncreasingIcon />,
    },
  ],

  navSecondary: [
    {
      title: "Settings",
      url: "/settings",
      icon: <Settings2Icon />,
    },
    {
      title: "Help",
      url: "/help",
      icon: <CircleHelpIcon />,
    },
  ],
};

export function AppSidebar({
  user,
  ...props
}: React.ComponentProps<typeof Sidebar> & {
  user: {
    name: string;
    email: string;
    avatar: string;
  };
}) {
  return (
    <Sidebar collapsible="offcanvas" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              asChild
              className="h-auto py-3 data-[slot=sidebar-menu-button]:p-3"
            >
              <Link
                href="/dashboard"
                className="flex items-center gap-3"
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-sm">
                  <ShieldCheckIcon className="h-5 w-5" />
                </div>

                <div className="flex flex-col">
                  <span className="text-base font-bold tracking-tight">
                    Kritique.ai
                  </span>

                  <span className="text-xs text-muted-foreground">
                    AI Code Review Platform
                  </span>
                </div>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      <SidebarContent>
        <NavMain items={data.navMain} />

        <NavSecondary
          items={data.navSecondary}
          className="mt-auto"
        />
      </SidebarContent>

      <SidebarFooter>
        <NavUser user={user} />
      </SidebarFooter>
    </Sidebar>
  );
}