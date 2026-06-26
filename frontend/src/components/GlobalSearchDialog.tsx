"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import {
  BookOpen,
  Building2,
  FileText,
  Loader2,
  MessageSquare,
  Search,
  UserRound,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/hooks/useAuth";
import { useTranslations } from "@/hooks/useTranslations";
import { cn } from "@/lib/utils";
import { ApiClientError } from "@/services/apiClient";
import { globalSearch, type SearchResultItem } from "@/services/searchService";

const TYPE_ICONS: Record<SearchResultItem["type"], React.ComponentType<{ className?: string }>> = {
  chat: MessageSquare,
  source: BookOpen,
  scholar: UserRound,
  company: Building2,
  document: FileText,
};

interface GlobalSearchDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function GlobalSearchDialog({ open, onOpenChange }: GlobalSearchDialogProps) {
  const { t } = useTranslations();
  const { accessToken } = useAuth();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResultItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const debounceRef = useRef<number | null>(null);

  useEffect(() => {
    if (open) {
      window.setTimeout(() => inputRef.current?.focus(), 0);
    } else {
      setQuery("");
      setResults([]);
      setError(null);
    }
  }, [open]);

  const runSearch = useCallback(
    async (value: string) => {
      if (!accessToken || value.trim().length < 2) {
        setResults([]);
        setError(null);
        return;
      }
      setLoading(true);
      setError(null);
      try {
        const response = await globalSearch(accessToken, value.trim());
        setResults(response.results);
      } catch (err) {
        setError(err instanceof ApiClientError ? err.message : t("errors.generic"));
        setResults([]);
      } finally {
        setLoading(false);
      }
    },
    [accessToken, t],
  );

  useEffect(() => {
    if (!open) return;
    if (debounceRef.current) window.clearTimeout(debounceRef.current);
    debounceRef.current = window.setTimeout(() => {
      void runSearch(query);
    }, 280);
    return () => {
      if (debounceRef.current) window.clearTimeout(debounceRef.current);
    };
  }, [open, query, runSearch]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-[100] flex items-start justify-center bg-black/60 px-4 pt-[12vh] backdrop-blur-sm"
      role="dialog"
      aria-modal="true"
      aria-label={t("search.title")}
      onClick={() => onOpenChange(false)}
    >
      <div
        className="glass-card w-full max-w-2xl overflow-hidden rounded-2xl border border-cyan-500/20 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-2 border-b border-border/50 px-4 py-3">
          <Search className="h-4 w-4 text-muted-foreground" />
          <Input
            ref={inputRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={t("search.placeholder")}
            className="border-0 bg-transparent shadow-none focus-visible:ring-0"
            aria-label={t("search.placeholder")}
          />
          <Button type="button" variant="ghost" size="sm" onClick={() => onOpenChange(false)}>
            {t("admin.cancel")}
          </Button>
        </div>

        <div className="max-h-[50vh] overflow-y-auto p-2">
          {loading && (
            <div className="flex items-center justify-center gap-2 py-8 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              {t("search.searching")}
            </div>
          )}
          {!loading && error && <p className="py-6 text-center text-sm text-destructive">{error}</p>}
          {!loading && !error && query.trim().length >= 2 && results.length === 0 && (
            <p className="py-6 text-center text-sm text-muted-foreground">{t("search.noResults")}</p>
          )}
          {!loading && query.trim().length < 2 && (
            <p className="py-6 text-center text-sm text-muted-foreground">{t("search.hint")}</p>
          )}
          {!loading &&
            results.map((result) => {
              const Icon = TYPE_ICONS[result.type];
              return (
                <Link
                  key={`${result.type}-${result.id}`}
                  href={result.href}
                  onClick={() => onOpenChange(false)}
                  className={cn(
                    "flex items-start gap-3 rounded-xl px-3 py-3 transition-colors hover:bg-accent/50",
                  )}
                >
                  <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-cyan-500/10 text-cyan-400">
                    <Icon className="h-4 w-4" />
                  </div>
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium">{result.title}</p>
                    {result.subtitle && (
                      <p className="truncate text-xs text-muted-foreground">{result.subtitle}</p>
                    )}
                    <p className="mt-1 text-[10px] uppercase tracking-wide text-cyan-400/80">
                      {t(`search.types.${result.type}`)}
                    </p>
                  </div>
                </Link>
              );
            })}
        </div>
      </div>
    </div>
  );
}

export function useGlobalSearchShortcut(onOpen: () => void) {
  useEffect(() => {
    const handler = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        onOpen();
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onOpen]);
}
