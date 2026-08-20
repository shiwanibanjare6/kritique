import { auth } from "@/auth";
import { redirect } from "next/navigation";

import {
  SidebarInset,
  SidebarProvider,
} from "@/components/ui/sidebar";

import { AppSidebar } from "@/components/app-sidebar";

export default async function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await auth();

  if (!session) {
    redirect("/login");
  }

  return (
    <SidebarProvider defaultOpen={true}>
      <AppSidebar
        user={{
          name: session.user?.name ?? "GitHub User",
          email: session.user?.email ?? "",
          avatar: session.user?.image ?? "",
        }}
      />

      <SidebarInset>
        {children}
      </SidebarInset>
    </SidebarProvider>
  );
}