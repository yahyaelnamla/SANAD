# SANAD/backend/app/config/

This directory contains application-specific configuration settings for the FastAPI backend. These settings can include database connection strings, external service URLs, and other environment-dependent variables.

## Purpose:
To centralize and manage configuration parameters, allowing for easy modification of application behavior without changing the core code. This supports different environments (development, testing, production) and simplifies deployment.

## Contents:
- `settings.py`: Defines application settings, often loaded from environment variables.
- `database.py`: Database-specific configuration (e.g., connection URL).

## Limitations:
- Sensitive information should be loaded from environment variables and not hardcoded.
- Configuration files should be version-controlled but sensitive values should be handled separately.

## Needs:
- Clear separation of configuration from code.
- Ability to easily switch configurations based on the deployment environment.
- Secure handling of sensitive configuration values.

## Usage for AI Agents:
AI agents should refer to this directory for all application-specific configuration values. They must ensure that configurations are correctly loaded and applied, and that sensitive information is handled securely.
