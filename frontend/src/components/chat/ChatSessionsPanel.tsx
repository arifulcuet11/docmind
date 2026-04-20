import { Plus, MessageSquare, Trash2 } from "lucide-react";
import { useDocMindStore } from "../../store";

export function ChatSessionsPanel() {
  const {
    chatSessions,
    activeSessionId,
    createChatSession,
    setActiveSession,
    deleteChatSession,
  } = useDocMindStore();

  const handleNewChat = () => createChatSession(`New chat ${chatSessions.length + 1}`);

  return (
    <div className="flex flex-col h-full bg-white">
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between gap-3">
          <div>
            <h2 className="font-semibold text-gray-800">Chats</h2>
            <p className="text-xs text-gray-400 mt-1">Create a new chat for each project</p>
          </div>
          <button
            onClick={handleNewChat}
            className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-3 py-2 text-xs font-semibold text-white transition hover:bg-blue-700"
          >
            <Plus size={14} /> New
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-3 py-4">
        {chatSessions.length === 0 ? (
          <div className="text-sm text-gray-500">No chats yet. Create one to get started.</div>
        ) : (
          <ul className="space-y-2">
            {chatSessions.map((session) => {
              const isActive = session.id === activeSessionId;
              return (
                <li key={session.id}>
                  <button
                    onClick={() => setActiveSession(session.id)}
                    className={`flex w-full items-center justify-between gap-3 rounded-2xl px-4 py-3 text-left transition ${
                      isActive ? "bg-blue-50 text-blue-900" : "bg-gray-50 text-gray-700 hover:bg-gray-100"
                    }`}
                  >
                    <div className="flex items-center gap-3 truncate">
                      <MessageSquare size={16} className={isActive ? "text-blue-500" : "text-gray-400"} />
                      <div className="truncate">
                        <div className="font-medium truncate">{session.name}</div>
                        <div className="text-xs text-gray-400 truncate">
                          {new Date(session.updatedAt).toLocaleString()}
                        </div>
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={(event) => {
                        event.stopPropagation();
                        deleteChatSession(session.id);
                      }}
                      className="rounded-full p-1 text-gray-400 hover:text-red-500"
                      title="Delete chat"
                    >
                      <Trash2 size={14} />
                    </button>
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </div>
    </div>
  );
}
