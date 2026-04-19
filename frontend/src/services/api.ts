import axios from "axios";
import type { ChatRequest, ChatResponse, DocumentIngested, DocumentListResponse, HealthResponse } from "../types";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

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

// ── Documents ─────────────────────────────────────────────────
export const uploadDocument = async (file: File): Promise<DocumentIngested> => {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await api.post<DocumentIngested>("/api/v1/documents/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
};

export const listDocuments = async (): Promise<DocumentListResponse> => {
  const { data } = await api.get<DocumentListResponse>("/api/v1/documents/");
  return data;
};
