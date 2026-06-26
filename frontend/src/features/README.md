# SANAD/frontend/src/features/

This directory contains feature-specific modules for the SANAD frontend application. Each subdirectory represents a distinct feature of the application, encapsulating all related components, logic, and styles.

## Purpose:
To organize the frontend codebase by feature, promoting modularity, scalability, and easier management of complex functionalities. This approach allows for independent development and deployment of features.

## Contents:
- `search/`: Modules related to the search functionality.
- `chat/`: Modules related to the chat interface.
- `history/`: Modules related to user query history.
- `sources/`: Modules related to displaying and managing knowledge sources.
- `admin/`: Modules for administrative functionalities.
- `review/`: Modules for human review of responses.
- `auth/`: Modules for user authentication and authorization UI.
- `settings/`: Modules for user settings and preferences.

Each feature subdirectory may contain:
- `components/`: Components specific to this feature.
- `hooks/`: Custom hooks specific to this feature.
- `services/`: Data fetching and business logic specific to this feature.
- `types/`: TypeScript types specific to this feature.
- `utils/`: Utility functions specific to this feature.

## Limitations:
- Features should be as self-contained as possible to minimize dependencies on other features.
- Avoid duplicating global components or utilities; reuse from `components/` or `lib/`.

## Needs:
- Clear definition of each feature's scope and responsibilities.
- Consistent structure within each feature module.
- Seamless integration with global state and routing.

## Usage for AI Agents:
AI agents should develop individual features within their respective subdirectories. They must ensure that each feature is fully functional, well-tested, and adheres to the overall UI/UX design and technical specifications. Agents should also consider the internationalization and theme requirements for each feature.
