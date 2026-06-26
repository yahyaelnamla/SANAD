# SANAD/frontend/src/hooks/

This directory contains custom React hooks for the SANAD frontend application. Custom hooks are reusable functions that encapsulate stateful logic and side effects, allowing for cleaner and more organized component code.

## Purpose:
To promote code reusability and abstract complex logic from components, making them more readable and easier to test. Hooks allow sharing logic without altering the component hierarchy.

## Contents:
- `useAuth.ts`: Hook for managing authentication state and actions.
- `useTheme.ts`: Hook for managing theme (light/dark mode) state.
- `useLanguage.ts`: Hook for managing language (Arabic/English) state.
- `useForm.ts`: Generic hook for form handling.

## Limitations:
- Hooks should follow React's rules of hooks.
- Avoid placing UI-specific logic directly within hooks; hooks should return data and functions that components can use.

## Needs:
- Clear and concise API for each hook.
- Thorough testing to ensure reliability.
- Good documentation for usage.

## Usage for AI Agents:
AI agents should create custom hooks to encapsulate reusable logic that can be shared across multiple components or features. They must ensure that hooks are well-designed, efficient, and adhere to React best practices.
