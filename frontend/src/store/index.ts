import { create } from "zustand";
import type { ChatSession, Message, ChatStatus, UploadStatus } from "../types";
import { streamMessage, uploadDocument, listDocuments, deleteDocument } from "../services/api";

const HISTORY_BUFFER = 8;

const STORAGE_KEY = "docmind_chat_sessions";

const createSession = (name = "New chat") => ({
  id: crypto.randomUUID(),
  name,
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
  messages: [] as Message[],
});

const restoreMessage = (message: any): Message => ({
  id: message.id,
  role: message.role,
  content: message.content,
  sources: message.sources,
  timestamp: message.timestamp ? new Date(message.timestamp) : new Date(),
});

const restoreSession = (session: any): ChatSession => ({
  id: session.id,
  name: session.name || "New chat",
  createdAt: session.createdAt || new Date().toISOString(),
  updatedAt: session.updatedAt || new Date().toISOString(),
  messages: Array.isArray(session.messages)
    ? session.messages.map(restoreMessage)
    : [],
});

const loadChatSessions = () => {
  if (typeof window === "undefined") {
    const session = createSession();
    return {
      chatSessions: [session],
      activeSessionId: session.id,
      messages: session.messages,
    };
  }

  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    const session = createSession();
    return {
      chatSessions: [session],
      activeSessionId: session.id,
      messages: session.messages,
    };
  }

  try {
    const parsed = JSON.parse(raw);
    const chatSessions = Array.isArray(parsed.chatSessions)
      ? parsed.chatSessions.map(restoreSession)
      : [];
    const activeSessionId = parsed.activeSessionId ?? chatSessions[0]?.id ?? null;
    const activeSession = chatSessions.find((session) => session.id === activeSessionId) ?? chatSessions[0];

    if (!activeSession) {
      const session = createSession();
      return {
        chatSessions: [session],
        activeSessionId: session.id,
        messages: session.messages,
      };
    }

    return {
      chatSessions,
      activeSessionId,
      messages: activeSession.messages,
    };
  } catch {
    const session = createSession();
    return {
      chatSessions: [session],
      activeSessionId: session.id,
      messages: session.messages,
    };
  }
};

const persistChatSessions = (chatSessions: ChatSession[], activeSessionId: string | null) => {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify({ chatSessions, activeSessionId }));
};

interface DocMindStore {
  // Chat
  messages: Message[];
  chatSessions: ChatSession[];
  activeSessionId: string | null;
  chatStatus: ChatStatus;
  sessionId: string | null;
  addMessage: (message: Message) => void;
  appendMessageContent: (messageId: string, chunk: string) => void;
  setMessageSources: (messageId: string, sources: string[]) => void;
  createChatSession: (name?: string) => void;
  setActiveSession: (sessionId: string) => void;
  deleteChatSession: (sessionId: string) => void;
  ask: (question: string) => Promise<void>;
  clearChat: () => void;

  // Documents
  documents: string[];
  selectedSources: string[];
  uploadStatus: UploadStatus;
  uploadError: string | null;
  upload: (file: File) => Promise<void>;
  fetchDocuments: () => Promise<void>;
  deleteDoc: (filename: string) => Promise<void>;
  toggleSource: (source: string) => void;
  selectAllSources: () => void;
  clearSourceSelection: () => void;
}

export const useDocMindStore = create<DocMindStore>((set, get) => {
  const initialState = loadChatSessions();

  return {
    // ── Chat ───────────────────────────────────────────────────
    messages: initialState.messages,
    chatSessions: initialState.chatSessions,
    activeSessionId: initialState.activeSessionId,
    chatStatus: "idle",
    sessionId: null,

    addMessage: (message) =>
      set((state) => {
        const activeId = state.activeSessionId ?? state.chatSessions[0]?.id ?? null;
        const updatedSessions = state.chatSessions.map((session) =>
          session.id === activeId
            ? {
                ...session,
                messages: [...session.messages, message],
                updatedAt: new Date().toISOString(),
              }
            : session
        );
        persistChatSessions(updatedSessions, activeId);
        return {
          chatSessions: updatedSessions,
          messages: updatedSessions.find((session) => session.id === activeId)?.messages ?? [],
          activeSessionId: activeId,
        };
      }),

    appendMessageContent: (messageId: string, chunk: string) =>
      set((state) => {
        const activeId = state.activeSessionId ?? state.chatSessions[0]?.id ?? null;
        const updatedSessions = state.chatSessions.map((session) =>
          session.id === activeId
            ? {
                ...session,
                messages: session.messages.map((message) =>
                  message.id === messageId
                    ? { ...message, content: (message.content ?? "") + chunk }
                    : message
                ),
                updatedAt: new Date().toISOString(),
              }
            : session
        );
        persistChatSessions(updatedSessions, activeId);
        return {
          chatSessions: updatedSessions,
          messages: updatedSessions.find((session) => session.id === activeId)?.messages ?? [],
        };
      }),

    setMessageSources: (messageId: string, sources: string[]) =>
      set((state) => {
        const activeId = state.activeSessionId ?? state.chatSessions[0]?.id ?? null;
        const updatedSessions = state.chatSessions.map((session) =>
          session.id === activeId
            ? {
                ...session,
                messages: session.messages.map((message) =>
                  message.id === messageId ? { ...message, sources } : message
                ),
                updatedAt: new Date().toISOString(),
              }
            : session
        );
        persistChatSessions(updatedSessions, activeId);
        return {
          chatSessions: updatedSessions,
          messages: updatedSessions.find((session) => session.id === activeId)?.messages ?? [],
        };
      }),

    createChatSession: (name = "New chat") =>
      set((state) => {
        const session = createSession(name);
        const updatedSessions = [...state.chatSessions, session];
        persistChatSessions(updatedSessions, session.id);
        return {
          chatSessions: updatedSessions,
          activeSessionId: session.id,
          messages: session.messages,
        };
      }),

    setActiveSession: (sessionId: string) =>
      set((state) => {
        const nextSession = state.chatSessions.find((session) => session.id === sessionId);
        if (!nextSession) return {};
        persistChatSessions(state.chatSessions, sessionId);
        return {
          activeSessionId: sessionId,
          messages: nextSession.messages,
        };
      }),

    deleteChatSession: (sessionId: string) =>
      set((state) => {
        const updatedSessions = state.chatSessions.filter((session) => session.id !== sessionId);
        let nextActiveSessionId = state.activeSessionId;
        let nextMessages: Message[] = [];

        if (nextActiveSessionId === sessionId) {
          nextActiveSessionId = updatedSessions[0]?.id ?? null;
        }

        if (nextActiveSessionId) {
          nextMessages = updatedSessions.find((session) => session.id === nextActiveSessionId)?.messages ?? [];
        }

        let finalSessions = updatedSessions;
        if (finalSessions.length === 0) {
          const session = createSession();
          finalSessions = [session];
          nextActiveSessionId = session.id;
          nextMessages = session.messages;
        }

        persistChatSessions(finalSessions, nextActiveSessionId);
        return {
          chatSessions: finalSessions,
          activeSessionId: nextActiveSessionId,
          messages: nextMessages,
        };
      }),

    ask: async (question: string) => {
      const { selectedSources } = get();
      const currentMessages = get().messages;
      const isFirstMessage = currentMessages.length === 0;

      // Collect prior messages as history before adding the new turn
      const chatHistory = currentMessages
        .filter((m) => m.content)
        .slice(-HISTORY_BUFFER)
        .map((m) => ({ role: m.role, content: m.content }));

      const userMessage: Message = {
        id: crypto.randomUUID(),
        role: "user",
        content: question,
        timestamp: new Date(),
      };
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: "",
        sources: [],
        timestamp: new Date(),
      };

      get().addMessage(userMessage);
      get().addMessage(assistantMessage);

      // Auto-name session from first message (first 10-20 chars)
      if (isFirstMessage) {
        const sessionName = question.slice(0, 20).trim();
        if (sessionName) {
          set((state) => {
            const activeId = state.activeSessionId;
            return {
              chatSessions: state.chatSessions.map((session) =>
                session.id === activeId
                  ? { ...session, name: sessionName, updatedAt: new Date().toISOString() }
                  : session
              ),
            };
          });
        }
      }

      set({ chatStatus: "loading" });

      try {
        await streamMessage(
          {
            question,
            session_id: get().sessionId ?? undefined,
            selected_sources: selectedSources.length > 0 ? selectedSources : undefined,
            chat_history: chatHistory.length > 0 ? chatHistory : undefined,
          },
          (chunk) => {
            get().appendMessageContent(assistantMessage.id, chunk);
          },
          (sources, sessionId) => {
            get().setMessageSources(assistantMessage.id, sources ?? []);
            set((state) => ({
              chatStatus: "idle",
              sessionId: sessionId ?? state.sessionId,
            }));
          }
        );
      } catch {
        set({ chatStatus: "error" });
      }
    },

    clearChat: () => {
      const session = createSession();
      persistChatSessions([session], session.id);
      set({
        chatSessions: [session],
        activeSessionId: session.id,
        messages: session.messages,
        sessionId: null,
      });
    },

    // ── Documents ──────────────────────────────────────────────
    documents: [],
    selectedSources: [],
    uploadStatus: "idle",
    uploadError: null,

    upload: async (file: File) => {
      set({ uploadStatus: "uploading", uploadError: null });
      try {
        await uploadDocument(file);
        set({ uploadStatus: "success" });
        get().fetchDocuments();
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : "Upload failed";
        set({ uploadStatus: "error", uploadError: message });
      }
    },

    fetchDocuments: async () => {
      try {
        const result = await listDocuments();
        set({ documents: result.documents });
      } catch {
        // silently fail
      }
    },

    deleteDoc: async (filename: string) => {
      try {
        await deleteDocument(filename);
        set((state) => ({
          documents: state.documents.filter((d) => !d.includes(filename)),
          selectedSources: state.selectedSources.filter((s) => !s.includes(filename)),
        }));
      } catch (err) {
        console.error("Delete failed:", err);
      }
    },

    toggleSource: (source: string) => {
      set((state) => {
        const isSelected = state.selectedSources.includes(source);
        return {
          selectedSources: isSelected
            ? state.selectedSources.filter((s) => s !== source)
            : [...state.selectedSources, source],
        };
      });
    },

    selectAllSources: () => {
      set((state) => ({ selectedSources: [...state.documents] }));
    },

    clearSourceSelection: () => set({ selectedSources: [] }),
  };
});
