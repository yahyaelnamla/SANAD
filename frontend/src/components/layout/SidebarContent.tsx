"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import {
  Bookmark,
  Building2,
  Calculator,
  ChevronLeft,
  ChevronRight,
  FileText,
  Gauge,
  GraduationCap,
  History,
  MessageSquarePlus,
  Network,
  PieChart,
  Search,
  Settings,
  Star,
} from "lucide-react";

import { ConversationSidebarSection } from "@/components/layout/ConversationSidebarSection";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useTranslations } from "@/hooks/useTranslations";
import { cn } from "@/lib/utils";
import { useSettingsStore } from "@/store/settingsStore";

interface NavItem {
  href: string;
  labelKey: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: "soon";
}

const MAIN_ITEMS: NavItem[] = [
  { href: "/chat?new=1", labelKey: "sidebar.newChat", icon: MessageSquarePlus },
  { href: "/history", labelKey: "sidebar.history", icon: History },
];

const FEATURE_ITEMS: NavItem[] = [
  { href: "/knowledge", labelKey: "sidebar.knowledgeBase", icon: FileText },
  { href: "/scholars", labelKey: "sidebar.scholars", icon: GraduationCap },
  { href: "/scanner/company", labelKey: "sidebar.companyScanner", icon: Building2 },
  { href: "/scanner/portfolio", labelKey: "sidebar.portfolioScanner", icon: PieChart },
  { href: "/tools/zakat", labelKey: "sidebar.zakatCalculator", icon: Calculator },
  { href: "/knowledge-graph", labelKey: "sidebar.knowledgeGraph", icon: Network },
  { href: "/evaluation", labelKey: "sidebar.evaluation", icon: Gauge },
];

const LIBRARY_ITEMS: NavItem[] = [
  { href: "/documents", labelKey: "sidebar.uploadedDocuments", icon: FileText },
  { href: "/bookmarks", labelKey: "sidebar.bookmarks", icon: Bookmark },
  { href: "/favorites", labelKey: "sidebar.favoriteFatwas", icon: Star },
  { href: "/settings", labelKey: "sidebar.settings", icon: Settings },
];

function NavLink({
  item,
  collapsed,
  onNavigate,
}: {
  item: NavItem;
  collapsed: boolean;
  onNavigate?: () => void;
}) {
  const pathname = usePathname();
  const { t } = useTranslations();
  const Icon = item.icon;
  const active = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));

  return (
    <Link
      href={item.href}
      onClick={onNavigate}
      title={collapsed ? t(item.labelKey) : undefined}
      className={cn(
        "group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200",
        "hover:bg-accent/60 hover:text-accent-foreground",
        active && "bg-accent/80 text-accent-foreground shadow-sm ring-1 ring-cyan-500/20",
        collapsed && "justify-center px-2",
      )}
    >
      <Icon className={cn("h-4 w-4 shrink-0 self-center", active && "text-cyan-400")} />
      {!collapsed && (
        <>
          <span className="truncate">{t(item.labelKey)}</span>
          {item.badge === "soon" && (
            <span className="ms-auto rounded-full bg-muted px-2 py-0.5 text-[10px] uppercase tracking-wide text-muted-foreground">
              {t("sidebar.soon")}
            </span>
          )}
        </>
      )}
    </Link>
  );
}

interface SidebarContentProps {
  collapsed?: boolean;
  showCollapseButton?: boolean;
  onNavigate?: () => void;
  className?: string;
}

export function SidebarContent({
  collapsed: collapsedProp,
  showCollapseButton = true,
  onNavigate,
  className,
}: SidebarContentProps) {
  const { t } = useTranslations();
  const collapsedStore = useSettingsStore((s) => s.sidebarCollapsed);
  const setSidebarCollapsed = useSettingsStore((s) => s.setSidebarCollapsed);
  const collapsed = collapsedProp ?? collapsedStore;
  const [searchQuery, setSearchQuery] = useState("");

  return (
    <div className={cn("flex h-full flex-col", className)}>
      <div className={cn("flex items-center gap-2 border-b border-border/40 p-3", collapsed && "justify-center")}>
        {!collapsed && (
          <div className="relative flex-1">
            <Search className="pointer-events-none absolute start-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={t("sidebar.searchConversations")}
              className="h-9 border-border/50 bg-background/50 ps-9 text-sm"
              aria-label={t("sidebar.searchConversations")}
            />
          </div>
        )}
        {showCollapseButton && (
          <Button
            variant="ghost"
            size="icon"
            className="h-9 w-9 shrink-0"
            onClick={() => setSidebarCollapsed(!collapsed)}
            aria-label={collapsed ? t("sidebar.expand") : t("sidebar.collapse")}
          >
            {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </Button>
        )}
      </div>

      <ScrollArea className="flex-1 px-2 py-3">
        <div className="space-y-6">
          <div className="space-y-1">
            {!collapsed && (
              <p className="px-3 pb-1 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                {t("sidebar.main")}
              </p>
            )}
            {MAIN_ITEMS.map((item) => (
              <NavLink key={item.href} item={item} collapsed={collapsed} onNavigate={onNavigate} />
            ))}
          </div>

          <ConversationSidebarSection
            searchQuery={searchQuery}
            collapsed={collapsed}
            onNavigate={onNavigate}
          />

          <div className="space-y-1">
            {!collapsed && (
              <p className="px-3 pb-1 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                {t("sidebar.tools")}
              </p>
            )}
            {FEATURE_ITEMS.map((item) => (
              <NavLink key={item.href} item={item} collapsed={collapsed} onNavigate={onNavigate} />
            ))}
          </div>

          <div className="space-y-1">
            {!collapsed && (
              <p className="px-3 pb-1 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                {t("sidebar.library")}
              </p>
            )}
            {LIBRARY_ITEMS.map((item) => (
              <NavLink key={item.href} item={item} collapsed={collapsed} onNavigate={onNavigate} />
            ))}
          </div>
        </div>
      </ScrollArea>
    </div>
  );
}
