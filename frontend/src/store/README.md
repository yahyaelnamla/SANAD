# Frontend store (Zustand)

Global client state using [Zustand](https://github.com/pmndrs/zustand) with selective `persist` middleware.

## Stores

| File | Purpose |
|------|---------|
| `authStore.ts` | JWT token, user profile, hydration |
| `conversationStore.ts` | Chat threads scoped to `ownerUserId` |
| `settingsStore.ts` | Locale, theme, madhhab, model preference |
| `bookmarkStore.ts` | Saved query bookmarks |
| `offlineQueueStore.ts` | Offline query queue for PWA |

Conversation data is persisted to `localStorage` with an `ownerUserId` guard to prevent cross-user leaks on shared devices.
