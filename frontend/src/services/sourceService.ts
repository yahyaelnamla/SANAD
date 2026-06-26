import { apiRequest } from "@/services/apiClient";
import type {
  AdminAnalytics,
  AdminStats,
  Source,
  SourceCreatePayload,
  SourceListResponse,
  SourceType,
  SourceUpdatePayload,
} from "@/types/source";

interface ListSourcesParams {
  is_authenticated?: boolean;
  source_type?: SourceType;
  limit?: number;
  offset?: number;
}

function buildQuery(params: ListSourcesParams): string {
  const search = new URLSearchParams();
  if (params.is_authenticated !== undefined) {
    search.set("is_authenticated", String(params.is_authenticated));
  }
  if (params.source_type) {
    search.set("source_type", params.source_type);
  }
  if (params.limit !== undefined) {
    search.set("limit", String(params.limit));
  }
  if (params.offset !== undefined) {
    search.set("offset", String(params.offset));
  }
  const query = search.toString();
  return query ? `?${query}` : "";
}

export async function listSources(
  accessToken: string,
  params: ListSourcesParams = {},
): Promise<SourceListResponse> {
  return apiRequest<SourceListResponse>(`/sources${buildQuery(params)}`, {
    accessToken,
  });
}

export async function createSource(
  accessToken: string,
  payload: SourceCreatePayload,
): Promise<Source> {
  return apiRequest<Source>("/sources", {
    method: "POST",
    accessToken,
    body: JSON.stringify(payload),
  });
}

export async function updateSource(
  accessToken: string,
  sourceId: string,
  payload: SourceUpdatePayload,
): Promise<Source> {
  return apiRequest<Source>(`/sources/${sourceId}`, {
    method: "PUT",
    accessToken,
    body: JSON.stringify(payload),
  });
}

export async function deleteSource(accessToken: string, sourceId: string): Promise<void> {
  await apiRequest<void>(`/sources/${sourceId}`, {
    method: "DELETE",
    accessToken,
  });
}

export async function getAdminStats(accessToken: string): Promise<AdminStats> {
  return apiRequest<AdminStats>("/admin/stats", { accessToken });
}

export async function getAdminAnalytics(accessToken: string): Promise<AdminAnalytics> {
  return apiRequest<AdminAnalytics>("/admin/analytics", { accessToken });
}
