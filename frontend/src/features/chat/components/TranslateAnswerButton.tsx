"use client";

import { Languages, Loader2, X } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { useTranslations } from "@/hooks/useTranslations";
import { detectContentLanguage } from "@/lib/detectLanguage";
import { cn } from "@/lib/utils";
import { translateText } from "@/services/featuresService";
import { ApiClientError } from "@/services/apiClient";

const TARGET_LANGUAGES = [
  { code: "ar", label: "العربية" },
  { code: "en", label: "English" },
  { code: "fr", label: "Français" },
  { code: "ur", label: "اردو" },
  { code: "tr", label: "Türkçe" },
  { code: "ms", label: "Bahasa Melayu" },
] as const;

interface TranslateAnswerButtonProps {
  accessToken: string;
  text: string;
  sourceLanguage: string;
  onTranslated: (translated: string, targetLang: string) => void;
  onClear?: () => void;
  activeTranslationLang?: string | null;
  className?: string;
}

export function TranslateAnswerButton({
  accessToken,
  text,
  sourceLanguage,
  onTranslated,
  onClear,
  activeTranslationLang,
  className,
}: TranslateAnswerButtonProps) {
  const { t } = useTranslations();
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const resolvedSource = detectContentLanguage(text, sourceLanguage);

  const handleTranslate = async (target: string) => {
    if (loading || target === resolvedSource) return;
    setLoading(true);
    setError(null);
    try {
      const { translated_text } = await translateText(
        accessToken,
        text,
        target,
        resolvedSource,
      );
      if (!translated_text?.trim()) {
        throw new Error(t("chatActions.translationFailed"));
      }
      const translatedLang = detectContentLanguage(translated_text, target);
      if (translatedLang === resolvedSource) {
        throw new Error(t("chatActions.translationFailed"));
      }
      onTranslated(translated_text, target);
      setOpen(false);
    } catch (err) {
      const message =
        err instanceof ApiClientError
          ? err.message
          : err instanceof Error
            ? err.message
            : t("chatActions.translationFailed");
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={cn("relative inline-flex flex-col", className)}>
      <div className="inline-flex">
        <Button
          type="button"
          variant="ghost"
          size="sm"
          className="h-7 gap-1 px-2 text-xs"
          disabled={loading || !text.trim()}
          aria-label={t("chatActions.translate")}
          aria-expanded={open}
          onClick={() => setOpen((value) => !value)}
        >
          {loading ? <Loader2 className="h-3 w-3 animate-spin" /> : <Languages className="h-3 w-3" />}
          {activeTranslationLang ? t("chatActions.translated") : t("chatActions.translate")}
        </Button>

        {activeTranslationLang && onClear && (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            className="h-7 px-1.5 text-xs text-muted-foreground"
            aria-label={t("chatActions.showOriginal")}
            onClick={onClear}
          >
            <X className="h-3 w-3" />
          </Button>
        )}
      </div>

      {error && <p className="mt-1 max-w-[14rem] text-[10px] text-destructive">{error}</p>}

      {open && (
        <div
          role="menu"
          className="absolute bottom-full start-0 z-50 mb-1 min-w-[11rem] rounded-xl border border-border/60 bg-card p-1 shadow-xl"
        >
          {TARGET_LANGUAGES.map((lang) => (
            <button
              key={lang.code}
              type="button"
              role="menuitem"
              disabled={lang.code === resolvedSource || loading}
              className="flex w-full rounded-lg px-3 py-2 text-start text-xs transition-colors hover:bg-muted/60 disabled:opacity-40"
              onClick={() => void handleTranslate(lang.code)}
            >
              {lang.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
