"use client";

import { motion } from "framer-motion";
import { useCallback, useEffect, useState } from "react";

import { AdminAnalyticsCharts } from "@/features/admin/components/AdminAnalyticsCharts";
import { AdminStatsCards } from "@/features/admin/components/AdminStatsCards";
import { SourceForm } from "@/features/admin/components/SourceForm";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { useAuth } from "@/hooks/useAuth";
import { useTranslations } from "@/hooks/useTranslations";
import { formatDate } from "@/lib/utils";
import { ApiClientError } from "@/services/apiClient";
import {
  createSource,
  deleteSource,
  getAdminAnalytics,
  getAdminStats,
  listSources,
  updateSource,
} from "@/services/sourceService";
import type { AdminAnalytics, AdminStats, Source, SourceCreatePayload } from "@/types/source";

export function AdminDashboard() {
  const { t, locale } = useTranslations();
  const { accessToken } = useAuth();
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [analytics, setAnalytics] = useState<AdminAnalytics | null>(null);
  const [sources, setSources] = useState<Source[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingSource, setEditingSource] = useState<Source | null>(null);

  const loadData = useCallback(async () => {
    if (!accessToken) return;
    setLoading(true);
    setError(null);
    try {
      const [statsResponse, analyticsResponse, sourcesResponse] = await Promise.all([
        getAdminStats(accessToken),
        getAdminAnalytics(accessToken),
        listSources(accessToken),
      ]);
      setStats(statsResponse);
      setAnalytics(analyticsResponse);
      setSources(sourcesResponse.items);
    } catch (err) {
      if (err instanceof ApiClientError) {
        setError(err.message);
      } else {
        setError(t("errors.generic"));
      }
    } finally {
      setLoading(false);
    }
  }, [accessToken, t]);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const handleCreate = async (payload: SourceCreatePayload) => {
    if (!accessToken) return;
    await createSource(accessToken, payload);
    setShowForm(false);
    await loadData();
  };

  const handleUpdate = async (payload: SourceCreatePayload) => {
    if (!accessToken || !editingSource) return;
    await updateSource(accessToken, editingSource.id, payload);
    setEditingSource(null);
    await loadData();
  };

  const handleToggleAuthenticated = async (source: Source, checked: boolean) => {
    if (!accessToken) return;
    await updateSource(accessToken, source.id, { is_authenticated: checked });
    await loadData();
  };

  const handleDelete = async (sourceId: string) => {
    if (!accessToken) return;
    await deleteSource(accessToken, sourceId);
    await loadData();
  };

  if (loading) {
    return <p className="text-center text-muted-foreground">{t("admin.loading")}</p>;
  }

  if (error) {
    return <p className="text-center text-destructive">{error}</p>;
  }

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">{t("admin.title")}</h1>
        <p className="text-sm text-muted-foreground">{t("admin.subtitle")}</p>
      </div>

      {stats && <AdminStatsCards stats={stats} />}

      {analytics && <AdminAnalyticsCharts analytics={analytics} />}

      <Card>
        <CardHeader className="flex flex-row flex-wrap items-center justify-between gap-3">
          <div>
            <CardTitle>{t("admin.sourcesTitle")}</CardTitle>
            <p className="text-sm text-muted-foreground">{t("admin.sourcesSubtitle")}</p>
          </div>
          <Button
            onClick={() => {
              setEditingSource(null);
              setShowForm((value) => !value);
            }}
          >
            {showForm ? t("admin.hideForm") : t("admin.newSource")}
          </Button>
        </CardHeader>
        <CardContent className="space-y-4">
          {showForm && !editingSource && (
            <SourceForm onSubmit={handleCreate} onCancel={() => setShowForm(false)} />
          )}

          {editingSource && (
            <SourceForm
              initial={editingSource}
              onSubmit={handleUpdate}
              onCancel={() => setEditingSource(null)}
            />
          )}

          {sources.length === 0 ? (
            <p className="text-center text-muted-foreground">{t("admin.emptySources")}</p>
          ) : (
            <div className="overflow-x-auto rounded-md border">
              <table className="w-full min-w-[720px] text-sm">
                <thead className="border-b bg-muted/40">
                  <tr>
                    <th className="px-3 py-2 text-start font-medium">{t("admin.colTitle")}</th>
                    <th className="px-3 py-2 text-start font-medium">{t("admin.colAuthor")}</th>
                    <th className="px-3 py-2 text-start font-medium">{t("admin.colType")}</th>
                    <th className="px-3 py-2 text-start font-medium">{t("admin.colStatus")}</th>
                    <th className="px-3 py-2 text-start font-medium">{t("admin.colDate")}</th>
                    <th className="px-3 py-2 text-start font-medium">{t("admin.colActions")}</th>
                  </tr>
                </thead>
                <tbody>
                  {sources.map((source, index) => (
                    <motion.tr
                      key={source.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: index * 0.03 }}
                      className="border-b last:border-b-0"
                    >
                      <td className="px-3 py-3 font-medium">{source.title}</td>
                      <td className="px-3 py-3 text-muted-foreground">{source.author}</td>
                      <td className="px-3 py-3">
                        <Badge variant="outline">{t(`admin.sourceTypes.${source.source_type}`)}</Badge>
                      </td>
                      <td className="px-3 py-3">
                        <div className="flex items-center gap-2">
                          <Switch
                            checked={source.is_authenticated}
                            onCheckedChange={(checked) =>
                              void handleToggleAuthenticated(source, checked)
                            }
                          />
                          <Badge variant={source.is_authenticated ? "secondary" : "destructive"}>
                            {source.is_authenticated
                              ? t("admin.authenticated")
                              : t("admin.pending")}
                          </Badge>
                        </div>
                      </td>
                      <td className="px-3 py-3 text-muted-foreground">
                        {formatDate(source.created_at, locale)}
                      </td>
                      <td className="px-3 py-3">
                        <div className="flex flex-wrap gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => {
                              setShowForm(false);
                              setEditingSource(source);
                            }}
                          >
                            {t("admin.edit")}
                          </Button>
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={() => void handleDelete(source.id)}
                          >
                            {t("admin.delete")}
                          </Button>
                        </div>
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
