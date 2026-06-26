"use client";

import { Loader2, Play, SendHorizonal, Trash2 } from "lucide-react";
import { useEffect, useRef } from "react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { VoiceWaveform } from "@/features/chat/components/VoiceWaveform";
import { useTranslations } from "@/hooks/useTranslations";

interface VoiceTranscriptReviewProps {
  audioUrl: string;
  transcript: string;
  transcribing?: boolean;
  onTranscriptChange: (value: string) => void;
  onSubmit: () => void;
  onDiscard: () => void;
}

export function VoiceTranscriptReview({
  audioUrl,
  transcript,
  transcribing,
  onTranscriptChange,
  onSubmit,
  onDiscard,
}: VoiceTranscriptReviewProps) {
  const { t } = useTranslations();
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
      }
    };
  }, []);

  const playRecording = () => {
    if (!audioRef.current) {
      audioRef.current = new Audio(audioUrl);
    }
    void audioRef.current.play();
  };

  return (
    <div className="mb-3 space-y-3 rounded-xl border border-cyan-500/20 bg-cyan-500/5 p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <VoiceWaveform />
          <span className="text-xs font-medium text-cyan-300">{t("chat.voiceReview")}</span>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="h-8 gap-1 border-cyan-500/30"
            onClick={playRecording}
            disabled={transcribing}
          >
            <Play className="h-3 w-3" />
            {t("chat.playRecording")}
          </Button>
          <Button
            type="button"
            variant="ghost"
            size="sm"
            className="h-8 gap-1 text-muted-foreground"
            onClick={onDiscard}
          >
            <Trash2 className="h-3 w-3" />
            {t("chat.discardTranscript")}
          </Button>
        </div>
      </div>

      {transcribing ? (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin text-cyan-400" />
          {t("chat.transcribing")}
        </div>
      ) : (
        <>
          <Textarea
            value={transcript}
            onChange={(e) => onTranscriptChange(e.target.value)}
            placeholder={t("chat.editTranscript")}
            className="min-h-[72px] resize-none border-border/50 bg-background/60 text-sm"
            aria-label={t("chat.editTranscript")}
          />
          <Button
            type="button"
            size="sm"
            className="gap-2 bg-gradient-to-r from-cyan-500 to-teal-500 text-slate-950 hover:from-cyan-400 hover:to-teal-400"
            disabled={!transcript.trim()}
            onClick={onSubmit}
          >
            <SendHorizonal className="h-3.5 w-3.5" />
            {t("chat.submitTranscript")}
          </Button>
        </>
      )}
    </div>
  );
}
