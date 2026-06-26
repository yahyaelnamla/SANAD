import { apiRequest } from "@/services/apiClient";

export interface EvaluationStats {
  total_completed_queries: number;
  average_latency_ms: number | null;
  average_tokens_estimate: number | null;
  total_tokens_estimate: number | null;
  unique_models_used: string[];
  guard_pass_rate: number | null;
  fast_pipeline_count: number;
  deep_pipeline_count: number;
  document_memory_queries: number;
  voice_ready: boolean;
}

export interface DemoPrompt {
  id: string;
  title: string;
  description: string;
  fanar_product: string;
  route: string;
  question: string | null;
}

export interface FeatureMatrixRow {
  id: string;
  feature: string;
  fanar_products: string[];
  description: string;
}

export interface RecentQueryMetric {
  query_id: string;
  question: string;
  latency_ms: number | null;
  tokens_estimate: number | null;
  pipeline_depth: string | null;
  models_used: string[];
  refused: boolean;
}

export interface EvaluationDashboard {
  fanar_capabilities: Record<string, string>;
  fanar_capability_improvements?: Record<string, string>;
  stats: EvaluationStats;
  demo_prompts: DemoPrompt[];
  feature_matrix: FeatureMatrixRow[];
  recent_queries: RecentQueryMetric[];
  limitations: string[];
  future_fanar_suggestions: string[];
}

export async function getEvaluationDashboard(accessToken: string): Promise<EvaluationDashboard> {
  return apiRequest<EvaluationDashboard>("/evaluation/dashboard", { accessToken });
}

export interface HarnessCase {
  id: string;
  category: string;
  question: string;
  language: string;
  expects_refusal: boolean;
  expects_evidence: boolean;
  expects_fanar_guard: boolean;
  rubric: string[];
}

export interface EvaluationHarness {
  version: string;
  total_cases: number;
  categories: string[];
  cases: HarnessCase[];
  scoring_notes: string[];
}

export async function getEvaluationHarness(accessToken: string): Promise<EvaluationHarness> {
  return apiRequest<EvaluationHarness>("/evaluation/harness", { accessToken });
}
