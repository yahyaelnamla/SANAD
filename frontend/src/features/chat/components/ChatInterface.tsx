"use client";

import { motion } from "framer-motion";
import { Check, Copy, Loader2, Mic, MicOff, Search, SendHorizonal, User, X } from "lucide-react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";

import { Button } from "@/components/ui/button";
import { ErrorMessageCard } from "@/components/ErrorMessageCard";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Textarea } from "@/components/ui/textarea";
import { ExplainabilityPanel } from "@/features/chat/components/ExplainabilityPanel";
import { AgentTraceTimeline } from "@/features/chat/components/AgentTraceTimeline";
import { AnswerContent } from "@/features/chat/components/AnswerContent";
import { ChatModeToggle } from "@/features/chat/components/ChatModeToggle";
import { FanarModelSelector } from "@/features/chat/components/FanarModelSelector";
import { PageGuide } from "@/components/PageGuide";
import { MessageActions } from "@/features/chat/components/MessageActions";
import { SourcesSidePanel } from "@/features/chat/components/SourcesSidePanel";
import { SuggestedQuestions } from "@/features/chat/components/SuggestedQuestions";
import { VoiceTranscriptReview } from "@/features/chat/components/VoiceTranscriptReview";
import { VoiceWaveform } from "@/features/chat/components/VoiceWaveform";
import { useAuth } from "@/hooks/useAuth";
import { useOnlineStatus } from "@/hooks/useOnlineStatus";
import { useTranslations } from "@/hooks/useTranslations";
import { useUserPreferences } from "@/hooks/useUserPreferences";
import { cn } from "@/lib/utils";
import {
  answerDisplayText,
  buildConversationHistory,
  threadToChatMessages,
} from "@/lib/chatSessionUtils";
import { detectContentLanguage } from "@/lib/detectLanguage";
import { sanitizeUserFacingText } from "@/lib/sanitizeResponse";
import { getConversationThread } from "@/services/conversationService";
import { transcribeAudio } from "@/services/audioService";
import { ApiClientError } from "@/services/apiClient";
import { submitQuery } from "@/services/queryService";
import { useConversationStore } from "@/store/conversationStore";
import { useOfflineQueryStore } from "@/store/offlineQueryStore";
import { useSettingsStore } from "@/store/settingsStore";
import type { ChatMessage, QueryResult } from "@/types/query";

function createId() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

interface VoiceReviewState {
  audioUrl: string;
  transcript: string;
  transcribing: boolean;
}

function formatTimestamp(date = new Date()) {
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function ChatSkeleton() {
  return (
    <div className="space-y-3 py-2">
      <div className="h-3 w-3/4 rounded-md shimmer" />
      <div className="h-3 w-full rounded-md shimmer" />
      <div className="h-3 w-5/6 rounded-md shimmer" />
    </div>
  );
}

function isDocumentQuestion(text: string): boolean {
  const lowered = text.toLowerCase();
  return (
    lowered.includes("document") ||
    lowered.includes("pdf") ||
    lowered.includes("report") ||
    lowered.includes("annual") ||
    lowered.includes("uploaded") ||
    lowered.includes("page ") ||
    lowered.includes("chapter") ||
    text.includes("مستند") ||
    text.includes("تقرير") ||
    text.includes("صفحة")
  );
}

export function ChatInterface() {
  const { t, locale } = useTranslations();
  const searchParams = useSearchParams();
  const { accessToken, user } = useAuth();
  const { preferences } = useUserPreferences();
  const online = useOnlineStatus();
  const sessionId = useConversationStore((state) => state.sessionId);
  const ownerUserId = useConversationStore((state) => state.ownerUserId);
  const bindSessionToUser = useConversationStore((state) => state.bindSessionToUser);
  const setSessionId = useConversationStore((state) => state.setSessionId);
  const setSessionMessages = useConversationStore((state) => state.setSessionMessages);
  const enqueueOffline = useOfflineQueryStore((state) => state.enqueue);
  const advancedAnalysisMode = useSettingsStore((state) => state.advancedAnalysisMode);
  const fanarModelPreference = useSettingsStore((state) => state.fanarModelPreference);
  const abortRef = useRef<AbortController | null>(null);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [recording, setRecording] = useState(false);
  const [voiceReview, setVoiceReview] = useState<VoiceReviewState | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [sourcesPanelResult, setSourcesPanelResult] = useState<QueryResult | null>(null);
  const [sessionLoading, setSessionLoading] = useState(false);
  const [chatSearch, setChatSearch] = useState("");
  const loadedSessionRef = useRef<string | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const prefilledRef = useRef(false);

  useEffect(() => {
    if (searchParams.get("new") === "1") {
      setMessages([]);
      setInput("");
      setChatSearch("");
      loadedSessionRef.current = null;
      useConversationStore.getState().resetSession();
      if (typeof window !== "undefined") {
        window.history.replaceState({}, "", "/chat");
      }
    }
  }, [searchParams]);

  useEffect(() => {
    const requestedSession = searchParams.get("session");
    if (requestedSession && requestedSession !== sessionId) {
      setSessionId(requestedSession);
      loadedSessionRef.current = null;
    }
  }, [searchParams, sessionId, setSessionId]);

  useEffect(() => {
    if (user?.id) {
      bindSessionToUser(user.id);
    }
  }, [user?.id, bindSessionToUser]);

  useEffect(() => {
    if (!sessionId || loadedSessionRef.current === sessionId) return;

    if (!accessToken || !user?.id) {
      setMessages([]);
      loadedSessionRef.current = sessionId;
      return;
    }

    if (ownerUserId && ownerUserId !== user.id) {
      setMessages([]);
      loadedSessionRef.current = sessionId;
      return;
    }

    let cancelled = false;
    setSessionLoading(true);
    setMessages([]);

    void getConversationThread(sessionId, accessToken)
      .then((thread) => {
        if (cancelled) return;
        const restored = threadToChatMessages(thread);
        setMessages(restored);
        setSessionMessages(sessionId, restored);
        loadedSessionRef.current = sessionId;
      })
      .catch(() => {
        if (!cancelled) {
          setMessages([]);
          loadedSessionRef.current = sessionId;
        }
      })
      .finally(() => {
        if (!cancelled) setSessionLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [sessionId, accessToken, user?.id, ownerUserId, setSessionMessages]);

  useEffect(() => {
    const stable = messages.filter((message) => !message.loading && !message.error);
    if (stable.length > 0) {
      setSessionMessages(sessionId, stable);
    }
  }, [messages, sessionId, setSessionMessages]);

  useEffect(() => {
    if (prefilledRef.current) return;
    const preset = searchParams.get("q");
    if (preset?.trim()) {
      setInput(preset.trim());
      prefilledRef.current = true;
    }
  }, [searchParams]);

  const userDisplayName = useMemo(() => {
    const saved = preferences?.display_name?.trim();
    if (saved) return saved;
    const local = user?.email?.split("@")[0]?.trim();
    if (local) return local;
    return t("chat.userLabel");
  }, [preferences?.display_name, user?.email, t]);

  const welcomeTitle = useMemo(() => {
    const saved = preferences?.display_name?.trim();
    if (saved) {
      return locale === "ar" ? `مرحباً، ${saved}` : `Welcome, ${saved}`;
    }
    return t("chat.welcome");
  }, [locale, preferences?.display_name, t]);

  const showDocumentHint = useMemo(
    () => isDocumentQuestion(input) || isDocumentQuestion(chatSearch),
    [input, chatSearch],
  );

  const filteredMessages = useMemo(() => {
    const query = chatSearch.trim().toLowerCase();
    if (!query) return messages;
    return messages.filter(
      (message) =>
        message.content.toLowerCase().includes(query) ||
        message.result?.summary?.toLowerCase().includes(query) ||
        message.result?.question.toLowerCase().includes(query),
    );
  }, [chatSearch, messages]);

  const clearVoiceReview = useCallback(() => {
    setVoiceReview((current) => {
      if (current?.audioUrl) {
        URL.revokeObjectURL(current.audioUrl);
      }
      return null;
    });
  }, []);

  const stopRecording = useCallback(() => {
    mediaRecorderRef.current?.stop();
    setRecording(false);
  }, []);

  const startRecording = useCallback(async () => {
    if (!accessToken || recording) return;
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      chunksRef.current = [];
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };
      recorder.onstop = async () => {
        stream.getTracks().forEach((track) => track.stop());
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        if (blob.size < 100) return;

        const audioUrl = URL.createObjectURL(blob);
        setVoiceReview({ audioUrl, transcript: "", transcribing: true });

        try {
          const { text } = await transcribeAudio(blob, accessToken, locale);
          const trimmed = text.trim();
          setVoiceReview((current) =>
            current ? { ...current, transcript: trimmed, transcribing: false } : null,
          );
          if (!trimmed) {
            setInput(t("chat.voiceError"));
          }
        } catch {
          setVoiceReview((current) =>
            current ? { ...current, transcript: "", transcribing: false } : null,
          );
          setInput(t("chat.voiceError"));
        }
      };
      mediaRecorderRef.current = recorder;
      recorder.start();
      setRecording(true);
    } catch {
      setInput(t("chat.micPermission"));
    }
  }, [accessToken, locale, recording, t]);

  const copyMessage = async (messageId: string, content: string) => {
    await navigator.clipboard.writeText(content);
    setCopiedId(messageId);
    window.setTimeout(() => setCopiedId(null), 1500);
  };

  const runQuery = async (question: string) => {
    if (!question.trim() || loading) return;

    if (!online) {
      enqueueOffline({
        question: question.trim(),
        language: locale,
        session_id: sessionId,
        conversation_history: buildConversationHistory(messages),
        advanced_analysis: advancedAnalysisMode,
        fanar_model: fanarModelPreference,
      });
      setMessages((prev) => [
        ...prev,
        {
          id: createId(),
          role: "user",
          content: question.trim(),
          createdAt: new Date().toISOString(),
        },
        {
          id: createId(),
          role: "assistant",
          content: t("errors.offlineQueued"),
          createdAt: new Date().toISOString(),
        },
      ]);
      setInput("");
      return;
    }

    if (!accessToken) {
      setMessages((prev) => [
        ...prev,
        {
          id: createId(),
          role: "assistant",
          content: t("errors.unauthorized"),
          error: t("errors.unauthorized"),
          createdAt: new Date().toISOString(),
        },
      ]);
      return;
    }

    const userMessage: ChatMessage = {
      id: createId(),
      role: "user",
      content: question.trim(),
      createdAt: new Date().toISOString(),
    };
    const loadingMessage: ChatMessage = {
      id: createId(),
      role: "assistant",
      content: "",
      loading: true,
      streaming: true,
      createdAt: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage, loadingMessage]);
    setInput("");
    setLoading(true);
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const result = await submitQuery(
        {
          question: question.trim(),
          language: locale,
          session_id: sessionId,
          conversation_history: buildConversationHistory(messages),
          advanced_analysis: advancedAnalysisMode,
          fanar_model: fanarModelPreference,
        },
        accessToken,
        {
          onProgress: (progress) => {
            setMessages((prev) =>
              prev.map((message) =>
                message.loading
                  ? {
                      ...message,
                      result: {
                        ...(message.result ?? {
                          query_id: progress.query_id,
                          status: progress.status,
                          question: question.trim(),
                          language: locale,
                          evidence: [],
                          principles: [],
                          opinions: [],
                          sources: [],
                          confidence: 0,
                          refused: false,
                          created_at: new Date().toISOString(),
                        }),
                        ...progress,
                        agent_trace:
                          progress.agent_trace && progress.agent_trace.length > 0
                            ? progress.agent_trace
                            : message.result?.agent_trace,
                      },
                    }
                  : message,
              ),
            );
          },
          onDraftToken: () => {
            // Draft reasoning text is kept server-side; answer shows only after full pipeline completion.
          },
          onToken: () => {
            // Final token replay happens after all agents (including ResponseBuilder) finish.
          },
          onSection: () => {
            setMessages((prev) =>
              prev.map((message) =>
                message.loading ? { ...message, streaming: false } : message,
              ),
            );
          },
        },
        controller.signal,
      );

      const assistantId = createId();

      const assistantText = result.refused
        ? (result.refusal_reason ?? result.summary ?? t("refusal.noEvidence"))
        : answerDisplayText(result, result.refusal_reason ?? t("refusal.noEvidence"));

      setMessages((prev) => {
        const withoutLoading = prev.filter((m) => !m.loading);
        return [
          ...withoutLoading,
          {
            id: assistantId,
            role: "assistant",
            content: assistantText,
            result,
            createdAt: new Date().toISOString(),
          },
        ];
      });
      useConversationStore.getState().bumpHistory();
    } catch (error) {
      let message = t("errors.generic");
      let result: QueryResult | undefined;

      if (error instanceof ApiClientError) {
        if (error.code === "NO_EVIDENCE") {
          message = error.message;
          result = {
            query_id: createId(),
            status: "failed",
            question: question.trim(),
            language: locale,
            summary: null,
            evidence: [],
            principles: [],
            reasoning: null,
            opinions: [],
            sources: [],
            confidence: 0,
            refused: true,
            refusal_reason: error.message,
            created_at: new Date().toISOString(),
          };
        } else if (error.code === "UNAUTHORIZED") {
          message = t("errors.unauthorized");
        } else if (error.status === 0) {
          message = t("errors.network");
        } else {
          message = error.message;
        }
      }

      setMessages((prev) => {
        const withoutLoading = prev.filter((m) => !m.loading);
        return [
          ...withoutLoading,
          {
            id: createId(),
            role: "assistant",
            content: message,
            error: message,
            retryQuestion: question.trim(),
            result,
            createdAt: new Date().toISOString(),
          },
        ];
      });
    } finally {
      setLoading(false);
      if (abortRef.current === controller) {
        abortRef.current = null;
      }
    }
  };

  const handleSubmit = async () => {
    await runQuery(input.trim());
  };

  const handleRegenerate = (question: string) => {
    void runQuery(question);
  };

  const sampleQueryKeys = ["riba", "tesla", "bitcoin", "zakat", "etf"] as const;

  return (
    <div className="relative flex h-full min-h-0 w-full flex-col">
      <div className="glass-card flex min-h-0 flex-1 flex-col overflow-hidden">
        <div className="flex shrink-0 items-center justify-end border-b border-border/40 px-3 py-2">
          <PageGuide pageKey="chat" inline />
        </div>
        {messages.length > 0 && (
          <div className="border-b border-border/50 px-4 py-3">
            <div className="relative">
              <Search className="pointer-events-none absolute start-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                value={chatSearch}
                onChange={(e) => setChatSearch(e.target.value)}
                placeholder={t("chat.searchMessages")}
                className="border-border/50 bg-background/60 ps-9 pe-9"
              />
              {chatSearch && (
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="absolute end-1 top-1/2 h-7 w-7 -translate-y-1/2"
                  onClick={() => setChatSearch("")}
                  aria-label={t("chat.clearSearch")}
                >
                  <X className="h-3.5 w-3.5" />
                </Button>
              )}
            </div>
          </div>
        )}

        <ScrollArea className="min-h-0 flex-1 px-2 py-3 md:px-6 md:py-4">
          {messages.length === 0 ? (
            <div className="flex min-h-[40vh] flex-col items-center justify-center px-4 py-12 text-center">
              <div className="sanad-brand-icon mb-4 flex h-12 w-12 items-center justify-center rounded-2xl text-lg font-bold">
                {locale === "ar" ? "س" : "S"}
              </div>
              <h1 className="text-xl font-semibold tracking-tight md:text-2xl">{welcomeTitle}</h1>
              <p className="mx-auto mt-2 max-w-lg text-sm text-muted-foreground">{t("chat.welcomeHint")}</p>
              <div className="mt-8 w-full max-w-2xl">
                <p className="mb-3 text-xs font-semibold uppercase tracking-wider text-nexus-cyan">
                  {t("landing.sampleQueriesTitle")}
                </p>
                <div className="flex flex-wrap justify-center gap-2">
                  {sampleQueryKeys.map((key) => (
                    <Button
                      key={key}
                      type="button"
                      variant="outline"
                      size="sm"
                      className="rounded-full border-nexus-cyan/30 text-xs hover:border-nexus-cyan/60"
                      onClick={() => void runQuery(t(`landing.sampleQueries.${key}`))}
                    >
                      {t(`landing.sampleQueries.${key}`)}
                    </Button>
                  ))}
                </div>
              </div>
            </div>
          ) : filteredMessages.length === 0 ? (
            <div className="flex h-full min-h-[120px] items-center justify-center text-sm text-muted-foreground">
              {t("chat.noSearchResults")}
            </div>
          ) : (
            <div className="mx-auto w-full max-w-4xl space-y-8 pb-6">
              {filteredMessages.map((message, index) => {
                const previousUserQuestion =
                  message.role === "assistant"
                    ? [...filteredMessages.slice(0, index)].reverse().find((m) => m.role === "user")?.content
                    : undefined;

                return (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={cn(
                      "group flex w-full gap-3",
                      message.role === "user" ? "justify-end" : "justify-start",
                    )}
                  >
                    {message.role === "assistant" && (
                      <div className="sanad-brand-icon mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-bold">
                        {locale === "ar" ? "س" : "S"}
                      </div>
                    )}

                    <div
                      className={cn(
                        "relative min-w-0 flex-1 space-y-3",
                        message.role === "user" &&
                          "max-w-[85%] rounded-2xl border border-primary/30 bg-primary/10 px-4 py-3 text-sm text-foreground shadow-sm",
                      )}
                    >
                      <div className="flex items-center justify-between gap-3 text-xs opacity-80">
                        <div className="flex items-center gap-2">
                          {message.role === "user" ? (
                            <>
                              <User className="h-3 w-3" />
                              {userDisplayName}
                            </>
                          ) : message.loading ? (
                            <>
                              <Loader2 className="h-3 w-3 animate-spin text-brand-accent" />
                              <span className="text-brand-accent">{t("chat.analyzing")}</span>
                            </>
                          ) : (
                            t("chat.assistantLabel")
                          )}
                        </div>
                        <span className="text-[10px] opacity-70">
                          {formatTimestamp(message.createdAt ? new Date(message.createdAt) : new Date())}
                        </span>
                      </div>

                      {message.loading ? (
                        <div className="space-y-3">
                          {message.result?.agent_trace && message.result.agent_trace.length > 0 ? (
                            <div className="rounded-xl border border-nexus-cyan/20 bg-nexus-cyan/5 p-3">
                              <p className="mb-2 text-xs font-semibold text-nexus-cyan">
                                {t("explainability.viewExecutionTrace")}
                              </p>
                              <AgentTraceTimeline
                                steps={message.result.agent_trace}
                                activeModel={
                                  message.result.agent_trace.find((s) => s.status === "running")
                                    ?.model
                                }
                                compact
                                showLatency
                              />
                            </div>
                          ) : (
                            <>
                              <div className="flex gap-1">
                                {[0, 1, 2].map((i) => (
                                  <motion.span
                                    key={i}
                                    className="h-2 w-2 rounded-full bg-brand-accent"
                                    animate={{ opacity: [0.3, 1, 0.3] }}
                                    transition={{ repeat: Infinity, duration: 1.2, delay: i * 0.2 }}
                                  />
                                ))}
                              </div>
                              <ChatSkeleton />
                            </>
                          )}
                          <p className="text-xs text-muted-foreground">{t("chat.pipelineHint")}</p>
                        </div>
                      ) : message.error ? (
                        <ErrorMessageCard
                          message={message.content}
                          offline={!online || message.content === t("errors.offline")}
                          onRetry={
                            message.retryQuestion
                              ? () => {
                                  setMessages((prev) => prev.filter((m) => m.id !== message.id));
                                  void runQuery(message.retryQuestion!);
                                }
                              : undefined
                          }
                        />
                      ) : (
                        <>
                          {(() => {
                            const displayText = message.translatedContent ?? message.content;
                            const contentLanguage =
                              message.translationLang ??
                              detectContentLanguage(displayText, message.result?.language ?? locale);
                            return (
                              <AnswerContent
                                text={displayText}
                                arabic={contentLanguage === "ar"}
                              />
                            );
                          })()}
                          {message.translationLang && message.translatedContent && (
                            <p className="text-[10px] text-muted-foreground">
                              {t("chatActions.translatedTo")} {message.translationLang.toUpperCase()}
                            </p>
                          )}
                          {!message.loading && message.role === "assistant" && (
                            <div className="flex flex-col gap-2 opacity-100 transition-opacity sm:opacity-0 sm:group-hover:opacity-100">
                              <div className="flex flex-wrap gap-1">
                                <Button
                                  type="button"
                                  variant="ghost"
                                  size="sm"
                                  className="h-7 gap-1 px-2 text-xs"
                                  onClick={() =>
                                    void copyMessage(
                                      message.id,
                                      message.translatedContent ?? message.content,
                                    )
                                  }
                                >
                                  {copiedId === message.id ? (
                                    <>
                                      <Check className="h-3 w-3" />
                                      {t("chat.copied")}
                                    </>
                                  ) : (
                                    <>
                                      <Copy className="h-3 w-3" />
                                      {t("chat.copyMessage")}
                                    </>
                                  )}
                                </Button>
                              </div>
                              {message.result && accessToken && (
                                <MessageActions
                                  result={message.result}
                                  accessToken={accessToken}
                                  displayText={message.translatedContent ?? message.content}
                                  originalText={message.content}
                                  sourceLanguage={message.result.language}
                                  onOpenSources={() => setSourcesPanelResult(message.result!)}
                                  onRegenerate={
                                    previousUserQuestion
                                      ? () => handleRegenerate(previousUserQuestion)
                                      : undefined
                                  }
                                  onTranslated={(translated, targetLang) => {
                                    setMessages((prev) =>
                                      prev.map((item) =>
                                        item.id === message.id
                                          ? {
                                              ...item,
                                              translatedContent: translated,
                                              translationLang: targetLang,
                                            }
                                          : item,
                                      ),
                                    );
                                  }}
                                  onClearTranslation={() => {
                                    setMessages((prev) =>
                                      prev.map((item) =>
                                        item.id === message.id
                                          ? {
                                              ...item,
                                              translatedContent: null,
                                              translationLang: null,
                                            }
                                          : item,
                                      ),
                                    );
                                  }}
                                  activeTranslationLang={message.translationLang}
                                />
                              )}
                            </div>
                          )}
                        </>
                      )}

                      {message.result && !message.loading && (
                        <>
                          <ExplainabilityPanel result={message.result} />
                          {message.result.suggested_questions &&
                            message.result.suggested_questions.length > 0 && (
                              <SuggestedQuestions
                                questions={message.result.suggested_questions}
                                onSelect={(q) => void runQuery(q)}
                              />
                            )}
                        </>
                      )}
                    </div>
                  </motion.div>
                );
              })}
            </div>
          )}
        </ScrollArea>

        <div className="shrink-0 border-t border-border/50 bg-background/40 p-3 md:p-4">
          {recording && (
            <div className="mb-2 flex items-center justify-center gap-3 rounded-xl border border-primary/20 bg-primary/5 px-4 py-2">
              <VoiceWaveform />
              <span className="text-xs text-brand-accent-muted">{t("chat.recording")}</span>
            </div>
          )}
          {voiceReview && !recording && (
            <VoiceTranscriptReview
              audioUrl={voiceReview.audioUrl}
              transcript={voiceReview.transcript}
              transcribing={voiceReview.transcribing}
              onTranscriptChange={(value) =>
                setVoiceReview((current) => (current ? { ...current, transcript: value } : null))
              }
              onSubmit={() => {
                const text = voiceReview.transcript.trim();
                clearVoiceReview();
                if (text) void runQuery(text);
              }}
              onDiscard={clearVoiceReview}
            />
          )}
          {showDocumentHint && (
            <p className="mb-2 text-xs text-brand-accent-muted">{t("chat.documentContextHint")}</p>
          )}
          <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
            <ChatModeToggle />
            <FanarModelSelector />
          </div>
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end">
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={t("chat.placeholder")}
              className="min-h-[72px] flex-1 resize-none border-border/50 bg-background/60 sm:min-h-[64px]"
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  void handleSubmit();
                }
              }}
            />
            <div className="flex shrink-0 flex-row gap-2 sm:flex-col">
              <Button
                type="button"
                variant={recording ? "destructive" : "outline"}
                onClick={() => (recording ? stopRecording() : void startRecording())}
                disabled={loading || !accessToken}
                className="h-10 flex-1 gap-2 sm:h-9 sm:flex-none"
                title={t("chat.voiceInput")}
              >
                {recording ? <MicOff className="h-4 w-4 shrink-0 animate-pulse" /> : <Mic className="h-4 w-4 shrink-0" />}
                <span className="sm:hidden">{recording ? t("chat.stopRecording") : t("chat.voiceInput")}</span>
              </Button>
              <Button
                onClick={() => void handleSubmit()}
                disabled={loading || !input.trim()}
                className="fanar-btn-primary h-10 flex-1 gap-2 sm:h-9 sm:flex-none"
              >
                {loading ? <Loader2 className="h-4 w-4 shrink-0 animate-spin" /> : <SendHorizonal className="h-4 w-4 shrink-0" />}
                {t("chat.submit")}
              </Button>
            </div>
          </div>
        </div>
      </div>
      {sourcesPanelResult && (
        <SourcesSidePanel
          open
          result={sourcesPanelResult}
          onClose={() => setSourcesPanelResult(null)}
        />
      )}
    </div>
  );
}
