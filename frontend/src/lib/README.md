# SANAD/frontend/src/lib/

This directory contains utility functions, helper libraries, and third-party integrations that are not specific to any particular feature or component but are used across the SANAD frontend application.

## Purpose:
To centralize generic, reusable code that enhances the functionality of the frontend without being directly tied to UI components or state management. This promotes code reusability and reduces redundancy.

## Contents:
- `utils.ts`: General utility functions (e.g., date formatting, string manipulation).
- `api.ts`: Configuration for API calls (e.g., base URL, default headers).
- `constants.ts`: Application-wide constants.

## Limitations:
- Avoid placing business logic or UI-specific code here.
- Libraries should be well-tested and have clear documentation.

## Needs:
- Well-organized and documented utility functions.
- Easy integration with third-party libraries.

## Usage for AI Agents:
AI agents should utilize the functions and configurations provided in this directory for common tasks. They should also contribute new generic utilities that can benefit the entire frontend application.
