"use client";

import { sidebarWidthClass } from "@/lib/sidebarLayout";
import { useSettingsStore } from "@/store/settingsStore";

export function SidebarSkeleton() {
  const collapsed = useSettingsStore((s) => s.sidebarCollapsed);

  return (
    <aside
      className={`hidden h-full shrink-0 flex-col border-e border-border/50 glass-panel lg:flex ${sidebarWidthClass(collapsed)}`}
    >
      <div className="space-y-4 p-3">
        <div className="h-9 w-full rounded-md skeleton-block" />
        {Array.from({ length: 5 }).map((_, index) => (
          <div key={index} className="h-10 w-full rounded-lg skeleton-block" />
        ))}
        <div className="min-h-[120px] space-y-2">
          {Array.from({ length: 3 }).map((_, index) => (
            <div key={`conv-${index}`} className="h-8 w-full rounded-md skeleton-block" />
          ))}
        </div>
      </div>
    </aside>
  );
}
