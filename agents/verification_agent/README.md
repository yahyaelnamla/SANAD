"""# SANAD/agents/verification_agent/

This directory contains the Verification Agent, which acts as a critical quality control layer in the SANAD multi-agent system. Its role is to scrutinize the output of the Reasoning Agent for accuracy, consistency, and adherence to integrity rules.

## Purpose:
To ensure the reliability and trustworthiness of the SANAD platform's responses by checking for missing references, hallucinations, contradictions, and unsupported claims. This agent is vital for maintaining the platform's no-hallucination policy and mandatory citation requirements.

## Contents:
- `agent.py`: The main logic for the Verification Agent.
- `prompt.md`: The system prompt or instructions for the Verification Agent.
- `tools.py`: Definitions of tools the Verification Agent can use (e.g., source cross-referencing, logical consistency checkers, fact-checking APIs).
- `models.py`: Data models specific to the Verification Agent (e.g., `VerificationReport`, `IntegrityCheckResult`).
- `tests.py`: Unit tests for the Verification Agent.

## Limitations:
- The effectiveness of verification depends on the comprehensiveness of the integrity rules and the agent's ability to detect subtle errors.
- May require human feedback loops to continuously improve its detection capabilities.

## Needs:
- Robust fact-checking and logical consistency algorithms.
- Access to original sources for cross-referencing.
- Mechanisms for flagging and rejecting unsupported answers.

## Usage for AI Agents:
AI agents should develop and refine the Verification Agent to rigorously check the output of the Reasoning Agent. They must focus on implementing the integrity rules (no hallucination, mandatory citations, transparency, explainability) and ensuring that only high-quality, evidence-based responses proceed to the Response Builder.
"""
