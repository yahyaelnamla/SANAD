"use client";

import { HelpCircle, X } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import { useTranslations } from "@/hooks/useTranslations";
import { cn } from "@/lib/utils";

interface PageGuideProps {
  pageKey: string;
  className?: string;
  /** Inline button in a toolbar row — avoids overlapping other controls. */
  inline?: boolean;
}

export function PageGuide({ pageKey, className, inline = false }: PageGuideProps) {
  const { t } = useTranslations();
  const [open, setOpen] = useState(false);
  const titleKey = `pageGuide.${pageKey}.title`;
  const bodyKey = `pageGuide.${pageKey}.body`;
  const title = t(titleKey);
  const body = t(bodyKey);

  if (title === titleKey) return null;

  return (
    <>
      <Button
        type="button"
        variant="outline"
        size="icon"
        className={cn(
          inline
            ? "h-8 w-8 shrink-0 rounded-full border-border/60 bg-background/80"
            : "absolute end-0 top-0 z-10 h-9 w-9 rounded-full border-border/60 bg-background/80 shadow-sm backdrop-blur-sm",
          className,
        )}
        onClick={() => setOpen(true)}
        aria-label={t("pageGuide.open")}
      >
        <HelpCircle className="h-4 w-4 text-cyan-400" />
      </Button>

      {open && (
        <div
          className="fixed inset-0 z-[80] flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm"
          role="dialog"
          aria-modal="true"
          aria-labelledby="page-guide-title"
          onClick={() => setOpen(false)}
        >
          <div
            className="glass-card relative max-h-[min(80vh,520px)] w-full max-w-md overflow-y-auto p-5 shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="absolute end-2 top-2 h-8 w-8"
              onClick={() => setOpen(false)}
              aria-label={t("pageGuide.close")}
            >
              <X className="h-4 w-4" />
            </Button>
            <h2 id="page-guide-title" className="pe-8 text-lg font-semibold">
              {title}
            </h2>
            <p className="mt-3 whitespace-pre-line text-sm leading-relaxed text-muted-foreground">
              {body}
            </p>
            <div className="mt-5 flex justify-end">
              <Button type="button" size="sm" onClick={() => setOpen(false)}>
                {t("pageGuide.dismiss")}
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

interface PageLayoutProps {
  guideKey?: string;
  children: React.ReactNode;
  className?: string;
}

/** Wraps page content with a help button in a dedicated header row. */
export function PageLayout({ guideKey, children, className }: PageLayoutProps) {
  return (
    <div className={cn(className)}>
      {guideKey && (
        <div className="mb-4 flex justify-end">
          <PageGuide pageKey={guideKey} inline />
        </div>
      )}
      {children}
    </div>
  );
}
