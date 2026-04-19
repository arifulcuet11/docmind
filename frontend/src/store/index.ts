import { create } from "zustand";
import type { Message, ChatStatus, UploadStatus } from "../types";
import { sendMessage, uploadDocument, listDocuments, deleteDocument } from "../services/api";

interface DocMindStore {
  // Chat
  messages: Message[];
  chatStatus: ChatStatus;
  sessionId: string | null;
  addMessage: (message: Message) => void;
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

export const useDocMindStore = create<DocMindStore>((set, get) => ({
  // ── Chat ───────────────────────────────────────────────────
  messages: [],
  chatStatus: "idle",
  sessionId: null,

  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),

  ask: async (question: string) => {
    const { selectedSources } = get();

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: question,
      timestamp: new Date(),
    };
    set((state) => ({
      messages: [...state.messages, userMessage],
      chatStatus: "loading",
    }));

    try {
      const response = await sendMessage({
        question,
        session_id: get().sessionId ?? undefined,
        selected_sources: selectedSources.length > 0 ? selectedSources : undefined,
      });

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: response.answer,
        sources: response.sources,
        timestamp: new Date(),
      };
      set((state) => ({
        messages: [...state.messages, assistantMessage],
        chatStatus: "idle",
        sessionId: response.session_id ?? state.sessionId,
      }));
    } catch {
      set({ chatStatus: "error" });
    }
  },

  clearChat: () => set({ messages: [], sessionId: null }),

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
}));