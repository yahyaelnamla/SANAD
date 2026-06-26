# SANAD/agents/financial_context_agent/

This directory contains the Financial Context Agent, which is responsible for understanding modern financial concepts and structures relevant to the user's query. It utilizes external financial APIs to gather up-to-date information.

## Purpose:
To bridge the gap between traditional Islamic jurisprudence and contemporary financial realities. This agent provides crucial context on complex financial products, markets, and company structures, enabling the Reasoning Agent to perform accurate jurisprudential adaptation.

## Contents:
- `agent.py`: The main logic for the Financial Context Agent.
- `prompt.md`: The system prompt or instructions for the Financial Context Agent.
- `tools.py`: Definitions of tools the Financial Context Agent can use (e.g., financial APIs, crypto APIs).
- `models.py`: Data models specific to the Financial Context Agent (e.g., `FinancialProduct`, `CompanyFinancials`).
- `tests.py`: Unit tests for the Financial Context Agent.

## Limitations:
- Relies on the availability and accuracy of external financial and crypto APIs.
- Needs to constantly adapt to new financial innovations and terminology.

## Needs:
- Robust integration with various financial and cryptocurrency APIs.
- Ability to parse and interpret complex financial data.
- Mechanisms for handling API rate limits and errors.

## Usage for AI Agents:
AI agents should develop and maintain the Financial Context Agent, focusing on its ability to accurately gather and interpret modern financial information. They must ensure reliable integration with external APIs and provide clear, concise financial context to the Reasoning Agent.
