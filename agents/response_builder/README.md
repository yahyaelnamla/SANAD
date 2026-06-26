# SANAD/agents/response_builder/

This directory contains the Response Builder Agent, which is the final agent in the SANAD multi-agent system. Its role is to synthesize the verified analysis into a coherent, well-structured, and user-friendly response.

## Purpose:
To generate the final output for the user, including a summary, evidences, scholarly opinions, sources, and a confidence score. This agent ensures that the response is clear, comprehensive, and adheres to the platform's transparency and explainability principles.

## Contents:
- `agent.py`: The main logic for the Response Builder Agent.
- `prompt.md`: The system prompt or instructions for the Response Builder Agent.
- `tools.py`: Definitions of tools the Response Builder Agent can use (e.g., text generation, summarization, formatting).
- `models.py`: Data models specific to the Response Builder Agent (e.g., `FinalResponse`, `ConfidenceScore`).
- `tests.py`: Unit tests for the Response Builder Agent.

## Limitations:
- The quality of the final response depends on the accuracy and completeness of the information provided by previous agents.
- Requires strong natural language generation capabilities to produce clear and nuanced explanations.

## Needs:
- Advanced text generation and summarization techniques.
- Ability to format responses according to predefined templates (e.g., Markdown, HTML).
- Integration with the Arabic Generation Model (Fanar-Sadiq) for high-quality Arabic output.

## Usage for AI Agents:
AI agents should develop and refine the Response Builder Agent to generate high-quality, comprehensive, and user-friendly responses. They must ensure that the agent accurately presents all the gathered information, scholarly opinions, and the confidence score, while adhering to the specified language (Arabic/English) and design considerations for modern design (light/dark mode, animations).
