"use client";

import { X } from "lucide-react";

import { SidebarContent } from "@/components/layout/SidebarContent";
import { Button } from "@/components/ui/button";
import { useTranslations } from "@/hooks/useTranslations";
import { cn } from "@/lib/utils";
import { useSettingsStore } from "@/store/settingsStore";

export function MobileSidebarDrawer() {
  const { t } = useTranslations();
  const open = useSettingsStore((s) => s.mobileSidebarOpen);
  const setMobileSidebarOpen = useSettingsStore((s) => s.setMobileSidebarOpen);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[60] lg:hidden">
      <button
        type="button"
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        aria-label={t("sidebar.closeMenu")}
        onClick={() => setMobileSidebarOpen(false)}
      />
      <aside
        className={cn(
          "absolute inset-y-0 start-0 flex w-[min(100vw-3rem,20rem)] flex-col glass-panel shadow-2xl",
          "animate-in slide-in-from-start duration-300",
        )}
      >
        <div className="flex items-center justify-between border-b border-border/40 px-3 py-2">
          <p className="text-sm font-semibold">{t("sidebar.menuTitle")}</p>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setMobileSidebarOpen(false)}
            aria-label={t("sidebar.closeMenu")}
          >
            <X className="h-5 w-5" />
          </Button>
        </div>
        <SidebarContent
          collapsed={false}
          showCollapseButton={false}
          onNavigate={() => setMobileSidebarOpen(false)}
          className="min-h-0 flex-1"
        />
      </aside>
    </div>
  );
}
