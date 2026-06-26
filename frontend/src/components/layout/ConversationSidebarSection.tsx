"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Pin, PinOff, RefreshCw } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useConversationThreads } from "@/hooks/useConversationThreads";
import { useTranslations } from "@/hooks/useTranslations";
import type { ConversationListItem } from "@/lib/chatSessionUtils";
import { cn, formatDate } from "@/lib/utils";

interface ConversationSidebarSectionProps {
  searchQuery: string;
  collapsed?: boolean;
  onNavigate?: () => void;
}

function ConversationRow({
  item,
  collapsed,
  pinned,
  onTogglePin,
  onNavigate,
}: {
  item: ConversationListItem;
  collapsed?: boolean;
  pinned: boolean;
  onTogglePin: () => void;
  onNavigate?: () => void;
}) {
  const pathname = usePathname();
  const { locale } = useTranslations();
  const href = `/chat?session=${encodeURIComponent(item.session_id)}`;
  const active = pathname === "/chat" && typeof window !== "undefined"
    ? new URLSearchParams(window.location.search).get("session") === item.session_id
    : false;
  const title = item.title;

  if (collapsed) {
    return (
      <Link
        href={href}
        onClick={onNavigate}
        title={title}
        className={cn(
          "flex h-9 w-9 items-center justify-center rounded-lg text-xs font-semibold transition-colors",
          active ? "bg-accent text-accent-foreground" : "hover:bg-accent/50",
          item.refused && "text-destructive",
        )}
      >
        {title.charAt(0).toUpperCase()}
      </Link>
    );
  }

  return (
    <div
      className={cn(
        "group flex items-start gap-1 rounded-xl border border-transparent px-2 py-1.5 transition-colors hover:border-border/50 hover:bg-accent/40",
        active && "border-cyan-500/20 bg-accent/60",
      )}
    >
      <Link href={href} onClick={onNavigate} className="min-w-0 flex-1 py-0.5">
        <p className="line-clamp-2 text-sm leading-snug">{title}</p>
        <p className="mt-1 text-[10px] text-muted-foreground">
          {formatDate(item.updated_at, locale)}
          {item.turn_count > 1 ? ` · ${item.turn_count}` : ""}
        </p>
      </Link>
      <Button
        type="button"
        variant="ghost"
        size="icon"
        className="h-7 w-7 shrink-0 opacity-0 transition-opacity group-hover:opacity-100"
        onClick={(e) => {
          e.preventDefault();
          onTogglePin();
        }}
        aria-label={pinned ? "Unpin" : "Pin"}
      >
        {pinned ? <PinOff className="h-3.5 w-3.5" /> : <Pin className="h-3.5 w-3.5" />}
      </Button>
    </div>
  );
}

export function ConversationSidebarSection({
  searchQuery,
  collapsed = false,
  onNavigate,
}: ConversationSidebarSectionProps) {
  const { t } = useTranslations();
  const { pinned, recent, loading, error, refresh, togglePin, isPinned } =
    useConversationThreads(searchQuery);

  if (collapsed) {
    return (
      <div className="flex flex-col items-center gap-1">
        {[...pinned, ...recent].slice(0, 5).map((item) => (
          <ConversationRow
            key={item.session_id}
            item={item}
            collapsed
            pinned={isPinned(item.last_query_id)}
            onTogglePin={() => togglePin(item.last_query_id)}
            onNavigate={onNavigate}
          />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {loading && (
        <div className="min-h-[120px] space-y-2 px-3" aria-hidden>
          {Array.from({ length: 4 }).map((_, index) => (
            <div key={index} className="h-8 w-full rounded-md skeleton-block" />
          ))}
        </div>
      )}
      {error && !loading && (
        <div className="mx-2 rounded-lg border border-destructive/20 bg-destructive/5 px-3 py-2">
          <p className="text-xs text-destructive">{error}</p>
          <Button
            type="button"
            variant="ghost"
            size="sm"
            className="mt-1.5 h-7 gap-1.5 px-2 text-xs text-destructive hover:text-destructive"
            onClick={() => void refresh()}
          >
            <RefreshCw className="h-3 w-3 shrink-0" />
            {t("sidebar.retry")}
          </Button>
        </div>
      )}

      {!loading && pinned.length > 0 && (
        <div>
          <p className="px-3 pb-1 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
            {t("sidebar.pinned")}
          </p>
          <div className="space-y-0.5">
            {pinned.map((item) => (
              <ConversationRow
                key={item.session_id}
                item={item}
                pinned
                onTogglePin={() => togglePin(item.last_query_id)}
                onNavigate={onNavigate}
              />
            ))}
          </div>
        </div>
      )}

      {!loading && (
        <div>
          <p className="px-3 pb-1 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
            {t("sidebar.recent")}
          </p>
          {recent.length === 0 ? (
            <p className="px-3 text-xs text-muted-foreground">{t("sidebar.noConversations")}</p>
          ) : (
            <div className="space-y-0.5">
              {recent.map((item) => (
                <ConversationRow
                  key={item.session_id}
                  item={item}
                  pinned={false}
                  onTogglePin={() => togglePin(item.last_query_id)}
                  onNavigate={onNavigate}
                />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
