"use client";

import { PartnerLogos } from "@/components/PartnerLogos";
import { useHealthCheck } from "@/hooks/useHealthCheck";
import { useTranslations } from "@/hooks/useTranslations";

export function Footer() {
  const { t } = useTranslations();
  const { health, version } = useHealthCheck();

  const statusLabel =
    health === "healthy"
      ? t("app.statusHealthy")
      : health === "degraded"
        ? t("app.statusDegraded")
        : health === "offline"
          ? t("app.statusOffline")
          : t("app.statusChecking");

  const statusColor =
    health === "healthy"
      ? "text-emerald-400"
      : health === "degraded"
        ? "text-amber-400"
        : health === "offline"
          ? "text-destructive"
          : "text-muted-foreground";

  return (
    <footer className="theme-zone-dark border-t border-border/40 bg-background py-5">
      <div className="mx-auto flex max-w-6xl flex-col items-center gap-3 px-4 text-center text-sm text-muted-foreground">
        <PartnerLogos variant="footer" />
        <p className="max-w-xl text-xs leading-relaxed">{t("app.footer")}</p>
        <div className="flex flex-wrap items-center justify-center gap-x-3 gap-y-1 text-xs">
          {version && (
            <span>
              {t("app.version")}: <span className="font-mono text-foreground/80">{version}</span>
            </span>
          )}
          <span className="inline-flex items-center gap-1.5">
            <span
              className={`inline-block h-1.5 w-1.5 rounded-full ${
                health === "healthy"
                  ? "bg-emerald-400"
                  : health === "degraded"
                    ? "bg-amber-400"
                    : health === "offline"
                      ? "bg-destructive"
                      : "bg-muted-foreground animate-pulse"
              }`}
              aria-hidden
            />
            <span className={statusColor}>{statusLabel}</span>
          </span>
        </div>
      </div>
    </footer>
  );
}
