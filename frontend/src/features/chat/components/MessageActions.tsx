"use client";

import {
  Bookmark,
  BookmarkCheck,
  Download,
  RefreshCw,
  Share2,
  ThumbsDown,
  ThumbsUp,
} from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { downloadMarkdown, downloadPdf } from "@/lib/exportResponse";
import { useTranslations } from "@/hooks/useTranslations";
import { cn } from "@/lib/utils";
import { useBookmarkStore } from "@/store/bookmarkStore";
import { useFeedbackStore } from "@/store/feedbackStore";
import { useUserPreferences } from "@/hooks/useUserPreferences";
import { TranslateAnswerButton } from "@/features/chat/components/TranslateAnswerButton";
import { SpeakAnswerButton } from "@/features/chat/components/SpeakAnswerButton";
import { SourcesPillButton } from "@/features/chat/components/SourcesPillButton";
import type { QueryResult } from "@/types/query";

interface MessageActionsProps {
  result: QueryResult;
  accessToken: string;
  displayText: string;
  originalText: string;
  sourceLanguage: string;
  onRegenerate?: () => void;
  onTranslated?: (translated: string, targetLang: string) => void;
  onClearTranslation?: () => void;
  activeTranslationLang?: string | null;
  onOpenSources?: () => void;
  className?: string;
}

export function MessageActions({
  result,
  accessToken,
  displayText,
  originalText,
  sourceLanguage,
  onRegenerate,
  onTranslated,
  onClearTranslation,
  activeTranslationLang,
  onOpenSources,
  className,
}: MessageActionsProps) {
  const { t } = useTranslations();
  const { save } = useUserPreferences();
  const { toggleBookmark, isBookmarked, toServerPayload } = useBookmarkStore();
  const { setFeedback, getFeedback } = useFeedbackStore();
  const [shareStatus, setShareStatus] = useState<string | null>(null);

  const bookmarked = isBookmarked(result.query_id);
  const feedback = getFeedback(result.query_id);

  const handleShare = async () => {
    const shareUrl =
      typeof window !== "undefined"
        ? `${window.location.origin}/history/${result.query_id}`
        : `/history/${result.query_id}`;
    const shareData = {
      title: "SANAD",
      text: result.summary ?? result.question,
      url: shareUrl,
    };

    try {
      if (typeof navigator !== "undefined" && navigator.share) {
        await navigator.share(shareData);
        setShareStatus(t("chatActions.shared"));
      } else if (typeof navigator !== "undefined" && navigator.clipboard) {
        await navigator.clipboard.writeText(`${shareData.text}\n${shareUrl}`);
        setShareStatus(t("chatActions.linkCopied"));
      }
    } catch {
      setShareStatus(null);
      return;
    }

    window.setTimeout(() => setShareStatus(null), 2000);
  };

  return (
    <div className={cn("flex flex-wrap items-center gap-1", className)}>
      <Button
        type="button"
        variant="ghost"
        size="sm"
        className="h-7 gap-1 px-2 text-xs"
        onClick={() => void handleShare()}
      >
        <Share2 className="h-3 w-3" />
        {shareStatus ?? t("chatActions.share")}
      </Button>

      <Button
        type="button"
        variant="ghost"
        size="sm"
        className="h-7 gap-1 px-2 text-xs"
        onClick={() => downloadMarkdown(result)}
      >
        <Download className="h-3 w-3" />
        {t("chatActions.exportMarkdown")}
      </Button>

      <Button
        type="button"
        variant="ghost"
        size="sm"
        className="h-7 gap-1 px-2 text-xs"
        onClick={() => downloadPdf(result)}
      >
        <Download className="h-3 w-3" />
        {t("chatActions.exportPdf")}
      </Button>

      {onTranslated && (
        <TranslateAnswerButton
          accessToken={accessToken}
          text={originalText}
          sourceLanguage={sourceLanguage}
          onTranslated={onTranslated}
          onClear={onClearTranslation}
          activeTranslationLang={activeTranslationLang}
        />
      )}

      <SpeakAnswerButton
        text={displayText}
        language={activeTranslationLang ?? sourceLanguage}
        accessToken={accessToken}
      />

      {onOpenSources && <SourcesPillButton result={result} onClick={onOpenSources} />}

      <Button
        type="button"
        variant="ghost"
        size="sm"
        className={cn("h-7 gap-1 px-2 text-xs", bookmarked && "text-cyan-400")}
        onClick={() => {
          toggleBookmark(result);
          void save({ bookmarks: toServerPayload() });
        }}
      >
        {bookmarked ? <BookmarkCheck className="h-3 w-3" /> : <Bookmark className="h-3 w-3" />}
        {bookmarked ? t("chatActions.bookmarked") : t("chatActions.bookmark")}
      </Button>

      {onRegenerate && (
        <Button
          type="button"
          variant="ghost"
          size="sm"
          className="h-7 gap-1 px-2 text-xs"
          onClick={onRegenerate}
        >
          <RefreshCw className="h-3 w-3" />
          {t("chatActions.regenerate")}
        </Button>
      )}

      <div className="ms-1 flex items-center gap-0.5 border-s border-border/40 ps-2">
        <Button
          type="button"
          variant="ghost"
          size="sm"
          className={cn("h-7 px-2", feedback === "up" && "text-emerald-400")}
          aria-label={t("chatActions.helpful")}
          onClick={() => setFeedback(result.query_id, "up")}
        >
          <ThumbsUp className="h-3 w-3" />
        </Button>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          className={cn("h-7 px-2", feedback === "down" && "text-destructive")}
          aria-label={t("chatActions.notHelpful")}
          onClick={() => setFeedback(result.query_id, "down")}
        >
          <ThumbsDown className="h-3 w-3" />
        </Button>
      </div>
    </div>
  );
}
