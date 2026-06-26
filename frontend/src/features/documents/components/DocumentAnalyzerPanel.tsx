"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { FileSearch, FileText, Loader2, MessageSquare, Trash2, Upload } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";

import { SafeText } from "@/components/SafeText";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/hooks/useAuth";
import { useTranslations } from "@/hooks/useTranslations";
import { cn, formatDate } from "@/lib/utils";
import { ApiClientError } from "@/services/apiClient";
import {
  analyzeDocument,
  deleteDocument,
  listDocuments,
  type DocumentAnalysisResult,
  type DocumentListItem,
} from "@/services/featuresService";
import { DocumentComparePanel } from "@/features/documents/components/DocumentComparePanel";

const MAX_PDF_BYTES = 10 * 1024 * 1024;
const ACCEPTED_PDF_TYPES = new Set([
  "application/pdf",
  "application/x-pdf",
  "application/octet-stream",
]);

function isPdfFile(file: File): boolean {
  if (file.name.toLowerCase().endsWith(".pdf")) return true;
  return Boolean(file.type && ACCEPTED_PDF_TYPES.has(file.type));
}

export function DocumentAnalyzerPanel() {
  const { t, locale } = useTranslations();
  const { accessToken } = useAuth();
  const inputRef = useRef<HTMLInputElement>(null);
  const [pendingFile, setPendingFile] = useState<File | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [result, setResult] = useState<DocumentAnalysisResult | null>(null);
  const [savedDocuments, setSavedDocuments] = useState<DocumentListItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshSaved = useCallback(async () => {
    if (!accessToken) return;
    try {
      const response = await listDocuments(accessToken);
      setSavedDocuments(response.items);
    } catch {
      setSavedDocuments([]);
    }
  }, [accessToken]);

  useEffect(() => {
    void refreshSaved();
  }, [refreshSaved]);

  const resetFileInput = () => {
    if (inputRef.current) {
      inputRef.current.value = "";
    }
  };

  const selectFile = (file: File | null) => {
    if (!file) return;
    if (!isPdfFile(file)) {
      setError(t("documents.invalidType"));
      resetFileInput();
      return;
    }
    if (file.size > MAX_PDF_BYTES) {
      setError(t("documents.fileTooLarge"));
      resetFileInput();
      return;
    }
    setPendingFile(file);
    setFileName(file.name);
    setError(null);
    setResult(null);
  };

  const runAnalysis = async () => {
    if (!pendingFile || !accessToken) {
      if (!accessToken) setError(t("errors.unauthorized"));
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const analysis = await analyzeDocument(accessToken, pendingFile, locale);
      setResult(analysis);
      setPendingFile(null);
      resetFileInput();
      await refreshSaved();
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : t("errors.generic"));
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (documentId: string) => {
    if (!accessToken || !window.confirm(t("documents.deleteConfirm"))) return;
    const normalizedId = String(documentId);
    setDeletingId(normalizedId);
    setError(null);
    try {
      await deleteDocument(accessToken, normalizedId);
      setSavedDocuments((prev) =>
        prev.filter((doc) => String(doc.document_id) !== normalizedId),
      );
      if (result?.document_id && String(result.document_id) === normalizedId) {
        setResult(null);
        setFileName(null);
      }
      await refreshSaved();
    } catch (err) {
      setError(err instanceof ApiClientError ? err.message : t("errors.generic"));
      await refreshSaved();
    } finally {
      setDeletingId(null);
    }
  };

  const onDrop = (event: React.DragEvent) => {
    event.preventDefault();
    setDragActive(false);
    const file = event.dataTransfer.files?.[0] ?? null;
    selectFile(file);
  };

  const canAnalyze = Boolean(pendingFile && accessToken && !loading);

  return (
    <div className="page-shell space-y-6">
      <Card className="glass-card border-cyan-500/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <FileText className="h-5 w-5 text-cyan-400" />
            {t("documents.title")}
          </CardTitle>
          <p className="text-sm text-muted-foreground">{t("documents.description")}</p>
        </CardHeader>
        <CardContent className="space-y-4">
          <input
            ref={inputRef}
            type="file"
            accept="application/pdf,.pdf"
            className="hidden"
            onChange={(event) => selectFile(event.target.files?.[0] ?? null)}
          />
          <button
            type="button"
            disabled={loading || !accessToken}
            onClick={() => inputRef.current?.click()}
            onDragOver={(e) => {
              e.preventDefault();
              setDragActive(true);
            }}
            onDragLeave={() => setDragActive(false)}
            onDrop={onDrop}
            className={cn(
              "flex w-full flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed px-4 py-10 text-center transition-colors",
              dragActive
                ? "border-cyan-400 bg-cyan-500/10"
                : "border-border/50 bg-background/40 hover:border-cyan-500/40 hover:bg-cyan-500/5",
              (loading || !accessToken) && "cursor-not-allowed opacity-60",
            )}
          >
            {loading ? (
              <Loader2 className="h-8 w-8 animate-spin text-cyan-400" />
            ) : (
              <Upload className="h-8 w-8 text-cyan-400" />
            )}
            <span className="text-sm font-medium">
              {loading
                ? t("documents.analyzing")
                : dragActive
                  ? t("documents.dropActive")
                  : t("documents.dropHint")}
            </span>
            {fileName && (
              <span className="text-xs text-muted-foreground">{fileName}</span>
            )}
          </button>

          {pendingFile && !loading && (
            <div className="flex flex-wrap items-center justify-center gap-2">
              <Button
                type="button"
                className="gap-2 bg-gradient-to-r from-cyan-500 to-teal-500 text-slate-950 hover:from-cyan-400 hover:to-teal-400"
                disabled={!canAnalyze}
                onClick={() => void runAnalysis()}
              >
                <FileSearch className="h-4 w-4 shrink-0" />
                {t("documents.analyzeAction")}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => {
                  setPendingFile(null);
                  setFileName(null);
                  resetFileInput();
                }}
              >
                {t("documents.clearFile")}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {savedDocuments.length > 0 && (
        <Card className="glass-card">
          <CardHeader>
            <CardTitle className="text-base">{t("documents.saved")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {savedDocuments.map((doc) => (
              <div
                key={doc.document_id}
                className="rounded-lg border border-border/50 p-3 text-sm"
              >
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <p className="min-w-0 flex-1 font-medium break-words">{doc.filename}</p>
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 shrink-0 text-destructive hover:text-destructive"
                    disabled={deletingId === doc.document_id}
                    onClick={() => void handleDelete(doc.document_id)}
                    aria-label={t("documents.delete")}
                  >
                    {deletingId === doc.document_id ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Trash2 className="h-4 w-4" />
                    )}
                  </Button>
                </div>
                <SafeText text={doc.summary} className="mt-1 text-muted-foreground line-clamp-2" />
                <p className="mt-1 text-xs text-muted-foreground">
                  {t("documents.pageCount")}: {doc.page_count} · {formatDate(doc.created_at, locale)}
                </p>
                <Button
                  asChild
                  type="button"
                  variant="outline"
                  size="sm"
                  className="mt-2 touch-target inline-flex items-center justify-center gap-2"
                >
                  <Link
                    href={`/chat?q=${encodeURIComponent(
                      locale === "ar"
                        ? `ماذا ذكر ${doc.filename} عن الإيرادات والديون؟`
                        : `What did ${doc.filename} mention about revenue and debt?`,
                    )}`}
                  >
                    <MessageSquare className="h-3.5 w-3.5 shrink-0" />
                    <span className="leading-none">{t("documents.askInChat")}</span>
                  </Link>
                </Button>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {savedDocuments.length >= 2 && (
        <DocumentComparePanel documents={savedDocuments} />
      )}

      {error && <p className="text-center text-sm text-destructive">{error}</p>}

      {result && (
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
          <Card className="glass-card">
            <CardHeader>
              <CardTitle className="text-base">{t("documents.summary")}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm text-muted-foreground">
              <SafeText text={result.summary} as="p" />
              <p className="text-xs">
                {t("documents.pageCount")}: {result.page_count}
              </p>
            </CardContent>
          </Card>

          <Card className="glass-card">
            <CardHeader>
              <CardTitle className="text-base">{t("documents.keyFindings")}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              {result.key_findings.map((finding) => (
                <SafeText key={finding} text={`• ${finding}`} as="p" />
              ))}
            </CardContent>
          </Card>

          {result.riba_findings.length > 0 && (
            <Card className="glass-card border-amber-500/30">
              <CardHeader>
                <CardTitle className="text-base">{t("documents.ribaFindings")}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {result.riba_findings.map((finding, index) => (
                  <div
                    key={`${finding.page}-${finding.label}-${index}`}
                    className="rounded-lg border border-border/50 p-3 text-sm"
                  >
                    <p className="font-medium">
                      {t("documents.page")} {finding.page}: {finding.label}
                    </p>
                    <SafeText text={finding.snippet} className="mt-1 text-muted-foreground" as="p" />
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {result.revenue_analysis.length > 0 && (
            <Card className="glass-card">
              <CardHeader>
                <CardTitle className="text-base">{t("documents.revenueAnalysis")}</CardTitle>
              </CardHeader>
              <CardContent className="responsive-table-wrap">
                <table className="w-full min-w-[420px] text-left text-sm">
                  <thead>
                    <tr className="border-b border-border/50 text-muted-foreground">
                      <th className="py-2 pe-3">{t("documents.page")}</th>
                      <th className="py-2 pe-3">{t("documents.metric")}</th>
                      <th className="py-2 pe-3">{t("documents.amount")}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.revenue_analysis.map((row, index) => (
                      <tr key={`${row.page}-${row.metric}-${index}`} className="border-b border-border/30">
                        <td className="py-2 pe-3">{row.page}</td>
                        <td className="max-w-[180px] truncate py-2 pe-3">{row.metric}</td>
                        <td className="py-2 pe-3">{row.amount}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </CardContent>
            </Card>
          )}

          {result.citations.length > 0 && (
            <Card className="glass-card">
              <CardHeader>
                <CardTitle className="text-base">{t("documents.citations")}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {result.citations.map((citation, index) => (
                  <div key={`${citation.page}-${index}`} className="rounded-lg border border-border/50 p-3 text-sm">
                    <p className="font-medium">
                      {t("documents.page")} {citation.page} — {citation.topic}
                    </p>
                    <SafeText text={citation.snippet} className="mt-1 text-muted-foreground" as="p" />
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
        </motion.div>
      )}
    </div>
  );
}
