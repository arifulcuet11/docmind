// ── Chat ─────────────────────────────────────────────────────
export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: string[];
  timestamp: Date;
}

export interface ChatRequest {
  question: string;
  session_id?: string;
  selected_sources?: string[];   // filter which docs to search
}

export interface ChatResponse {
  answer: string;
  sources: string[];
  session_id?: string;
}

// ── Documents ─────────────────────────────────────────────────
export interface DocumentIngested {
  file: string;
  chunks: number;
  pages: number;
  message: string;
}

export interface DocumentDeleted {
  file: string;
  message: string;
}

export interface DocumentListResponse {
  documents: string[];
  count: number;
}

// ── Health ────────────────────────────────────────────────────
export interface HealthResponse {
  status: string;
  app: string;
  version: string;
  provider: string;
  model: string;
}

// ── UI State ──────────────────────────────────────────────────
export type UploadStatus = "idle" | "uploading" | "success" | "error";
export type ChatStatus = "idle" | "loading" | "error";