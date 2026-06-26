import { API_BASE_URL, API_PREFIX } from "@/lib/constants";
import { apiRequest, ApiClientError } from "@/services/apiClient";
import type {
  QueryCreatePayload,
  QueryListItem,
  QueryListResponse,
  QueryResult,
} from "@/types/query";

const POLL_INTERVAL_MS = 2000;
const MAX_POLL_ATTEMPTS = 300;
const STREAM_TIMEOUT_MS = 900_000;

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function isTerminalStatus(status: QueryResult["status"]): boolean {
  return status === "completed" || status === "failed";
}

function isStreamFallbackError(error: unknown): boolean {
  if (error instanceof ApiClientError) {
    return error.status === 0 || error.code === "NETWORK_ERROR";
  }
  return (
    error instanceof Error &&
    (error.message.includes("Stream") ||
      error.message.includes("timeout") ||
      error.message.includes("Network"))
  );
}

export interface QueryStreamCallbacks {
  onProgress?: (result: QueryResult) => void;
  onToken?: (token: string, streamedText: string) => void;
  onDraftToken?: (token: string, streamedText: string) => void;
  onSection?: (section: string) => void;
}

interface ParsedSSEEvent {
  event: string;
  data: string;
}

function parseSSEBuffer(buffer: string): { events: ParsedSSEEvent[]; remaining: string } {
  const events: ParsedSSEEvent[] = [];
  const blocks = buffer.split("\n\n");
  const remaining = blocks.pop() ?? "";

  for (const block of blocks) {
    if (!block.trim()) continue;
    let event = "message";
    const dataLines: string[] = [];

    for (const line of block.split("\n")) {
      if (line.startsWith("event:")) {
        event = line.slice(6).trim();
      } else if (line.startsWith("data:")) {
        dataLines.push(line.slice(5).trim());
      }
    }

    if (dataLines.length > 0) {
      events.push({ event, data: dataLines.join("\n") });
    }
  }

  return { events, remaining };
}

export async function consumeQueryStream(
  queryId: string,
  accessToken: string,
  callbacks: QueryStreamCallbacks = {},
  signal?: AbortSignal,
): Promise<QueryResult> {
  const url = `${API_BASE_URL}${API_PREFIX}/queries/${queryId}/stream`;
  let response: Response;

  const timeoutController = new AbortController();
  const timeoutId = window.setTimeout(() => timeoutController.abort(), STREAM_TIMEOUT_MS);

  const onAbort = () => timeoutController.abort();
  signal?.addEventListener("abort", onAbort);

  try {
    response = await fetch(url, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
        Accept: "text/event-stream",
      },
      signal: timeoutController.signal,
    });
  } catch (error) {
    if (timeoutController.signal.aborted) {
      throw new Error("Stream timed out waiting for analysis.");
    }
    throw new ApiClientError(0, "NETWORK_ERROR", "Network request failed");
  } finally {
    window.clearTimeout(timeoutId);
    signal?.removeEventListener("abort", onAbort);
  }

  if (!response.ok) {
    let errorBody = { code: "INTERNAL_ERROR", message: response.statusText };
    try {
      errorBody = (await response.json()) as typeof errorBody;
    } catch {
      // keep default
    }
    throw new ApiClientError(response.status, errorBody.code, errorBody.message);
  }

  if (!response.body) {
    throw new Error("Streaming response body unavailable.");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let streamedText = "";
  let draftText = "";
  let latestProgress: QueryResult | null = null;
  let completeResult: QueryResult | null = null;
  let lastActivity = Date.now();

  while (true) {
    if (signal?.aborted) {
      await reader.cancel();
      throw new Error("Query cancelled.");
    }

    if (Date.now() - lastActivity > STREAM_TIMEOUT_MS) {
      await reader.cancel();
      throw new Error("Stream timed out waiting for analysis.");
    }

    const { done, value } = await reader.read();
    if (done) break;

    lastActivity = Date.now();
    buffer += decoder.decode(value, { stream: true });
    const { events, remaining } = parseSSEBuffer(buffer);
    buffer = remaining;

    for (const sseEvent of events) {
      const payload = JSON.parse(sseEvent.data) as Record<string, unknown>;

      switch (sseEvent.event) {
        case "status": {
          const progress = {
            ...(latestProgress ?? {}),
            query_id: String(payload.query_id ?? queryId),
            status: payload.status as QueryResult["status"],
            agent_trace: (payload.agent_trace as QueryResult["agent_trace"]) ?? [],
          } as QueryResult;
          latestProgress = progress;
          callbacks.onProgress?.(progress);
          break;
        }
        case "draft_token": {
          const token = String(payload.text ?? "");
          draftText += token;
          callbacks.onDraftToken?.(token, draftText);
          break;
        }
        case "token": {
          const token = String(payload.text ?? "");
          streamedText += token;
          callbacks.onToken?.(token, streamedText);
          break;
        }
        case "section":
          callbacks.onSection?.(String(payload.section ?? ""));
          break;
        case "complete":
          completeResult = payload as unknown as QueryResult;
          break;
        case "error":
          throw new Error(String(payload.message ?? "Streaming failed."));
        default:
          break;
      }
    }
  }

  if (!completeResult) {
    throw new Error("Stream ended without a complete response.");
  }

  return completeResult;
}

async function pollQueryUntilComplete(
  queryId: string,
  accessToken: string,
  onProgress?: (result: QueryResult) => void,
  signal?: AbortSignal,
): Promise<QueryResult> {
  for (let attempt = 0; attempt < MAX_POLL_ATTEMPTS; attempt += 1) {
    if (signal?.aborted) {
      throw new Error("Query cancelled.");
    }
    await sleep(POLL_INTERVAL_MS);
    const result = await getQuery(queryId, accessToken);
    onProgress?.(result);
    if (isTerminalStatus(result.status)) {
      return result;
    }
  }

  throw new Error("Query timed out while waiting for analysis.");
}

export async function submitQuery(
  payload: QueryCreatePayload,
  accessToken: string,
  callbacks: QueryStreamCallbacks = {},
  signal?: AbortSignal,
): Promise<QueryResult> {
  const { onProgress, onToken, onDraftToken, onSection } = callbacks;

  const accepted = await apiRequest<QueryResult>("/queries", {
    method: "POST",
    body: JSON.stringify(payload),
    accessToken,
    signal,
  });

  onProgress?.(accepted);

  if (isTerminalStatus(accepted.status) && accepted.summary) {
    onToken?.(accepted.summary, accepted.summary);
    return accepted;
  }

  if (isTerminalStatus(accepted.status)) {
    return accepted;
  }

  try {
    return await consumeQueryStream(accepted.query_id, accessToken, callbacks, signal);
  } catch (error) {
    if (signal?.aborted) throw error;
    if (!isStreamFallbackError(error)) throw error;
    return pollQueryUntilComplete(accepted.query_id, accessToken, onProgress, signal);
  }
}

export async function getQuery(queryId: string, accessToken: string): Promise<QueryResult> {
  return apiRequest<QueryResult>(`/queries/${queryId}`, { accessToken });
}

export async function listQueries(
  accessToken: string,
  limit = 50,
  offset = 0,
  includeArchived = false,
): Promise<QueryListResponse> {
  return apiRequest<QueryListResponse>(
    `/queries?limit=${limit}&offset=${offset}&include_archived=${includeArchived}`,
    { accessToken },
  );
}

export interface QueryUpdatePayload {
  display_title?: string | null;
  archived?: boolean;
  folder?: string | null;
  tags?: string[];
}

export async function updateQueryMetadata(
  queryId: string,
  accessToken: string,
  payload: QueryUpdatePayload,
): Promise<QueryListItem> {
  return apiRequest<QueryListItem>(`/queries/${queryId}`, {
    method: "PATCH",
    accessToken,
    body: JSON.stringify(payload),
  });
}

export async function deleteQuery(queryId: string, accessToken: string): Promise<void> {
  await apiRequest<void>(`/queries/${queryId}`, {
    method: "DELETE",
    accessToken,
  });
}

export async function exportQueryMarkdown(
  queryId: string,
  accessToken: string,
): Promise<{ filename: string; content: string }> {
  return apiRequest<{ filename: string; content: string }>(`/queries/${queryId}/export`, {
    accessToken,
  });
}
