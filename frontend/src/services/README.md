# Frontend services

API clients for the SANAD backend. All requests go through `apiClient.ts` with base path `/api/v1`.

## Files

| Service | Purpose |
|---------|---------|
| `apiClient.ts` | Shared HTTP client, JWT header injection |
| `authService.ts` | Register, login, profile |
| `queryService.ts` | Queries, SSE stream, export |
| `conversationService.ts` | Conversation threads |
| `preferencesService.ts` | User preferences |
| `featuresService.ts` | Scanners, zakat, documents, knowledge graph, translate, TTS |
| `scholarService.ts` | Scholar directory |
| `evaluationService.ts` | Judge dashboard |
| `billingService.ts` | Subscription and checkout |
| `searchService.ts` | Global search |
| `sourceService.ts` | Admin source CRUD |
| `audioService.ts` | Voice transcription (multipart) |
| `saasService.ts` | SSO and onboarding |

Live API reference: `/api/v1/docs` on the backend. Overview: [docs/API.md](../../../docs/API.md).
