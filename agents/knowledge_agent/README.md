# SANAD/agents/knowledge_agent/

This directory contains the Knowledge Agent, which is responsible for collecting and synthesizing relevant evidences, jurisprudential principles, previous fatwas, and similar cases based on the information retrieved by the Retrieval Agent.

## Purpose:
To build a comprehensive context for the Reasoning Agent by organizing and structuring the retrieved raw data into actionable knowledge. This involves identifying key arguments, legal maxims, and historical precedents relevant to the user's query.

## Contents:
- `agent.py`: The main logic for the Knowledge Agent.
- `prompt.md`: The system prompt or instructions for the Knowledge Agent.
- `tools.py`: Definitions of tools the Knowledge Agent can use (e.g., text summarization, concept extraction, cross-referencing).
- `models.py`: Data models specific to the Knowledge Agent (e.g., `KnowledgeContext`, `JurisprudentialPrinciple`).
- `tests.py`: Unit tests for the Knowledge Agent.

## Limitations:
- The quality of the synthesized knowledge depends on the accuracy of the retrieved information and the agent's ability to identify salient points.
- Requires robust natural language processing capabilities to understand and extract complex jurisprudential concepts.

## Needs:
- Advanced text analysis and summarization techniques.
- Ability to identify and categorize different types of jurisprudential evidence.
- Integration with the RAG pipeline for detailed document analysis.

## Usage for AI Agents:
AI agents should develop and refine the Knowledge Agent to effectively process retrieved information and construct a coherent knowledge base for the Reasoning Agent. They must ensure that the agent can accurately identify and present all relevant evidences and principles.
