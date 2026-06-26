import { apiRequest } from "@/services/apiClient";
import type { ConversationListItem, ConversationThread } from "@/lib/chatSessionUtils";

export interface ConversationListResponse {
  items: ConversationListItem[];
  total: number;
  limit: number;
  offset: number;
}

export async function listConversations(
  accessToken: string,
  limit = 50,
  offset = 0,
  includeArchived = false,
): Promise<ConversationListResponse> {
  return apiRequest<ConversationListResponse>(
    `/conversations?limit=${limit}&offset=${offset}&include_archived=${includeArchived}`,
    { accessToken },
  );
}

export async function getConversationThread(
  sessionId: string,
  accessToken: string,
): Promise<ConversationThread> {
  return apiRequest<ConversationThread>(`/conversations/${encodeURIComponent(sessionId)}`, {
    accessToken,
  });
}
