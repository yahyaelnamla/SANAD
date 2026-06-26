"use client";

import { motion } from "framer-motion";
import { GraduationCap, Loader2, RefreshCw, Search } from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { PageLayout } from "@/components/PageGuide";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/hooks/useAuth";
import { useTranslations } from "@/hooks/useTranslations";
import { scholarDisplayName } from "@/lib/scholarDisplay";
import { localizeExpertiseTag, localizeScholarInstitution } from "@/lib/domainLocalizations";
import { ApiClientError } from "@/services/apiClient";
import { listScholars, type ScholarListItem } from "@/services/scholarService";

export function ScholarBrowsePanel() {
  const { t, locale } = useTranslations();
  const { accessToken } = useAuth();
  const [items, setItems] = useState<ScholarListItem[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [initialized, setInitialized] = useState(false);

  const load = useCallback(async () => {
    if (!accessToken) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const response = await listScholars(accessToken, query || undefined);
      setItems(response.items);
      setInitialized(true);
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : t("errors.generic"));
    } finally {
      setLoading(false);
    }
  }, [accessToken, query, locale]);

  useEffect(() => {
    if (!accessToken) return;
    const timer = window.setTimeout(() => void load(), query ? 300 : 0);
    return () => window.clearTimeout(timer);
  }, [load, accessToken, query]);

  const showInitialSpinner = loading && !initialized;

  return (
    <PageLayout guideKey="scholars" className="mx-auto max-w-4xl space-y-6">
      <Card className="glass-card border-cyan-500/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <GraduationCap className="h-5 w-5 text-cyan-400" />
            {t("scholars.title")}
          </CardTitle>
          <p className="text-sm text-muted-foreground">{t("scholars.subtitle")}</p>
        </CardHeader>
        <CardContent>
          <div className="relative">
            <Search className="absolute start-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={t("scholars.searchPlaceholder")}
              className="ps-9"
              aria-label={t("scholars.searchPlaceholder")}
            />
          </div>
        </CardContent>
      </Card>

      {error && (
        <div className="rounded-lg border border-destructive/30 bg-destructive/5 px-4 py-3 text-center">
          <p className="text-sm text-destructive">{error}</p>
          <Button type="button" variant="ghost" size="sm" className="mt-2 gap-1" onClick={() => void load()}>
            <RefreshCw className="h-3.5 w-3.5" />
            {t("sidebar.retry")}
          </Button>
        </div>
      )}

      {showInitialSpinner && (
        <div className="flex justify-center py-12">
          <Loader2 className="h-6 w-6 animate-spin text-cyan-400" />
        </div>
      )}

      {!showInitialSpinner && !error && items.length === 0 && (
        <p className="text-center text-muted-foreground">{t("scholars.empty")}</p>
      )}

      <div className="relative grid gap-4 sm:grid-cols-2">
        {loading && initialized && (
          <div className="pointer-events-none absolute inset-0 z-10 flex items-start justify-center bg-background/40 pt-8 backdrop-blur-[1px]">
            <Loader2 className="h-5 w-5 animate-spin text-cyan-400" />
          </div>
        )}
        {items.map((scholar, index) => {
          const names = scholarDisplayName(scholar, locale);
          return (
            <motion.div
              key={scholar.slug}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.04 }}
            >
              <Link href={`/scholars/${scholar.slug}`}>
                <Card className="glass-card h-full border-border/50 transition-colors hover:border-cyan-500/30">
                  <CardContent className="pt-5">
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0">
                        <p className="font-semibold leading-snug">{names.primary}</p>
                        {names.secondary && (
                          <p className="mt-0.5 text-xs text-muted-foreground">{names.secondary}</p>
                        )}
                        {scholar.institution && (
                          <p className="mt-1 line-clamp-2 text-xs text-muted-foreground">
                            {localizeScholarInstitution(
                              scholar.slug,
                              scholar.institution,
                              locale,
                            )}
                          </p>
                        )}
                      </div>
                      {scholar.is_seed && (
                        <Badge variant="secondary" className="shrink-0 text-[10px]">
                          {t("scholars.verified")}
                        </Badge>
                      )}
                    </div>
                    <div className="mt-3 flex flex-wrap gap-1">
                      {scholar.expertise.slice(0, 4).map((tag) => (
                        <Badge key={tag} variant="outline" className="text-[10px]">
                          {localizeExpertiseTag(tag, locale)}
                        </Badge>
                      ))}
                    </div>
                    <p className="mt-3 text-xs text-muted-foreground">
                      {scholar.source_count} {t("scholars.sourcesLabel")}
                    </p>
                  </CardContent>
                </Card>
              </Link>
            </motion.div>
          );
        })}
      </div>
    </PageLayout>
  );
}
