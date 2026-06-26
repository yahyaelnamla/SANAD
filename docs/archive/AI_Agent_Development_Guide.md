# AI Agent Development Guide for SANAD Project

This guide outlines a comprehensive strategy for AI agents, such as Cursor or Manus, to systematically develop the SANAD platform. It emphasizes a phase-by-phase approach, adherence to modern design principles, and strict compliance with project integrity rules.

## 1. Project Overview: SANAD Platform

SANAD is an AI-powered multi-agent platform designed to provide evidence-based jurisprudential analysis for contemporary financial and economic issues. It aims to bridge modern economic realities with established Islamic jurisprudence through retrieval, reasoning, and human supervision. The platform does not issue independent fatwas but offers transparent, traceable analyses supported by classical references, contemporary fatwas, and Islamic finance standards.

**Core Capabilities:**
*   **Contemporary Financial Fatwas:** Analysis of cryptocurrencies, stocks, ETFs, DeFi, etc.
*   **Shariah Compliance Screening:** Determining Shariah compliance for companies and stocks.
*   **Multiple Opinions:** Presenting diverse jurisprudential opinions with explanations.
*   **Source Attribution:** Mandatory references for every statement.

**Multi-Agent Architecture:**
The system employs a series of specialized agents:
1.  **Intent Agent:** Understands user questions and extracts key entities.
2.  **Retrieval Agent:** Searches authenticated classical and contemporary sources.
3.  **Knowledge Agent:** Collects relevant evidences and jurisprudential principles.
4.  **Financial Context Agent:** Understands modern financial concepts using external APIs.
5.  **Reasoning Agent:** Performs jurisprudential adaptation (Takyeef Fiqhi).
6.  **Verification Agent:** Checks for missing references, hallucinations, and contradictions.
7.  **Response Builder:** Generates the final summary, evidences, opinions, sources, and confidence score.

## 2. AI Agent Development Workflow: Phase-by-Phase Implementation

AI agents are instructed to follow a strict phase-by-phase development methodology. The `sanad/phases/` directory contains detailed task files (`phaseX_description.md`) that outline the objectives, deliverables, and constraints for each phase. The `sanad/TODO.md` file serves as the main project checklist.

**General Workflow for AI Agents:**
1.  **Read Phase Documentation:** Before initiating any work, the AI agent *must* thoroughly read the `README.md` in the relevant project directory (e.g., `sanad/backend/README.md`) and the specific `phaseX_description.md` file for the current phase.
2.  **Update `TODO.md`:** Mark the current phase as 
in progress in the `TODO.md` file.
3.  **Implement Phase Tasks:** Develop the code, configurations, and documentation required for the current phase, strictly adhering to the guidelines in the `phaseX_description.md` and relevant `README.md` files within the project structure.
4.  **Write Tests:** For each implemented feature, write comprehensive unit, integration, and end-to-end tests in the `sanad/tests/` directory.
5.  **Update Documentation:** Ensure all relevant documentation (e.g., `PRD.md`, `SYSTEM_ARCHITECTURE.md`, `API_SPEC.md`) is updated to reflect changes or additions made during the phase.
6.  **Verify and Test:** Run all tests to ensure the phase is complete and stable. Address any failures or issues.
7.  **Mark Phase Complete:** Once all tasks for a phase are finished and verified, mark it as complete in `sanad/TODO.md`.
8.  **Proceed to Next Phase:** Move to the next phase as outlined in the `sanad/phases/` directory.

**Example Phase Breakdown (from `sanad/phases/`):**
*   **Phase 0: Setup:** Repository, architecture, Docker, CI/CD.
*   **Phase 1: Database:** Schema, migrations, ORM, models.
*   **Phase 2: RAG:** Pipeline, chunking, embeddings, vector store.
*   **Phase 3: Agents:** Multi-agent system development.
*   **Phase 4: API:** FastAPI implementation, Swagger, schemas.
*   **Phase 5: Frontend:** Next.js, Tailwind, Shadcn, responsive design.
*   **Phase 6: Auth:** JWT, RBAC, admin roles.
*   **Phase 7: Admin Panel:** Review dashboard, source editor.
*   **Phase 8: Testing:** Unit, integration, E2E tests.
*   **Phase 9: Deployment:** Docker, Nginx, Redis, Celery, monitoring.

## 3. Modern Design Principles & Localization

For the frontend development (Phase 5), AI agents must prioritize modern design principles and localization requirements:

*   **Arabic & English Language Support:** All UI elements, content, and dynamic text must support both Arabic and English. This includes proper text direction (RTL for Arabic, LTR for English), font selection, and localization of dates, numbers, and currencies.
*   **Light and Dark Mode:** The application must offer a seamless toggle between light and dark themes, ensuring all components and elements are visually consistent and accessible in both modes.
*   **Animations and Transitions:** Implement subtle, purposeful animations and transitions to enhance user experience, provide visual feedback, and improve perceived performance. Avoid excessive or distracting animations.
*   **Responsive Design:** The UI must be fully responsive, adapting gracefully to various screen sizes and devices (desktop, tablet, mobile) without compromising usability or aesthetics.
*   **Clean Typography and Color Palette:** Adhere to a well-defined typography scale and color palette that aligns with the project's branding and ensures readability and visual appeal.
*   **Accessibility:** Ensure the application is accessible to users with disabilities, following WCAG guidelines. This includes proper semantic HTML, keyboard navigation, and ARIA attributes.

## 4. Fanar Model API Integration

The Fanar API key (`tZEtEl576j28wwn1tBQUhhy5pBVRnuQ3o`) is provided in `sanad/config/fanar_api_keys.py`. AI agents will integrate this key for specific functionalities:

*   **Fanar Embedding Models:** Used in `sanad/rag/embeddings/fanar_embedding_model.py` for generating high-quality vector embeddings of text, crucial for the RAG pipeline.
*   **Fanar-Sadiq-Agentic (Primary Reasoning Model):** Used for planning, tool usage, multi-step reasoning, and agent orchestration within the `sanad/agents/` directory.
*   **Fanar-Sadiq (Arabic Generation Model):** Utilized by the `Response Builder Agent` (`sanad/agents/response_builder/`) for high-quality Arabic text generation, summarization, and response formatting.
*   **Fanar-C-2-27B (Advanced Reasoning Model):** Employed by the `Reasoning Agent` (`sanad/agents/reasoning_agent/`) for difficult cases, long-chain reasoning, and comparative analysis.
*   **Fanar-Guard-2 (Safety Model):** Integrated with the `Verification Agent` (`sanad/agents/verification_agent/`) for hallucination reduction, validation, and safety checks.

**Integration Guidelines:**
*   **Secure Handling:** The API key must be loaded securely from `sanad/config/fanar_api_keys.py` and never hardcoded directly into application logic or committed to version control outside of this designated file.
*   **Error Handling:** Implement robust error handling for all API calls to Fanar models, including retries, timeouts, and informative error messages.
*   **Rate Limiting:** Be mindful of API rate limits and implement appropriate back-off strategies.

## 5. Project Integrity Rules

AI agents *must* strictly adhere to the following integrity rules throughout the development process:

*   **No Hallucination Policy:** If no evidence exists to support a claim, the system *must* refuse to answer or clearly state the lack of evidence. The `Verification Agent` is critical here.
*   **Mandatory Citations:** Every answer and factual claim *must* be accompanied by clear, traceable references to authenticated sources. The `Response Builder` and `Verification Agent` are responsible for enforcing this.
*   **Transparency:** When disagreement exists among scholars or sources, all major opinions *must* be displayed with explanations of agreement and disagreement. This is a core function of the `Reasoning Agent` and `Response Builder`.
*   **Explainability:** Every conclusion *must* show the chain of reasoning: Evidence → Principles → Reasoning → Final Analysis. This ensures users understand *how* a conclusion was reached.
*   **Strict Structure Adherence:** Do not add folders or files that are not explicitly defined in the project structure or required by a specific phase. If a new structure is needed, it must be proposed and approved.
*   **Phase-by-Phase Implementation:** Do not implement features from future phases while working on the current one. Each phase must be completed and verified independently.

## 6. How to Use AI Agents (Cursor/Manus) to Complete the Project

To effectively use AI agents like Cursor or Manus for the SANAD project, follow these steps:

1.  **Initial Setup:**
    *   Provide the AI agent with the entire `sanad/` project directory (as a ZIP file or by granting access to the workspace).
    *   Share this `AI_Agent_Development_Guide.md` with the agent.
    *   Instruct the agent to start with `Phase 0: Setup` as outlined in `sanad/phases/phase0_setup.md`.

2.  **Phase Execution Loop:**
    *   **Agent's Action:** The AI agent reads the current `phaseX_description.md` and the relevant `README.md` files for the directories it will be working in.
    *   **Agent's Action:** The agent updates the `TODO.md` to reflect the current phase's status.
    *   **Agent's Action:** The agent implements the tasks for the current phase, writing code, configurations, and internal documentation (e.g., `prompt.md` for other agents).
    *   **Agent's Action:** The agent writes and runs tests for the implemented features.
    *   **Agent's Action:** The agent updates project-level documentation (e.g., `SYSTEM_ARCHITECTURE.md`, `API_SPEC.md`) as needed.
    *   **Agent's Action:** The agent verifies that all tests pass and the phase objectives are met.
    *   **Agent's Action:** The agent marks the phase as complete in `TODO.md`.
    *   **User's Action (or Agent's Self-Initiation):** The agent proceeds to the next phase, repeating the loop.

3.  **Specific Instructions for AI Agents:**
    *   **Code Generation:** When generating code, ensure it adheres to the technology stack (FastAPI, Next.js, PostgreSQL, pgvector, LangGraph) and follows best practices for each framework.
    *   **Documentation:** Generate comprehensive inline comments and docstrings for all code. Update Markdown documentation files (`.md`) as development progresses.
    *   **Testing:** Prioritize test-driven development (TDD) where feasible. Ensure high test coverage for all critical components.
    *   **Security:** Always consider security implications, especially when handling user data, authentication, and external API integrations.
    *   **Performance:** Optimize code for performance, particularly in data-intensive parts like the RAG pipeline and API endpoints.
    *   **User Interface (Frontend):** When working on the frontend, pay close attention to the modern design principles, localization, and accessibility requirements detailed in Section 3.
    *   **Agent Prompts:** When defining `prompt.md` for each agent, ensure they are clear, concise, and provide sufficient context and constraints for the agent to perform its task effectively.

By following this guide, AI agents can systematically build the SANAD platform, ensuring a high-quality, well-documented, and robust system that meets all specified requirements.
