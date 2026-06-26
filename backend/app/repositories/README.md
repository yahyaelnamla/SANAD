# SANAD/backend/app/repositories/

This directory contains the data access layer (repositories) for the SANAD backend application. Repositories abstract the underlying database operations, providing a clean interface for services to interact with data without knowing the specifics of the database implementation.

## Purpose:
To centralize data access logic, making it easier to manage and test database interactions. This layer is responsible for performing CRUD (Create, Read, Update, Delete) operations on the database models.

## Contents:
- Files defining repositories for various models (e.g., `user_repository.py`, `fatwa_repository.py`, `source_repository.py`).

## Limitations:
- Repositories should not contain business logic; they should focus solely on data persistence and retrieval.
- Avoid direct exposure of ORM session or database connections to the service layer.

## Needs:
- Consistent interface for data access operations.
- Efficient and optimized database queries.
- Error handling for database-related issues.

## Usage for AI Agents:
AI agents should implement the repository classes, ensuring they provide all necessary methods for interacting with the database models. They must adhere to the `DATABASE_SCHEMA.md` and ensure that data operations are performed efficiently and securely.
