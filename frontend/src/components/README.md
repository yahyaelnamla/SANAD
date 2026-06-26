# SANAD/frontend/src/components/

This directory contains reusable UI components for the SANAD frontend application. These components are designed to be modular, independent, and focused on presenting specific pieces of the user interface.

## Purpose:
To promote reusability, maintainability, and consistency across the application's user interface. By breaking down the UI into smaller, manageable components, development becomes faster and easier to scale.

## Contents:
- `Button.tsx`: A reusable button component.
- `Card.tsx`: A generic card component for displaying content.
- `Navbar.tsx`: Navigation bar component.
- `Footer.tsx`: Footer component.
- `LanguageSwitcher.tsx`: Component for switching between Arabic and English.
- `ThemeToggle.tsx`: Component for switching between light and dark modes.

## Limitations:
- Components should be stateless or manage minimal local state. Complex state management should be handled by the `store/`.
- Avoid embedding business logic directly into presentational components.

## Needs:
- Clear props interface for each component.
- Adherence to design system guidelines (e.g., Shadcn UI).
- Accessibility considerations.

## Usage for AI Agents:
AI agents should develop and maintain these UI components, ensuring they are highly reusable, well-tested, and visually consistent with the overall design. They must also ensure that components support internationalization (Arabic/English) and theme switching (light/dark mode).
