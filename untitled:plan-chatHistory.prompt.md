## Plan: Add Chat History Persistence

TL;DR: Persist chat history in the frontend by saving the Zustand chat state to localStorage and restoring it on page load. This fits your current project structure and avoids adding a backend storage layer unless you want cross-device/history sharing later.

Steps
1. Add a localStorage persistence helper for chat state. Use a stable key such as `docmind_chat_history`.
2. Update `frontend/src/store/index.ts` so the store initializes `messages` and `sessionId` from saved JSON if present.
3. Serialize and save `messages` and `sessionId` whenever `messages` changes or when a new session is created.
4. Update `clearChat` to remove the saved localStorage entry and reset the store state.
5. Ensure timestamp values are restored as `Date` objects after parsing JSON.
6. Optionally add a small `frontend/src/utils/storage.ts` helper if you want cleaner separation from the store.
7. Keep current streaming and session handling unchanged; local persistence only preserves the visible chat history and session metadata.

Relevant files
- `frontend/src/store/index.ts` — main place to implement load/save and clear logic
- `frontend/src/components/chat/ChatWindow.tsx` — no required changes unless you want a UI control for history reset
- `frontend/src/types/index.ts` — optional if you want to add a new typed storage payload interface

Verification
1. Start frontend and backend.
2. Ask a question in the chat and verify messages appear normally.
3. Refresh the browser and confirm the previous chat messages and assistant answer are restored.
4. Click clear chat and verify the UI empties and localStorage key is removed.
5. Confirm `sessionId` is preserved across refresh if present.

Decisions
- Primary approach: browser localStorage persistence because the project currently has no backend chat storage API.
- Extension path: add backend chat history routes later if you need server-side persistence or sharing across devices.

Further Considerations
1. If you want cross-device history or long-lived chat sessions, the next step is a backend route plus a simple JSON storage file or database.
2. If your app needs multiple saved conversations, the persistence schema should store multiple sessions rather than a single chat history object.
