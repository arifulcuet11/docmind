import axios from "axios";
import type { ChatRequest, ChatResponse, DocumentIngested, DocumentListResponse, HealthResponse } from "../types";

const BASE_URL = (import.meta as any).env?.VITE_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
});

// ── Health ────────────────────────────────────────────────────
export const getHealth = async (): Promise<HealthResponse> => {
  const { data } = await api.get<HealthResponse>("/health");
  return data;
};

// ── Chat ──────────────────────────────────────────────────────
export const sendMessage = async (request: ChatRequest): Promise<ChatResponse> => {
  const { data } = await api.post<ChatResponse>("/api/v1/chat/", request);
  return data;
};

export const streamMessage = async (
  request: ChatRequest,
  onChunk: (chunk: string) => void,
  onDone: (sources: string[] | undefined, sessionId?: string) => void
): Promise<void> => {
  const response = await fetch(`${BASE_URL}/api/v1/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || "Streaming request failed");
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error("Unable to read streaming response");
  }

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (!line.trim()) continue;
      if (!line.startsWith("data:")) continue;
      const payload = line.slice(5).trim();
      if (!payload) continue;
      if (payload === "[DONE]") continue;

      let event;
      try {
        event = JSON.parse(payload);
      } catch (error) {
        continue;
      }

      if (event.type === "chunk" && typeof event.text === "string") {
        onChunk(event.text);
      }

      if (event.type === "done") {
        onDone(event.sources, event.session_id);
      }

      if (event.type === "error") {
        throw new Error(event.error || "Streaming error");
      }
    }
  }

  if (buffer.trim().startsWith("data:")) {
    const payload = buffer.trim().slice(5).trim();
    if (payload && payload !== "[DONE]") {
      const event = JSON.parse(payload);
      if (event.type === "done") {
        onDone(event.sources, event.session_id);
      }
    }
  }
};

// ── Documents ─────────────────────────────────────────────────
export const uploadDocument = async (file: File): Promise<DocumentIngested> => {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await api.post<DocumentIngested>("/api/v1/documents/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
};

export const deleteDocument = async (filename: string): Promise<void> => {
  await api.delete(`/api/v1/documents/${encodeURIComponent(filename)}`);
};

export const listDocuments = async (): Promise<DocumentListResponse> => {
  const { data } = await api.get<DocumentListResponse>("/api/v1/documents/");
  return data;
};
