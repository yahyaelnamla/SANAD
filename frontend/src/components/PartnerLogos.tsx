"use client";

import Image from "next/image";

import { useTranslations } from "@/hooks/useTranslations";
import { cn } from "@/lib/utils";

interface PartnerLogosProps {
  className?: string;
  variant?: "footer" | "splash" | "inline";
}

/** Fanar primary branding with QCRI & HBKU partner marks — always full-color artwork. */
export function PartnerLogos({ className, variant = "footer" }: PartnerLogosProps) {
  const { t } = useTranslations();
  const isSplash = variant === "splash";
  const isInline = variant === "inline";

  const fanarHeight = isSplash ? 56 : isInline ? 28 : 44;
  const partnerHeight = isSplash ? 32 : isInline ? 18 : 24;

  return (
    <div
      className={cn(
        "flex flex-wrap items-center justify-center gap-x-10 gap-y-4",
        isSplash && "flex-col sm:flex-row sm:gap-x-12",
        className,
      )}
    >
      <Image
        src="/icons/Fanar2.svg"
        alt="Fanar AI"
        width={fanarHeight * 2.5}
        height={fanarHeight}
        className="partner-logo h-auto w-auto object-contain"
        style={{ height: fanarHeight, width: "auto" }}
        priority={isSplash}
      />

      <div
        className={cn(
          "flex flex-wrap items-center justify-center gap-x-8 gap-y-3",
          isSplash && "opacity-95",
        )}
      >
        <Image
          src="/icons/QCRI.svg"
          alt={t("partners.qcriAlt")}
          width={partnerHeight * 5}
          height={partnerHeight}
          className="partner-logo partner-logo--subtle h-auto w-auto object-contain"
          style={{ height: partnerHeight, width: "auto" }}
          priority={isSplash}
        />
        <Image
          src="/icons/hbku.svg"
          alt="Hamad Bin Khalifa University"
          width={partnerHeight * 4}
          height={partnerHeight}
          className="partner-logo partner-logo--subtle h-auto w-auto object-contain"
          style={{ height: partnerHeight, width: "auto" }}
          priority={isSplash}
        />
      </div>
    </div>
  );
}
