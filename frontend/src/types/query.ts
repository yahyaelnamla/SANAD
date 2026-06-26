import type { QueryStatus } from "./common";

export interface Evidence {
  text: string;
  source_id: string;
  chunk_id: string;
  citation: string;
  source_title: string;
  source_author: string;
  source_type: string;
  language: string;
  score: number;
  metadata?: Record<string, unknown>;
}

export interface Principle {
  name: string;
  description: string;
  citation: string;
}

export interface Opinion {
  scholar: string;
  position: string;
  citations: string[];
  institution?: string | null;
  strength?: string | null;
  book?: string | null;
  fatwa?: string | null;
  page?: string | null;
  standard?: string | null;
  section?: string | null;
  date?: string | null;
}

export interface MadhhabPosition {
  school: string;
  position: string;
  alignment: string;
  source?: string | null;
}

export interface MarketQuote {
  symbol: string;
  price?: number | null;
  currency?: string | null;
  market_cap?: number | null;
  exchange?: string | null;
}

export interface FinancialContext {
  entities: string[];
  notes?: string;
  has_external_data?: boolean;
  screening_notes?: string[];
  market_quotes?: MarketQuote[];
}

export interface ExecutionMetrics {
  total_latency_ms: number;
  steps_completed: number;
  steps_total: number;
  models_used: string[];
  tokens_estimate?: number | null;
  tokens_total?: number | null;
  fanar_model_preference?: string | null;
  pipeline_depth?: "fast" | "standard" | "deep" | null;
  document_context_used?: boolean | null;
  conversation_memory_used?: boolean | null;
  auto_mode?: string | null;
  fanar_capabilities?: Record<string, string> | null;
}

export interface SourceReference {
  source_id: string;
  title: string;
  author: string;
  type: string;
  citation: string;
  source_url?: string | null;
}

export interface AgentTraceStep {
  phase: string;
  agent: string;
  model: string;
  status: string;
  latency_ms?: number | null;
  started_at?: string | null;
  completed_at?: string | null;
  tokens_estimate?: number | null;
}

export interface QueryResult {
  query_id: string;
  status: QueryStatus;
  question: string;
  language: string;
  summary: string | null;
  evidence: Evidence[];
  principles: Principle[];
  reasoning: string | null;
  opinions: Opinion[];
  sources: SourceReference[];
  confidence: number;
  confidence_breakdown?: {
    retrieval?: number;
    grounding?: number;
    model?: number;
    guard?: number;
    verification?: number;
    scholarly_coverage?: number;
  } | null;
  refused: boolean;
  refusal_reason: string | null;
  agent_trace?: AgentTraceStep[];
  thinking_trace?: string | null;
  financial_context?: FinancialContext | null;
  execution_metrics?: ExecutionMetrics | null;
  madhhab_matrix?: MadhhabPosition[];
  suggested_questions?: string[];
  draft_summary?: string | null;
  created_at: string;
}

export interface QueryCreatePayload {
  question: string;
  language?: "ar" | "en";
  session_id?: string;
  conversation_history?: Array<{ role: "user" | "assistant"; content: string }>;
  advanced_analysis?: boolean;
  fanar_model?: "auto" | "sadiq" | "c2" | "guard";
}

export interface QueryListItem {
  query_id: string;
  question: string;
  display_title?: string | null;
  language: string;
  status: QueryStatus;
  summary: string | null;
  confidence: number;
  refused: boolean;
  archived?: boolean;
  folder?: string | null;
  tags?: string[];
  session_id?: string | null;
  turn_count?: number;
  created_at: string;
}

export function queryDisplayTitle(item: QueryListItem): string {
  return item.display_title?.trim() || item.question;
}

export interface QueryListResponse {
  items: QueryListItem[];
  total: number;
  limit: number;
  offset: number;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  result?: QueryResult;
  error?: string;
  retryQuestion?: string;
  loading?: boolean;
  streaming?: boolean;
  createdAt?: string;
  translatedContent?: string | null;
  translationLang?: string | null;
}
