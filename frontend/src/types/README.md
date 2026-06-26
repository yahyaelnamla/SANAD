# SANAD/frontend/src/types/

This directory contains TypeScript type definitions for the SANAD frontend application. These types ensure type safety, improve code readability, and facilitate better developer experience.

## Purpose:
To define clear and consistent data structures for props, state, API responses, and other data used throughout the frontend. This helps catch errors during development, provides better autocompletion, and makes the codebase easier to understand.

## Contents:
- `auth.ts`: Type definitions for authentication-related data.
- `query.ts`: Type definitions for query inputs and responses.
- `common.ts`: Common utility types.

## Limitations:
- Types should accurately reflect the data structures. Outdated types can lead to errors.
- Avoid overly complex or deeply nested types; simplify where possible.

## Needs:
- Comprehensive type coverage for all data structures.
- Alignment with backend API schemas.
- Clear and descriptive type names.

## Usage for AI Agents:
AI agents should define and maintain TypeScript types within this directory, ensuring they are consistent with the backend API specifications and accurately represent the data used in the frontend. They must leverage these types to write type-safe and robust code.
