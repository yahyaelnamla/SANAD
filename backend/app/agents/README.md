# SANAD/backend/app/agents/

This directory serves as the integration point between the FastAPI backend and the multi-agent system. It contains modules that facilitate communication and orchestration of the specialized AI agents.

## Purpose:
To provide an interface for the backend services to interact with the various AI agents (Intent Agent, Retrieval Agent, Reasoning Agent, etc.). This ensures that the agent logic is decoupled from the core backend services, allowing for independent development and scaling.

## Contents:
- `agent_orchestrator.py`: Module responsible for coordinating the flow between different agents.
- `agent_interface.py`: Defines the communication protocols and data structures for interacting with agents.

## Limitations:
- This directory should not contain the core logic of the agents themselves; that resides in the top-level `sanad/agents/` directory.
- Focus on the communication and integration aspects, not the internal workings of each agent.

## Needs:
- Clear communication channels with the multi-agent system.
- Robust error handling for agent interactions.
- Efficient data exchange between backend and agents.

## Usage for AI Agents:
AI agents working on the backend should implement the integration logic within this directory. They must ensure that the backend can effectively invoke and receive responses from the multi-agent system, as defined in `AGENTS_DESIGN.md`.
