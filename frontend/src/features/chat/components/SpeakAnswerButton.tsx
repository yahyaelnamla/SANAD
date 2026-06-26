"use client";

import { Volume2, VolumeX, Loader2 } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { useTranslations } from "@/hooks/useTranslations";
import { detectContentLanguage } from "@/lib/detectLanguage";
import { cn } from "@/lib/utils";
import { synthesizeSpeech } from "@/services/featuresService";

interface SpeakAnswerButtonProps {
  text: string;
  language: string;
  accessToken: string;
  className?: string;
}

export function SpeakAnswerButton({
  text,
  language,
  accessToken,
  className,
}: SpeakAnswerButtonProps) {
  const { t } = useTranslations();
  const [speaking, setSpeaking] = useState(false);
  const [loading, setLoading] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const objectUrlRef = useRef<string | null>(null);

  const cleanup = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    if (objectUrlRef.current) {
      URL.revokeObjectURL(objectUrlRef.current);
      objectUrlRef.current = null;
    }
    setSpeaking(false);
  }, []);

  useEffect(() => cleanup, [cleanup]);

  const stop = useCallback(() => {
    cleanup();
  }, [cleanup]);

  const speak = useCallback(async () => {
    if (!text.trim() || loading) return;

    if (speaking) {
      stop();
      return;
    }

    setLoading(true);
    try {
      const speechLang = detectContentLanguage(text, language === "ar" ? "ar" : "en");
      const blob = await synthesizeSpeech(
        accessToken,
        text,
        speechLang === "ar" ? "ar" : "en",
      );
      cleanup();
      const url = URL.createObjectURL(blob);
      objectUrlRef.current = url;
      const audio = new Audio(url);
      audioRef.current = audio;
      audio.onended = () => cleanup();
      audio.onerror = () => cleanup();
      setSpeaking(true);
      await audio.play();
    } catch {
      cleanup();
    } finally {
      setLoading(false);
    }
  }, [accessToken, cleanup, language, loading, speaking, stop, text]);

  return (
    <Button
      type="button"
      variant="ghost"
      size="sm"
      className={cn("h-7 gap-1 px-2 text-xs", speaking && "text-cyan-400", className)}
      disabled={!text.trim() || loading}
      aria-label={speaking ? t("chatActions.stopSpeaking") : t("chatActions.listen")}
      aria-pressed={speaking}
      onClick={() => void speak()}
    >
      {loading ? (
        <Loader2 className="h-3 w-3 animate-spin" />
      ) : speaking ? (
        <VolumeX className="h-3 w-3" />
      ) : (
        <Volume2 className="h-3 w-3" />
      )}
      {loading
        ? t("chatActions.generatingAudio")
        : speaking
          ? t("chatActions.stopSpeaking")
          : t("chatActions.listen")}
    </Button>
  );
}
