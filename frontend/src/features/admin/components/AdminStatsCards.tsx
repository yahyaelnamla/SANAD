"use client";

import { motion } from "framer-motion";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useTranslations } from "@/hooks/useTranslations";
import type { AdminStats } from "@/types/source";

interface AdminStatsCardsProps {
  stats: AdminStats;
}

export function AdminStatsCards({ stats }: AdminStatsCardsProps) {
  const { t } = useTranslations();

  const cards = [
    { key: "total", value: stats.total_sources, label: t("admin.statsTotal") },
    {
      key: "authenticated",
      value: stats.authenticated_sources,
      label: t("admin.statsAuthenticated"),
    },
    { key: "pending", value: stats.pending_sources, label: t("admin.statsPending") },
  ];

  return (
    <div className="grid gap-4 sm:grid-cols-3">
      {cards.map((card, index) => (
        <motion.div
          key={card.key}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.08 }}
        >
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {card.label}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-3xl font-bold">{card.value}</p>
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </div>
  );
}
