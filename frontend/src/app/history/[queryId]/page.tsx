"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, Loader2 } from "lucide-react";

import { AuthGuard } from "@/features/auth/components/AuthGuard";
import { ExplainabilityPanel } from "@/features/chat/components/ExplainabilityPanel";
import { AnswerContent } from "@/features/chat/components/AnswerContent";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/useAuth";
import { useTranslations } from "@/hooks/useTranslations";
import { ApiClientError } from "@/services/apiClient";
import { getQuery } from "@/services/queryService";
import type { QueryResult } from "@/types/query";

function QueryDetailContent({ queryId }: { queryId: string }) {
  const { t } = useTranslations();
  const { accessToken } = useAuth();
  const [result, setResult] = useState<QueryResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!accessToken) {
      setLoading(false);
      setError(t("errors.unauthorized"));
      return;
    }

    getQuery(queryId, accessToken)
      .then(setResult)
      .catch((err) => {
        if (err instanceof ApiClientError) {
          setError(err.message);
        } else {
          setError(t("errors.generic"));
        }
      })
      .finally(() => setLoading(false));
  }, [accessToken, queryId, t]);

  if (loading) {
    return (
      <div className="flex items-center justify-center gap-2 py-20 text-muted-foreground">
        <Loader2 className="h-5 w-5 animate-spin" />
        {t("common.loading")}
      </div>
    );
  }

  if (error || !result) {
    return <p className="py-20 text-center text-destructive">{error ?? t("errors.generic")}</p>;
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div className="flex items-start gap-3">
        <Link href="/history">
          <Button variant="ghost" size="icon" aria-label={t("history.back")}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div>
          <h1 className="text-xl font-semibold tracking-tight">{result.question}</h1>
          <p className="mt-1 text-sm text-muted-foreground">{t("history.viewDetail")}</p>
        </div>
      </div>

      {!result.refused && result.summary && (
        <div className="glass-card rounded-2xl border border-border/50 p-4">
          <AnswerContent text={result.summary} arabic={result.language === "ar"} />
        </div>
      )}

      <ExplainabilityPanel result={result} />
    </div>
  );
}

export default function QueryDetailPage({ params }: { params: { queryId: string } }) {
  return (
    <AuthGuard>
      <QueryDetailContent queryId={params.queryId} />
    </AuthGuard>
  );
}
