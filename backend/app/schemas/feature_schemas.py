"""Pydantic schemas for feature endpoints (Zakat, scanners, knowledge graph)."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class ZakatHolding(BaseModel):
    """Stock or crypto holding with quantity for live price valuation."""

    symbol: str = Field(..., min_length=1, max_length=12)
    quantity: float = Field(..., gt=0)
    asset_type: Literal["stock", "crypto"] = "stock"


class ZakatAssetsRequest(BaseModel):
    cash: float = Field(default=0, ge=0)
    cash_currency: str = Field(default="USD", max_length=3)
    gold_grams: float = Field(default=0, ge=0)
    gold_price_currency: str = Field(default="USD", max_length=3)
    gold_price_per_gram: float | None = Field(default=None, ge=0)
    stock_holdings: list[ZakatHolding] = Field(default_factory=list)
    crypto_holdings: list[ZakatHolding] = Field(default_factory=list)
    stocks: float = Field(default=0, ge=0)
    crypto: float = Field(default=0, ge=0)
    debts: float = Field(default=0, ge=0)
    debt_currency: str = Field(default="USD", max_length=3)
    output_currency: str = Field(default="USD", max_length=3)
    fetch_live_prices: bool = True
    include_ai_guidance: bool = True
    language: str = Field(default="en", pattern="^(ar|en)$")


class ZakatAssetBreakdown(BaseModel):
    category: str
    label: str
    amount: float
    currency: str
    value_in_output_currency: float
    unit_price: float | None = None
    quantity: float | None = None
    quantity_display: str | None = None
    unit_price_display: str | None = None


class ZakatCalculationResponse(BaseModel):
    total_wealth: float
    net_wealth: float
    nisab_threshold: float
    zakat_due: float
    is_above_nisab: bool
    gold_value: float
    rate: float = 0.025
    notes: list[str] = Field(default_factory=list)
    output_currency: str = "USD"
    gold_price_per_gram: float = 0.0
    gold_price_currency: str = "USD"
    asset_breakdown: list[ZakatAssetBreakdown] = Field(default_factory=list)
    price_sources: dict[str, str] = Field(default_factory=dict)
    ai_guidance: str | None = None
    live_prices_used: bool = False


class CompanyScanRequest(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=120)
    language: str = Field(default="en", pattern="^(ar|en)$")
    fanar_model: str = Field(default="auto", max_length=32)


class QualitativeScreening(BaseModel):
    status: Literal["pass", "fail"] = "pass"
    analysis: str = ""


class AaoifiRatios(BaseModel):
    non_permissible_income_ratio: float | None = None
    interest_bearing_debt_ratio: float | None = None
    interest_earning_investments_ratio: float | None = None
    dividend_purification_ratio: float | None = None
    debt_threshold: float = 0.30
    income_threshold: float = 0.05
    investments_threshold: float = 0.30


class FinancialMetrics(BaseModel):
    pe_ratio: float | None = None
    pb_ratio: float | None = None
    peg_ratio: float | None = None
    gross_profit_margin: float | None = None
    net_profit_margin: float | None = None
    roe: float | None = None
    current_ratio: float | None = None
    debt_to_equity: float | None = None


class ScannerSourceReference(BaseModel):
    title: str
    citation: str
    source_type: str = "reference"
    source_url: str | None = None


class ScannerAgentTraceStep(BaseModel):
    phase: str
    agent: str
    model: str
    status: str
    latency_ms: int | None = None
    tokens_estimate: int | None = None


class ScannerExecutionMetrics(BaseModel):
    total_latency_ms: int = 0
    steps_completed: int = 0
    steps_total: int = 0
    models_used: list[str] = Field(default_factory=list)
    tokens_total: int | None = None
    fanar_model_preference: str | None = None


class PeerComparison(BaseModel):
    company_name: str
    compliance_score: float
    status: str


class ComplianceTrendPoint(BaseModel):
    period: str
    compliance_score: float


class CompanyScanResponse(BaseModel):
    company_name: str
    symbol: str | None = None
    business_activity: str
    debt_ratio: float | None = None
    interest_income_ratio: float | None = None
    revenue_estimate: float | None = None
    compliance_score: float
    status: str
    risk_level: Literal["low", "medium", "high"] = "medium"
    purification_estimate: float | None = None
    peer_comparison: list[PeerComparison] = Field(default_factory=list)
    trend_history: list[ComplianceTrendPoint] = Field(default_factory=list)
    screening_notes: list[str] = Field(default_factory=list)
    market_price: float | None = None
    currency: str | None = None
    verdict: Literal["halal", "haram", "doubtful"] = "doubtful"
    verdict_reason: str = ""
    investment_favorable: bool = False
    investment_outlook: str = ""
    # SANAD v2 scanner fields
    sector: str | None = None
    industry: str | None = None
    logo_url: str | None = None
    price_change_percent: float | None = None
    ai_summary: str = ""
    key_takeaways: list[str] = Field(default_factory=list)
    qualitative_screening: QualitativeScreening | None = None
    aaoifi_ratios: AaoifiRatios | None = None
    financial_metrics: FinancialMetrics | None = None
    ai_financial_assessment: str = ""
    agent_trace: list[ScannerAgentTraceStep] = Field(default_factory=list)
    sources: list[ScannerSourceReference] = Field(default_factory=list)
    execution_metrics: ScannerExecutionMetrics | None = None


class PortfolioHolding(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=12)
    name: str | None = None
    quantity: float = Field(..., gt=0)
    asset_type: Literal["stock", "crypto", "etf", "fund", "reit"] = "stock"
    purchase_price: float | None = Field(default=None, ge=0)
    manual_price: float | None = Field(default=None, ge=0)
    use_market_price: bool = True


class PortfolioScanRequest(BaseModel):
    holdings: list[PortfolioHolding] = Field(..., min_length=1, max_length=50)
    language: str = Field(default="en", pattern="^(ar|en)$")
    fanar_model: str = Field(default="auto", max_length=32)
    include_ai: bool = True
    output_currency: str = Field(default="USD", max_length=3)


class AllocationSlice(BaseModel):
    label: str
    weight_pct: float
    value: float


class PortfolioHoldingResult(BaseModel):
    symbol: str
    name: str
    asset_type: str
    quantity: float
    current_price: float | None = None
    price_source: str = "unavailable"
    use_market_price: bool = True
    purchase_price: float | None = None
    value: float
    weight_pct: float
    currency: str | None = None
    exchange: str | None = None
    sector: str | None = None
    industry: str | None = None
    country: str | None = None
    previous_close: float | None = None
    daily_change_pct: float | None = None
    market_cap: float | None = None
    status: str
    compliance_score: float
    verdict: Literal["halal", "haram", "doubtful"] = "doubtful"
    verdict_reason: str = ""
    compliance_explanation: str = ""
    aaoifi_ratios: AaoifiRatios | None = None
    screening_notes: list[str] = Field(default_factory=list)
    unrealized_gain_loss: float | None = None
    unrealized_gain_loss_pct: float | None = None
    data_unavailable: list[str] = Field(default_factory=list)


class ShariahMethodology(BaseModel):
    standards_used: list[str] = Field(default_factory=list)
    screening_methodology: str = ""
    financial_ratio_methodology: str = ""
    business_activity_methodology: str = ""
    purification_methodology: str = ""
    aggregation_methodology: str = ""


class PortfolioInsights(BaseModel):
    holdings_count: int = 0
    largest_position: str | None = None
    smallest_position: str | None = None
    daily_change_value: float | None = None
    daily_change_pct: float | None = None
    unrealized_gain_loss: float | None = None
    unrealized_gain_loss_pct: float | None = None


class PortfolioScanResponse(BaseModel):
    halal_score: float
    total_value: float
    diversification_score: float = 0.0
    violations: list[str] = Field(default_factory=list)
    purification_amount: float
    recommendations: list[str] = Field(default_factory=list)
    holdings: list[PortfolioHoldingResult] = Field(default_factory=list)
    output_currency: str = "USD"
    insights: PortfolioInsights = Field(default_factory=PortfolioInsights)
    sector_allocation: list[AllocationSlice] = Field(default_factory=list)
    country_allocation: list[AllocationSlice] = Field(default_factory=list)
    currency_allocation: list[AllocationSlice] = Field(default_factory=list)
    asset_type_allocation: list[AllocationSlice] = Field(default_factory=list)
    shariah_methodology: ShariahMethodology = Field(default_factory=ShariahMethodology)
    portfolio_assessment: str = ""
    portfolio_assessment_detail: str = ""
    ai_analysis: str = ""
    ai_observations: list[str] = Field(default_factory=list)
    ai_limitations: list[str] = Field(default_factory=list)
    sources: list[ScannerSourceReference] = Field(default_factory=list)
    agent_trace: list[ScannerAgentTraceStep] = Field(default_factory=list)
    execution_metrics: ScannerExecutionMetrics | None = None
    data_gaps: list[str] = Field(default_factory=list)
    scan_id: str | None = None
    scanned_at: str | None = None


class KnowledgeSourceItem(BaseModel):
    id: str
    title: str
    author: str
    source_type: str
    language: str


class KnowledgeBrowseResponse(BaseModel):
    items: list[KnowledgeSourceItem]
    total: int


class GraphNodeSchema(BaseModel):
    id: str
    label: str
    type: str
    x: float
    y: float


class GraphEdgeSchema(BaseModel):
    source: str
    target: str
    label: str | None = None


class KnowledgeGraphResponse(BaseModel):
    nodes: list[GraphNodeSchema]
    edges: list[GraphEdgeSchema]


class SearchResultItem(BaseModel):
    """Unified global search result."""

    type: Literal["chat", "source", "scholar", "company", "document"]
    id: str
    title: str
    subtitle: str | None = None
    href: str
    score: float = 1.0


class GlobalSearchResponse(BaseModel):
    query: str
    results: list[SearchResultItem]
    total: int


class DocumentFinding(BaseModel):
    category: str
    label: str
    page: int
    snippet: str
    severity: str = "medium"


class DocumentRevenueRow(BaseModel):
    page: int
    metric: str
    amount: str
    snippet: str


class DocumentPageHighlight(BaseModel):
    page: int
    snippet: str
    topic: str


class DocumentCitation(BaseModel):
    page: int
    snippet: str
    topic: str


class DocumentAnalysisResponse(BaseModel):
    document_id: UUID | None = None
    filename: str
    page_count: int
    summary: str
    key_findings: list[str] = Field(default_factory=list)
    riba_findings: list[DocumentFinding] = Field(default_factory=list)
    revenue_analysis: list[DocumentRevenueRow] = Field(default_factory=list)
    highlighted_pages: list[DocumentPageHighlight] = Field(default_factory=list)
    citations: list[DocumentCitation] = Field(default_factory=list)


class DocumentListItem(BaseModel):
    document_id: UUID
    filename: str
    page_count: int
    summary: str
    created_at: datetime


class DocumentListResponse(BaseModel):
    items: list[DocumentListItem]
    total: int


class DocumentCompareRequest(BaseModel):
    document_ids: list[UUID] = Field(..., min_length=2, max_length=4)


class DocumentCompareItem(BaseModel):
    document_id: UUID
    filename: str
    page_count: int
    summary: str
    riba_signal_count: int
    revenue_signal_count: int
    key_findings: list[str] = Field(default_factory=list)
    riba_labels: list[str] = Field(default_factory=list)


class DocumentCompareResponse(BaseModel):
    documents: list[DocumentCompareItem]
    shared_riba_signals: list[str] = Field(default_factory=list)
    unique_riba_by_document: dict[str, list[str]] = Field(default_factory=dict)
    comparison_notes: list[str] = Field(default_factory=list)
