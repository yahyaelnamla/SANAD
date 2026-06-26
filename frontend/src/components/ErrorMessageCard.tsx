"use client";

import { AlertCircle, RefreshCw, WifiOff } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useTranslations } from "@/hooks/useTranslations";
import { cn } from "@/lib/utils";

interface ErrorMessageCardProps {
  message: string;
  offline?: boolean;
  onRetry?: () => void;
  className?: string;
}

export function ErrorMessageCard({ message, offline, onRetry, className }: ErrorMessageCardProps) {
  const { t } = useTranslations();

  return (
    <div
      role="alert"
      className={cn(
        "rounded-xl border border-red-500/30 bg-red-500/5 px-4 py-3",
        className,
      )}
    >
      <div className="flex items-start gap-3">
        <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-red-500/10">
          {offline ? (
            <WifiOff className="h-4 w-4 text-red-400" aria-hidden />
          ) : (
            <AlertCircle className="h-4 w-4 text-red-400" aria-hidden />
          )}
        </div>
        <div className="min-w-0 flex-1 space-y-2">
          <p className="text-sm font-medium text-red-200">{offline ? t("errors.offline") : t("errors.title")}</p>
          <p className="text-sm leading-relaxed text-muted-foreground">{message}</p>
          {onRetry && (
            <Button
              type="button"
              variant="outline"
              size="sm"
              className="h-8 gap-2 border-red-500/30 text-red-200 hover:bg-red-500/10"
              onClick={onRetry}
            >
              <RefreshCw className="h-3.5 w-3.5" />
              {t("errors.retry")}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
