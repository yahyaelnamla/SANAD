# SANAD/backend/

This directory contains the backend services and API implementation for the SANAD platform. It is built using FastAPI and is responsible for handling data processing, agent orchestration, and external integrations.

## Purpose:
To provide a robust and scalable API layer that supports the frontend application and interacts with various internal and external services, including the RAG pipeline, multi-agent system, and external financial/crypto APIs.

## Contents:
- `app/`: The main FastAPI application, containing API endpoints, models, schemas, services, and business logic.
- `config/`: Backend-specific configuration files.
- `tests/`: Unit and integration tests for backend components.

## Limitations:
- This directory should only contain backend-related code and configurations. Frontend assets or logic should reside in the `frontend/` directory.
- Direct database access should be abstracted through repositories or services.

## Needs:
- Implementation of FastAPI application.
- Integration with PostgreSQL and pgvector.
- Communication with the multi-agent system.
- Secure handling of API keys and credentials.

## Usage for AI Agents:
AI agents should focus on implementing the API endpoints, business logic, and data models as defined in the `API_SPEC.md` and `DATABASE_SCHEMA.md` documents. They should also ensure proper testing and documentation of all backend components.
