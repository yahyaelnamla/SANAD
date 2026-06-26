"use client";

import { SidebarContent } from "@/components/layout/SidebarContent";
import { sidebarWidthClass } from "@/lib/sidebarLayout";
import { cn } from "@/lib/utils";
import { useSettingsStore } from "@/store/settingsStore";

export function Sidebar() {
  const collapsed = useSettingsStore((s) => s.sidebarCollapsed);

  return (
    <aside
      className={cn(
        "hidden h-full shrink-0 flex-col border-e border-border/50 glass-panel lg:flex",
        sidebarWidthClass(collapsed),
      )}
    >
      <SidebarContent />
    </aside>
  );
}
