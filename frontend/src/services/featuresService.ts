import { API_BASE_URL, API_PREFIX } from "@/lib/constants";
import { apiRequest, ApiClientError } from "@/services/apiClient";

export interface ZakatHoldingPayload {
  symbol: string;
  quantity: number;
  asset_type?: "stock" | "crypto";
}

export interface ZakatAssetsPayload {
  cash: number;
  cash_currency?: string;
  gold_grams: number;
  gold_price_currency?: string;
  gold_price_per_gram?: number | null;
  stock_holdings?: ZakatHoldingPayload[];
  crypto_holdings?: ZakatHoldingPayload[];
  stocks?: number;
  crypto?: number;
  debts: number;
  debt_currency?: string;
  output_currency?: string;
  fetch_live_prices?: boolean;
  include_ai_guidance?: boolean;
  language?: "ar" | "en";
}

export interface ZakatAssetBreakdownItem {
  category: string;
  label: string;
  amount: number;
  currency: string;
  value_in_output_currency: number;
  unit_price?: number | null;
  quantity?: number | null;
  quantity_display?: string | null;
  unit_price_display?: string | null;
}

export interface ZakatResult {
  total_wealth: number;
  net_wealth: number;
  nisab_threshold: number;
  zakat_due: number;
  is_above_nisab: boolean;
  gold_value: number;
  rate: number;
  notes: string[];
  output_currency: string;
  gold_price_per_gram: number;
  gold_price_currency: string;
  asset_breakdown: ZakatAssetBreakdownItem[];
  price_sources: Record<string, string>;
  ai_guidance?: string | null;
  live_prices_used: boolean;
}

export interface ZakatPricesResult {
  output_currency: string;
  gold_price_per_gram: number;
  gold_price_currency: string;
  gold_source: string;
  stocks: Record<
    string,
    {
      unit_price: number;
      quote_currency: string;
      value_currency: string;
      unit_price_converted: number;
      source: string;
    }
  >;
  crypto: Record<
    string,
    {
      unit_price_usd: number;
      value_currency: string;
      unit_price_converted: number;
      source: string;
    }
  >;
  fx_source: string;
}

export interface CompanyScanResult {
  company_name: string;
  symbol: string | null;
  business_activity: string;
  debt_ratio: number | null;
  interest_income_ratio: number | null;
  revenue_estimate: number | null;
  compliance_score: number;
  status: "green" | "yellow" | "red" | string;
  risk_level: "low" | "medium" | "high" | string;
  purification_estimate: number | null;
  peer_comparison: Array<{
    company_name: string;
    compliance_score: number;
    status: string;
  }>;
  trend_history: Array<{
    period: string;
    compliance_score: number;
  }>;
  screening_notes: string[];
  market_price: number | null;
  currency: string | null;
  verdict: "halal" | "haram" | "doubtful" | string;
  verdict_reason: string;
  investment_favorable: boolean;
  investment_outlook: string;
  sector: string | null;
  industry: string | null;
  logo_url: string | null;
  price_change_percent: number | null;
  ai_summary: string;
  key_takeaways: string[];
  qualitative_screening: {
    status: "pass" | "fail";
    analysis: string;
  } | null;
  aaoifi_ratios: {
    non_permissible_income_ratio: number | null;
    interest_bearing_debt_ratio: number | null;
    interest_earning_investments_ratio: number | null;
    dividend_purification_ratio: number | null;
    debt_threshold: number;
    income_threshold: number;
    investments_threshold: number;
  } | null;
  financial_metrics: {
    pe_ratio: number | null;
    pb_ratio: number | null;
    peg_ratio: number | null;
    gross_profit_margin: number | null;
    net_profit_margin: number | null;
    roe: number | null;
    current_ratio: number | null;
    debt_to_equity: number | null;
  } | null;
  ai_financial_assessment: string;
  agent_trace: Array<{
    phase: string;
    agent: string;
    model: string;
    status: string;
    latency_ms?: number | null;
    tokens_estimate?: number | null;
  }>;
  sources: Array<{
    title: string;
    citation: string;
    source_type: string;
    source_url?: string | null;
  }>;
  execution_metrics: {
    total_latency_ms: number;
    steps_completed: number;
    steps_total: number;
    models_used: string[];
    tokens_total?: number | null;
    fanar_model_preference?: string | null;
  } | null;
}

export interface PortfolioHoldingPayload {
  symbol: string;
  name?: string;
  quantity: number;
  asset_type?: "stock" | "crypto" | "etf" | "fund" | "reit";
  purchase_price?: number | null;
  manual_price?: number | null;
  use_market_price?: boolean;
}

export interface AllocationSlice {
  label: string;
  weight_pct: number;
  value: number;
}

export interface PortfolioHoldingResult {
  symbol: string;
  name: string;
  asset_type: string;
  quantity: number;
  current_price: number | null;
  price_source: string;
  use_market_price: boolean;
  purchase_price: number | null;
  value: number;
  weight_pct: number;
  currency: string | null;
  exchange: string | null;
  sector: string | null;
  industry: string | null;
  country: string | null;
  previous_close: number | null;
  daily_change_pct: number | null;
  market_cap: number | null;
  status: string;
  compliance_score: number;
  verdict: string;
  verdict_reason: string;
  compliance_explanation: string;
  aaoifi_ratios: CompanyScanResult["aaoifi_ratios"];
  screening_notes: string[];
  unrealized_gain_loss: number | null;
  unrealized_gain_loss_pct: number | null;
  data_unavailable: string[];
}

export interface ShariahMethodology {
  standards_used: string[];
  screening_methodology: string;
  financial_ratio_methodology: string;
  business_activity_methodology: string;
  purification_methodology: string;
  aggregation_methodology: string;
}

export interface PortfolioInsights {
  holdings_count: number;
  largest_position: string | null;
  smallest_position: string | null;
  daily_change_value: number | null;
  daily_change_pct: number | null;
  unrealized_gain_loss: number | null;
  unrealized_gain_loss_pct: number | null;
}

export interface PortfolioScanResult {
  halal_score: number;
  total_value: number;
  diversification_score: number;
  violations: string[];
  purification_amount: number;
  recommendations: string[];
  holdings: PortfolioHoldingResult[];
  output_currency: string;
  insights: PortfolioInsights;
  sector_allocation: AllocationSlice[];
  country_allocation: AllocationSlice[];
  currency_allocation: AllocationSlice[];
  asset_type_allocation: AllocationSlice[];
  shariah_methodology: ShariahMethodology;
  portfolio_assessment: string;
  portfolio_assessment_detail: string;
  ai_analysis: string;
  ai_observations: string[];
  ai_limitations: string[];
  sources: CompanyScanResult["sources"];
  agent_trace: CompanyScanResult["agent_trace"];
  execution_metrics: CompanyScanResult["execution_metrics"];
  data_gaps: string[];
  scan_id: string | null;
  scanned_at: string | null;
}

export interface KnowledgeSourceItem {
  id: string;
  title: string;
  author: string;
  source_type: string;
  language: string;
}

export interface KnowledgeGraphData {
  nodes: Array<{ id: string; label: string; type: string; x: number; y: number }>;
  edges: Array<{ source: string; target: string; label?: string | null }>;
}

export interface DocumentFinding {
  category: string;
  label: string;
  page: number;
  snippet: string;
  severity: string;
}

export interface DocumentRevenueRow {
  page: number;
  metric: string;
  amount: string;
  snippet: string;
}

export interface DocumentCitation {
  page: number;
  snippet: string;
  topic: string;
}

export interface DocumentAnalysisResult {
  document_id?: string | null;
  filename: string;
  page_count: number;
  summary: string;
  key_findings: string[];
  riba_findings: DocumentFinding[];
  revenue_analysis: DocumentRevenueRow[];
  highlighted_pages: Array<{ page: number; snippet: string; topic: string }>;
  citations: DocumentCitation[];
}

export async function calculateZakat(
  accessToken: string,
  payload: ZakatAssetsPayload,
): Promise<ZakatResult> {
  return apiRequest<ZakatResult>("/tools/zakat/calculate", {
    method: "POST",
    accessToken,
    body: JSON.stringify(payload),
  });
}

export async function fetchZakatPrices(
  accessToken: string,
  payload: {
    output_currency?: string;
    gold_currency?: string;
    stock_symbols?: string[];
    crypto_symbols?: string[];
  },
): Promise<ZakatPricesResult> {
  return apiRequest<ZakatPricesResult>("/tools/zakat/prices", {
    method: "POST",
    accessToken,
    body: JSON.stringify(payload),
  });
}

export async function scanCompany(
  accessToken: string,
  companyName: string,
  options?: { language?: "ar" | "en"; fanar_model?: string },
): Promise<CompanyScanResult> {
  return apiRequest<CompanyScanResult>("/tools/scanner/company", {
    method: "POST",
    accessToken,
    body: JSON.stringify({
      company_name: companyName,
      language: options?.language ?? "en",
      fanar_model: options?.fanar_model ?? "auto",
    }),
  });
}

export async function scanPortfolio(
  accessToken: string,
  holdings: PortfolioHoldingPayload[],
  options?: {
    language?: "ar" | "en";
    fanar_model?: string;
    include_ai?: boolean;
    output_currency?: string;
  },
): Promise<PortfolioScanResult> {
  return apiRequest<PortfolioScanResult>("/tools/scanner/portfolio", {
    method: "POST",
    accessToken,
    body: JSON.stringify({
      holdings,
      language: options?.language ?? "en",
      fanar_model: options?.fanar_model ?? "auto",
      include_ai: options?.include_ai ?? true,
      output_currency: options?.output_currency ?? "USD",
    }),
  });
}

export async function browseKnowledgeSources(
  accessToken: string,
  limit = 50,
): Promise<{ items: KnowledgeSourceItem[]; total: number }> {
  return apiRequest(`/knowledge/sources?limit=${limit}`, { accessToken });
}

export async function fetchKnowledgeGraph(
  accessToken: string,
  language = "en",
): Promise<KnowledgeGraphData> {
  return apiRequest<KnowledgeGraphData>(`/knowledge/graph?language=${language}`, { accessToken });
}

export interface DocumentListItem {
  document_id: string;
  filename: string;
  page_count: number;
  summary: string;
  created_at: string;
}

export async function listDocuments(accessToken: string): Promise<{ items: DocumentListItem[]; total: number }> {
  return apiRequest("/tools/documents", { accessToken });
}

export async function deleteDocument(accessToken: string, documentId: string): Promise<void> {
  await apiRequest<void>(`/tools/documents/${documentId}`, {
    method: "DELETE",
    accessToken,
  });
}

export interface DocumentCompareItem {
  document_id: string;
  filename: string;
  page_count: number;
  summary: string;
  riba_signal_count: number;
  revenue_signal_count: number;
  key_findings: string[];
  riba_labels: string[];
}

export interface DocumentCompareResult {
  documents: DocumentCompareItem[];
  shared_riba_signals: string[];
  unique_riba_by_document: Record<string, string[]>;
  comparison_notes: string[];
}

export async function compareDocuments(
  accessToken: string,
  documentIds: string[],
): Promise<DocumentCompareResult> {
  return apiRequest<DocumentCompareResult>("/tools/documents/compare", {
    method: "POST",
    accessToken,
    body: JSON.stringify({ document_ids: documentIds }),
  });
}

export async function analyzeDocument(
  accessToken: string,
  file: File,
  language: "ar" | "en" = "en",
): Promise<DocumentAnalysisResult> {
  const formData = new FormData();
  formData.append("file", file, file.name);
  formData.append("language", language);

  const { API_BASE_URL, API_PREFIX } = await import("@/lib/constants");
  const url = `${API_BASE_URL}${API_PREFIX}/tools/documents/analyze`;

  const response = await fetch(url, {
    method: "POST",
    headers: { Authorization: `Bearer ${accessToken}` },
    body: formData,
  });

  if (!response.ok) {
    let message = "Document analysis failed";
    try {
      const body = (await response.json()) as { message?: string; code?: string };
      message = body.message ?? message;
      throw new ApiClientError(response.status, body.code ?? "ANALYSIS_FAILED", message);
    } catch (err) {
      if (err instanceof ApiClientError) throw err;
      throw new ApiClientError(response.status, "ANALYSIS_FAILED", message);
    }
  }

  return response.json() as Promise<DocumentAnalysisResult>;
}

export async function translateText(
  accessToken: string,
  text: string,
  targetLanguage: string,
  sourceLanguage?: string,
): Promise<{ translated_text: string; model: string }> {
  return apiRequest("/tools/translate", {
    method: "POST",
    accessToken,
    body: JSON.stringify({
      text,
      target_language: targetLanguage,
      source_language: sourceLanguage,
    }),
  });
}

export async function synthesizeSpeech(
  accessToken: string,
  text: string,
  language: "ar" | "en" = "ar",
): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}${API_PREFIX}/tools/tts`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text, language }),
  });

  if (!response.ok) {
    throw new ApiClientError(response.status, "TTS_FAILED", "Speech synthesis failed");
  }

  return response.blob();
}
