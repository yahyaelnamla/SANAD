export type SourceType = "classical" | "contemporary" | "standard" | "fatwa";

export interface Source {
  id: string;
  title: string;
  author: string;
  source_type: SourceType;
  language: "ar" | "en";
  url: string | null;
  is_authenticated: boolean;
  created_at: string;
}

export interface SourceListResponse {
  items: Source[];
  total: number;
}

export interface SourceCreatePayload {
  title: string;
  author: string;
  source_type: SourceType;
  language: "ar" | "en";
  url?: string;
  is_authenticated?: boolean;
}

export interface SourceUpdatePayload {
  title?: string;
  author?: string;
  source_type?: SourceType;
  language?: "ar" | "en";
  url?: string | null;
  is_authenticated?: boolean;
}

export interface AdminStats {
  total_sources: number;
  authenticated_sources: number;
  pending_sources: number;
}

export interface AdminDailyQueryCount {
  date: string;
  count: number;
}

export interface AdminModelUsage {
  model: string;
  count: number;
}

export interface AdminAnalytics extends AdminStats {
  total_queries: number;
  completed_queries: number;
  failed_queries: number;
  refused_queries: number;
  refusal_rate: number;
  average_latency_ms: number | null;
  queries_by_day: AdminDailyQueryCount[];
  model_usage: AdminModelUsage[];
}
