"""Tests for feature endpoints (Zakat, scanners, knowledge)."""

import pytest


@pytest.mark.asyncio
async def test_zakat_calculate(async_client, auth_headers: dict[str, str]) -> None:
    response = await async_client.post(
        "/api/v1/tools/zakat/calculate",
        json={
            "cash": 10000,
            "cash_currency": "USD",
            "gold_grams": 50,
            "gold_price_per_gram": 75,
            "gold_price_currency": "USD",
            "stock_holdings": [{"symbol": "AAPL", "quantity": 5, "asset_type": "stock"}],
            "crypto_holdings": [{"symbol": "BTC", "quantity": 0.1, "asset_type": "crypto"}],
            "debts": 2000,
            "debt_currency": "USD",
            "output_currency": "USD",
            "fetch_live_prices": False,
            "include_ai_guidance": False,
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["zakat_due"] >= 0
    assert data["net_wealth"] > 0
    assert data["output_currency"] == "USD"
    assert isinstance(data["asset_breakdown"], list)
    gold_rows = [row for row in data["asset_breakdown"] if row["category"] == "gold"]
    if gold_rows:
        assert "g" in gold_rows[0]["quantity_display"]


@pytest.mark.asyncio
async def test_company_scanner(async_client, auth_headers: dict[str, str]) -> None:
    response = await async_client.post(
        "/api/v1/tools/scanner/company",
        json={"company_name": "Apple"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["company_name"]
    assert data["status"] in {"green", "yellow", "red"}
    assert data["risk_level"] in {"low", "medium", "high"}
    assert "peer_comparison" in data
    assert "trend_history" in data
    assert "ai_summary" in data
    assert "aaoifi_ratios" in data
    assert "financial_metrics" in data
    assert "agent_trace" in data


@pytest.mark.asyncio
async def test_portfolio_scanner(async_client, auth_headers: dict[str, str]) -> None:
    response = await async_client.post(
        "/api/v1/tools/scanner/portfolio",
        json={
            "holdings": [
                {
                    "symbol": "AAPL",
                    "quantity": 10,
                    "asset_type": "stock",
                    "use_market_price": True,
                },
                {
                    "symbol": "TSLA",
                    "quantity": 5,
                    "asset_type": "stock",
                    "use_market_price": True,
                },
            ],
            "include_ai": False,
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_value"] > 0
    assert len(data["holdings"]) == 2
    assert "diversification_score" in data
    assert "shariah_methodology" in data
    assert "insights" in data
    assert "sector_allocation" in data
    assert data["holdings"][0]["compliance_explanation"]


@pytest.mark.asyncio
async def test_knowledge_graph(async_client, auth_headers: dict[str, str], seeded_knowledge: None) -> None:
    response = await async_client.get("/api/v1/knowledge/graph", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["nodes"]) >= 5
    assert len(data["edges"]) >= 3


@pytest.mark.asyncio
async def test_knowledge_sources(async_client, auth_headers: dict[str, str], seeded_knowledge: None) -> None:
    response = await async_client.get("/api/v1/knowledge/sources", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_document_analyze_endpoint(async_client, auth_headers: dict[str, str]) -> None:
    from tests.backend.test_document_service import _build_sample_pdf

    pdf_bytes = _build_sample_pdf("Interest income disclosure and total revenue: 500,000")
    response = await async_client.post(
        "/api/v1/tools/documents/analyze",
        files={"file": ("annual-report.pdf", pdf_bytes, "application/pdf")},
        data={"language": "en"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "annual-report.pdf"
    assert data["document_id"]
    assert data["summary"]
    assert isinstance(data["key_findings"], list)

    list_resp = await async_client.get("/api/v1/tools/documents", headers=auth_headers)
    assert list_resp.status_code == 200
    assert list_resp.json()["total"] >= 1
