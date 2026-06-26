# SANAD/frontend/src/

This directory contains the source code for the Next.js frontend application. It follows a modular structure to organize components, features, and utilities.

## Purpose:
To house all the development-related files for the user interface, ensuring a clean separation of concerns and facilitating efficient development and maintenance of the frontend application.

## Contents:
- `app/`: Next.js application routing and layout.
- `components/`: Reusable UI components.
- `features/`: Feature-specific modules (e.g., search, chat, history).
- `hooks/`: Custom React hooks for shared logic.
- `services/`: Frontend services for API interaction.
- `store/`: State management (e.g., Redux, Zustand).
- `types/`: TypeScript type definitions.
- `lib/`: Utility functions and libraries.
- `styles/`: Global styles and Tailwind CSS configurations.

## Limitations:
- This directory should not contain any backend logic or sensitive API keys.
- All data fetching should be done through the `services/` layer.

## Needs:
- Clear component hierarchy.
- Consistent styling and theming.
- Efficient state management.

## Usage for AI Agents:
AI agents should develop the frontend components and features within this directory, adhering to the UI/UX design guidelines. They must ensure responsiveness, accessibility, and cross-browser compatibility, and integrate with the backend API via the `services/` modules.
