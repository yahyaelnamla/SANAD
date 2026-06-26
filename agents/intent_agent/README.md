# SANAD/agents/intent_agent/

This directory contains the Intent Agent, which is the first agent in the SANAD multi-agent system. Its primary role is to understand the user's query and extract key information to guide the subsequent agents.

## Purpose:
To accurately interpret user questions, identify the core intent, and extract relevant entities such as asset types, financial domains, and keywords. This initial analysis is crucial for directing the query to the appropriate knowledge sources and reasoning paths.

## Contents:
- `agent.py`: The main logic for the Intent Agent.
- `prompt.md`: The system prompt or instructions for the Intent Agent.
- `tools.py`: Definitions of tools the Intent Agent can use (e.g., keyword extraction, entity recognition).
- `models.py`: Data models specific to the Intent Agent (e.g., `Intent`, `ExtractedEntities`).
- `tests.py`: Unit tests for the Intent Agent.

## Limitations:
- The accuracy of subsequent agents heavily relies on the Intent Agent's ability to correctly interpret the user's query.
- Ambiguous queries may require clarification or additional context.

## Needs:
- Robust natural language understanding capabilities.
- Ability to identify financial and Islamic jurisprudential concepts.
- Integration with external NLP tools if necessary.

## Usage for AI Agents:
AI agents should develop and refine the Intent Agent to accurately parse user queries. They must focus on improving its ability to extract relevant information and classify the intent, ensuring that the agent's output is precise and useful for the next stage of the multi-agent system.
