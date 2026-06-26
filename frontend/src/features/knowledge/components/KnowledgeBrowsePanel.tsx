"use client";

import { Loader2 } from "lucide-react";
import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/hooks/useAuth";
import { useTranslations } from "@/hooks/useTranslations";
import { ApiClientError } from "@/services/apiClient";
import { browseKnowledgeSources, type KnowledgeSourceItem } from "@/services/featuresService";

export function KnowledgeBrowsePanel() {
  const { t } = useTranslations();
  const { accessToken } = useAuth();
  const [items, setItems] = useState<KnowledgeSourceItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!accessToken) {
      setLoading(false);
      return;
    }
    browseKnowledgeSources(accessToken)
      .then((response) => setItems(response.items))
      .catch((err) => setError(err instanceof ApiClientError ? err.message : t("errors.generic")))
      .finally(() => setLoading(false));
  }, [accessToken, t]);

  if (loading) {
    return (
      <div className="flex justify-center py-20">
        <Loader2 className="h-6 w-6 animate-spin text-cyan-400" />
      </div>
    );
  }

  if (error) {
    return <p className="py-20 text-center text-destructive">{error}</p>;
  }

  if (items.length === 0) {
    return <p className="py-20 text-center text-muted-foreground">{t("knowledge.empty")}</p>;
  }

  return (
    <div className="mx-auto grid max-w-4xl gap-3">
      {items.map((item) => (
        <Card key={item.id} className="glass-card">
          <CardHeader className="pb-2">
            <div className="flex items-start justify-between gap-3">
              <CardTitle className="text-base">{item.title}</CardTitle>
              <Badge variant="outline">{item.source_type}</Badge>
            </div>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            {item.author} · {item.language.toUpperCase()}
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
