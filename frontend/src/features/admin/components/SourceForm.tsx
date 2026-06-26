"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { useTranslations } from "@/hooks/useTranslations";
import type { Source, SourceCreatePayload, SourceType } from "@/types/source";

const SOURCE_TYPES: SourceType[] = ["classical", "contemporary", "standard", "fatwa"];

interface SourceFormProps {
  initial?: Source;
  onSubmit: (payload: SourceCreatePayload) => Promise<void>;
  onCancel: () => void;
}

export function SourceForm({ initial, onSubmit, onCancel }: SourceFormProps) {
  const { t } = useTranslations();
  const [title, setTitle] = useState(initial?.title ?? "");
  const [author, setAuthor] = useState(initial?.author ?? "");
  const [sourceType, setSourceType] = useState<SourceType>(initial?.source_type ?? "classical");
  const [language, setLanguage] = useState<"ar" | "en">(initial?.language ?? "ar");
  const [url, setUrl] = useState(initial?.url ?? "");
  const [isAuthenticated, setIsAuthenticated] = useState(initial?.is_authenticated ?? false);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    try {
      await onSubmit({
        title,
        author,
        source_type: sourceType,
        language,
        url: url.trim() || undefined,
        is_authenticated: isAuthenticated,
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-lg border bg-card p-4 shadow-sm">
      <div className="grid gap-4 md:grid-cols-2">
        <div className="space-y-2">
          <label className="text-sm font-medium">{t("admin.formTitle")}</label>
          <Input value={title} onChange={(e) => setTitle(e.target.value)} required />
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium">{t("admin.formAuthor")}</label>
          <Input value={author} onChange={(e) => setAuthor(e.target.value)} required />
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium">{t("admin.formType")}</label>
          <select
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            value={sourceType}
            onChange={(e) => setSourceType(e.target.value as SourceType)}
          >
            {SOURCE_TYPES.map((type) => (
              <option key={type} value={type}>
                {t(`admin.sourceTypes.${type}`)}
              </option>
            ))}
          </select>
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium">{t("admin.formLanguage")}</label>
          <select
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            value={language}
            onChange={(e) => setLanguage(e.target.value as "ar" | "en")}
          >
            <option value="ar">{t("admin.languageAr")}</option>
            <option value="en">{t("admin.languageEn")}</option>
          </select>
        </div>
        <div className="space-y-2 md:col-span-2">
          <label className="text-sm font-medium">{t("admin.formUrl")}</label>
          <Input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://"
          />
        </div>
      </div>

      <div className="flex items-center justify-between rounded-md border px-3 py-2">
        <div>
          <p className="text-sm font-medium">{t("admin.formAuthenticated")}</p>
          <p className="text-xs text-muted-foreground">{t("admin.formAuthenticatedHint")}</p>
        </div>
        <Switch checked={isAuthenticated} onCheckedChange={setIsAuthenticated} />
      </div>

      <div className="flex flex-wrap gap-2">
        <Button type="submit" disabled={submitting}>
          {initial ? t("admin.saveSource") : t("admin.addSource")}
        </Button>
        <Button type="button" variant="outline" onClick={onCancel}>
          {t("admin.cancel")}
        </Button>
      </div>
    </form>
  );
}
