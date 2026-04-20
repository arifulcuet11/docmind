import { useEffect, useState } from "react";
import { Brain, Server, ChevronLeft, ChevronRight } from "lucide-react";
import { ChatWindow } from "./components/chat/ChatWindow";
import { DocumentPanel } from "./components/documents/DocumentPanel";
import { ChatSessionsPanel } from "./components/chat/ChatSessionsPanel";
import { getHealth } from "./services/api";
import type { HealthResponse } from "./types";

export default function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [sessionsMinimized, setSessionsMinimized] = useState(false);

  useEffect(() => {
    getHealth()
      .then(setHealth)
      .catch(() => setHealth(null));
  }, []);

  return (
    <div className="flex flex-col h-screen bg-gray-50 font-sans">
      {/* Navbar */}
      <header className="flex items-center justify-between px-6 py-3 bg-white border-b border-gray-200 shadow-sm">
        <div className="flex items-center gap-2">
          <Brain size={22} className="text-blue-600" />
          <span className="font-bold text-gray-900 text-lg tracking-tight">DocMind</span>
          <span className="text-xs text-gray-400 ml-1">LLM Chatbot</span>
        </div>
        {health && (
          <div className="flex items-center gap-2 text-xs text-gray-500 bg-gray-100 px-3 py-1.5 rounded-full">
            <Server size={12} className="text-green-500" />
            <span className="capitalize font-medium">{health.provider}</span>
            <span className="text-gray-400">·</span>
            <span>{health.model}</span>
          </div>
        )}
      </header>

      {/* Main content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar — Documents */}
        <aside className="w-72 bg-white border-r border-gray-200 flex flex-col overflow-hidden">
          <DocumentPanel />
        </aside>

        {/* Chat area */}
        <main className="flex-1 flex flex-col overflow-hidden">
          <ChatWindow />
        </main>

        {/* Toggle button for sessions */}
        <button
          onClick={() => setSessionsMinimized(!sessionsMinimized)}
          className="px-2 hover:bg-gray-100 transition-colors border-l border-gray-200 flex items-center justify-center"
        >
          {sessionsMinimized ? (
            <ChevronLeft size={18} className="text-gray-400" />
          ) : (
            <ChevronRight size={18} className="text-gray-400" />
          )}
        </button>

        {/* Sidebar — Chat sessions */}
        {!sessionsMinimized && (
          <aside className="w-80 bg-white border-l border-gray-200 flex flex-col overflow-hidden">
            <ChatSessionsPanel />
          </aside>
        )}
      </div>
    </div>
  );
}
