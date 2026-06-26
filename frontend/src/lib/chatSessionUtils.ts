import type { ChatMessage, QueryResult } from "@/types/query";

export function answerDisplayText(result: QueryResult, fallback: string): string {
  const summary = result.summary?.trim();
  if (summary) return summary;
  const reasoning = result.reasoning?.trim();
  if (reasoning) return reasoning;
  return fallback;
}

const MAX_HISTORY_CHARS = 100_000;

export function buildAssistantHistoryContent(message: ChatMessage): string {
  let content = (message.translatedContent ?? message.content).trim();
  const result = message.result;
  if (!result) return content.slice(0, MAX_HISTORY_CHARS);

  const summary = result.summary?.trim();
  const reasoning = result.reasoning?.trim();
  if (summary && !content.includes(summary.slice(0, 80))) {
    content = summary;
  }
  if (reasoning && !content.includes(reasoning.slice(0, 80))) {
    content = `${content}\n\n${reasoning}`;
  }
  if (result.evidence.length > 0) {
    const cites = result.evidence
      .slice(0, 20)
      .map((item) => `- ${item.citation}: ${item.text.slice(0, 240)}`)
      .join("\n");
    content = `${content}\n\n[Evidence from this answer]\n${cites}`;
  }
  if (result.opinions.length > 0) {
    const opinions = result.opinions
      .slice(0, 10)
      .map((item) => `- ${item.scholar}: ${item.position.slice(0, 180)}`)
      .join("\n");
    content = `${content}\n\n[Scholarly views]\n${opinions}`;
  }
  return content.slice(0, MAX_HISTORY_CHARS);
}

export function buildConversationHistory(messages: ChatMessage[]) {
  return messages
    .filter((message) => !message.loading && !message.error && message.content.trim())
    .slice(-30)
    .map((message) => ({
      role: message.role,
      content:
        message.role === "assistant"
          ? buildAssistantHistoryContent(message)
          : (message.translatedContent ?? message.content).slice(0, MAX_HISTORY_CHARS),
    }));
}

export interface ConversationThreadMessage {
  message_id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
  query_id?: string | null;
  result?: QueryResult | null;
}

export interface ConversationThread {
  session_id: string;
  title: string;
  language: string;
  message_count: number;
  turn_count: number;
  created_at: string;
  updated_at: string;
  messages: ConversationThreadMessage[];
}

export interface ConversationListItem {
  session_id: string;
  title: string;
  language: string;
  turn_count: number;
  message_count: number;
  preview: string | null;
  last_query_id: string;
  refused: boolean;
  archived: boolean;
  created_at: string;
  updated_at: string;
}

export function threadToChatMessages(thread: ConversationThread): ChatMessage[] {
  return thread.messages.map((message) => {
    if (message.role === "user") {
      return {
        id: message.message_id,
        role: "user" as const,
        content: message.content,
        createdAt: message.created_at,
      };
    }

    const result = message.result ?? undefined;
    const content = result
      ? answerDisplayText(result, message.content)
      : message.content;

    return {
      id: message.message_id,
      role: "assistant" as const,
      content,
      result,
      createdAt: message.created_at,
    };
  });
}
