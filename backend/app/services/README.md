# SANAD/backend/app/services/

This directory contains the business logic and service layer for the SANAD backend application. Services encapsulate complex operations, orchestrate interactions between different components (e.g., repositories, agents), and enforce business rules.

## Purpose:
To separate business logic from API endpoints and data access layers, promoting a clean architecture, reusability, and testability. Services act as the primary interface for performing application-specific operations.

## Contents:
- Files defining various services (e.g., `user_service.py`, `query_service.py`, `fatwa_service.py`).

## Limitations:
- Services should not directly handle HTTP requests or responses; that is the responsibility of the API layer.
- Services should not directly interact with the database; they should use repositories for data access.

## Needs:
- Clear definition of business operations.
- Dependency injection for external components (repositories, agents).
- Robust error handling and logging.

## Usage for AI Agents:
AI agents should implement the core business logic within these service files. They must ensure that services are well-defined, testable, and adhere to the overall system architecture. Services will be called by the API endpoints to perform complex tasks.
