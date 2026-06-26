"use client";

import { AnimatePresence, motion } from "framer-motion";
import Image from "next/image";
import { useEffect, useState } from "react";

import { useTranslations } from "@/hooks/useTranslations";

const SPLASH_KEY = "sanad_splash_shown";

export function SplashScreen() {
  const { t } = useTranslations();
  const [visible, setVisible] = useState(false);
  const [phase, setPhase] = useState(0);

  useEffect(() => {
    if (typeof window === "undefined") return;
    if (sessionStorage.getItem(SPLASH_KEY)) return;
    setVisible(true);
    const phaseTimer = window.setTimeout(() => setPhase(1), 600);
    const hideTimer = window.setTimeout(() => {
      sessionStorage.setItem(SPLASH_KEY, "1");
      setVisible(false);
    }, 3200);
    return () => {
      window.clearTimeout(phaseTimer);
      window.clearTimeout(hideTimer);
    };
  }, []);

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.5 }}
          className="fixed inset-0 z-[100] flex flex-col items-center justify-center gap-8 bg-background"
        >
          <motion.div
            initial={{ scale: 0.7, opacity: 0, y: 12 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
            className="relative flex flex-col items-center gap-6 px-6"
          >
            <motion.div
              animate={{ y: [0, -6, 0] }}
              transition={{ duration: 2.4, repeat: Infinity, ease: "easeInOut" }}
            >
              <Image
                src="/icons/Fanar2.svg"
                alt="Fanar"
                width={160}
                height={80}
                priority
                className="partner-logo h-16 w-auto object-contain sm:h-20"
              />
            </motion.div>

            <div className="text-center">
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.35 }}
                className="text-lg font-bold tracking-tight nexus-gradient-text"
              >
                {t("app.name")}
              </motion.p>

              <motion.div
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: phase >= 1 ? 1 : 0, y: phase >= 1 ? 0 : 6 }}
                transition={{ duration: 0.5 }}
                className="mt-3 flex items-center justify-center gap-1.5 text-xs font-medium tracking-[0.2em] text-muted-foreground uppercase"
              >
                <span>{t("splash.poweredBy")}</span>
                <span className="font-bold tracking-widest text-brand-accent">{t("splash.fanarAi")}</span>
              </motion.div>
            </div>
          </motion.div>

          <motion.div
            className="h-1 w-40 overflow-hidden rounded-full bg-border/40"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            <motion.div
              className="h-full rounded-full bg-brand-accent"
              initial={{ width: "0%" }}
              animate={{ width: "100%" }}
              transition={{ duration: 2.8, ease: "easeInOut" }}
            />
          </motion.div>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.7 }}
            transition={{ delay: 0.5 }}
            className="text-xs text-muted-foreground"
          >
            {t("splash.loading")}
          </motion.p>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
