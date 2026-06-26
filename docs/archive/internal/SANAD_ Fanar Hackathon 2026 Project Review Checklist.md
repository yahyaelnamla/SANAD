# SANAD: "Road to Victory" Hackathon Review & Implementation Checklist

As a Cursor agent, your mission is to ensure **SANAD** wins the Fanar Hackathon 2026. You are not just a reviewer; you are an **active developer**. For every item below, you must follow this logic:
1.  **Check:** Does the codebase satisfy this requirement?
2.  **Act (Missing):** If not, **write the code** to implement it immediately.
3.  **Highlight (Existing):** If yes, ensure it is **explicitly mentioned in the README** and **visually highlighted in the UI** (e.g., adding a "Powered by Fanar" badge or a specific feature card).
4.  **Analyze:** Document how Fanar enabled this and what could be improved.

---

## 1. Impact & Problem Solving (25% Weight)
*   **[ ] Domain Specificity:** Is SANAD clearly solving a "Smart Government" or "Financial/Legal" problem for the Arabic world? 
    *   *Action:* If vague, update the Landing Page and README with a concrete "Problem Statement" focused on Shariah compliance in modern finance.
*   **[ ] Value Proposition:** Is the benefit to researchers and scholars obvious?
    *   *Action:* Add a "Quick Start for Scholars" guide to the README.

## 2. Agentic Design & Innovation (30% Weight)
*   **[ ] Multi-Agent Orchestration:** Does the system use a mesh of agents (Intent, Fiqh, Financial, Zakat, Reasoning, Guard)?
    *   *Action:* If any agent is missing or just a "mock," implement the full logic using `Fanar-Sadiq-Agentic`.
*   **[ ] Tool Usage:** Are agents using external tools (Yahoo Finance, Serper, Zakat Engine)?
    *   *Action:* Ensure all tools in `SANAD.md` are fully integrated and functional.
*   **[ ] Traceability:** Can the user see the "Agentic Thought Process"?
    *   *Action:* Implement a "View Execution Trace" button in the UI showing which agent did what.

## 3. Effective Use of Fanar (20% Weight)
*   **[ ] Multimodal Power:** Are we using Voice (`Fanar-Aura-STT-1`) and PDF Vision (`Fanar-Oryx-IVU-2`)?
    *   *Action:* If the UI has buttons but no backend logic, **write the integration code**.
*   **[ ] Arabic Excellence:** Is the system using `Fanar-C-2-27B` for complex Arabic reasoning?
    *   *Action:* Force the reasoning prompt to use Chain-of-Thought in Arabic.
*   **[ ] Safety First:** Is `Fanar-Guard-2` checking every response?
    *   *Action:* Implement a middleware that runs all outputs through the Guard model.

## 4. User Experience & Polish (10% Weight)
*   **[ ] Precision Nexus Theme:** Does the UI use the Deep Navy (#0A192F) and Electric Cyan (#00F0FF) palette?
    *   *Action:* Update CSS/Tailwind configs to match this high-spec visual language.
*   **[ ] Demonstration Readiness:** Is there a "Demo Mode" or "Sample Queries" section?
    *   *Action:* Add 3-5 high-impact sample queries (e.g., "Is Tesla Shariah compliant?") to the home page.

## 5. Evaluation & Insights (15% Weight)
*   **[ ] Fanar Capability Report:** Have we documented what Fanar does better than GPT-4/Claude?
    *   *Action:* Create `FANAR_INSIGHTS.md` with specific examples of Fanar's superior Arabic/Fiqh performance.
*   **[ ] Feedback for Fanar:** Are there clear suggestions for the Fanar team?
    *   *Action:* List 3 technical recommendations for future Fanar API versions in the README.

---

## Deliverable Status
*   [ ] **Working Prototype:** Every button works.
*   [ ] **Technical README:** Includes Architecture Diagram, Agent Flows, and API Metrics.
*   [ ] **Feature Showcase:** A dedicated section in the UI/README titled "Why SANAD Wins."
