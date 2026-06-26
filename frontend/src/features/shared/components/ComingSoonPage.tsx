"use client";

import { motion } from "framer-motion";
import { Sparkles } from "lucide-react";

import { useTranslations } from "@/hooks/useTranslations";

interface ComingSoonPageProps {
  titleKey: string;
  descriptionKey: string;
}

export function ComingSoonPage({ titleKey, descriptionKey }: ComingSoonPageProps) {
  const { t } = useTranslations();

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="mx-auto flex max-w-2xl flex-col items-center justify-center py-20 text-center"
    >
      <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-cyan-500/10 ring-1 ring-cyan-500/20">
        <Sparkles className="h-8 w-8 text-cyan-400" />
      </div>
      <h1 className="text-2xl font-bold tracking-tight">{t(titleKey)}</h1>
      <p className="mt-3 max-w-md text-sm leading-relaxed text-muted-foreground">{t(descriptionKey)}</p>
      <span className="mt-6 rounded-full border border-cyan-500/30 bg-cyan-500/10 px-4 py-1.5 text-xs font-medium text-cyan-300">
        {t("common.comingSoon")}
      </span>
    </motion.div>
  );
}
