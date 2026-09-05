"use client";

import { usePathname } from "next/navigation";
import type { ReactNode } from "react";
import { ConversationSidebar } from "@/components/chat/ConversationSidebar";

type AppShellProps = { children: ReactNode };

export function AppShell({ children }: AppShellProps) {
  const pathname = usePathname();
  const singleColumn = pathname === "/";

  return (
    <div className={singleColumn ? "app-shell app-shell-single" : "app-shell"}>
      <ConversationSidebar />
      <div className="app-content">{children}</div>
    </div>
  );
}