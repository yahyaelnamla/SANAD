"use client";

import { Loader2 } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SafeText } from "@/components/SafeText";
import { useAuth } from "@/hooks/useAuth";
import { useTranslations } from "@/hooks/useTranslations";
import { cn } from "@/lib/utils";
import { ApiClientError } from "@/services/apiClient";
import {
  compareDocuments,
  type DocumentCompareResult,
  type DocumentListItem,
} from "@/services/featuresService";

interface DocumentComparePanelProps {
  documents: DocumentListItem[];
}

export function DocumentComparePanel({ documents }: DocumentComparePanelProps) {
  const { t } = useTranslations();
  const { accessToken } = useAuth();
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [result, setResult] = useState<DocumentCompareResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setSelected((prev) => {
      const valid = new Set(documents.map((doc) => String(doc.document_id)));
      const next = new Set([...prev].filter((id) => valid.has(id)));
      return next.size === prev.size ? prev : next;
    });
  }, [documents]);

  const toggle = (id: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else if (next.size < 4) {
        next.add(id);
      }
      return next;
    });
    setResult(null);
  };

  const handleCompare = useCallback(async () => {
    if (!accessToken || selected.size < 2) return;
    setLoading(true);
    setError(null);
    try {
      setResult(await compareDocuments(accessToken, [...selected]));
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : t("errors.generic"));
    } finally {
      setLoading(false);
    }
  }, [accessToken, selected, t]);

  if (documents.length < 2) {
    return (
      <p className="text-sm text-muted-foreground">{t("documents.compareNeedUploads")}</p>
    );
  }

  return (
    <Card className="glass-card border-violet-500/20">
      <CardHeader>
        <CardTitle className="text-base">{t("documents.compareTitle")}</CardTitle>
        <p className="text-sm text-muted-foreground">{t("documents.compareHint")}</p>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex flex-wrap gap-2">
          {documents.map((doc) => {
            const isSelected = selected.has(doc.document_id);
            return (
              <button
                key={doc.document_id}
                type="button"
                onClick={() => toggle(doc.document_id)}
                className={cn(
                  "touch-target rounded-xl border px-3 py-2 text-start text-sm transition-colors",
                  isSelected
                    ? "border-cyan-500/50 bg-cyan-500/10"
                    : "border-border/50 bg-muted/10 hover:border-cyan-500/30",
                )}
                aria-pressed={isSelected}
              >
                <span className="font-medium break-words">{doc.filename}</span>
                <span className="mt-0.5 block text-xs text-muted-foreground">
                  {doc.page_count} {t("documents.pageCount")}
                </span>
              </button>
            );
          })}
        </div>

        <Button
          type="button"
          disabled={selected.size < 2 || loading}
          onClick={() => void handleCompare()}
          className="gap-2"
        >
          {loading && <Loader2 className="h-4 w-4 animate-spin" />}
          {t("documents.compareAction")} ({selected.size}/4)
        </Button>

        {error && <p className="text-sm text-destructive">{error}</p>}

        {result && (
          <div className="space-y-4">
            {result.comparison_notes.map((note) => (
              <p key={note} className="rounded-lg border border-border/40 bg-muted/10 p-3 text-sm">
                {note}
              </p>
            ))}

            {result.shared_riba_signals.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {result.shared_riba_signals.map((signal) => (
                  <Badge key={signal} variant="secondary">
                    {signal}
                  </Badge>
                ))}
              </div>
            )}

            <div className="grid gap-4 md:grid-cols-2">
              {result.documents.map((doc) => (
                <div key={doc.document_id} className="rounded-xl border border-border/50 p-4">
                  <p className="font-semibold break-words">{doc.filename}</p>
                  <div className="mt-2 flex flex-wrap gap-2 text-xs text-muted-foreground">
                    <span>{t("documents.pageCount")}: {doc.page_count}</span>
                    <span>{t("documents.ribaSignals")}: {doc.riba_signal_count}</span>
                    <span>{t("documents.revenueSignals")}: {doc.revenue_signal_count}</span>
                  </div>
                  <SafeText text={doc.summary} className="mt-2 line-clamp-3 text-sm text-muted-foreground" as="p" />
                  {doc.key_findings.length > 0 && (
                    <ul className="mt-2 space-y-1 text-xs text-muted-foreground">
                      {doc.key_findings.map((finding) => (
                        <li key={finding}>• {finding}</li>
                      ))}
                    </ul>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
